# Target User Profile

## Who Uses Campus

People who have already purchased an Arkandia workshop and need to access their content. They are the same personas as the arkandia.co buyer profile, but now in **learner mode** — they've already committed, and their expectations shift from "convince me" to "deliver what I paid for."

## Learner Personas

### 1. The Busy Senior Dev

- Bought the workshop but has limited time between work and life
- Needs quick access to specific sessions — wants to jump in, watch, and leave
- Values downloadable resources for offline review (commute, travel)
- Frustrated by slow loading, confusing navigation, or needing to re-authenticate
- **Campus priority:** Fast page loads, clear content organization, persistent sessions

### 2. The Methodical Tech Lead

- Wants to go through content sequentially, session by session
- Needs clear session order, cohort context (dates, title), and supplementary materials
- May share learnings with their team — values well-organized reference material
- **Campus priority:** Ordered content list with position-based sequencing, cohort metadata

### 3. The Returning Architect

- Has purchased multiple offerings across different topics
- Needs a dashboard that scales to N offerings without clutter
- Expects a clean, no-nonsense interface that respects their time and seniority
- **Campus priority:** Multi-offering dashboard, easy navigation between offerings

## Common Traits

- **Experience level:** 5+ years in software development
- **Technical sophistication:** Know what APIs, design patterns, and architecture trade-offs are — no hand-holding needed
- **Language:** Primarily Spanish-speaking (Latin America), English as secondary
- **Time-constrained:** Professionals balancing learning with demanding jobs
- **Mindset:** Pragmatic, anti-hype, values fundamentals over trends
- **Trust already earned:** They paid — Campus must not break that trust with a poor experience

## Who Does NOT Use Campus

- **Browsers and prospects** — they use arkandia.co, not Campus
- **Non-purchasers** — they see an empty dashboard with a redirect message
- **Admins** — there is no admin panel; data is managed via direct SQL

## Implications for Development

| Trait | Implication |
|---|---|
| Time-constrained | Minimize clicks to content. Fast loads. No unnecessary steps. |
| Spanish-first | All UI copy in es-CO. Date formatting with `es-CO` locale. |
| Technically sophisticated | Clean information density. No hand-holding UI or tooltips. |
| Multiple purchases | Dashboard must scale to many offerings without pagination issues. |
| Trust already earned | Reliability over features — the basics must always work. |
| Anti-hype mindset | No gamification, badges, or engagement tricks. Just the content. |
