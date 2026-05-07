{{
  config(
    materialized = 'table',
    cluster_by = ['user_pseudo_id']
  )
}}

-- Lifetime stats per player. Grain: user_pseudo_id (unique).
--
-- Sources fct_revenue_daily for the per-day rollups, and the synthetic_iap
-- staging for the payer_segment label (whale/dolphin/minnow), since segment
-- is assigned at generation time per ADR-0013's percentile classification.
--
-- Non-payers get payer_segment = 'non_payer' so the column is NOT NULL.

with daily as (
    select * from {{ ref('fct_revenue_daily') }}
),

payer_segments as (
    select
        user_pseudo_id,
        any_value(payer_segment) as payer_segment
    from {{ ref('stg_synthetic_iap__events') }}
    group by user_pseudo_id
),

aggregated as (
    select
        user_pseudo_id,
        any_value(country)                            as country,
        min(event_date)                               as first_seen_date,
        max(event_date)                               as last_seen_date,
        count(distinct case when is_active_today then event_date end) as days_active,
        sum(ad_revenue_usd)                           as total_ad_revenue_usd,
        sum(iap_revenue_usd)                          as total_iap_revenue_usd,
        sum(total_revenue_usd)                        as ltv_usd,
        sum(iap_purchase_count)                       as total_iap_purchases,
        min(case when is_paying_today then event_date end) as first_purchase_date
    from daily
    group by user_pseudo_id
)

select
    a.user_pseudo_id,
    a.country,
    a.first_seen_date,
    a.last_seen_date,
    a.days_active,
    a.total_ad_revenue_usd,
    a.total_iap_revenue_usd,
    a.ltv_usd,
    a.total_iap_purchases,
    a.first_purchase_date,
    a.first_purchase_date is not null              as is_payer,
    coalesce(p.payer_segment, 'non_payer')         as payer_segment
from aggregated a
left join payer_segments p using (user_pseudo_id)
