# ADR-0001: AI Workflow Framework

**Date**: 2026-05-06
**Status**: accepted

## Context

This project relies heavily on AI-assisted development via Claude Code. Without a structured workflow, AI-assisted projects tend toward "vibes-driven" output — inconsistent code quality, missing reviews, no security audits, and documentation that drifts from reality. Several workflow frameworks exist (gstack, Superpowers, GSD/get-shit-done, Hermes Agent, VoltAgent's awesome-agent-skills, Anthropic's official skills, TurboDocx).

## Decision

Adopt **gstack** as the AI workflow framework, with a **full install** rather than selective install. gstack is an opinionated, role-based "engineering team in a box" sprint workflow with explicit slash commands for product strategy (`/office-hours`, `/plan-ceo-review`), engineering planning (`/plan-eng-review`), code review (`/review`), shipping (`/ship`), security audits (`/cso`), documentation maintenance (`/document-release`), investigation (`/investigate`), and learning capture (`/learn`).

Full install accepted because the noise from unused slash commands (the design pipeline: `/design-shotgun`, `/design-html`, etc.) is judged less costly than the friction of a selective install and missing a useful tool later.

## Alternatives

- **Superpowers** — stronger TDD discipline (RED-GREEN-REFACTOR), but narrower scope. Rejected because monetization data work is more about analysis discipline than test discipline.
- **GSD / get-shit-done** — better for context-rot during long sessions, but doesn't cover product/engineering/security/docs at the breadth gstack does.
- **VoltAgent's awesome-agent-skills (1000+ skills)** — too broad; library of building blocks rather than an opinionated workflow.
- **Selective gstack install** — rejected for now because the cost of curating which slash commands to enable is higher than the cost of ignoring the unused ones. Revisit if the design pipeline becomes intrusive.

## Consequences

- Some gstack slash commands (the design pipeline) will be visible but unused. Acceptable noise.
- gstack is biased toward consumer/SaaS shipping, not data engineering. Some prompts (e.g., `/office-hours`) will need pushback during use to avoid the "ship the 10-star consumer product" framing in a domain where the right answer is often "ship the boring thing the analyst can use."
- The custom monetization skill (built per ADR-0010 methodology) will need to encode the domain context that gstack lacks.
