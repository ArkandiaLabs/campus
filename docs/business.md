# Business Context

## What is Arkandia Campus

Arkandia is an education and consulting company founded by **Manuel Zapata** and **David Lopera**, both software architects and educators. Manuel has 19+ years of experience and a 46K+ developer community on YouTube. The company teaches software architecture and AI-assisted development to experienced developers in Latin America.

**Arkandia Campus** is the post-purchase learning portal at [campus.arkandia.co](https://campus.arkandia.co). It is where paying customers access the content they purchased — recorded sessions, downloadable resources, and reference links.

Campus does not sell anything. Purchases happen on external platforms (Gumroad, Hotmart, etc.) and are recorded in a shared database. Campus reads those records and grants access accordingly.

## How it Fits in the Arkandia Ecosystem

| | arkandia.co | campus.arkandia.co |
|---|---|---|
| **Purpose** | Marketing, content, sales | Content delivery, learning |
| **Users** | Visitors, prospects | Paying customers |
| **Auth** | None (static site) | Email + password login |
| **Checkout** | Links to Gumroad / Hotmart | None |

When a sale is recorded with a matching customer email, Campus can show that offering on the user's dashboard.

## Revenue Model

Campus generates no direct revenue. It is a **delivery and retention tool**.

- Revenue comes from workshop and course sales on external platforms (Gumroad, Hotmart, direct sales, in-person events)
- Pricing is tiered per workshop (e.g., On Demand $99-129, Live $159-199, Architect $299-399)
- Early-bird pricing with time-limited deadlines is used on the sales site

## Target Audience

See [docs/target-user.md](target-user.md) for the full profile.

**Summary:** Senior developers, tech leads, and software architects (5+ years) in Latin America who have already purchased an Arkandia workshop. They expect a professional, no-frills experience that respects their time and technical sophistication.

## Brand Voice

- **Direct and practical** — no corporate fluff, no marketing superlatives
- **Anti-hype** — focused on patterns and fundamentals, not trends
- **Spanish-first** — all UI copy in Spanish (es-CO), using "tuteo" (informal *tu*, not *usted*)
- **Peer-level** — speaks developer-to-developer, not teacher-to-student
- Examples from actual UI: "Hola, {firstName}", "Mis workshops", "Aun no tienes productos"

