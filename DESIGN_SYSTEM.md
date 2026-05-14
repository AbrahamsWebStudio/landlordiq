# Design System — LandlordIQ

This document records the canonical design tokens, component guidance, and usage rules to match the Figma system.

## Color Tokens (Tailwind)
- `brand` : #2D5A27
- `brand-dark` : #1e3a1e
- `brand-muted` : #3A6B35
- `brand-deep` : #142E14
- `bg-primary` : #d4e8d2
- `bg-sidebar` : #1a2e1a
- `bg-card` : #FFFFFF
- `text-primary` : #1a2e1a
- `text-muted` : #a3c9a0
- `text-white` : #FFFFFF
- `ui-success` : #4CAF50
- `ui-danger` : #e63946
- `ui-warning` : #f4a261
- `ui-info` : #175281

These tokens are defined in `tailwind.config.js` under `theme.extend.colors`. Use token classes (e.g. `bg-brand`, `text-text-muted`, `bg-ui-success`) rather than raw hex values.

## Typography
- Primary family: `DM Sans` (vendored in `static/fonts/DM_Sans`)
- Sizes follow the Tailwind scale; custom sizes are defined in `tailwind.config.js` (`heading-1`, `body-base`, etc.).

## Components (canonical)
- Buttons: use `templates/components/button.html` partial. Variants: `primary` → `bg-brand text-white hover:bg-brand-dark`, `ghost` → `bg-transparent border border-brand-muted`.
- Stat cards: `templates/components/stat_card.html` — consumes `icon`, `icon_color`, `value`, `label`, `trend`, `trend_color`. Pass token class names for colors (e.g. `text-brand`, `text-ui-success`).
- Chart bars: supply `color` as either a hex string (`#rrggbb`) or a Tailwind class (e.g. `bg-ui-success`). The chart partial supports both.

## Rules / Workflow
1. Always map a new color to a token in `tailwind.config.js` before using it in templates.
2. Update or add component partials in `templates/components/` so screens compose from canonical parts.
3. Avoid inline hex colors in templates; leave inline style only for dynamic numeric values (height, widths) or for third-party assets.
4. Vendor fonts and icons locally under `static/fonts/` and `static/vendor/` (already done).

## Next steps for QA
- Run `python manage.py collectstatic --noinput` and visually check pages listed in `templates/dashboard/index.html` and `templates/properties/list.html` against Figma.
- If any component appears off, adjust token hex values in `tailwind.config.js` (this keeps visuals consistent across files).

---
Generated as part of the host-vendor-assets finalization patch.
