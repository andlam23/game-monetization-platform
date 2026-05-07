{{
  config(
    materialized = 'view'
  )
}}

-- 1:1 staging from Flood-It's daily-sharded GA4 event tables.
-- Light cleaning only: rename columns, cast types, extract event_params,
-- filter rows that lack a usable user identifier. No business logic.
--
-- ADR-0012: staging models read from source() only, never from another
-- staging model. `floodit` source declared in _floodit__sources.yml.
--
-- Cross-project query cost discipline: filter on _TABLE_SUFFIX so we
-- don't scan tables outside our window on every refresh. The actual
-- populated data ends 2018-10-03 (later daily-sharded tables exist but
-- are empty); the filter is set wider to '20181231' as a defensive
-- guard in case Flood-It is ever extended — costs nothing because
-- empty tables don't contribute bytes scanned.

with source as (
    select
        event_timestamp                                            as event_timestamp_us,
        timestamp_micros(event_timestamp)                          as event_timestamp,
        parse_date('%Y%m%d', _table_suffix)                        as event_date,
        event_name,
        user_pseudo_id,
        geo.country                                                as country,
        platform,
        device.category                                            as device_category,
        device.operating_system                                    as device_os,
        traffic_source.name                                        as traffic_source_name,
        traffic_source.medium                                      as traffic_source_medium,
        traffic_source.source                                      as traffic_source_source,
        -- engagement_time_msec is the only meaningful numeric param across
        -- most events; pull it out so downstream models don't unnest.
        (select value.int_value from unnest(event_params)
            where key = 'engagement_time_msec')                    as engagement_time_msec
    from {{ source('floodit', 'events') }}
    where _table_suffix between '20180801' and '20181231'
      and user_pseudo_id is not null
)

select * from source
