# SlideWorks Creative Director — Visual Design Knowledge Base

This document is the canonical reference for the SlideWorks Creative Director agent.
It encodes the full visual design methodology for producing consulting-quality slides,
grounded in the work of Tufte, Parkinson, Rams, IDEO, and the house styles of
McKinsey, BCG, Gartner, Oracle Health, and the SlideWorks design system itself.

Every rule here is machine-referenceable. When the agent generates a slide spec,
a layout mockup, or a quality-gate checklist, it draws from these sections.

---

## 1. Edward Tufte — Data-Ink Principles

### The Five Laws of Data-Ink (in order of priority)

1. **Above all else, show the data.**
   The purpose of a chart is to communicate data. Every design decision must
   serve that purpose or be removed.

2. **Maximize the data-ink ratio.**
   `data-ink ratio = ink used to present data / total ink used in the graphic`
   A ratio of 1.0 is the theoretical ideal. Every increment of ink that does not
   encode data pulls the ratio down.

3. **Erase non-data-ink.**
   Remove any graphical element that does not directly represent a data value
   or structural relationship in the dataset.

4. **Erase redundant data-ink.**
   If two elements encode the same information (e.g., a bar height AND a data
   label AND a gridline all conveying the same value), keep only the most
   direct encoding.

5. **Revise and edit.**
   Iterate. Strip. Test. Show someone unfamiliar with the data and ask what
   they see. If they see decoration before data, revise again.

### Mandatory Removals (Chartjunk Checklist)

Always remove the following elements from any chart or data graphic:

- 3D effects (perspective, extrusion, rotation)
- Gradient fills on bars, areas, or backgrounds
- Drop shadows on any chart element
- Pattern fills (hatching, dots, diagonal lines)
- Frame borders / bounding boxes around charts
- Legend boxes when direct labeling is possible
- Background fills or shading in the chart plot area
- Decorative icons or clip art in or near the chart
- Unnecessary axis lines (if data labels are present)

### Lie Factor

`Lie Factor = size of graphic effect / size of data effect`

- Target Lie Factor = 1.0
- Lie Factor > 1.05 or < 0.95 is distortion
- Common violation: bubble charts where radius encodes value instead of area
- Common violation: truncated y-axes that exaggerate small differences

### Small Multiples

A series of charts using IDENTICAL scales placed side by side for comparison.

- Y-axis range must NEVER vary between panels
- X-axis categories and ordering must be identical
- Consistent color mapping across all panels
- Titles differ; everything else is structurally identical
- Ideal for: time series by segment, regional comparisons, before/after

### Sparklines

Word-sized, intense, simple graphics embedded inline with text or tables.

- No axes, no labels, no frame
- Convey shape and trend only
- Height matches line height of surrounding text
- Ideal for: KPI dashboards, executive summary tables

### Micro/Macro Readings

A well-designed graphic supports two modes of reading:

- **Macro**: the overall pattern is visible at a glance (trend, distribution, outlier)
- **Micro**: on closer inspection, individual data points are readable and precise

Design for both. Never sacrifice one for the other.

---

## 2. Think-Cell Visual Grammar

### Axis Styling

- Color: light gray `#CCCCCC`
- Weight: 0.5pt
- Tick marks: none (remove entirely)
- Axis labels: 9-10pt, dark gray `#333333`

### Gridlines

- Default: NO gridlines
- Absolute maximum tolerance: very faint dotted lines, light gray `#E0E0E0`, 0.25pt
- If gridlines are present, they must be the least visible element in the chart

### Direct Data Labels

- Place labels on or immediately adjacent to the bar, point, or segment
- NEVER use a separate legend box when direct labeling is feasible
- Font size: 8-10pt minimum
- Color: `#333333` on light backgrounds, `#FFFFFF` inside dark bars
- Format: use commas for thousands, one decimal for percentages

### Color Fills

- Flat, solid fills only
- No gradients, no transparency blending
- Colors must come from the approved palette for the active brand system
- Maximum 4 distinct colors per chart

### Bar Charts

- Bar width ratio: 0.6 (bar width relative to category spacing)
- Gap between bars: 2pt white space minimum
- Border/edge on bars: none (`edgecolor='none'`)
- Horizontal bars preferred for category labels longer than 3 words

### Waterfall Charts

- Positive increments: green `#2E7D32`
- Negative increments: red `#C62828`
- Subtotals/totals: gray `#9E9E9E`
- Thin horizontal connector lines between bars (0.5pt, `#999999`)
- Base starts at zero unless explicitly noted

### Gantt Charts

- Uniform row heights across all tasks
- Horizontal bars for task duration
- Diamond symbol (&#9670;) for milestones
- Vertical dashed line for "Today" or reference date
- Color-code by workstream or owner (max 4 colors)

### Marimekko Charts

- Column width = market size (or segment volume)
- Column height segments = market share by player
- Maximum 7 columns
- Direct label each segment; no legend
- Column width percentages shown along x-axis

### CAGR Annotations

- Bracket spanning the relevant time range, placed below the x-axis
- Diagonal arrow from start to end value
- Text format: `X% CAGR (YYYY-YYYY)`
- Font: 9pt, bold, dark gray

### Delta Arrows

- Vertical arrow between two values showing the absolute or percentage change
- Arrow color: green for positive, red for negative
- Label next to arrow: `+X%` or `-X%`

### Label Placement Rules

- Outside the bar if space allows (preferred)
- White text inside dark-colored bars only when external placement causes overlap
- Never place labels inside light-colored bars

### Annotation Lines

- Weight: 0.5pt
- Color: dark gray `#666666`
- Style: clean right-angle callouts (horizontal + vertical segments)
- End with a small circle or no terminator (never arrowheads on annotations)

---

## 3. Mike Parkinson — Visual Hierarchy (Billion Dollar Graphics)

### Hierarchy Order

The human eye processes visual weight in this order:

1. **Size** — the largest element is seen first
2. **Color** — saturated or contrasting color draws attention next
3. **Position** — top-left and center carry more visual weight
4. **Shape** — irregular or unique shapes attract the eye last

Design the slide so that the most important element wins on at least two of
these four dimensions.

### Cognitive Load — Miller's Law

- Maximum 3-5 distinct elements per visual grouping
- If a chart has more than 5 series, aggregate or use small multiples
- If a slide has more than 5 text blocks, restructure into hierarchy or multiple slides

### F-Pattern (Text-Heavy Slides)

- Eyes scan left-to-right across the top, then sweep down the left edge
- Most important information: top-left quadrant
- Supporting detail: right side and lower body
- Call to action or conclusion: bottom of the F sweep

### Z-Pattern (Visual Slides)

- Eyes move: top-left -> top-right -> diagonal to bottom-left -> bottom-right
- Hero element: center of the slide
- Title/context: top-left
- Call to action or takeaway: bottom-right

### The 3-Second Glance Test

The viewer must understand the slide's main point within 3 seconds of seeing it.

Test procedure:
1. Show the slide to someone for exactly 3 seconds
2. Ask: "What is this slide about?"
3. If they cannot answer, the slide fails — simplify or restructure

### One Dominant Element Rule

Every slide must have exactly one visually dominant element. This element:
- Is the largest or boldest thing on the slide
- Carries or directly supports the key message
- Is placed according to F-pattern or Z-pattern rules
- Does not compete with other elements for attention

---

## 4. Dieter Rams — 10 Principles Applied to Slides

| # | Principle | Slide Application |
|---|-----------|-------------------|
| 1 | Good design is innovative | Find a fresh, clear way to present the data — avoid templates by default |
| 2 | Good design makes a product useful | Every element on the slide must serve the message; decorative elements are waste |
| 3 | Good design is aesthetic | Only well-executed, clean visuals can be called beautiful; rough drafts are not aesthetics |
| 4 | Good design makes a product understandable | The slide must be self-explanatory without a verbal walkthrough |
| 5 | Good design is unobtrusive | Content dominates; the design system is invisible to the audience |
| 6 | Good design is honest | Charts must not mislead; axes must not be truncated to exaggerate; proportions must be accurate |
| 7 | Good design is long-lasting | Use classic layouts and type; avoid trendy effects that date the deck in 6 months |
| 8 | Good design is thorough down to the last detail | Alignment, spacing, font consistency, source lines — every detail matters |
| 9 | Good design is environmentally friendly | Efficient use of slide real estate; no wasted space, no unnecessary slides |
| 10 | Good design involves as little design as possible | Less, but better. Remove until only the essential remains |

---

## 5. IDEO — Human-Centered Presentation Design

### Progressive Disclosure

Reveal complexity in layers, not all at once:
- Slide 1: the headline finding
- Slide 2: the supporting data
- Slide 3: the methodology or detail
- Never dump all three layers onto one slide

### Emotional Design Moments

Every deck needs at least one "wow" slide that resets audience attention:
- A single large number that surprises
- A before/after image pair
- A quote from a real user or customer
- A visual that reframes the problem

Place these at narrative turning points, not randomly.

### Designed for the Room

Before finalizing any slide, ask: will this read from 15 feet away?

- Title text must be legible at 15 feet (24pt minimum)
- Chart labels must be legible at 10 feet (14pt minimum in projected context)
- Fine print (sources, footnotes) is for the leave-behind, not the projection
- Test: shrink the slide to 25% zoom — if you cannot read the title, increase the size

### Empathy Mapping per Slide

For each slide, consider:
- **Think**: what does the audience already believe about this topic?
- **Feel**: what emotional state are they in at this point in the deck?
- **Need**: what must they understand before the next slide makes sense?

Design the slide to meet the audience where they are, not where you are.

### Storytelling Through Sequence

Each slide builds on the previous one:
- Slide N sets up a question or tension
- Slide N+1 answers it or advances the argument
- No slide should be understandable only in isolation
- No slide should repeat the previous slide's message

---

## 6. McKinsey Firm Graphics — Visual Layer

### The 60/30/10 Color Rule

| Share | Role | Typical Color |
|-------|------|---------------|
| 60% | Dominant (backgrounds, large areas) | White `#FFFFFF` or Light Gray `#F5F5F5` |
| 30% | Secondary (headers, chart elements) | Navy `#1C2833` or Dark Blue |
| 10% | Accent (highlights, callouts, alerts) | Red, Teal, or Brand Accent |

### Typography Constraints

- Maximum 3 font sizes per slide: title, body, caption
- Never mix serif and sans-serif on the same slide
- Bold for emphasis only — never for entire paragraphs

### Layout Grid

- Consistent margins: 0.5 inches on all sides
- Element spacing: 0.3 inches minimum between adjacent elements
- 12-column grid: all elements snap to column boundaries
- Gutter width: 0.15 inches between columns

### Chart Constraints

- Maximum 4 colors per chart
- No 3D chart types — ever
- Approved chart types: horizontal bar, vertical bar, line, scatter, waterfall, Gantt, pie (rarely, and only for 2-3 segments)
- Pie charts: maximum 4 slices, always with direct percentage labels

---

## 7. BCG Slide Grammar

### Three-Zone Layout

Every BCG-style content slide follows a three-zone structure:

| Zone | Position | Style | Content |
|------|----------|-------|---------|
| Header Strip | Top, full width | Dark background, white text | Action title (sentence with a verb and a conclusion) |
| Body | Center, main area | White or light background | Evidence: charts, tables, diagrams |
| Source Strip | Bottom, full width | 8pt font, gray text | Data attribution on every slide that contains data |

### Action Titles

- Must be a complete sentence
- Must contain a verb
- Must state the conclusion, not describe the chart
- Bad: "Revenue by Region"
- Good: "North America drives 72% of revenue growth, offsetting EMEA decline"
- Maximum length: 15 words

### BCG Emphasis Technique

In a multi-bar or multi-segment chart:
- Make ALL bars/segments gray `#BDBDBD`
- Color ONLY the bar/segment that IS the message in the brand accent color
- This forces the eye to the point of the slide

### Callout Box

- Maximum one callout box per slide
- Green border `#2E7D32` or brand accent border, 1.5pt
- Contains: one large bold number + one line of context
- Purpose: proves the action title with a single data point
- Position: adjacent to the relevant chart element

### Direct Labeling (BCG Standard)

- Category names go ON the chart (axis labels or direct bar labels)
- No separate legend box
- If a legend is unavoidable (e.g., overlapping lines), place it inside the plot area, not outside

---

## 8. Gartner Conference Style

### Visual Identity

- Backgrounds: white `#FFFFFF` or light gray `#F5F5F5`
- Grid: minimal, nearly invisible
- Typography: clean sans-serif throughout (no decorative fonts)
- One accent color for emphasis: Gartner orange `#FF8000`

### Research Authority

- Every claim must be sourced
- Formal attribution format: "Source: Gartner (YYYY)"
- No unsourced data points on any slide

### Signature Frameworks

**Magic Quadrant:**
- X-axis: Completeness of Vision
- Y-axis: Ability to Execute
- Four quadrants: Leaders (top-right), Challengers (top-left), Visionaries (bottom-right), Niche Players (bottom-left)
- Dots positioned for each vendor, directly labeled

**Hype Cycle:**
- Non-linear curve with 5 named phases:
  1. Innovation Trigger
  2. Peak of Inflated Expectations
  3. Trough of Disillusionment
  4. Slope of Enlightenment
  5. Plateau of Productivity
- Technology dots placed on the curve with direct labels
- Time-to-mainstream annotations where applicable

### Layout Conventions

- Formal footer on every slide: document ID, date, confidentiality notice
- Matrix layouts: color-coded 2x2, 3x3, or heat maps
- Heat maps: sequential color ramp from light to dark (never rainbow)

---

## 9. SlideWorks Design System

### Primary Palette

| Name | Hex | Usage |
|------|-----|-------|
| Navy Blue | `#1C2833` | Headers, emphasis text, dark backgrounds |
| Light Blue | `#5DADE2` | Accents, data highlights, interactive elements |
| White | `#FFFFFF` | Primary background |
| Cream | `#F4E8D8` | Alternate/warm background |

### Supporting Palette

| Name | Hex | Usage |
|------|-----|-------|
| Dark Gray | `#2C3E50` | Body text |
| Light Gray | `#ECF0F1` | Subtle backgrounds, divider lines |

### Typography Hierarchy

| Level | Size Range | Weight | Usage |
|-------|-----------|--------|-------|
| Header | 24-32pt | Bold | Slide titles, section headers |
| Subheader | 18-22pt | Bold | Zone titles, chart titles |
| Body | 11-14pt | Regular | Narrative text, bullet points |
| Footnote | 8-10pt | Regular | Sources, disclaimers, fine print |

### Font Selection

- Primary: Arial or a comparable sans-serif (Helvetica, Calibri)
- Monospace (for code or data tables): Consolas or Source Code Pro
- Never use more than 2 font families on a single slide

### Layout Rules

1. **One message per slide.** If the slide says two things, split it.
2. **40/60 rule:** text occupies 40% of the slide area, visuals occupy 60% (or the inverse). Never 50/50.
3. **Consistent positioning:** headers appear in the same position on every slide. Sources appear in the same position. The eye should never hunt.
4. **Breathing room:** white space is not wasted space. Leave margins. Leave gaps. Do not fill every pixel.

---

## 10. Oracle Health Brand System

### Brand Colors (from KPI Template)

| Name | Hex | Usage |
|------|-----|-------|
| Navy | `#1B2A4A` | Primary dark, header backgrounds |
| Oracle Red | `#C74334` | Accent only — NEVER for body text or large areas |
| Teal | `#0E6E8E` | Secondary accent, positive indicators |
| White | `#FFFFFF` | Light backgrounds |
| Warm Gray | `#F5F5F5` | Alternate light backgrounds |

### Layout Modes

- **Dark layouts**: for hero slides, section dividers, and title slides
- **Light layouts**: for all content, data, and evidence slides

### Logo Placement

- Title slides: Oracle logo top-right
- Content slides: Oracle logo bottom-right, small, non-intrusive

### Clinical Canvas Palette (from v6 Deck)

| Tier | Color | Hex | Meaning |
|------|-------|-----|---------|
| Tier 1 | Green | `#1B7A4D` | Primary / highest priority / on track |
| Tier 2 | Amber | `#D48B00` | Secondary / caution / in progress |
| Tier 3 | Slate | `#6B707B` | Tertiary / deferred / neutral |

---

## 11. Fusion Palette — SlideWorks + Oracle Health

When producing slides that must satisfy both design systems:

| Role | Source | Hex | Rationale |
|------|--------|-----|-----------|
| Primary Dark | Oracle Navy | `#1B2A4A` | Near-identical to SlideWorks Navy `#1C2833` |
| Data Highlight | SlideWorks Light Blue | `#5DADE2` | Bright, accessible, data-forward |
| Accent/Alert | Oracle Red | `#C74334` | Used sparingly for warnings or emphasis only |
| Positive/Secondary | Oracle Teal | `#0E6E8E` | Secondary data series, positive indicators |
| Background (light) | White / Warm Gray | `#FFFFFF` / `#F5F5F5` | Shared across both systems |

### Typography in Fusion Mode

- Follow SlideWorks typography hierarchy (sizes, weights)
- Use Oracle-approved font families when Oracle branding is required
- Fallback: Arial (acceptable in both systems)

---

## 12. matplotlib to Think-Cell Conversion Rules

Python code patterns that produce Think-Cell-quality chart output:

### Remove Chartjunk

```python
# Strip non-data ink from axes
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(0.5)
ax.spines['left'].set_color('#CCCCCC')
ax.spines['bottom'].set_linewidth(0.5)
ax.spines['bottom'].set_color('#CCCCCC')

# Remove tick marks, keep labels
ax.tick_params(axis='both', which='both', length=0)
ax.tick_params(axis='both', labelsize=9, labelcolor='#333333')
```

### Eliminate Gridlines

```python
ax.grid(False)
ax.set_axisbelow(True)  # if any grid is forced, keep it behind data
```

### Direct Data Labels (No Legend)

```python
for i, v in enumerate(values):
    ax.text(
        i, v + offset,
        f'{v:,.0f}',
        ha='center', va='bottom',
        fontsize=9, color='#333333',
        fontweight='regular'
    )
```

### Bar Chart Standard

```python
bars = ax.bar(
    x, y,
    width=0.6,
    color=palette,
    edgecolor='none',
    zorder=3
)
```

### Waterfall Chart Colors

```python
WATERFALL_POSITIVE = '#2E7D32'
WATERFALL_NEGATIVE = '#C62828'
WATERFALL_SUBTOTAL = '#9E9E9E'
WATERFALL_CONNECTOR_COLOR = '#999999'
WATERFALL_CONNECTOR_WIDTH = 0.5
```

### Export for Slide Embedding

```python
fig.savefig(
    output_path,
    dpi=300,
    transparent=True,
    bbox_inches='tight',
    pad_inches=0.1,
    format='png'
)
```

### Figure Setup (Slide-Sized)

```python
fig, ax = plt.subplots(figsize=(10, 5.625))  # 16:9 aspect ratio
fig.patch.set_alpha(0)  # transparent figure background
ax.set_facecolor('none')  # transparent axes background
```

---

## 13. 9-Rule Quality Gate (Machine-Testable)

Every slide must pass all applicable rules before delivery.

| # | Rule | Machine Test | Pass Criteria |
|---|------|-------------|---------------|
| 1 | Action title on every slide | Parse title shape text | Contains a verb, is a sentence, 15 words or fewer |
| 2 | One chart per body zone | Count chart shapes in body region | Count <= 1 |
| 3 | Source line on data slides | Search footer zone for "Source:" | Present on every slide containing a chart or data table |
| 4 | Max 2 font families | Enumerate fonts across all shapes | Unique font family count <= 2 |
| 5 | Max 4 colors per chart | Enumerate fill colors in chart XML | Unique color count <= 4 |
| 6 | No 3D chart types | Check chart type enumeration | No bar3d, pie3d, line3d, area3d, or surface types |
| 7 | Data label font >= 8pt | Inspect font size on all data labels | All sizes >= 8pt (600 EMU minimum) |
| 8 | Embedded image DPI >= 300 | Read image metadata or compute from EMU dimensions | DPI >= 300 for all raster images |
| 9 | Title position consistent <= 1pt drift | Compare title shape coordinates across all slides | Max deviation <= 1pt (12700 EMU) in both x and y |

### Quality Gate Scoring

- 9/9 pass: ready for delivery
- 7-8/9 pass: fix before delivery, flag specific failures
- Below 7/9: return to design phase

---

## 14. Creative Loop Process

For each slide or slide group, follow this production cycle:

### Step 1 — Analyze Message Intent

- What must the audience understand after seeing this slide?
- What is the single takeaway?
- What data or evidence supports it?
- Write the action title first, before any design work begins.

### Step 2 — Select Candidate Layouts

Choose 2-3 candidate layout types from the SlideWorks catalog (271 types):
- Consider the data type (comparison, trend, composition, distribution, relationship)
- Consider the audience (executive, technical, mixed)
- Consider the deck position (opening, evidence, conclusion)

### Step 3 — Generate Three Mockup Options

| Option | Style | Character |
|--------|-------|-----------|
| A | Clean McKinsey | Minimal, data-forward, Think-Cell precision, muted palette |
| B | Conference Impact | Big hero numbers, strong visual hierarchy, "wow" moment design |
| C | Data Studio | Tufte-inspired, maximum data-ink ratio, dense but clean, small multiples |

### Step 4 — Present as HTML/CSS Mockups

Render mockup options in Claude Preview as interactive HTML/CSS.
- Accurate colors from the active palette
- Correct typography hierarchy
- Approximate layout proportions
- Placeholder data that matches the real data structure

### Step 5 — User Selection

User selects one option or mixes:
- "Use A's layout with C's chart style"
- "B, but swap the hero number for a waterfall chart"
- "C, but use the Oracle palette instead of SlideWorks"

### Step 6 — Produce Per-Slide Visual Spec

Output a YAML spec with exact positioning for the slide builder:

```yaml
slide:
  layout: three_zone_bcg
  title:
    text: "North America drives 72% of revenue growth"
    position: { left: 457200, top: 274638, width: 8229600, height: 457200 }
    font: { family: Arial, size: 2400, bold: true, color: "FFFFFF" }
  body:
    chart:
      type: bar_horizontal
      position: { left: 457200, top: 1143000, width: 5486400, height: 3657600 }
      colors: ["#1B2A4A", "#5DADE2", "#BDBDBD"]
      labels: direct
  source:
    text: "Source: Company financial reports (2025)"
    position: { left: 457200, top: 5029200, width: 8229600, height: 228600 }
    font: { family: Arial, size: 800, color: "999999" }
```

---

## Appendix A — Chart Type Decision Tree

| Data Relationship | Recommended Chart | Avoid |
|-------------------|-------------------|-------|
| Comparison (few items) | Horizontal bar | Pie, radar |
| Comparison (many items) | Small multiples | Grouped bar with 6+ groups |
| Change over time | Line chart | Area chart (unless stacked composition) |
| Part-to-whole | Stacked bar, treemap | Pie (unless 2-3 segments) |
| Distribution | Histogram, box plot | Bar chart pretending to be a histogram |
| Correlation | Scatter plot | Dual-axis line chart |
| Flow / process | Waterfall, Sankey | Circular flow diagrams |
| Schedule | Gantt | Table of dates |
| Market composition | Marimekko | Grouped bar |

## Appendix B — Common Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Rainbow palette | No visual hierarchy, cognitive overload | Use 2-3 colors from approved palette |
| Dual y-axes | Misleading scale relationships | Use two separate charts |
| Truncated y-axis | Exaggerates differences | Start axis at zero (or clearly mark break) |
| Rotated x-axis labels | Hard to read | Switch to horizontal bar chart |
| Pie chart with 7+ slices | Impossible to compare angles accurately | Use horizontal bar chart |
| Center-aligned bullet text | Looks unprofessional | Left-align all body text |
| Logo as watermark | Reduces data-ink ratio, distracting | Place logo in designated corner only |
| Animated transitions | Distracts from content in live presentations | Use cuts, no transitions |
