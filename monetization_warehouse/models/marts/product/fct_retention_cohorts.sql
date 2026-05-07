{{
  config(
    materialized = 'table',
    cluster_by = ['cohort_date']
  )
}}

-- Cohort retention. Grain: (cohort_date, day_offset). One row per cohort ×
-- day-offset combination, with cohort_size, retained_users, retention_rate.
--
-- Cohort definition: cohort_date = user's first_seen_date (UTC). All users
-- whose first session falls on cohort_date are in that cohort.
--
-- Day offset: integer days after cohort_date (0..30). day_offset=0 is the
-- install/first-session day itself (always 100% by construction). D1 is
-- day_offset=1; D7 is 7; D30 is 30.
--
-- Retention rule: a user is "retained on day N" if they have any active
-- Flood-It event on date = cohort_date + N. Calendar-day boundaries in UTC.
-- Industry norm uses user-local time; we use UTC for simplicity and
-- because Flood-It's geo data is country-grain only (no IANA tz).
--
-- Right-censoring: cohorts late in the data window cannot reach D30. Rows
-- where cohort_date + day_offset exceeds the latest available date are
-- omitted entirely so retention_rate is never artificially deflated by
-- missing follow-up data.

with first_seen as (
    select
        user_pseudo_id,
        first_seen_date as cohort_date
    from {{ ref('dim_players') }}
),

activity as (
    select distinct
        user_pseudo_id,
        event_date
    from {{ ref('fct_revenue_daily') }}
    where is_active_today
),

max_date as (
    select max(event_date) as last_event_date from activity
),

day_offsets as (
    select day_offset
    from unnest(generate_array(0, 30)) as day_offset
),

cohort_offset_pairs as (
    select
        fs.cohort_date,
        fs.user_pseudo_id,
        d.day_offset,
        date_add(fs.cohort_date, interval d.day_offset day) as expected_activity_date
    from first_seen fs
    cross join day_offsets d
    cross join max_date m
    where date_add(fs.cohort_date, interval d.day_offset day) <= m.last_event_date
)

select
    cop.cohort_date,
    cop.day_offset,
    count(distinct cop.user_pseudo_id) as cohort_size,
    count(distinct a.user_pseudo_id)   as retained_users,
    safe_divide(
        count(distinct a.user_pseudo_id),
        count(distinct cop.user_pseudo_id)
    ) as retention_rate
from cohort_offset_pairs cop
left join activity a
    on a.user_pseudo_id = cop.user_pseudo_id
    and a.event_date    = cop.expected_activity_date
group by cop.cohort_date, cop.day_offset
