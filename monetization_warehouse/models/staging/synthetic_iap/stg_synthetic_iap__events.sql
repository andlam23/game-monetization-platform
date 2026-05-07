{{
  config(
    materialized = 'view'
  )
}}

-- 1:1 staging from raw.synthetic_iap_events. Same shape conventions as the
-- other staging models. payer_segment passed through unchanged — it's a
-- denormalized cohort label assigned at generation time, useful in marts.

with source as (
    select
        event_timestamp_us,
        timestamp_micros(event_timestamp_us)                       as event_timestamp,
        cast(event_date as date)                                   as event_date,
        user_pseudo_id,
        ga_session_id,
        event_name,
        product_id,
        product_category,
        price_usd,
        country,
        payer_segment,
        is_synthetic
    from {{ source('synthetic_iap', 'synthetic_iap_events') }}
)

select * from source
