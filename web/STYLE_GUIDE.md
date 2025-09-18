# LeftLeak UI/UX Rules (Single‑Page Template)

These rules govern the entire Next.js app. All screens are variants of one template; UI elements change in place — no route changes for the chat flow.

1) Core principles
- Single page interaction: no client-side navigation after first render. All state transitions happen within `src/app/page.tsx`.
- Minimal, legible, high-contrast text on a soft background. No competing accent colors on text.
- Smooth but subtle motion (<= 600ms), no bouncing.

2) Fonts
- Stack: system UI stack with Inter fallback: `-apple-system, BlinkMacSystemFont, 'Segoe UI', var(--font-inter), system-ui, sans-serif`.
- Headings: weight 800 (extrabold), tight tracking.
- Body: 400–500; never below 14px.

3) Colors
- Text: #0F172A to #111827 (Tailwind gray-900). Secondary text: gray-600.
- Surfaces (cards/chat): white with 90–95% opacity, subtle blur.
- Accents: pink→purple for small highlights (buttons/loader). Never for paragraph text.

4) Layout
- Header brand “LeftLeak” pinned at top on all states.
- First view: centered hero (title + prompt). On first prompt, the hero collapses in place (no navigation) and messages area takes focus.
- After first prompt, the input docks to the bottom bar.

5) Chat box
- Large, borderless textarea inside a rounded white card.
- Focus: neutral dark ring (no red/blue system outlines). No inner borders.
- Max width: 80ch (max-w-5xl) on desktop.

6) Motion
- `animate-fade-in` for entrance.
- `animate-slide-up` for small text transitions.
- Hero uses `.hero`, `.hero--center`, `.hero--hidden` (CSS in globals.css) to collapse/expand.

7) Loading
- Inline loading card with three dots + thin progress bar, accent gradient.

8) Follow-ups
- Shown beneath the last assistant message when idle; selectable buttons.

9) Accessibility
- Keyboard submit: Enter (Shift+Enter for newline).
- Focus styles visible and neutral (rgba(0,0,0,.35)).
- Sufficient color contrast (WCAG AA) for all text.

10) Branding
- App name: LeftLeak (exact casing) — used in header and metadata.

File map
- Page and state: `web/src/app/page.tsx`
- Components: `web/src/components/*`
- Global styles and animations: `web/src/app/globals.css`
