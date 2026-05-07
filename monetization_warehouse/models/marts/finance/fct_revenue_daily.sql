{{
  config(
    materialized = 'table',
    partition_by = {
      'field': 'event_date',
      'data_type': 'date',
      'granularity': 'day'
    },
    cluster_by = ['user_pseudo_id']
  )
}}

-- Per-day-per-player revenue and activity. Grain: (event_date, user_pseudo_id).
--
-- Combines three sources:
--   * Real Flood-It activity (gameplay events) — drives DAU
--   * Synthetic ad revenue layer (per ADR-0013)
--   * Synthetic IAP layer (per ADR-0013 amendment)
--
-- Both revenue components are nullable per row: a player active that day
-- may have no ad fills and no purchases. Coalesced to 0 in the totals.
--
-- Row inclusion rule: a row exists for (date, user) if the user had ANY
-- of: a Flood-It event, an ad event, an IAP that day. Pure inactive
-- user-days produce no row (DAU is COUNT DISTINCT against this table).

with floodit_activity as (
    select
        event_date,
        user_pseudo_id,
        any_value(country) as country,
        count(*)           as floodit_event_count
    from {{ ref('stg_floodit__events') }}
    group by event_date, user_pseudo_id
),

ad_daily as (
    select
        event_date,
        user_pseudo_id,
        sum(case when event_name = 'ad_request'    then 1 else 0 end) as ad_request_count,
        sum(case when event_name = 'ad_impression' then 1 else 0 end) as ad_impression_count,
        sum(case when event_name = 'ad_revenue'    then revenue_usd else 0 end) as ad_revenue_usd
    from {{ ref('stg_synthetic_ads__events') }}
    group by event_date, user_pseudo_id
),

iap_daily as (
    select
        event_date,
        user_pseudo_id,
        count(*)            as iap_purchase_count,
        sum(price_usd)      as iap_revenue_usd
    from {{ ref('stg_synthetic_iap__events') }}
    group by event_date, user_pseudo_id
),

unioned_keys as (
    select event_date, user_pseudo_id from floodit_activity
    union distinct
    select event_date, user_pseudo_id from ad_daily
    union distinct
    select event_date, user_pseudo_id from iap_daily
)

select
    k.event_date,
    k.user_pseudo_id,
    coalesce(f.country, 'unknown')                                   as country,
    coalesce(f.floodit_event_count, 0)                               as floodit_event_count,
    coalesce(a.ad_request_count, 0)                                  as ad_request_count,
    coalesce(a.ad_impression_count, 0)                               as ad_impression_count,
    coalesce(a.ad_revenue_usd, 0)                                    as ad_revenue_usd,
    coalesce(i.iap_purchase_count, 0)                                as iap_purchase_count,
    coalesce(i.iap_revenue_usd, 0)                                   as iap_revenue_usd,
    coalesce(a.ad_revenue_usd, 0) + coalesce(i.iap_revenue_usd, 0)   as total_revenue_usd,
    f.user_pseudo_id is not null                                     as is_active_today,
    coalesce(i.iap_purchase_count, 0) > 0                            as is_paying_today
from unioned_keys k
left join floodit_activity f using (event_date, user_pseudo_id)
left join ad_daily         a using (event_date, user_pseudo_id)
left join iap_daily        i using (event_date, user_pseudo_id)
