# Slide Design Studio Agent — Knowledge Base
## Research Packet: Professional Slide Design Standards

**Research question:** What are the specific, codifiable design rules, measurements, and visual grammar principles from Think-Cell, McKinsey, BCG, Gartner, Duarte, and Tufte that can be embedded in a slide design studio agent system prompt?

**Scope boundaries:**
- Covers visual grammar, layout, typography, color, and chart-type selection rules
- Includes python-pptx implementation protocols
- Excludes narrative/storytelling methodology (covered separately by content agents)
- Does not cover animation, transitions, or live presentation delivery

**Status:** Complete
**Date:** 2026-03-12

---

## 1. Canonical Definitions

**Action title:** A slide headline written as a complete declarative sentence stating the key takeaway or implication of the slide — not a label describing what the slide contains. Originated at BCG in the 1990s.

**Data-ink ratio:** Tufte's measure. The proportion of a graphic's total ink devoted to non-redundant display of data. Formula: data-ink / total ink used. Target: maximize toward 1.0.

**Chartjunk:** Any visual element in a chart that does not encode data and cannot be erased without loss of data-information. Coined by Tufte. Includes decorative fills, 3D effects, unnecessary gridlines, excessive tick marks, clipart.

**Smart simplicity:** BCG's operating principle. Maximum insight with minimum complexity. Test: can the slide be understood in 10 seconds? If not, redesign.

**Glance test:** Duarte's 3-second comprehension test. A slide passes if a viewer can understand the single point it makes within 3 seconds from normal viewing distance.

**Signal-to-noise ratio:** The proportion of slide content that contributes to the core message vs. content that distracts from it. High signal = few elements, each load-bearing. High noise = decorative text, redundant labels, visual clutter.

**CAGR arrow:** Think-Cell annotation style for compounding annual growth rate. Rendered as a bracket with a diagonal arrow spanning a time series, annotated with the percentage and period.

**Marimekko (Mekko) chart:** A two-dimensional stacked bar chart where column width represents one variable (typically market size) and column height represents another (typically share or composition). Used for simultaneous market-sizing and share analysis.

**Ghost deck:** The pre-design phase artifact. A sequence of action titles written and ordered before PowerPoint is opened. Tests whether the argument is logically complete.

**Pyramid Principle:** Barbara Minto's structure, adopted universally at MBB. Lead with the answer (recommendation), then support with 3–5 arguments, then evidence. Applied at deck level and at individual slide level.

---

## 2. Think-Cell Visual Grammar

### 2.1 The Ten Design Principles (from think-cell Academy)

1. **Chart format** — Select the chart type that best expresses the specific comparison being made. Match format to insight type: trend = line, composition = stacked bar or Mekko, comparison = clustered bar, flow/bridge = waterfall, schedule = Gantt.
2. **Color** — Limit to a corporate palette. Use color to encode data meaning, not decoration. Never use rainbow fills. Apply color hierarchically: primary series gets brand color, secondary gets gray.
3. **Text, labels, and legends** — Prefer direct labels over legends. Labels must be large enough to read without zoom. Remove any text that restates what the axis already communicates.
4. **Readability** — Chart must be legible at normal projection distance. Minimum data label font: 9pt. Category labels: 8pt minimum. Axis labels: 8pt minimum.
5. **Scales** — Value axes must always include the full data range. Do not truncate Y-axes to artificially amplify differences. Think-Cell auto-scales; manual overrides should be intentional and disclosed.
6. **Data integrity** — Never distort area, length, or slope to misrepresent magnitude. Area charts especially prone to distortion — prefer absolute values.
7. **Chartjunk** — Remove: 3D effects, gradient fills, shadow effects, decorative borders on chart areas, pattern fills, clip art. These are rejected by Think-Cell's default style.
8. **Data density** — Aim for high data density: the number of distinct data points visible per unit of chart area. Avoid wide spacing or oversized bars that underuse chart real estate.
9. **Data richness** — Show the full picture. A chart that shows only totals when components are available fails the richness test. CAGR arrows add richness to time series without adding noise.
10. **Attribution** — Every chart must have a source line. Format: "Source: [Primary source]; [firm] analysis." Position: bottom-left of the chart area or slide footer.

### 2.2 Think-Cell Waterfall Chart Rules

- Start bar (leftmost): solid fill, labeled with absolute value
- Positive delta bars: green fill by convention; labeled with "+X" or just "X"
- Negative delta bars: red fill; labeled with "(X)" or "-X"
- End/total bar (rightmost): solid fill, same color as start bar
- Connector lines: thin horizontal lines at each delta bar top/bottom, aligned to previous column end
- Column break: use to separate logical groupings (e.g., FY sections)
- Never omit the absolute start and end values — these anchor the reader
- CAGR bracket: shown as a horizontal bracket below x-axis spanning multiple periods, with diagonal arrow and annotation "X% CAGR (YYYY–YYYY)"

### 2.3 Think-Cell Gantt Chart Rules

- Row height: uniform across all activities
- Milestone markers: diamond shape at specific date
- Bar fills: one color per workstream or track
- Critical path: highlight with bold border or distinct fill, not a separate color collision
- Date axis: always show at top, tick intervals matched to project cadence (week/month/quarter)
- Today line: thin vertical line labeled "Today" or current date
- Dependencies: avoid visual clutter — show only critical dependencies; use thin arrows, not thick

### 2.4 Think-Cell Mekko (Marimekko) Chart Rules

- X-axis: represents total volume/size; always labeled with units (e.g., "$B") at axis end
- Y-axis: 0–100% for share charts; absolute scale for absolute-value stacked
- Column widths: proportional to the X variable — never equal-width unless data is equal
- Segment labels: direct labels inside segments when space permits; minimum legibility threshold is segment representing >5% of column
- Maximum columns: 7 is the visual limit before the chart becomes unreadable
- Color coding: consistent across all columns for the same category/series

### 2.5 Think-Cell Style File Configuration (for programmatic replication)

- Style files are XML-based and define default colors, fills, font sizes, line weights
- Corporate template should lock: font family, primary brand colors, approved fill styles, minimum font sizes
- Harvey balls and checkmarks use fixed size relative to cell/text height

---

## 3. McKinsey Firm Graphics Standards

### 3.1 Core Structural Rules

**Rule 1: Action titles on every slide**
- Complete declarative sentence. Maximum 2 lines. Maximum 15 words.
- Active voice: "Revenue grew 12%" not "Revenue was up 12%"
- Specific and quantitative when possible: "German market growing 12% annually, 3x faster than US"
- Never a topic label: "Market Overview" fails; "Market growing 12% annually since 2022" passes
- Test: reading only the action title must convey the entire slide message

**Rule 2: One message per slide**
- If the action title contains the word "and," split into two slides
- Single chart or exhibit per slide
- All content in the body supports exactly one conclusion

**Rule 3: Pyramid structure at the slide level**
- Action title = apex of the pyramid (the answer)
- 2–4 supporting arguments = middle layer
- Data/charts/evidence = base layer
- If body content does not support the title, delete it

**Rule 4: Vertical flow**
- The logical chain must run: title → supporting arguments → evidence
- A reader moving top-to-bottom should not be surprised by what they encounter

**Rule 5: The Titles Test**
- Read all slide titles in sequence without viewing body content
- The complete argument must be legible from titles alone
- This is the primary quality gate before client delivery

**Rule 6: The 60-second rule**
- Each slide must be explainable in 60 seconds or less
- If it takes longer, the slide is too complex — split or simplify

### 3.2 McKinsey Typography Rules

- Body font: Arial
- Title font: Georgia (or Arial where Georgia unavailable)
- Action title size: 18–20pt (fixed across all slides in a deck — never varying)
- Body text: 11–12pt minimum
- Source/footer: 8pt
- Rule: if font size is reduced to fit content, the problem is content, not formatting — simplify instead

### 3.3 McKinsey Color Palette

- Primary brand: McKinsey Blue (#002F6C)
- Accent: Medium Blue (~#0070C0)
- Neutral: Gray (#7D7D7D)
- Positive/growth: Green (#2E7D32)
- Negative/risk: Red (#C62828)
- Totals/benchmarks: Black or near-black
- Maximum 3–4 colors per chart. Never use color for decoration.

### 3.4 McKinsey Slide Anatomy (3-zone layout)

```
┌─────────────────────────────────────────────────────┐
│  ACTION TITLE (1-2 lines, 18-20pt, top of slide)    │
│  Subtitle if needed (12pt, lighter weight)           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  BODY: single chart, table, or framework            │
│  (supports action title exclusively)                │
│                                                     │
│  Optional: callout box highlighting key number      │
│                                                     │
├─────────────────────────────────────────────────────┤
│  Source: [attribution] (8pt)          Page # (8pt)  │
└─────────────────────────────────────────────────────┘
```

### 3.5 McKinsey Source Citation Format

Exact format: `Source: [Primary data source] ([year]); McKinsey analysis`
Examples:
- `Source: Bloomberg (2024); McKinsey analysis`
- `Source: Company annual reports (2021–2024); McKinsey analysis`
- `Source: Expert interviews (n=24); McKinsey analysis`
- Never omit source on quantitative claims

### 3.6 McKinsey Approved Chart Types

| Insight type | Approved chart |
|---|---|
| Trend over time | Line chart, clustered bar (few periods) |
| Composition | Stacked bar, 100% stacked bar, Mekko |
| Comparison | Horizontal bar (long labels), vertical bar (few categories) |
| Flow/bridge | Waterfall |
| Relationship | Scatter plot, bubble chart |
| Distribution | Histogram, box plot |
| Schedule | Gantt |
| Portfolio/positioning | 2x2 matrix |

Explicitly rejected: 3D charts of any type, pie charts (except when showing 2–3 parts of a whole with clear dominance), radar/spider charts, bubble charts with >10 categories.

---

## 4. BCG Slide Grammar

### 4.1 Smart Simplicity: The Operating Principle

BCG's design philosophy distilled to a decision test applied to every slide element:
1. Does this element directly support the action title?
2. Can the reader understand this in 5–10 seconds?
3. Is there a simpler way to show this?

If any answer is "no" — redesign or delete.

### 4.2 BCG Action Titles (vs. McKinsey)

BCG action titles are shorter and punchier than McKinsey's. McKinsey writes comprehensive titles that stand alone; BCG writes punchy titles paired with visual proof.

- Maximum 15 words, ideally under 10
- Lead with the number: "67% of growth driven by premium segment" not "Premium segment drove 67% of growth"
- One line maximum for the main title (BCG dropped subtitle lines in recent template evolution)
- The chart makes the title immediately verifiable — reader confirms in under 5 seconds

### 4.3 BCG Three-Zone Layout

Identical zones to McKinsey with key differences:
- Header strip: action title only, no subtitle in current BCG style
- Body: more chart-heavy, less supporting text than McKinsey
- Source strip: same format as McKinsey

### 4.4 BCG Color System

| Role | Color | Hex |
|---|---|---|
| Brand accent | BCG Green | #009639 |
| Primary data series | Dark Blue | #003F5C |
| Secondary/context data | Medium Gray | #7D7D7D |
| Positive change | Green | #2E7D32 |
| Negative change | Red | #C62828 |
| Totals/benchmarks | Black or Dark Gray | #1A1A1A |

Maximum 3 colors per chart. Color must encode meaning, not decorate.

**BCG emphasis technique:** In a bar chart comparing 8 segments, 7 bars are gray and 1 bar is brand color — the colored bar IS the message. This appears consistently across BCG output.

### 4.5 BCG Callout Box Convention

- Used to highlight the specific number that proves the action title
- Typically a green-bordered or shaded box placed adjacent to the relevant chart element
- Contains: the key number in large bold font (14–16pt), optionally a 1-line annotation
- Never multiple callout boxes per slide — limits focus to the single key insight

### 4.6 BCG Preferred Chart Types

| Use case | BCG preference | BCG avoids |
|---|---|---|
| Change over time | Line chart, column chart | Area chart, 3D |
| Composition/share | Stacked bar, Mekko | Pie chart, donut |
| Comparison | Bar chart (horizontal for long labels) | Radar chart |
| Flow/bridge | Waterfall | Complex Sankey |
| Part-to-whole | 100% stacked bar | Multiple pies |
| Market sizing | Mekko | Nested circle |

BCG waterfall: mandatory green/red fills for positive/negative. Every bar labeled with exact value. Start and end columns use solid fills different from delta columns.

### 4.7 Direct Labeling Rule

BCG strongly prefers direct labels over legends. Category name goes directly next to the data point, line end, or bar. Legends are acceptable only when 8+ categories create clutter — and even then, consider grouping into "Other."

### 4.8 BCG Formatting Specifications

- Font: Arial or Helvetica throughout (one family only)
- Hierarchy: size only, not font variety
- Title: 18–20pt bold
- Body text: 11–12pt
- Source footer: 8pt
- White space: aggressive — leave visible margins around all elements
- Alignment: pixel-perfect; title position must not shift when flipping through slides

---

## 5. Gartner Research Presentation Style

### 5.1 Visual Language Identifiers

Gartner presentations are immediately identifiable by three visual signatures:
1. The Magic Quadrant scatter plot (2x2 matrix with bubble markers)
2. The Hype Cycle (non-linear curve with 5 labeled phases)
3. A formal corporate style with heavy use of orange/yellow as accent against gray/white

### 5.2 Magic Quadrant Specifications

**Structure:**
- X-axis: "Completeness of Vision" (left = niche/narrow, right = comprehensive)
- Y-axis: "Ability to Execute" (bottom = limited, top = strong)
- Axes intersect at center, dividing plot into four quadrants
- Quadrant labels (top-right to bottom-left): Leaders, Challengers, Visionaries, Niche Players
- Bubble markers: each vendor = one bubble; bubble size occasionally encodes a third variable (company size or revenue)
- Quadrant dividing lines: thin gray dashed or solid lines through the center

**Visual rules:**
- Axis labels: sentence case, set in gray
- Quadrant labels: set in corners, gray, medium weight
- Vendor name labels: set directly adjacent to bubble
- Color: bubbles typically one solid color (Gartner uses blue-gray palette); no rainbow encoding
- Background: white or light gray grid
- Legend: minimal — bubble identity comes from direct labels only

**Typography:**
- Primary font: Arial or a sans-serif house font
- Gartner accent color: orange (#FF8000 range) used for callout boxes and highlighted data
- Secondary: dark gray body text, light gray for structural elements

### 5.3 Hype Cycle Specifications

**Structure:**
- X-axis: "Maturity" (time, implied — no specific dates)
- Y-axis: "Expectations" (visibility/hype level)
- Curve: non-monotonic — rises steeply to Peak, falls sharply to Trough, rises gradually through Slope to Plateau
- Five labeled phases on the curve: Innovation Trigger, Peak of Inflated Expectations, Trough of Disillusionment, Slope of Enlightenment, Plateau of Productivity
- Technology markers: small circles or dots on the curve labeled by technology name
- Time-to-plateau indicator: colored flag or icon (< 2 years, 2–5 years, 5–10 years, >10 years, or "obsolete before plateau")

**Visual rules:**
- Curve: smooth, rendered as a continuous line — not a series of linear segments
- Phase labels: positioned above or below the curve, connected with thin lines if needed
- Technology dots: direct labels, not a legend
- Slope of Enlightenment: lighter shaded region or no shading
- Plateau of Productivity: rightmost shaded region, slightly distinct

### 5.4 Gartner Slide Template Conventions

- Header: Gartner logo top-right; slide title in large sans-serif left-aligned
- Body: mostly chart or diagram; minimal bullet points (Gartner research slides lean toward diagram-heavy)
- Footer: Gartner copyright notice, date, document ID in small gray text
- Color accent: orange for call-outs and emphasis boxes
- Watermark/classification: "Gartner Confidential" or similar in footer on client-facing work

---

## 6. Nancy Duarte's Slide Design Rules (from slide:ology and Duarte Inc.)

### 6.1 The Glance Test

**Definition:** A slide passes the Glance Test if a viewer can comprehend the main point within 3 seconds or less from normal viewing distance.

**How to apply:**
1. Set a 3-second timer
2. View the slide as if seeing it for the first time
3. After 3 seconds, articulate the main point
4. If you cannot, the slide has failed — pare down or redesign

**Why it matters:** Audience members cannot simultaneously read text-heavy slides AND listen to the presenter. The slide must communicate its point as a visual aid, not a document.

### 6.2 Signal vs. Noise Framework

**Signal:** Every element that contributes to communicating the core message
**Noise:** Every element that does not contribute — decorative backgrounds, clip art, non-essential text, redundant labels, excessive bullet points, fussy borders

**Rule:** Remove every noise element. When uncertain whether something is signal or noise, ask: "If I removed this element, would the message be lost or weakened?" If not, remove it.

**Five critical design elements per slide (Duarte's framework):**
1. Contrast — differentiates key information from supporting
2. Flow — guides eye movement from most important to supporting
3. Hierarchy — size/weight/color communicates importance order
4. Unity — consistent visual system across all slides
5. Proximity — related elements grouped; unrelated elements separated

### 6.3 Visual Hierarchy Rules

**Size hierarchy:**
- Title: largest element on slide
- Key numbers/callouts: second largest
- Body/supporting labels: standard reading size
- Footer/attribution: smallest

**Weight hierarchy:**
- Bold = primary message
- Regular = supporting content
- Light = contextual, supplementary

**Color hierarchy:**
- Saturated brand color = key message, call to action
- Mid-gray = supporting content
- Light gray = structural/background elements

**Rule:** Every slide must have one visually dominant element — the element that the eye goes to first. That element must carry the key message.

### 6.4 One Idea Per Slide

- Each slide = one idea, one point
- Multiple ideas = multiple slides
- If you cannot state the slide's point in one sentence, you have multiple points

### 6.5 Slide as Billboard, Not Document

A slide must function as a billboard — understood at speed, from a distance. Not as a document to be read word by word.

Implication: slides must use large type, minimal text, strong visual contrast, and simple diagrams. If content requires reading, it belongs in a handout (Slidedoc), not a projected slide.

### 6.6 Recommended Duarte Type Scale (for projected presentations)

| Element | Minimum size |
|---|---|
| Slide title | 36pt |
| Section header | 28–32pt |
| Body text | 24pt minimum |
| Caption/source | 18pt minimum |
| Do not use below 18pt for projected content |

*Note: These are projected presentation standards. Printed/PDF handout standards differ — 11–12pt body is acceptable for print.*

### 6.7 Background and Contrast Rules

- High contrast between text and background: minimum 4.5:1 contrast ratio (WCAG AA)
- Dark backgrounds: use white or near-white text
- Light backgrounds: use near-black text
- Avoid patterned or gradient backgrounds — they compete with content
- Full-bleed photography acceptable only when image directly supports the message

---

## 7. Edward Tufte's Data Visualization Rules

### 7.1 The Five Laws of Data-Ink

1. **Above all else, show the data** — the graphic exists to display data, nothing else
2. **Maximize the data-ink ratio** — increase proportion of ink encoding data, reduce all else
3. **Erase non-data-ink** — remove elements that do not encode data: decorative fills, unnecessary gridlines, tick marks for unlabeled positions, frame boxes around chart areas
4. **Erase redundant data-ink** — remove labels that restate what the axis already communicates; remove values already visible in another form
5. **Revise and edit** — improvement is iterative; strip after each pass

### 7.2 Chartjunk: What to Remove

**Always remove:**
- 3D effects on any chart type (bars, pies, lines — all are distortions)
- Drop shadows and glow effects on chart elements
- Gradient fills on bars or areas
- Decorative pattern fills (hatching, crosshatch)
- Unnecessary gridlines (if the value can be read from direct labels, gridlines are redundant)
- Heavy tick marks without data labels
- Chart area borders/frames
- Legend boxes when direct labeling is possible
- Background colors/fills on chart areas when white serves equally well

**Gray zone (context-dependent):**
- Light gray gridlines at 0.5pt (acceptable when precise reading is required by the audience)
- Minor tick marks (acceptable when scale is dense and precision is needed)

### 7.3 Small Multiples

**Definition:** A series of charts or maps using the same scale and axes, designed to facilitate comparison across many variables or time periods simultaneously.

**Rules:**
- Identical scales across all panels — never vary the Y-axis range between panels
- Same chart dimensions for all panels
- Panels arranged in a grid that encodes a meaningful variable (time by row, category by column)
- Label each panel clearly but minimally
- No internal chart titles — the grid structure provides context
- This is one of Tufte's highest-value techniques for data-dense communication

### 7.4 Sparklines

**Definition:** Small, simple, word-sized graphics — data visualizations the size of a word, embedded in text or tables.

**Design rules:**
- No axes, no labels, no titles — the surrounding text provides context
- Scale: the entire data range fills the height of the graphic
- Width: proportional to the number of data points (1–2px per point is typical)
- Use for: inline trend summaries, table-embedded trends, dashboard KPIs

### 7.5 Graphical Integrity: The Six Principles

1. **The representation of numbers should be directly proportional to the numerical quantities represented** — no bar chart where the bar length does not start at zero (unless clearly disclosed and justified)
2. **Clear, detailed, thorough labeling should be used to defeat graphical distortion** — label all axes; do not rely on readers inferring scale
3. **Show data variation, not design variation** — visual variation should come from the data, not from stylistic choices in the graphic
4. **In time-series displays, do not use money amounts deflated by a non-financial variable** unless clearly documented
5. **The number of information-carrying dimensions depicted should not exceed the number of dimensions in the data** — 3D charts for 2D data violate this principle
6. **Graphics must not quote data out of context** — if the baseline matters, show it

### 7.6 The Lie Factor

**Definition:** Lie Factor = (size of effect shown in graphic) / (size of effect in data)

A perfect graphic has a Lie Factor of 1.0. Values above 1.0 exaggerate; values below 1.0 understate.

**Common sources of Lie Factor > 1.0:**
- Y-axis that does not start at zero (exaggerates change)
- Area encodings where one dimension is scaled while both are perceived (e.g., circle area vs. radius)
- 3D bar charts where depth adds apparent volume not in the data

---

## 8. python-pptx Implementation Protocol for Think-Cell Quality

### 8.1 Coordinate System

python-pptx uses EMU (English Metric Units). All coordinates and dimensions are in EMUs.

```python
from pptx.util import Inches, Pt, Emu, Cm

# Conversion constants
1 inch = 914400 EMU
1 cm = 360000 EMU
1 pt = 12700 EMU

# Standard slide dimensions (widescreen 16:9)
slide_width = Inches(13.33)   # 12192000 EMU
slide_height = Inches(7.5)    # 6858000 EMU

# Standard slide dimensions (4:3)
slide_width = Inches(10)
slide_height = Inches(7.5)
```

### 8.2 Three-Zone Layout Template (Consulting Standard)

```python
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor

# Zone dimensions for 16:9 widescreen (13.33" x 7.5")
MARGIN_LEFT   = Inches(0.5)
MARGIN_RIGHT  = Inches(0.5)
MARGIN_TOP    = Inches(0.3)

TITLE_TOP     = Inches(0.3)
TITLE_LEFT    = Inches(0.5)
TITLE_WIDTH   = Inches(12.33)
TITLE_HEIGHT  = Inches(0.9)   # 1-2 lines at 18-20pt

BODY_TOP      = Inches(1.35)
BODY_LEFT     = Inches(0.5)
BODY_WIDTH    = Inches(12.33)
BODY_HEIGHT   = Inches(5.6)

FOOTER_TOP    = Inches(7.0)
FOOTER_LEFT   = Inches(0.5)
FOOTER_WIDTH  = Inches(12.33)
FOOTER_HEIGHT = Inches(0.35)
```

### 8.3 Typography Standards in python-pptx

```python
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Action title
title_tf = title_shape.text_frame
title_para = title_tf.paragraphs[0]
title_para.alignment = PP_ALIGN.LEFT
run = title_para.add_run()
run.text = "Action title text here"
run.font.name = "Arial"
run.font.size = Pt(18)
run.font.bold = True
run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)  # near-black

# Body text
body_run.font.name = "Arial"
body_run.font.size = Pt(11)
body_run.font.bold = False
body_run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

# Source footer
footer_run.font.name = "Arial"
footer_run.font.size = Pt(8)
footer_run.font.color.rgb = RGBColor(0x7D, 0x7D, 0x7D)
```

### 8.4 Native Chart Formatting in python-pptx

python-pptx supports native PPTX chart objects (not images). These are editable and cleaner than embedded matplotlib images.

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.util import Pt
from pptx.dml.color import RGBColor

# Add a bar chart
chart_data = CategoryChartData()
chart_data.categories = ['Category A', 'Category B', 'Category C']
chart_data.add_series('Series 1', (42.0, 27.0, 31.0))

chart_frame = slide.shapes.add_chart(
    XL_CHART_TYPE.BAR_CLUSTERED,
    BODY_LEFT, BODY_TOP,
    BODY_WIDTH, Inches(4.5),
    chart_data
)
chart = chart_frame.chart

# Remove legend (use direct labels instead — consulting standard)
chart.has_legend = False

# Add data labels
plot = chart.plots[0]
plot.has_data_labels = True
data_labels = plot.data_labels
data_labels.font.size = Pt(9)
data_labels.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)

# Style the chart area
chart.chart_style = 2  # minimal/clean style number

# Remove chart border
from pptx.oxml.ns import qn
from lxml import etree
# Chart area formatting requires lxml for full control
```

### 8.5 Matplotlib to PPTX: The Embed-as-Vector Approach

When using matplotlib for charts that python-pptx cannot natively render (e.g., waterfall, Mekko, sparklines):

```python
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
from pptx.util import Inches

# Step 1: Set matplotlib to match the font system
matplotlib.rcParams['font.family'] = 'Arial'
matplotlib.rcParams['font.size'] = 9
matplotlib.rcParams['axes.linewidth'] = 0.5
matplotlib.rcParams['xtick.major.width'] = 0.5
matplotlib.rcParams['ytick.major.width'] = 0.5

# Step 2: Remove chartjunk from matplotlib defaults
fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=300)  # 16:9 ratio, 300dpi for sharp rendering
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(0.5)
ax.spines['bottom'].set_linewidth(0.5)
ax.yaxis.grid(True, linewidth=0.3, color='#E0E0E0', linestyle='-')
ax.set_axisbelow(True)

# Step 3: Match consulting color palette
PRIMARY_COLOR = '#003F5C'
ACCENT_COLOR  = '#009639'
GRAY_COLOR    = '#7D7D7D'

# Step 4: Remove tick marks where not needed
ax.tick_params(axis='both', which='both', length=0)

# Step 5: Save as PNG at 300dpi to BytesIO buffer
buffer = BytesIO()
fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
buffer.seek(0)
plt.close(fig)

# Step 6: Embed in slide at known position
slide.shapes.add_picture(buffer, BODY_LEFT, BODY_TOP, BODY_WIDTH, Inches(4.5))
```

### 8.6 Known python-pptx Limitations and Workarounds

| Limitation | Workaround |
|---|---|
| No native waterfall chart type | Build with stacked bar + invisible base series; or use matplotlib embed |
| No native Mekko/Marimekko | Use matplotlib or plotly with embed approach |
| No native Gantt | Use stacked horizontal bar with date axis; or draw shapes programmatically |
| Plot area size not directly controllable | Use lxml to write `<c:plotArea>` XML directly |
| No CAGR bracket annotation natively | Draw as combined line + text shape using python-pptx shapes API |
| Font inheritance is undocumented | Always explicitly set font properties; do not rely on theme inheritance |
| Chart style numbers undocumented | Test chart_style = 2 or 10 for minimal clean styles; trial and error required |
| Legend font size limited | Use lxml direct XML edit on `<c:txPr>` element in legend XML |

### 8.7 Color Definition Patterns

```python
# Standard consulting color palette
class ConsultingPalette:
    # McKinsey
    MCKINSEY_BLUE     = RGBColor(0x00, 0x2F, 0x6C)
    MCKINSEY_ACCENT   = RGBColor(0x00, 0x70, 0xC0)

    # BCG
    BCG_GREEN         = RGBColor(0x00, 0x96, 0x39)
    BCG_DARK_BLUE     = RGBColor(0x00, 0x3F, 0x5C)

    # Universal
    GRAY_MEDIUM       = RGBColor(0x7D, 0x7D, 0x7D)
    GRAY_LIGHT        = RGBColor(0xC8, 0xC8, 0xC8)
    POSITIVE_GREEN    = RGBColor(0x2E, 0x7D, 0x32)
    NEGATIVE_RED      = RGBColor(0xC6, 0x28, 0x28)
    NEAR_BLACK        = RGBColor(0x1A, 0x1A, 0x1A)
    WHITE             = RGBColor(0xFF, 0xFF, 0xFF)

    # Gartner
    GARTNER_ORANGE    = RGBColor(0xFF, 0x80, 0x00)
    GARTNER_GRAY      = RGBColor(0x4D, 0x4D, 0x4D)
```

### 8.8 DPI and Resolution Protocol

- Charts embedded as images: always render at 300 DPI minimum
- For on-screen use only (not print): 150 DPI acceptable
- Save PNG with `bbox_inches='tight'` and `facecolor='white'` to avoid transparent backgrounds that render poorly in PPTX
- Figure size in inches: set the matplotlib figsize to match the intended output dimensions on the slide so that font sizes are consistent

```python
# If the chart will occupy 6.4" x 3.6" on the slide:
fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=300)
# This ensures a 9pt axis label in matplotlib = ~9pt on the slide
```

---

## 9. Synthesis: Unified Design Rule Set for Agent System Prompt

The following is a distilled, agent-ready rule set drawing from all seven sources. It is ordered by decision priority.

### 9.1 Structure Rules (apply before any visual decision)

1. Every slide has one action title — a complete declarative sentence stating the takeaway, max 15 words, max 2 lines
2. Every slide communicates exactly one message
3. All body content must support the action title; if it does not, delete it
4. The sequence of action titles, read alone, must tell the complete argument
5. Source attribution is mandatory on every slide with quantitative data

### 9.2 Visual Hierarchy Rules (apply to every slide)

6. One element must be visually dominant — the viewer's eye must go there first, and that element must carry the key message
7. Size encodes importance: title > key number/callout > body > footer — never invert this
8. Color encodes meaning: primary = brand/key, gray = supporting, green = positive, red = negative — never use color for decoration
9. Maximum 3–4 colors per chart
10. Direct labels always preferred over legends

### 9.3 Chart Rules (apply to every data visualization)

11. Remove all chartjunk: no 3D effects, no gradient fills, no drop shadows, no pattern fills, no decorative borders
12. Remove all non-data-ink: frame borders, unnecessary gridlines (keep only light gray horizontal gridlines at 0.5pt when precision is needed), redundant axis labels
13. Maximize data-ink ratio: every pixel must earn its place
14. Never truncate Y-axis to artificially amplify differences without disclosure
15. Chart type must match insight type: trend→line, composition→stacked bar/Mekko, comparison→bar, flow→waterfall, schedule→Gantt, positioning→2x2
16. Scales must be identical across all comparison panels (small multiples rule)

### 9.4 Typography Rules

17. Maximum 2 font families per deck (1 is better)
18. Font sizes are fixed within each element type — never vary action title font size across slides
19. Minimum body text: 11pt (print), 24pt (projected presentation)
20. Source footer: 8pt, gray
21. Never reduce font size to make content fit — simplify the content instead

### 9.5 Layout Rules

22. Three-zone layout: header strip (action title) / body (one chart or exhibit) / source strip
23. Consistent margins: left and right margins equal; fixed title position that does not shift when flipping through slides
24. White space is active — do not fill every inch; leave breathing room
25. Align everything to an invisible grid; pixel-perfect alignment is a credibility signal

### 9.6 The Glance Test (apply as quality gate)

26. Every slide must be comprehensible within 3 seconds (Duarte) or 10 seconds (BCG) from normal viewing distance
27. If the slide fails the glance test: simplify the message, remove noise elements, increase visual hierarchy contrast

---

## 10. Source Map

| Domain | Primary sources used | Authority level |
|---|---|---|
| Think-Cell design principles | think-cell Academy (academy.think-cell.com), think-cell manual (think-cell.com/en/resources/manual) | High — primary vendor documentation |
| McKinsey standards | deckary.com/blog/consulting-slide-standards, slideworks.io/resources/how-to-write-action-titles-like-mckinsey, slidescience.co/action-titles | Medium-high — synthesized from multiple consultant accounts |
| BCG slide grammar | deckary.com/blog/bcg-presentation-style, slideworks.io/resources/bcg-approach-to-great-slides-practical-guide | Medium-high — former BCG consultant accounts |
| Gartner visual language | gartner.com/en/research/methodologies/magic-quadrants-research, gartner.com/en/research/methodologies/gartner-hype-cycle | High for methodology; Gartner style files not publicly available |
| Nancy Duarte | duarte.com/resources/guides-tools/the-glance-test, HBR article (2012), slide:ology (book) | High — primary source |
| Edward Tufte | edwardtufte.com (book page), academic synthesis at umich.edu/~jpboyd/eng403_chap2_tuftegospel.pdf | High — canonical primary work |
| python-pptx | python-pptx.readthedocs.io, stackoverflow confirmed by library author (scanny) | High for API; chart style numbers remain undocumented |

---

## 11. Benchmark Targets

A slide design studio agent should target the following measurable quality criteria:

| Criterion | Target | Test method |
|---|---|---|
| Action title present | 100% of slides | String analysis: contains verb, is a sentence |
| Action title length | ≤ 15 words, ≤ 2 lines | Word count + line count |
| One chart per slide | ≤ 1 chart object in body zone | Shape count in body zone |
| Source attribution | 100% of slides with quantitative data | Presence of "Source:" in footer zone |
| Font families | ≤ 2 per deck | Font enumeration across all shapes |
| Colors used | ≤ 4 per chart | Color enumeration in chart XML |
| No 3D chart types | 0 3D chart type codes | XL_CHART_TYPE enum check |
| Data label font | ≥ 8pt | Font size check on all data labels |
| Chart DPI (embedded images) | ≥ 300 DPI | Image metadata |
| Title position consistency | ≤ 1pt variation across slides | Coordinate comparison |
| Glance test proxy | Title + one chart, no dense bullet text | Element type + count check |

---

## 12. Open Unknowns

1. **Think-Cell exact font size specifications** — the academy course describes principles but does not publish exact pt values for corporate default style files. The XML style file format is documented but example corporate defaults are proprietary.

2. **Gartner internal style guide** — Gartner's Magic Quadrant and Hype Cycle templates are proprietary. The visual specifications documented here are reverse-engineered from published outputs, not from a primary style guide.

3. **McKinsey and BCG internal template specifications** — Exact px/pt measurements, grid specifications, and approved color hex values are derived from multiple secondhand accounts (former consultants). They are directionally accurate but should be treated as approximations.

4. **python-pptx chart_style numbers** — The integer codes for built-in chart styles (chart.chart_style) are not documented in the official python-pptx documentation. Behavior requires empirical testing against specific PowerPoint versions.

5. **Plot area resizing via python-pptx** — The library author (scanny) confirmed there is no API support for chart plot area sizing. This requires direct lxml XML manipulation. The exact XML path and element structure needs implementation testing.

6. **Duarte's specific grid system** — slide:ology describes visual hierarchy and signal/noise but does not specify a numerical grid system. The typographic scale recommendations (36/28/24pt) come from Duarte Inc. training materials, not the book itself.

---

## 13. Recommended Next Research Steps

1. **Obtain a real McKinsey or BCG PPTX template** (publicly available from leaked/shared decks) and reverse-engineer the exact slide master settings: font sizes, color theme values, margin guides, placeholder positions.

2. **Test python-pptx chart_style integer values** experimentally (1–48) and document which produce minimal/consulting-appropriate styles in PowerPoint 365.

3. **Build a reference implementation** of the three-zone consulting layout in python-pptx with all formatting specifications hardcoded, then test rendering in both PowerPoint and Google Slides.

4. **Research the lxml XML path for chart plot area sizing** — inspect the raw PPTX XML of a Think-Cell-formatted chart to understand the `<c:plotArea>` structure, then implement a python-pptx extension for this.

5. **Research Apex Charts or Plotly alternatives** for Mekko and waterfall charts that produce cleaner SVG output than matplotlib, allowing vector embedding rather than raster PNG.

6. **Audit Duarte's slide:ology for numerical specifications** — the book contains specific grid and proportion guidelines that were not captured in web-based sources. Prioritize the 4:3 vs. 16:9 proportion rules and the typographic hierarchy system.

---

*Output file: `/Users/mikerodgers/Startup-Intelligence-OS/.claude/skills/research-packet/outputs/slide-design-studio-agent-knowledge-base.md`*
*Sources: think-cell Academy, deckary.com, slideworks.io, slidescience.co, duarte.com, edwardtufte.com, python-pptx documentation, gartner.com*
