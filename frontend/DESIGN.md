---
version: alpha
name: Arkandia
description: Warm amber warmth, cool blue precision, flat discipline.

colors:
  # Primitives
  amber-500: "#FBB03B"
  amber-600: "#E89A2A"
  amber-700: "#D08819"
  amber-200: "#FBD68B"
  stone-500: "#78716C"
  sapphire-500: "#3B86FB"
  parchment-50: "#FEFAF6"
  cream-100: "#F1E9DA"
  ink-900: "#000000"
  white: "#FFFFFF"
  crimson-800: "#991B1B"

  # Semantic
  primary: "{colors.amber-500}"
  primary-hover: "{colors.amber-600}"
  primary-active: "{colors.amber-700}"
  primary-disabled: "{colors.amber-200}"
  secondary: "{colors.stone-500}"
  tertiary: "{colors.sapphire-500}"
  neutral: "{colors.parchment-50}"
  surface: "{colors.cream-100}"
  on-primary: "{colors.ink-900}"
  on-secondary: "{colors.white}"
  on-tertiary: "{colors.white}"
  foreground: "{colors.ink-900}"
  destructive: "{colors.crimson-800}"
  on-destructive: "{colors.white}"
  focus-ring: "{colors.sapphire-500}"

typography:
  h1:
    fontFamily: Aleo
    fontSize: 2.25rem
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  h2:
    fontFamily: Aleo
    fontSize: 1.5rem
    fontWeight: 700
    lineHeight: 1.25
  body:
    fontFamily: Rubik
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: Rubik
    fontSize: 0.875rem
    fontWeight: 500
    lineHeight: 1.4
  code:
    fontFamily: Fira Code
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.5

rounded:
  sm: 3px
  md: 6px
  lg: 12px

spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
---

## Overview

Arkandia is a warm, editorial design system. Amber gold anchors all primary actions; a cool sapphire blue handles links and accents. Aleo serif headlines lend intellectual weight; Rubik keeps the UI approachable. Corners are near-flat — discipline over decoration.

This file is the contract between humans, designers, and AI coding agents. Tokens are the normative values; prose explains how to apply them. Agents must consume tokens from this file and never invent new ones.

## Colors

The palette is built on warm earth tones with a single cool accent. Tokens are organized in two layers.

**Primitives** are the raw values. They carry no meaning, only appearance. Components must not reference primitives directly.

**Semantics** describe role and intent. Components reference these. Changing a brand or theme means swapping semantic mappings, never editing component code.

Semantic mapping:

- **Primary (amber gold):** the single driver of primary interaction.
- **Secondary (warm stone):** captions, metadata, and muted borders.
- **Tertiary (sapphire blue):** links and accent UI; never primary actions.
- **Neutral (warm parchment):** the page foundation, softer than pure white.
- **Surface (toasted cream):** cards and elevated regions.
- **Foreground (pure ink):** all primary text.
- **Destructive (deep crimson):** errors and irreversible actions only.

State colors (`primary-hover`, `primary-active`, `primary-disabled`, `focus-ring`) live as semantic tokens so components never compute states with opacity hacks or filter functions.

## Typography

Three typefaces cover all roles. Do not introduce a fourth.

- **h1, h2:** Aleo, editorial weight for headlines and section titles.
- **body:** Rubik 1rem with 1.5 line-height, humanist sans for UI prose.
- **label:** Rubik 0.875rem at weight 500, for form labels, tags, and metadata.
- **code:** Fira Code 0.875rem, for inline and block code.

Pair Aleo headlines with Rubik body. Never use Aleo for body copy or Rubik for headline-level text.

## Layout

Spacing follows an 8px grid via the `spacing` tokens, with a 4px half-step (`xs`) for micro-adjustments. Content breathes at moderate density.

Components must be fluid by default. Assume any component renders between 320px and 1920px wide. Avoid component-local breakpoints; prefer container queries and fluid units (`clamp()`, `%`, `rem`) so behavior scales without media query proliferation.

Tap targets for any interactive control on touch surfaces must be at least 44 × 44px.

## Shapes

Corners use a near-flat 3px radius (`rounded.sm`) by default. Arkandia is angular and precise — no pill buttons, no excessive softening. The square feel is intentional and load-bearing.

`rounded.md` and `rounded.lg` exist for cards and large containers, never for buttons or inputs.

## Do's and Don'ts

- **Do** use Primary (amber) for exactly one call-to-action per screen.
- **Do** pair Aleo headlines with Rubik body text for editorial contrast.
- **Do** keep button and input corners at `rounded.sm` (3px).
- **Do** maintain WCAG AA contrast (4.5:1 for body text, 3:1 for large text and UI controls).
- **Do** render a visible focus ring on every interactive element.
- **Don't** use Tertiary (sapphire) for primary actions. Reserve it for links and accent UI.
- **Don't** introduce gradients or decorative shadows. This system is flat on purpose.
- **Don't** mix warm and cool accent colors inside the same component.
- **Don't** hardcode hex values, pixel values, or millisecond timings in component code. Use tokens.
- **Don't** suppress the focus ring without an equivalent replacement.
