# Phase 2 — IoTSense design system and interaction specification

**Status:** Initial design specification, ready to guide the Phase 3 prototype.

**Depends on:** [Phase 1 UX blueprint](phase-1-ux-blueprint.md)

**Scope:** Establish the shared visual language, reusable components, responsive rules, accessibility requirements and interaction patterns for the IoTSense web application. This is a design specification; it does not yet implement React components.

## 1. Design principles

1. **Operational clarity first.** A user should recognize status, freshness and next action at a glance.
2. **Show the evidence.** Scores and causes must expose the source inputs, time window, data quality and whether they are live or simulated.
3. **Calm, technical visual language.** Use a restrained clinical/industrial IoT style: neutral surfaces, strong typography, clear dividers and limited accent color.
4. **One meaning per color.** Status colors remain consistent throughout the product and are always paired with a text label/icon.
5. **Accessible density.** Dense operational tables are acceptable when row spacing, contrast, labels and focus states remain readable.
6. **No hidden data substitution.** Missing, invalid or stale readings have explicit states and are never visually styled as current readings.

## 2. Visual identity

### Tone

Professional, measured and practical. Avoid playful gradients, alarmist language, decorative dashboards, glowing effects and marketing claims about AI or “guaranteed cleanliness.”

### Base palette

The following initial values are proposed design tokens. Review them in the Phase 3 prototype for contrast and legibility before treating them as final.

| Token | Hex | Usage |
|---|---|---|
| `color.canvas` | `#F5F7FA` | Main application background |
| `color.surface` | `#FFFFFF` | Cards, panels, menus and forms |
| `color.surface-subtle` | `#EEF2F6` | Secondary row, input and panel background |
| `color.border` | `#D8E0E8` | Dividers, outlines and table borders |
| `color.text-primary` | `#17212B` | Main text and headings |
| `color.text-secondary` | `#526170` | Supporting text and labels |
| `color.text-muted` | `#687887` | Timestamps and low-priority metadata; verify contrast per use |
| `color.brand` | `#176B87` | Primary brand, links and primary actions |
| `color.brand-hover` | `#11566E` | Hover/active brand state |
| `color.focus` | `#2563EB` | Keyboard focus ring |
| `color.clean` | `#18794E` | Clean status and positive completion |
| `color.clean-bg` | `#E9F7EF` | Clean status soft background |
| `color.moderate` | `#986000` | Moderate/caution status |
| `color.moderate-bg` | `#FFF4D6` | Moderate status soft background |
| `color.dirty` | `#B42318` | Dirty/critical status |
| `color.dirty-bg` | `#FEECEB` | Dirty status soft background |
| `color.offline` | `#596579` | Offline/unknown device status |
| `color.offline-bg` | `#EEF1F5` | Offline status soft background |
| `color.cleaning` | `#5B4BC4` | Cleaning task in progress |
| `color.cleaning-bg` | `#F0EDFF` | Cleaning status soft background |
| `color.info` | `#145DA0` | Informational state |
| `color.info-bg` | `#EAF3FC` | Informational background |

**Color rule:** Do not encode status using hue alone. A status badge must include a readable word and may include a distinct icon. Do not use clean green to mean “no recent alert” when sensor data is unknown.

### Typography

- Use a neutral system sans-serif stack for Phase 3; avoid loading a custom font before performance and licensing are considered.
- Base body text: 14–16 px, line-height 1.45–1.6.
- Small labels/metadata: 12–13 px with sufficient contrast; do not use small text for essential warnings.
- Page title: 24–30 px, semibold; section title: 18–20 px; card title: 15–17 px; body: 14–16 px.
- Numeric score values may be large, but the status label, scale and timestamp must remain nearby.
- Use tabular numerals for readings, counts and timestamps when supported.
- Use sentence case for navigation and controls. Avoid all-caps except short mode/status badges.

## 3. Layout and spacing

### Grid and shell

- Desktop application shell: fixed-width left navigation with a flexible content area; top bar stays aligned across authenticated pages.
- Main content maximum width: approximately 1440 px; use wider space for tables and analytics, narrower reading width for forms and explanations.
- Desktop page padding: 24–32 px. Tablet: 20–24 px. Mobile: 16 px.
- Use a 4 px base spacing unit. Typical steps: 4, 8, 12, 16, 24, 32, 40, 48.
- Cards use consistent 16–20 px internal padding; increase only for primary score/hero panels.
- Align repeated cards and form labels to shared grid lines. Avoid uneven card heights unless content needs it.

### Responsive breakpoints

| Name | Width guideline | Behavior |
|---|---:|---|
| Mobile | `< 640 px` | One-column content; drawer/menu navigation; tables become labeled stacked rows or horizontally scroll within a named region; filters collapse into a panel |
| Tablet | `640–1023 px` | Compact navigation or drawer; two-column cards when readable; charts stack if labels collide |
| Desktop | `1024–1439 px` | Sidebar plus main content; dashboard grids; normal tables |
| Wide | `≥ 1440 px` | Keep a readable content max-width; use extra space for side-by-side detail panels rather than stretching text |

Do not hide critical device-offline, stale-data, alert or simulation labels on smaller screens. Mobile forms and task actions should remain reachable without hover.

## 4. Shape, elevation and icon rules

- Card/button radius: 8 px; larger modal/panel radius: 10–12 px. Use one radius family.
- Prefer borders and surface contrast over heavy shadows. Use a light shadow only for floating menus/dialogs.
- Icons should come from one consistent line-icon set. Pair unfamiliar icons with text; status icons do not replace status labels.
- Avoid illustration or animation that competes with sensor state and work queues.
- Motion is functional and short: 120–200 ms for hover/open transitions. Respect reduced-motion preferences. No flashing status indicators.

## 5. Core component specifications

### Application shell

- Sidebar shows logo/product name and primary routes, then grouped support/admin routes.
- Current route has a clear selected state with icon plus text; do not rely on background tint alone.
- Top bar includes selected organization/site context, page breadcrumb/title, notifications and profile menu.
- Mobile shell exposes the same route destinations through a labeled menu/drawer.

### Mode banner

- Required whenever displayed data is simulated/sample or a page has mixed source data.
- **Live Hardware:** small neutral/green-blue label only when there is recent authenticated device data; include “Last live update” timestamp.
- **Simulation:** persistent high-visibility blue/purple banner with scenario name and generated-data label.
- **Sample Data:** use only in prototype/public demo; make clear the values are examples.
- If live data is stale, show **STALE / LAST LIVE UPDATE …**; never let a “Live” label imply fresh when last update exceeds the configured threshold.

### Status badge

- Content: icon (optional) + status text; optional short qualifier such as “Stale 4 min.”
- Use the status color/background tokens; maintain accessible text contrast.
- States: Clean, Moderate, Dirty, Cleaning, Offline, Stale, Sensor Issue and Unknown.
- Unknown must look neutral, not like a successful/clean state.

### Hygiene score card

- Show numeric score only if the engine can calculate it from sufficient valid inputs.
- Keep score band, scale (e.g. “0–100”), engine/version and freshness visible.
- Provide “How this is calculated” affordance that opens a concise explanation of inputs, rules and missing-data effect.
- If score is not valid, show “Score unavailable” plus the reason (e.g. “BME680 not reporting”) instead of a placeholder number.

### Sensor card

- Show sensor name/type, value and unit, last reading time, health/validity and data source.
- Separate raw electrical readings (ADC/voltage) from normalized relative indices and environmental units.
- Missing/stale/invalid value has explicit textual state, not a zero or blank that could be misread.
- Detail link opens sensor history/device context.

### Data table/list

- Use persistent column labels, aligned numeric columns and consistent row heights.
- Support search/filter/sort only where the data source supports it; show active filters and a clear reset.
- Row actions appear in a labeled action menu and remain keyboard-accessible.
- Provide loading skeletons, empty search results, no records, error and permission states.
- On mobile, use labeled stacked rows or a horizontally scrollable region with an accessible label; never remove key status/freshness fields.

### Chart panel

- Title, selected period, units, data source and accessible text summary accompany the chart.
- Tooltip shows timestamp, value, unit, mode, sensor/device and quality state.
- Missing periods appear as gaps; do not connect across missing intervals unless the aggregation explicitly explains it.
- Thresholds use labeled lines/bands and are distinct from observed readings.

### Alert row/detail

- List shows severity, state, washroom, opened time, most recent supporting update and assigned owner if any.
- Detail presents observed evidence and data quality before action buttons.
- Acknowledge/resolution actions require clear confirmation when consequential; state changes show actor/time and audit note.
- Offline/stale alerts do not present old sensor readings as current evidence.

### Cleaning task and event timeline

- Task card shows washroom, assignee, due time, state and linked alert.
- Timeline distinguishes task events entered by a person from sensor observations.
- Before/after evidence displays its own timestamps and quality. If absent, say “Sensor verification unavailable.”
- Completion copy refers to work recorded as done; sensor response wording remains cautious.

### Forms and dialogs

- Labels remain visible; placeholders are examples, not labels.
- Inline validation appears next to the field and is also summarized on submission when needed.
- Confirm irreversible/high-impact actions with a dialog naming the affected record/action.
- Dialogs have a clear title, cancel and explicit action button; keyboard focus is trapped and returned to opener.
- Never display device secrets in logs or persist them in client-side storage beyond the approved secure flow.

### Toasts and notifications

- Use for short success or non-blocking status updates; include the affected action/result.
- Errors that require user action stay in-page and are not communicated only by a transient toast.
- Provide an accessible announcement without moving focus unexpectedly.

## 6. Interaction rules

- **Navigation:** preserve selected filters/context when returning from a detail page where feasible; back navigation must not erase an in-progress form without warning.
- **Loading:** use skeletons for stable layouts; avoid showing stale data under a fresh loading indicator. If cached data is shown, label it as cached and show its timestamp.
- **Refresh:** indicate last update and provide manual refresh when useful. Do not imply a refresh succeeded until a response is received.
- **Filters:** apply clear labels, active filter chips and a reset action; communicate when results are empty because of filters.
- **Destructive/critical actions:** confirm, explain consequence and show completion/error result. Disable duplicate submissions while a request is pending.
- **Permission errors:** show a clear lack-of-access state with a safe route back; never reveal hidden organization data.
- **Offline behavior:** keep last-known timestamp visible; offer retry/troubleshooting; do not make failed updates look successful.
- **Simulation controls:** only authorized roles can start/stop/change a simulation; show scenario and mode across routes; clearly return to live state after exit.
- **Status changes:** explain source of change—sensor-derived, user action, rule evaluation or simulation.

## 7. Accessibility requirements

- Target WCAG 2.2 AA for the web interface as a design target; verify actual foreground/background combinations during implementation.
- All interactive controls work with keyboard; visible focus ring uses `color.focus` and is not clipped.
- Use semantic headings, landmarks, buttons/links and form labels. Maintain logical focus order.
- Provide text equivalents for chart takeaways and status; do not require color vision or hovering to understand data.
- Ensure text contrast and control boundaries remain visible in default, hover, focus, disabled and error states.
- Support zoom/reflow and reduced motion. Avoid time-limited dismissals for critical errors.
- Announce asynchronous updates with appropriate live-region semantics, without flooding screen readers on rapidly updating telemetry.
- Provide accessible names for icon-only actions and table mobile scroll regions.

## 8. Chart and data visualization conventions

- Use a consistent series palette: observed sensor data in brand blue/teal; derived score in a distinct purple/navy; thresholds as labeled dashed lines; event markers as separate icons/annotations.
- Simulation series use a visually distinct treatment and stay behind a persistent Simulation label; never blend into live series without explicit separation.
- Missing data renders as gaps. Invalid samples may be shown in a separate quality/event lane but are not plotted as normal values.
- Every axis names the metric and unit. Avoid dual axes unless necessary and clearly labeled.
- Use consistent time zone and date formatting; tooltips expose full timestamp and time zone.
- For aggregate windows, state the aggregation (e.g. mean/min/max) and number of samples when meaningful.
- Use a non-color distinction (line style, marker shape or panel label) for multiple series.

## 9. Voice and terminology

Prefer:

- “Air-quality sensor index increased” instead of “toxic gas detected.”
- “Possible contributor” or “associated indicator” instead of “cause confirmed.”
- “Sensor-based response observed after cleaning” instead of “cleaning verified” when the only evidence is sensor change.
- “Score unavailable — sensor data stale” instead of a stale numeric score styled as current.
- “Simulation data” instead of “live demo.”
- “Rule-based analysis” instead of “AI” unless a real ML capability is implemented and validated.

## 10. Design token implementation shape

When Phase 3 begins, expose design values as semantic CSS variables or Tailwind theme tokens rather than hardcoding per-screen colors. Suggested namespaces:

```text
--color-canvas / --color-surface / --color-border
--color-text-primary / --color-text-secondary / --color-text-muted
--color-brand / --color-focus
--color-status-clean / --color-status-moderate / --color-status-dirty
--color-status-offline / --color-status-cleaning / --color-status-info
--space-1 ... --space-12
--radius-control / --radius-card / --radius-dialog
--shadow-popover
```

Keep status token mapping in one place so dashboard badges, charts, alerts and device lists cannot drift in meaning.

## 11. Phase 2 completion checklist

- [x] Visual principles and proposed palette documented.
- [x] Type, spacing, shell and responsive behavior specified.
- [x] Shared components and interaction states specified.
- [x] Chart conventions distinguish raw, derived, missing and simulated data.
- [x] Accessibility and terminology rules documented.
- [ ] Review palette contrast and status terms in the Phase 3 prototype.
- [ ] Apply changes from Phase 1 review before coding final component tokens.

The system is ready to guide the prototype. Final token values remain subject to contrast and usability review in actual screens.
