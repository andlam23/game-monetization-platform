{{
  config(
    materialized = 'view'
  )
}}

-- 1:1 staging from raw.synthetic_ad_events. Light cleaning only:
-- cast event_date to DATE, normalize a TIMESTAMP from the event_timestamp_us
-- microsecond epoch. Forwards the is_synthetic flag downstream — every row
-- coming out of this model is True.

with source as (
    select
        event_timestamp_us,
        timestamp_micros(event_timestamp_us)                       as event_timestamp,
        cast(event_date as date)                                   as event_date,
        user_pseudo_id,
        ga_session_id,
        event_name,
        placement,
        ad_unit,
        country,
        ad_network,
        ecpm_usd,
        revenue_usd,
        is_synthetic
    from {{ source('synthetic_ads', 'synthetic_ad_events') }}
)

select * from source
