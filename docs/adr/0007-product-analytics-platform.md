# ADR-0007: Product Analytics Platform

**Date**: 2026-05-06
**Status**: accepted

## Context

JDs for game monetization analyst roles routinely require fluency in at least one product analytics platform — Amplitude, GameAnalytics, Unity Analytics, Firebase, or deltaDNA. Direct hands-on experience with one of these signals "can do the work" more strongly than any infrastructure piece.

## Decision

Adopt **Amplitude** (Spark plan, free up to 10M events/month) as the primary product analytics platform. Instrument a small set of synthetic events to gain hands-on familiarity.

## Alternatives

- **GameAnalytics** — purpose-built for games with more game-specific features out of the box and a generous free tier (up to 2M MAU). Rejected as primary because it's a niche tool for indie/mobile studios. Lower portability across the 20% fallback adjacent verticals (e-commerce, SaaS, fintech).
- **Unity Analytics** — only useful inside Unity-built games. Rejected as too narrow.
- **Firebase Analytics** — free, ubiquitous in mobile, but less strong on the analyst-facing analysis surface. Rejected as primary; could be added later as a free secondary.
- **deltaDNA** — strong gaming pedigree but smaller ecosystem and reduced market presence after the Unity acquisition. Rejected.

## Consequences

- Amplitude is recognized across SaaS, e-commerce, fintech, and gaming JDs — one tool covers both the 80% goal (gaming) and the 20% fallback (cross-vertical analytics).
- Amplitude's event taxonomy assumptions are SaaS-leaning; some adaptation needed for game-specific events (sessions, levels, IAPs). Manageable.
- Free tier of 10M events/month is more than generous for synthetic-data portfolio work.
