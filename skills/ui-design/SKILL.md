---
name: ui-design
description: Design-first UI workflow. Draw static design pages for the user to review, and write application code only after the design is approved. Use when designing new UI, changing the look of existing UI, comparing layout options, or working in the project's design pages directory. Not for pure logic changes or bug fixes that do not change how the UI looks.
---

# UI design

These guidelines apply to any project. Paths are relative to the repository root.

## Design first

- When a UI does not exist in the code yet, always design it first. Do not write
  application code for it until the user has reviewed the design.
- Changes to the look of existing UI also start in the design pages, then move to code.
- Exception: when the user explicitly says to skip the design, or the change is a tiny
  visual tweak (for example one spacing or one colour), change the code directly, and
  say in your report that you skipped the design step.

## Find or set up the design workspace

- First look for an existing design workspace in the project (for example `design/`,
  `docs/design/`, `mockups/`) and its README or build commands, and follow its
  conventions. Where the project's conventions conflict with the rules below, the
  project wins.
- If the project has no design workspace, confirm the location and tooling with the
  user before creating one. Default proposal:
  - Source in `design/system/pages/<page>.*`, shared parts in
    `design/system/components/`, and theme values (colours, fonts, spacing) defined once
    in one file (for example `design/system/theme.*`).
  - Build output in `design/pages/<page>.html`, added to `.gitignore`.
  - Reuse the project's existing stack: if it uses JSX/TSX, render JSX to HTML at build
    time; if it uses Tailwind, use Tailwind utilities. With no frontend tooling at all,
    write plain HTML and CSS.
- Prefer normal HTML elements and CSS (or utility classes) for layout and styling, so the
  design source stays close to the final implementation. Pages do not have to be SVG;
  keep SVG where it is useful, such as icon assets.
- Never edit build output by hand. Commit the source only.
- Reuse existing components and theme values. When a part repeats, extract it into a
  component instead of copying it. Use theme values instead of literal values.
- If other design pages exist, use one as a template for the page structure, title,
  subtitle and notes.

## The design system is static

- Design pages are only static visual demos. They are not the final application and do
  not share code with it.
- The output HTML contains no JavaScript. If there is a build step, make the build fail
  when it finds JavaScript; templating (such as JSX) runs only at build time.
- Show interaction states (hover, selected, disabled, editing) as separate static
  mock-ups side by side, not as behaviour.
- Where relevant, also draw content edge cases: empty, loading, error, very long text,
  and large amounts of data.

## Page layout

A design page is a document about the UI, not the UI itself. Its layout should make
the relationships between mock-ups visible at a glance: what is the UI and what is
commentary, which views belong together, and which views are meant to be compared.

- Separate the page from the UI. Pages use a neutral light background, and page titles,
  headings and captions use dark text. Only the mock-ups use the app's own theme, so they
  read as UI on a sheet of paper. If the app itself has a light theme, give the mock-ups
  a border or shadow so the UI's edges stay clear. Do not paint the whole page in the
  app's background colour.
- Group views by logical unit. Give each unit (for example, the menus that open in one
  panel, or the states of one component) a section with a heading and a one-line
  description, separated from the previous section by a rule. Rows inside a section hold
  related variants.
- Align what is compared. Views in one row share their tracks: titles on one line,
  captions on one line, and mock-ups starting at the same height, even when one caption
  is longer or missing. Use a shared grid (for example CSS Grid with children using
  `grid-template-rows: subgrid`), not per-item offsets.
- Never let text overlap. A caption that does not fit its column wraps, and the row
  grows to fit it.
- Let content flow. Lay out sections and rows with normal flow and grids rather than
  absolute coordinates, so adding a view or a longer caption never needs manual
  repositioning.
- If the UI must support several sizes (for example mobile and desktop), show the
  mock-up for each breakpoint side by side.

## Page content

- The design system overview page (for example `00-design-system`) is the source of
  truth for shared components. Other pages and app code use its components exactly.
  Variants within a set keep one shape and differ only in colour or fill. If the project
  has no overview page yet, create it the first time you extract a shared component.
- Put notes and comments in the page margin, outside the drawn UI. Text inside a
  mock-up reads as real UI.
- Show each fact once. Do not add hints, labels or buttons the user did not ask for.
- When proposing options, draw them side by side on one page with a short note each,
  and let the user pick.
- Keep text contrast readable (WCAG AA as the baseline), and do not rely on colour alone
  to convey state.

## UI text

All text on a design page goes through the unslop rules: text inside mock-ups (labels,
buttons, headings, empty states, error messages, placeholder content) and the page's own
titles, descriptions and margin notes.

- Read `../unslop/SKILL.md` (the `unslop` skill next to this one) before writing any
  text, and apply its rules while writing, not only as a later pass. The unslop skill
  is user-invoked only, so read the file instead of calling it as a skill. If the file
  is missing, tell the user and continue without it.
- Its Chinese rules (34 to 37) apply to Chinese UI text.
- Short UI labels such as buttons, tabs and column headers may stay as single words or
  short phrases. Rule 33 (over-compression) applies to sentences, such as descriptions,
  hints and error messages.

## Review

- Before reporting, reread every piece of text on the page against the unslop rules and
  fix what you find.
- After building, check the rendered page visually (for example a headless Chrome
  screenshot of the HTML) before reporting. If the environment cannot take a screenshot,
  say clearly in your report that you did not check it visually.
- Stop after each design step and let the user review. Report the page with a
  clickable link.

## From design to code

- Start application code only after the user approves the design. When implementing,
  reuse the theme values and component structure from the design pages; do not invent
  new colours or spacing. Copy the UI text from the design, and write any new UI text
  under the same unslop rules.
- When the implementation has to differ from the design (for example a technical
  limit), update the design page or tell the user first; do not let the two drift apart
  silently.
