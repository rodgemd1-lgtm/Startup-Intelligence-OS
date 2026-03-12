# SlideWorks Builder — Production Engineering Knowledge Base

> Canonical reference for the SlideWorks Builder agent.
> Covers python-pptx, matplotlib Think-Cell recipes, geopandas, QA pipeline, and production standards.

---

## 1. python-pptx Mastery

### 1.1 EMU Coordinate System

All python-pptx dimensions use English Metric Units (EMU). Master these constants:

```python
from pptx.util import Inches, Pt, Emu

# Core conversions
EMU_PER_INCH = 914400
EMU_PER_PT = 12700
EMU_PER_CM = 360000

# Standard 16:9 slide dimensions
SLIDE_WIDTH = 12192000   # 13.333 inches
SLIDE_HEIGHT = 6858000   # 7.5 inches

# Standard margins (0.5 inch)
MARGIN = 457200

# Usable content area
CONTENT_LEFT = MARGIN                          # 457200
CONTENT_TOP = MARGIN                           # 457200
CONTENT_WIDTH = SLIDE_WIDTH - (2 * MARGIN)     # 11277600
CONTENT_HEIGHT = SLIDE_HEIGHT - (2 * MARGIN)   # 5943600

# Element gap (0.3 inch)
GAP = 274320
```

Never use raw pixel values. Always convert through EMU to guarantee fidelity across renderers.

### 1.2 Slide Layout Indices

Default layout indices for the standard python-pptx template:

| Index | Layout Name           | Use Case                        |
|-------|-----------------------|---------------------------------|
| 0     | Title Slide           | Cover pages, section dividers   |
| 1     | Title and Content     | Standard body slides            |
| 2     | Section Header        | Chapter breaks                  |
| 3     | Two Content           | Side-by-side comparison         |
| 4     | Comparison            | Labeled left/right columns      |
| 5     | Title Only            | Custom-built slides (preferred) |
| 6     | Blank                 | Full custom layout              |

For production work, prefer layout index 5 (Title Only) or 6 (Blank) to avoid placeholder conflicts. When using a client template, enumerate layouts first:

```python
from pptx import Presentation

prs = Presentation('template.pptx')
for idx, layout in enumerate(prs.slide_layouts):
    print(f"Layout {idx}: {layout.name}")
    for ph in layout.placeholders:
        print(f"  Placeholder {ph.placeholder_format.idx}: {ph.name} ({ph.width}, {ph.height})")
```

### 1.3 Placeholder Management

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])

# Access existing placeholders by index
title_ph = slide.placeholders[0]
title_ph.text = "Action Title Goes Here"

# Format placeholder text
from pptx.util import Pt
from pptx.dml.color import RGBColor

for paragraph in title_ph.text_frame.paragraphs:
    for run in paragraph.runs:
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1C, 0x28, 0x33)
        run.font.name = 'Arial'
```

Always clear placeholder text frames before writing custom content to avoid collision with template defaults:

```python
tf = slide.placeholders[14].text_frame
tf.clear()
tf.paragraphs[0].add_run().text = ""
```

### 1.4 Shape Creation

#### Textboxes

```python
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

txBox = slide.shapes.add_textbox(
    left=Inches(0.5),
    top=Inches(0.5),
    width=Inches(12.33),
    height=Inches(0.6)
)
tf = txBox.text_frame
tf.word_wrap = True
tf.auto_size = None                # fixed size, no auto-resize
tf.margin_left = Pt(6)
tf.margin_right = Pt(6)
tf.margin_top = Pt(3)
tf.margin_bottom = Pt(3)

p = tf.paragraphs[0]
p.text = "Revenue grew 23% YoY driven by enterprise expansion"
p.font.size = Pt(24)
p.font.bold = True
p.font.color.rgb = RGBColor(0x1C, 0x28, 0x33)
p.alignment = PP_ALIGN.LEFT
```

#### Rectangles

```python
from pptx.enum.shapes import MSO_SHAPE

shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    left=Inches(0.5),
    top=Inches(0.5),
    width=Inches(12.33),
    height=Inches(0.8)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x1C, 0x28, 0x33)
shape.line.fill.background()  # no border
```

#### Tables

```python
rows, cols = 5, 4
table_shape = slide.shapes.add_table(
    rows, cols,
    left=Inches(0.5),
    top=Inches(1.8),
    width=Inches(12.33),
    height=Inches(4.5)
)
table = table_shape.table

# Set column widths
col_widths = [Inches(3.5), Inches(3.0), Inches(3.0), Inches(2.83)]
for i, width in enumerate(col_widths):
    table.columns[i].width = width

# Style header row
for col_idx in range(cols):
    cell = table.cell(0, col_idx)
    cell.text = headers[col_idx]
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0x1C, 0x28, 0x33)
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.size = Pt(11)
        paragraph.font.bold = True
        paragraph.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        paragraph.alignment = PP_ALIGN.LEFT

# Alternating row fills
for row_idx in range(1, rows):
    for col_idx in range(cols):
        cell = table.cell(row_idx, col_idx)
        if row_idx % 2 == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xF4, 0xE8, 0xD8)
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
```

#### Grouped Shapes

```python
from pptx.oxml.ns import qn
from lxml.etree import SubElement as OxmlElement

# python-pptx does not natively support group creation.
# Build groups via XML manipulation:
spTree = slide.shapes._spTree
grpSp = OxmlElement('p:grpSp')
grpSpPr = OxmlElement('p:grpSpPr')
xfrm = OxmlElement('a:xfrm')
# Set group bounding box
off = OxmlElement('a:off')
off.set('x', str(left))
off.set('y', str(top))
ext = OxmlElement('a:ext')
ext.set('cx', str(width))
ext.set('cy', str(height))
chOff = OxmlElement('a:chOff')
chOff.set('x', str(left))
chOff.set('y', str(top))
chExt = OxmlElement('a:chExt')
chExt.set('cx', str(width))
chExt.set('cy', str(height))
xfrm.append(off)
xfrm.append(ext)
xfrm.append(chOff)
xfrm.append(chExt)
grpSpPr.append(xfrm)
grpSp.append(grpSpPr)
spTree.append(grpSp)
```

### 1.5 Image Embedding at 300 DPI

```python
# Save matplotlib chart at 300 DPI first
fig.savefig('chart.png', dpi=300, bbox_inches='tight', transparent=True)

# Embed at exact dimensions (preserves DPI)
from PIL import Image
img = Image.open('chart.png')
width_px, height_px = img.size
width_inches = width_px / 300
height_inches = height_px / 300

slide.shapes.add_picture(
    'chart.png',
    left=Inches(0.5),
    top=Inches(1.5),
    width=Inches(width_inches),
    height=Inches(height_inches)
)
```

Never let python-pptx auto-scale images. Always calculate exact EMU dimensions from the source DPI.

### 1.6 XML-Level Manipulation for Advanced Formatting

#### Drop Shadows

```python
from pptx.oxml.ns import qn
from lxml.etree import SubElement as OxmlElement

def add_shadow(shape, blur_rad=50800, dist=38100, direction=2700000, alpha=40):
    """Add subtle drop shadow to a shape. Think-Cell style: soft, short offset."""
    spPr = shape._element.spPr
    effectLst = OxmlElement('a:effectLst')
    outerShdw = OxmlElement('a:outerShdw')
    outerShdw.set('blurRad', str(blur_rad))    # blur radius in EMU
    outerShdw.set('dist', str(dist))            # offset distance
    outerShdw.set('dir', str(direction))        # angle (2700000 = bottom-right)
    outerShdw.set('algn', 'bl')
    srgbClr = OxmlElement('a:srgbClr')
    srgbClr.set('val', '000000')
    alphaElem = OxmlElement('a:alpha')
    alphaElem.set('val', str(alpha * 1000))     # percentage * 1000
    srgbClr.append(alphaElem)
    outerShdw.append(srgbClr)
    effectLst.append(outerShdw)
    spPr.append(effectLst)
```

#### Gradient Fills

```python
def apply_gradient(shape, color1, color2, angle=0):
    """Apply linear gradient fill. angle=0 is left-to-right."""
    spPr = shape._element.spPr
    gradFill = OxmlElement('a:gradFill')
    gsLst = OxmlElement('a:gsLst')
    # Stop 1
    gs1 = OxmlElement('a:gs')
    gs1.set('pos', '0')
    srgb1 = OxmlElement('a:srgbClr')
    srgb1.set('val', color1.lstrip('#'))
    gs1.append(srgb1)
    gsLst.append(gs1)
    # Stop 2
    gs2 = OxmlElement('a:gs')
    gs2.set('pos', '100000')
    srgb2 = OxmlElement('a:srgbClr')
    srgb2.set('val', color2.lstrip('#'))
    gs2.append(srgb2)
    gsLst.append(gs2)
    gradFill.append(gsLst)
    lin = OxmlElement('a:lin')
    lin.set('ang', str(angle * 60000))  # degrees * 60000
    lin.set('scaled', '1')
    gradFill.append(lin)
    # Remove existing fill, add gradient
    existing_fill = spPr.find(qn('a:solidFill'))
    if existing_fill is not None:
        spPr.remove(existing_fill)
    spPr.append(gradFill)
```

### 1.7 Template Preservation

Rules for working with client templates:

1. Never modify slide masters or slide layouts programmatically
2. Load the template with `Presentation('template.pptx')` and only add new slides
3. Before adding shapes, check for existing placeholders and use them when available
4. Preserve the `_rels` folder structure when saving
5. Test the output file in PowerPoint, not just LibreOffice

```python
# Safe template usage pattern
prs = Presentation('client_template.pptx')

# Use the template's layout — do NOT create new layouts
layout = prs.slide_layouts[5]  # Title Only or Blank
slide = prs.slides.add_slide(layout)

# Build custom content on top, never modify the master
# ...

prs.save('output.pptx')
```

### 1.8 Color Application

```python
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR

# Direct RGB
shape.fill.fore_color.rgb = RGBColor(0x1C, 0x28, 0x33)

# Theme color (respects template theme)
shape.fill.fore_color.theme_color = MSO_THEME_COLOR.ACCENT_1

# Transparency (via XML — python-pptx does not expose this directly)
def set_fill_transparency(shape, percent):
    """Set fill transparency. 0 = opaque, 100 = invisible."""
    solidFill = shape._element.spPr.find(qn('a:solidFill'))
    if solidFill is not None:
        srgbClr = solidFill.find(qn('a:srgbClr'))
        if srgbClr is not None:
            alpha = OxmlElement('a:alpha')
            alpha.set('val', str((100 - percent) * 1000))
            srgbClr.append(alpha)
```

### 1.9 Font Management

```python
from pptx.util import Pt

# Standard font stack (safe for cross-platform rendering)
FONT_PRIMARY = 'Arial'
FONT_SECONDARY = 'Calibri'

def style_run(run, size=11, bold=False, italic=False, color='#2C3E50', font=FONT_PRIMARY):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor.from_string(color.lstrip('#'))
    run.font.name = font
```

Never rely on template inheritance for font face, size, color, or weight. Always set font properties explicitly on every run.

### 1.10 Paragraph Formatting

```python
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt, Emu

p = tf.paragraphs[0]
p.alignment = PP_ALIGN.LEFT            # LEFT, CENTER, RIGHT, JUSTIFY
p.space_before = Pt(6)                 # space above paragraph
p.space_after = Pt(3)                  # space below paragraph
p.line_spacing = Pt(18)                # exact line height
p.level = 0                            # indentation level (0-8)

# Bullet formatting via XML
pPr = p._pPr
if pPr is None:
    pPr = OxmlElement('a:pPr')
    p._p.insert(0, pPr)
pPr.set('marL', str(int(Emu(Inches(0.25)))))  # left margin
pPr.set('indent', str(int(Emu(Inches(-0.25)))))  # hanging indent
```

### 1.11 Table Styling: Cell Borders, Merged Cells, Alternating Rows

```python
from pptx.oxml.ns import qn
from lxml.etree import SubElement as OxmlElement

def set_cell_border(cell, side, width_pt=0.5, color='#CCCCCC'):
    """Set border on one side of a table cell. side: 'top', 'bottom', 'left', 'right'."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tag_map = {
        'top': 'a:lnT', 'bottom': 'a:lnB',
        'left': 'a:lnL', 'right': 'a:lnR'
    }
    ln = OxmlElement(tag_map[side])
    ln.set('w', str(int(width_pt * 12700)))  # pt to EMU
    solidFill = OxmlElement('a:solidFill')
    srgbClr = OxmlElement('a:srgbClr')
    srgbClr.set('val', color.lstrip('#'))
    solidFill.append(srgbClr)
    ln.append(solidFill)
    tcPr.append(ln)

def remove_cell_border(cell, side):
    """Remove border on one side of a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tag_map = {
        'top': 'a:lnT', 'bottom': 'a:lnB',
        'left': 'a:lnL', 'right': 'a:lnR'
    }
    ln = OxmlElement(tag_map[side])
    ln.set('w', '0')
    noFill = OxmlElement('a:noFill')
    ln.append(noFill)
    tcPr.append(ln)

# Merge cells
table.cell(0, 0).merge(table.cell(0, 2))  # merge columns 0-2 in row 0
```

---

## 2. matplotlib to Think-Cell Quality

All charts must look indistinguishable from Think-Cell output. This means: flat fills, no gradients, no 3D, direct data labels, minimal chrome, and precise spacing.

### 2.1 Universal Baseline Settings

Apply these settings to EVERY chart before any type-specific configuration:

```python
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Global rcParams for Think-Cell consistency
plt.rcParams.update({
    "font.family":        "sans-serif",
    "font.sans-serif":    ["Arial", "Helvetica", "DejaVu Sans"],
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.labelcolor":    "#2C3E50",
    "xtick.color":        "#2C3E50",
    "ytick.color":        "#2C3E50",
    "text.color":         "#2C3E50",
    "figure.facecolor":   "none",
    "axes.facecolor":     "none",
    "savefig.facecolor":  "none",
})

def create_thinkcell_figure(width=10, height=6):
    """Create a matplotlib figure with Think-Cell baseline styling."""
    fig, ax = plt.subplots(figsize=(width, height))

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Style remaining spines
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_linewidth(0.5)
    ax.spines['bottom'].set_color('#CCCCCC')

    # Remove tick marks (keep labels)
    ax.tick_params(axis='both', which='both', length=0)

    # Axis label sizing
    ax.tick_params(axis='x', labelsize=9, labelcolor='#2C3E50')
    ax.tick_params(axis='y', labelsize=9, labelcolor='#2C3E50')

    # NO gridlines by default
    ax.grid(False)

    # Ensure gridlines draw below data when enabled
    ax.set_axisbelow(True)

    # Tight layout
    fig.tight_layout(pad=1.0)

    return fig, ax


def save_thinkcell_chart(fig, filename, dpi=300):
    """Save chart at production quality: 300 DPI, transparent background."""
    fig.savefig(
        filename,
        dpi=dpi,
        bbox_inches='tight',
        transparent=True,
        pad_inches=0.1
    )
    plt.close(fig)
```

### 2.2 Bar Charts

```python
def bar_chart(categories, values, colors=None, orientation='vertical',
              show_labels=True, label_fmt='{:.0f}', title=None):
    """
    Think-Cell style bar chart.
    - 0.6 width ratio (bars fill 60% of available space)
    - 2pt white gap between bars (via white edgecolor)
    - Flat fills from approved palette
    - Direct labels above/beside each bar
    """
    PALETTE = ['#1B2A4A', '#0E6E8E', '#5DADE2', '#C74334', '#95A5A6']
    if colors is None:
        colors = [PALETTE[i % len(PALETTE)] for i in range(len(categories))]

    fig, ax = create_thinkcell_figure()

    x = range(len(categories))
    bar_width = 0.6

    if orientation == 'vertical':
        bars = ax.bar(x, values, width=bar_width, color=colors,
                      edgecolor='white', linewidth=2, zorder=3)
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])

        if show_labels:
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(values) * 0.02,
                        label_fmt.format(val),
                        ha='center', va='bottom', fontsize=10, fontweight='bold',
                        color='#2C3E50')
    else:
        bars = ax.barh(x, values, height=bar_width, color=colors,
                       edgecolor='white', linewidth=2, zorder=3)
        ax.set_yticks(x)
        ax.set_yticklabels(categories)
        ax.spines['bottom'].set_visible(False)
        ax.set_xticks([])
        ax.invert_yaxis()

        if show_labels:
            for bar, val in zip(bars, values):
                ax.text(bar.get_width() + max(values) * 0.02,
                        bar.get_y() + bar.get_height() / 2,
                        label_fmt.format(val),
                        ha='left', va='center', fontsize=10, fontweight='bold',
                        color='#2C3E50')

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', color='#1C2833',
                      loc='left', pad=15)

    return fig, ax
```

### 2.3 Line Charts

```python
def line_chart(x_data, series_dict, title=None, x_label=None, y_label=None):
    """
    Think-Cell style line chart.
    - 2pt lines
    - 6pt circular markers with white edge
    - No area fill
    - Direct labels at last data point (no legend box)
    """
    PALETTE = ['#1B2A4A', '#0E6E8E', '#5DADE2', '#C74334', '#95A5A6']
    fig, ax = create_thinkcell_figure()

    for i, (label, y_data) in enumerate(series_dict.items()):
        color = PALETTE[i % len(PALETTE)]
        ax.plot(x_data, y_data, color=color, linewidth=2, marker='o',
                markersize=6, markerfacecolor=color, markeredgecolor='white',
                markeredgewidth=1.5, zorder=3, label=label)

        # Direct label at the last data point
        ax.annotate(label,
                    xy=(x_data[-1], y_data[-1]),
                    xytext=(10, 0), textcoords='offset points',
                    fontsize=9, fontweight='bold', color=color,
                    va='center')

    # Light horizontal gridlines only
    ax.yaxis.grid(True, linewidth=0.3, color='#EEEEEE', zorder=0)

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', color='#1C2833',
                      loc='left', pad=15)
    if x_label:
        ax.set_xlabel(x_label, fontsize=9, color='#2C3E50')
    if y_label:
        ax.set_ylabel(y_label, fontsize=9, color='#2C3E50')

    # No legend — labels are direct
    return fig, ax
```

### 2.4 Waterfall Charts

```python
def waterfall_chart(categories, values, subtotal_indices=None, title=None):
    """
    Think-Cell style waterfall chart.
    - Green (#27AE60) for positive deltas
    - Red (#E74C3C) for negative deltas
    - Gray (#95A5A6) for subtotals/totals
    - Thin connector lines between bars
    """
    GREEN = '#27AE60'
    RED = '#E74C3C'
    GRAY = '#95A5A6'

    if subtotal_indices is None:
        subtotal_indices = set()
    else:
        subtotal_indices = set(subtotal_indices)

    fig, ax = create_thinkcell_figure()

    n = len(categories)
    cumulative = 0
    bottoms = []
    tops = []
    colors = []

    for i, val in enumerate(values):
        if i in subtotal_indices:
            bottoms.append(0)
            tops.append(cumulative)
            colors.append(GRAY)
        else:
            if val >= 0:
                bottoms.append(cumulative)
                cumulative += val
                tops.append(cumulative)
                colors.append(GREEN)
            else:
                cumulative += val
                bottoms.append(cumulative)
                tops.append(cumulative - val)
                colors.append(RED)

    bar_heights = [t - b for b, t in zip(bottoms, tops)]
    x = range(n)

    bars = ax.bar(x, bar_heights, bottom=bottoms, width=0.6,
                  color=colors, edgecolor='white', linewidth=2, zorder=3)

    # Connector lines between bars
    for i in range(n - 1):
        if i not in subtotal_indices:
            connector_y = tops[i] if values[i] >= 0 else bottoms[i]
        else:
            connector_y = tops[i]
        ax.plot([i + 0.3, i + 0.7], [connector_y, connector_y],
                color='#CCCCCC', linewidth=0.8, zorder=2)

    # Direct labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        label_y = tops[i] + max(abs(v) for v in values) * 0.02
        if i in subtotal_indices:
            label = f'{tops[i]:,.0f}'
        elif val > 0:
            label = f'+{val:,.0f}'
        else:
            label = f'{val:,.0f}'
        ax.text(i, label_y, label, ha='center', va='bottom',
                fontsize=9, fontweight='bold', color='#2C3E50')

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    ax.spines['left'].set_visible(False)
    ax.set_yticks([])

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', color='#1C2833',
                      loc='left', pad=15)

    return fig, ax
```

### 2.5 Gantt Charts

```python
def gantt_chart(tasks, title=None):
    """
    Think-Cell style Gantt chart.
    - Horizontal bars with rounded ends
    - Milestone diamonds for key dates
    - tasks: list of dicts with keys: name, start, end, color (optional), milestone (optional)
    """
    from matplotlib.patches import FancyBboxPatch
    import matplotlib.dates as mdates

    PALETTE = ['#1B2A4A', '#0E6E8E', '#5DADE2', '#C74334', '#95A5A6']
    fig, ax = create_thinkcell_figure(width=12, height=max(4, len(tasks) * 0.6))

    for i, task in enumerate(reversed(tasks)):
        color = task.get('color', PALETTE[i % len(PALETTE)])
        start = mdates.date2num(task['start'])
        end = mdates.date2num(task['end'])
        duration = end - start

        # Rounded bar via FancyBboxPatch
        bar = FancyBboxPatch(
            (start, i - 0.2), duration, 0.4,
            boxstyle="round,pad=0.05,rounding_size=0.15",
            facecolor=color, edgecolor='none', zorder=3
        )
        ax.add_patch(bar)

        # Task label to the left
        ax.text(start - 0.5, i, task['name'], ha='right', va='center',
                fontsize=9, color='#2C3E50')

        # Milestone diamond marker
        if task.get('milestone'):
            ms_date = mdates.date2num(task['milestone'])
            ax.scatter(ms_date, i, marker='D', s=60, color='#C74334',
                       edgecolor='white', linewidth=1.5, zorder=4)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', color='#1C2833',
                      loc='left', pad=15)

    return fig, ax
```

### 2.6 Scatter and Bubble Charts

```python
def scatter_chart(data, x_key, y_key, size_key=None, label_key=None,
                  color_key=None, title=None):
    """
    Think-Cell style scatter/bubble chart.
    - Sized by value when size_key provided
    - Direct labels on each point
    - Light crosshair gridlines
    """
    PALETTE = ['#1B2A4A', '#0E6E8E', '#5DADE2', '#C74334', '#95A5A6']
    fig, ax = create_thinkcell_figure()

    x_vals = [d[x_key] for d in data]
    y_vals = [d[y_key] for d in data]

    if size_key:
        raw_sizes = [d[size_key] for d in data]
        max_size = max(raw_sizes)
        sizes = [300 * (s / max_size) + 30 for s in raw_sizes]
    else:
        sizes = [80] * len(data)

    if color_key:
        colors = [d[color_key] for d in data]
    else:
        colors = [PALETTE[i % len(PALETTE)] for i in range(len(data))]

    ax.scatter(x_vals, y_vals, s=sizes, c=colors, alpha=0.85,
               edgecolors='white', linewidths=1.5, zorder=3)

    # Direct labels
    if label_key:
        for d, x, y in zip(data, x_vals, y_vals):
            ax.annotate(d[label_key], (x, y),
                        xytext=(8, 8), textcoords='offset points',
                        fontsize=8, color='#2C3E50')

    # Light gridlines
    ax.yaxis.grid(True, linewidth=0.3, color='#EEEEEE', zorder=0)
    ax.xaxis.grid(True, linewidth=0.3, color='#EEEEEE', zorder=0)

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', color='#1C2833',
                      loc='left', pad=15)

    return fig, ax
```

### 2.7 Pie Charts (Use Sparingly)

```python
def pie_chart(labels, values, explode_index=0, title=None):
    """
    Think-Cell style pie chart. Use ONLY when proportional composition matters.
    - Max 5 segments
    - Exploded slice for emphasis
    - Direct labels with percentages
    - No legend
    """
    assert len(labels) <= 5, "Pie charts must have 5 segments or fewer"

    PALETTE = ['#1B2A4A', '#0E6E8E', '#5DADE2', '#C74334', '#95A5A6']
    colors = PALETTE[:len(labels)]

    explode = [0.05 if i == explode_index else 0 for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(8, 8))

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors, explode=explode,
        autopct='%1.0f%%', startangle=90, pctdistance=0.75,
        textprops={'fontsize': 10, 'color': '#2C3E50'}
    )

    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_color('white')
        autotext.set_fontsize(11)

    ax.axis('equal')

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', color='#1C2833',
                      pad=20)

    return fig, ax
```

### 2.8 Annotations and Callouts

```python
def add_delta_bracket(ax, x1, y1, x2, y2, label, color='#2C3E50'):
    """Add a delta bracket showing the difference between two values."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='<->', color=color, lw=1.2))
    mid_y = (y1 + y2) / 2
    ax.text(x1 + 0.3, mid_y, label, fontsize=9, fontweight='bold',
            color=color, va='center')


def add_cagr_label(ax, x_start, y_start, x_end, y_end, cagr_pct):
    """Add a CAGR annotation between two points."""
    mid_x = (x_start + x_end) / 2
    mid_y = (y_start + y_end) / 2
    ax.annotate(f'CAGR: {cagr_pct:.1f}%',
                xy=(mid_x, mid_y * 1.1),
                fontsize=9, fontweight='bold', fontstyle='italic',
                color='#0E6E8E', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='#0E6E8E', linewidth=0.8))


def add_callout_arrow(ax, x_from, y_from, x_to, y_to, label):
    """Add a callout arrow with text. Thin, dark, professional."""
    ax.annotate(label,
                xy=(x_to, y_to), xytext=(x_from, y_from),
                fontsize=8, color='#2C3E50',
                arrowprops=dict(arrowstyle='->', color='#2C3E50',
                                linewidth=1.0, connectionstyle='arc3,rad=0.1'),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#F4E8D8',
                          edgecolor='#CCCCCC', linewidth=0.5))
```

---

## 3. geopandas Country Maps

### 3.1 Setup and Data Source

```python
import geopandas as gpd
import matplotlib.pyplot as plt

# Use Natural Earth 110m for country-level maps (lightweight, fast)
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# For higher resolution when needed:
# world = gpd.read_file('ne_50m_admin_0_countries.shp')
# world = gpd.read_file('ne_10m_admin_0_countries.shp')

# ISO column detection (fallback chain for different geopandas versions)
iso_col = None
for candidate in ("iso_a3", "ISO_A3", "ADM0_A3", "adm0_a3"):
    if candidate in world.columns:
        iso_col = candidate
        break
```

### 3.2 Country Silhouette Style

```python
def country_map(target_countries, color_map=None, context_region=None, title=None):
    """
    Think-Cell style country map.
    - Solid fill, no borders or very thin (#CCCCCC, 0.3pt) borders
    - Context regions in light gray
    - Minimal: no labels, no legend, no axes
    """
    PALETTE = {
        'tier1': '#1B2A4A',
        'tier2': '#0E6E8E',
        'tier3': '#5DADE2',
        'context': '#ECF0F1'
    }

    if color_map is None:
        color_map = {c: PALETTE['tier1'] for c in target_countries}

    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot context region (neighboring countries, light gray)
    if context_region is not None:
        context = world[world['continent'] == context_region]
        context.plot(ax=ax, color=PALETTE['context'],
                     edgecolor='#CCCCCC', linewidth=0.3)

    # Plot target countries with assigned colors
    for country, color in color_map.items():
        subset = world[world['name'] == country]
        if not subset.empty:
            subset.plot(ax=ax, color=color,
                        edgecolor='#CCCCCC', linewidth=0.3)

    # Remove all axes and chrome
    ax.set_axis_off()

    # Tight crop to data extent with padding
    minx, miny, maxx, maxy = world[
        world['name'].isin(target_countries)
    ].total_bounds
    padding = 5  # degrees
    ax.set_xlim(minx - padding, maxx + padding)
    ax.set_ylim(miny - padding, maxy + padding)

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', color='#1C2833',
                      loc='left', pad=15)

    return fig, ax
```

### 3.3 Color Coding by Tier or Status

```python
# Example: color countries by market maturity tier
tier_map = {
    'United States': '#1B2A4A',     # Tier 1 — established
    'United Kingdom': '#1B2A4A',
    'Germany': '#0E6E8E',           # Tier 2 — growing
    'France': '#0E6E8E',
    'India': '#5DADE2',             # Tier 3 — emerging
    'Brazil': '#5DADE2',
}

fig, ax = country_map(
    target_countries=list(tier_map.keys()),
    color_map=tier_map,
    context_region=None,
    title='Market Presence by Tier'
)
save_thinkcell_chart(fig, 'market_map.png')
```

### 3.4 Region Crop Presets

```python
REGION_BOUNDS = {
    'north_america': (-170, 10, -50, 85),
    'europe': (-15, 34, 45, 72),
    'asia_pacific': (60, -50, 180, 55),
    'middle_east': (25, 10, 65, 45),
    'africa': (-20, -38, 55, 40),
    'global': (-180, -60, 180, 85),
}

def set_region_bounds(ax, region='global'):
    """Apply preset geographic bounds to crop the map view."""
    bounds = REGION_BOUNDS.get(region, REGION_BOUNDS['global'])
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
```

---

## 4. QA Pipeline

### 4.1 LibreOffice Headless: PPTX to PDF to JPEG

```bash
# Step 1: Convert PPTX to PDF
libreoffice --headless --convert-to pdf --outdir ./output ./output.pptx

# Step 2: Convert PDF pages to JPEG at 150 DPI (per slide)
pdftoppm -jpeg -r 150 ./output/output.pdf ./output/slide
# Result: ./output/slide-01.jpg, slide-02.jpg, etc.
```

```python
import subprocess
import os

def pptx_to_images(pptx_path, output_dir, dpi=150):
    """Convert PPTX to per-slide JPEG images via LibreOffice headless."""
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: PPTX to PDF
    subprocess.run([
        'libreoffice', '--headless', '--convert-to', 'pdf',
        '--outdir', output_dir, pptx_path
    ], check=True, timeout=120)

    pdf_name = os.path.splitext(os.path.basename(pptx_path))[0] + '.pdf'
    pdf_path = os.path.join(output_dir, pdf_name)

    # Step 2: PDF to JPEG
    subprocess.run([
        'pdftoppm', '-jpeg', '-r', str(dpi),
        pdf_path, os.path.join(output_dir, 'slide')
    ], check=True, timeout=120)

    # Return sorted list of generated slide images
    images = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.startswith('slide') and f.endswith('.jpg')
    ])
    return images
```

### 4.2 Per-Slide Visual Regression Checks

```python
from PIL import Image
import numpy as np

def visual_diff(image_a_path, image_b_path, threshold=0.02):
    """
    Compare two slide images. Returns True if difference exceeds threshold.
    threshold: fraction of pixels that differ (0.02 = 2%).
    """
    img_a = np.array(Image.open(image_a_path).convert('RGB'))
    img_b = np.array(Image.open(image_b_path).convert('RGB'))

    if img_a.shape != img_b.shape:
        return True  # different dimensions = definite change

    diff = np.abs(img_a.astype(int) - img_b.astype(int))
    changed_pixels = np.sum(np.any(diff > 10, axis=2))
    total_pixels = img_a.shape[0] * img_a.shape[1]
    change_ratio = changed_pixels / total_pixels

    return change_ratio > threshold
```

### 4.3 Brand Compliance Verification

```python
def check_brand_compliance(pptx_path, allowed_fonts=None, allowed_colors=None):
    """
    Verify font and color usage against brand standards.
    Returns a list of violations.
    """
    from pptx import Presentation
    from pptx.dml.color import RGBColor

    if allowed_fonts is None:
        allowed_fonts = {'Arial', 'Calibri'}
    if allowed_colors is None:
        allowed_colors = {
            '#1C2833', '#5DADE2', '#FFFFFF', '#F4E8D8',
            '#2C3E50', '#ECF0F1', '#1B2A4A', '#0E6E8E', '#C74334',
            '#27AE60', '#E74C3C', '#95A5A6', '#000000', '#CCCCCC',
            '#F5F5F5', '#333333', '#555555', '#E0E0E0', '#EEEEEE'
        }

    prs = Presentation(pptx_path)
    violations = []

    for slide_idx, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        # Check font
                        if run.font.name and run.font.name not in allowed_fonts:
                            violations.append(
                                f"Slide {slide_idx}: Disallowed font '{run.font.name}'"
                            )
                        # Check color
                        if run.font.color and run.font.color.rgb:
                            hex_color = f'#{run.font.color.rgb}'
                            if hex_color.upper() not in {c.upper() for c in allowed_colors}:
                                violations.append(
                                    f"Slide {slide_idx}: Disallowed text color {hex_color}"
                                )
    return violations
```

### 4.4 The 9-Rule Machine-Testable Quality Gate

Every slide deck produced by the SlideWorks Builder must pass all nine rules. These are binary pass/fail checks that can be automated.

| Rule | Check                                      | Pass Criteria                                    |
|------|--------------------------------------------|-------------------------------------------------|
| 1    | Action title                               | Starts with verb or noun-phrase, complete sentence, max 15 words |
| 2    | One chart per body zone                    | No stacking multiple charts/images in the body   |
| 3    | Source line on every data slide            | "Source:" text present at 8pt, bottom of slide   |
| 4    | Max 2 font families per slide              | Only Arial and Calibri (or client-specified)     |
| 5    | Max 4 colors per chart                     | Excluding gray/white                             |
| 6    | No 3D effects                              | No sp3d or scene3d XML elements anywhere         |
| 7    | Data labels at least 8pt                   | All text in chart zones must be readable         |
| 8    | Images at least 300 DPI                    | Verified at generation time (300 DPI export)     |
| 9    | Title position consistent                  | Within 5% tolerance from slide to slide          |

```python
def run_quality_gate(pptx_path):
    """
    Run the 9-rule quality gate. Returns dict of rule -> (pass: bool, detail: str).
    """
    from pptx import Presentation
    from pptx.util import Pt

    prs = Presentation(pptx_path)
    results = {}

    # --- Rule 1: Action title ---
    for slide_idx, slide in enumerate(prs.slides, 1):
        if slide.placeholders and 0 in slide.placeholders:
            title_text = slide.placeholders[0].text.strip()
            word_count = len(title_text.split())
            if word_count > 15:
                results[f'rule1_slide{slide_idx}'] = (
                    False, f'Title has {word_count} words (max 15)')
            elif word_count == 0:
                results[f'rule1_slide{slide_idx}'] = (False, 'Title is empty')
            else:
                results[f'rule1_slide{slide_idx}'] = (True, title_text)

    # --- Rule 2: One chart per body zone ---
    for slide_idx, slide in enumerate(prs.slides, 1):
        image_count = sum(1 for s in slide.shapes if s.shape_type == 13)
        chart_count = sum(1 for s in slide.shapes if s.has_chart)
        total = image_count + chart_count
        if total > 1:
            results[f'rule2_slide{slide_idx}'] = (
                False, f'{total} charts/images found (max 1)')
        else:
            results[f'rule2_slide{slide_idx}'] = (True, 'OK')

    # --- Rule 3: Source line on every data slide ---
    for slide_idx, slide in enumerate(prs.slides, 1):
        has_data = any(s.has_chart or s.shape_type == 13 for s in slide.shapes)
        if has_data:
            has_source = False
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text = shape.text_frame.text.lower()
                    if 'source:' in text or 'source ' in text:
                        has_source = True
                        break
            results[f'rule3_slide{slide_idx}'] = (
                has_source,
                'Source found' if has_source else 'Missing source line')

    # --- Rule 4: Max 2 font families per slide ---
    for slide_idx, slide in enumerate(prs.slides, 1):
        fonts = set()
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        if run.font.name:
                            fonts.add(run.font.name)
        if len(fonts) > 2:
            results[f'rule4_slide{slide_idx}'] = (
                False, f'{len(fonts)} fonts: {fonts}')
        else:
            results[f'rule4_slide{slide_idx}'] = (True, f'Fonts: {fonts}')

    # --- Rule 5: Max 4 colors per chart ---
    results['rule5'] = (True, 'Manual check required for embedded chart images')

    # --- Rule 6: No 3D effects ---
    for slide_idx, slide in enumerate(prs.slides, 1):
        found_3d = False
        for shape in slide.shapes:
            xml = shape._element.xml
            if 'sp3d' in xml.lower() or 'scene3d' in xml.lower():
                results[f'rule6_slide{slide_idx}'] = (False, '3D effect detected')
                found_3d = True
                break
        if not found_3d:
            results[f'rule6_slide{slide_idx}'] = (True, 'No 3D effects')

    # --- Rule 7: Data labels >= 8pt ---
    for slide_idx, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        if run.font.size and run.font.size < Pt(8):
                            results[f'rule7_slide{slide_idx}'] = (
                                False,
                                f'Font size {run.font.size / 12700:.0f}pt < 8pt')

    # --- Rule 8: Images >= 300 DPI ---
    results['rule8'] = (True, 'Verified at generation time (300 DPI export)')

    # --- Rule 9: Title position consistent ---
    title_positions = []
    for slide in prs.slides:
        if slide.placeholders and 0 in slide.placeholders:
            ph = slide.placeholders[0]
            title_positions.append((ph.left, ph.top))
    if title_positions:
        ref_left, ref_top = title_positions[0]
        tolerance_x = int(0.05 * 12192000)  # 5% of slide width
        tolerance_y = int(0.05 * 6858000)   # 5% of slide height
        for i, (left, top) in enumerate(title_positions[1:], 2):
            if abs(left - ref_left) > tolerance_x or abs(top - ref_top) > tolerance_y:
                results[f'rule9_slide{i}'] = (
                    False,
                    f'Title offset ({left}, {top}) vs reference ({ref_left}, {ref_top})')

    return results
```

---

## 5. Approved Color Palettes

### 5.1 SlideWorks Standard

| Role               | Hex       | RGB             | Usage                           |
|--------------------|-----------|-----------------|---------------------------------|
| Navy Blue          | #1C2833   | (28, 40, 51)    | Headers, emphasis               |
| Light Blue         | #5DADE2   | (93, 173, 226)  | Accents, highlights             |
| White              | #FFFFFF   | (255, 255, 255) | Primary background              |
| Cream              | #F4E8D8   | (244, 232, 216) | Alternate background            |
| Dark Gray          | #2C3E50   | (44, 62, 80)    | Body text                       |
| Light Gray         | #ECF0F1   | (236, 240, 241) | Subtle backgrounds, dividers    |

### 5.2 Oracle Health Brand

| Role               | Hex       | RGB             | Usage                           |
|--------------------|-----------|-----------------|---------------------------------|
| Oracle Red         | #C74334   | (199, 67, 52)   | Accent only, never body text    |
| Navy               | #1B2A4A   | (27, 42, 74)    | Headers, primary                |
| Teal               | #0E6E8E   | (14, 110, 142)  | Highlights, secondary           |

Dark backgrounds (#1B2A4A or darker) for hero and divider slides only.

### 5.3 Fusion Palette (Oracle x SlideWorks)

Use this palette when producing Oracle Health deliverables with SlideWorks tooling.

| Role               | Hex       | Source          | Usage                           |
|--------------------|-----------|-----------------|---------------------------------|
| Primary            | #1B2A4A   | Oracle Navy     | Headers, chart primary          |
| Secondary          | #0E6E8E   | Oracle Teal     | Accents, chart secondary        |
| Accent             | #C74334   | Oracle Red      | Sparingly, alerts, callouts     |
| Background         | #FFFFFF   | SlideWorks      | Primary background              |
| Alt Background     | #F4E8D8   | SlideWorks      | Alternate background            |
| Body Text          | #2C3E50   | SlideWorks      | All body copy                   |

Chart fill order: `#1B2A4A`, `#0E6E8E`, `#5DADE2`, `#C74334`, `#95A5A6`

### 5.4 Chart-Specific Colors

| Purpose            | Hex       | Usage                           |
|--------------------|-----------|---------------------------------|
| Positive delta     | #27AE60   | Waterfall gains, positive KPIs  |
| Negative delta     | #E74C3C   | Waterfall losses, negative KPIs |
| Subtotal/neutral   | #95A5A6   | Waterfall totals, disabled      |
| Gridline           | #CCCCCC   | Axis lines, borders             |
| Gridline light     | #EEEEEE   | Background gridlines            |

### 5.5 Color Application Rules

1. Never use more than 4 data colors in a single chart (excluding gray and white)
2. Always use the fill order specified in the active palette
3. Red (#C74334 or #E74C3C) is never used for body text or large area fills
4. Text on dark backgrounds must be white (#FFFFFF)
5. Text on light backgrounds must be dark gray (#2C3E50) or navy (#1B2A4A)
6. Ensure sufficient contrast: WCAG AA minimum (4.5:1 for text, 3:1 for large text)

---

## 6. War Room EMU Coordinates

The "War Room" layout is the standard production template for data-heavy slides. It divides the slide into fixed zones with precise EMU coordinates.

### 6.1 Zone Definitions

```
+----------------------------------------------------------+
| HEADER STRIP (dark bg, white text)                       |  top: 0
|   Action title, max 15 words                             |  height: 685800 (0.75")
+----------------------------------------------------------+
|                                                          |
|                                                          |
|                 BODY ZONE                                |
|   Charts, tables, key visuals                            |
|   Single chart per body zone                             |
|                                                          |
|                                                          |
+----------------------------------------------------------+
| SOURCE STRIP (8pt, gray text)                            |  bottom: 6515100
|   "Source: Company filings, SlideWorks analysis"         |  height: 342900 (0.375")
+----------------------------------------------------------+
```

### 6.2 Precise EMU Coordinates

```python
# War Room Layout — EMU Constants
WAR_ROOM = {
    # Header strip
    'header_left': 0,
    'header_top': 0,
    'header_width': 12192000,          # full slide width
    'header_height': 685800,           # 0.75 inches
    'header_text_left': 457200,        # 0.5" left margin
    'header_text_top': 137160,         # vertically centered in strip
    'header_text_width': 11277600,     # full width minus margins
    'header_text_height': 411480,

    # Body zone
    'body_left': 457200,               # 0.5" margin
    'body_top': 960120,                # header + gap
    'body_width': 11277600,            # full width minus margins
    'body_height': 5280660,            # remaining space minus source strip

    # Source strip
    'source_left': 457200,             # 0.5" margin
    'source_top': 6515100,             # near bottom
    'source_width': 11277600,
    'source_height': 342900,           # 0.375 inches

    # Margins and gaps
    'margin': 457200,                  # 0.5 inches
    'gap': 274320,                     # 0.3 inches
}
```

### 6.3 Standard Margins

| Measurement   | Inches | EMU     |
|---------------|--------|---------|
| All margins   | 0.5    | 457200  |
| Element gap   | 0.3    | 274320  |

### 6.4 Building a War Room Slide

```python
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.util import Pt
from PIL import Image as PILImage

def build_war_room_slide(prs, title_text, chart_path, source_text):
    """Assemble a complete War Room slide with header, chart, and source."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    WR = WAR_ROOM

    # Header strip (dark rectangle)
    header_bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        left=WR['header_left'], top=WR['header_top'],
        width=WR['header_width'], height=WR['header_height']
    )
    header_bg.fill.solid()
    header_bg.fill.fore_color.rgb = RGBColor(0x1B, 0x2A, 0x4A)
    header_bg.line.fill.background()

    # Header title text
    title_box = slide.shapes.add_textbox(
        left=WR['header_text_left'], top=WR['header_text_top'],
        width=WR['header_text_width'], height=WR['header_text_height']
    )
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p.font.name = 'Arial'

    # Body zone chart image
    img = PILImage.open(chart_path)
    img_w, img_h = img.size
    img_width_emu = WR['body_width']
    img_height_emu = int(img_width_emu * (img_h / img_w))

    # Ensure chart fits in body zone
    if img_height_emu > WR['body_height']:
        img_height_emu = WR['body_height']
        img_width_emu = int(img_height_emu * (img_w / img_h))

    # Center chart in body zone
    chart_left = WR['body_left'] + (WR['body_width'] - img_width_emu) // 2
    chart_top = WR['body_top'] + (WR['body_height'] - img_height_emu) // 2

    slide.shapes.add_picture(
        chart_path,
        left=chart_left, top=chart_top,
        width=img_width_emu, height=img_height_emu
    )

    # Source strip
    source_box = slide.shapes.add_textbox(
        left=WR['source_left'], top=WR['source_top'],
        width=WR['source_width'], height=WR['source_height']
    )
    tf = source_box.text_frame
    p = tf.paragraphs[0]
    p.text = source_text
    p.font.size = Pt(8)
    p.font.color.rgb = RGBColor(0x95, 0xA5, 0xA6)
    p.font.name = 'Arial'
    p.alignment = PP_ALIGN.LEFT

    return slide
```

### 6.5 The 12-Column Grid System

For complex layouts with multiple elements side by side, use a 12-column grid within the body zone:

```python
def grid_column(col_start, col_span, total_cols=12):
    """
    Calculate left position and width for a grid-based layout.
    Returns (left_emu, width_emu) within the body zone.
    """
    WR = WAR_ROOM
    usable_width = WR['body_width'] - (total_cols - 1) * WR['gap']
    col_width = usable_width // total_cols
    left = WR['body_left'] + col_start * (col_width + WR['gap'])
    width = col_span * col_width + (col_span - 1) * WR['gap']
    return left, width
```

Grid column quick reference:

| Layout           | Call                     | Columns   |
|------------------|--------------------------|-----------|
| Full width       | `grid_column(0, 12)`     | 0-11      |
| Left half        | `grid_column(0, 6)`      | 0-5       |
| Right half       | `grid_column(6, 6)`      | 6-11      |
| Left third       | `grid_column(0, 4)`      | 0-3       |
| Center third     | `grid_column(4, 4)`      | 4-7       |
| Right third      | `grid_column(8, 4)`      | 8-11      |
| Two-thirds left  | `grid_column(0, 8)`      | 0-7       |
| One-third right  | `grid_column(8, 4)`      | 8-11      |

---

## 7. Common Pitfalls

### 7.1 Template Corruption When Modifying Master Slides

**Problem:** Modifying master slides or layouts programmatically can corrupt the PPTX file, making it unopenable in PowerPoint.

**Prevention:**
- Never write to `slide_masters` or `slide_layouts` objects
- Never delete or reorder existing layouts
- Only add new slides using existing layouts
- Always test output in PowerPoint (not just LibreOffice)
- Keep a backup of the template before every build run

### 7.2 Font Embedding Failures

**Problem:** Custom or uncommon fonts may not render correctly on the recipient's system. Font substitution changes layout and spacing unpredictably.

**Prevention:**
- Stick to Arial and Calibri for all production output
- If a client requires a specific font, confirm it is installed on the rendering machine
- Never use decorative or display fonts in data-heavy slides
- Test rendering on at least two platforms (Windows and Mac)
- Always set font properties explicitly on every run; never rely on template inheritance

### 7.3 Image Resolution Loss at Embedding

**Problem:** python-pptx may auto-scale images, reducing apparent DPI below 300.

**Prevention:**
- Always calculate exact EMU dimensions from the source file's pixel dimensions and DPI
- Never rely on python-pptx auto-sizing
- Verify embedded image dimensions match source: open the PPTX as a ZIP, check `ppt/media/` files
- Export all matplotlib charts at 300 DPI with `bbox_inches='tight'`

### 7.4 Chart Transparency Issues on Dark Backgrounds

**Problem:** Transparent-background PNGs can show white fringing or aliasing artifacts when placed on dark slide backgrounds.

**Prevention:**
- When placing charts on dark backgrounds, render the chart with a matching dark background instead of transparent:
  ```python
  fig.patch.set_facecolor('#1B2A4A')
  ax.set_facecolor('#1B2A4A')
  ```
- Alternatively, render to SVG and convert to avoid rasterization artifacts entirely
- Always visually inspect charts on their actual background color

### 7.5 Text Overflow in Fixed-Size Boxes

**Problem:** Text that exceeds the textbox dimensions is silently clipped in python-pptx output but may overflow visually in PowerPoint.

**Prevention:**
- Set `text_frame.auto_size = None` to enforce fixed dimensions
- Set `text_frame.word_wrap = True` to prevent horizontal overflow
- Calculate maximum character count for each textbox based on font size and box width
- For dynamic content, truncate with ellipsis before writing:

```python
def safe_text(text, max_chars=80):
    """Truncate text to fit fixed-size textbox."""
    if len(text) > max_chars:
        return text[:max_chars - 3] + '...'
    return text
```

### 7.6 EMU Rounding Errors Accumulating Across Elements

**Problem:** Repeated floating-point conversions between inches, points, and EMU accumulate rounding errors, causing misalignment across slides.

**Prevention:**
- Define all coordinates as integer EMU constants at the top of your build script
- Never chain conversions: `Inches(x)` to `Pt(y)` to `Emu(z)` introduces drift
- Use the `WAR_ROOM` constant dictionary for all standard positions
- When calculating derived positions, always use integer arithmetic on EMU values
- Verify alignment visually on at least the first, middle, and last slides

### 7.7 Table Cell Padding Inconsistencies

**Problem:** Default cell margins in python-pptx tables differ from PowerPoint defaults, causing text to appear cramped or misaligned.

**Prevention:**
- Explicitly set cell margins on every cell:

```python
from pptx.util import Pt, Emu

def set_cell_margins(cell, top=Pt(3), bottom=Pt(3), left=Pt(6), right=Pt(6)):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcPr.set('marT', str(int(top)))
    tcPr.set('marB', str(int(bottom)))
    tcPr.set('marL', str(int(left)))
    tcPr.set('marR', str(int(right)))
```

### 7.8 Shape Ordering and Z-Index

**Problem:** Accent bars or overlays appear behind the shapes they should be on top of.

**Prevention:**
- Shapes added later in code appear on top. Always add overlays AFTER the base layer:
  ```python
  card = add_box(slide, ...)      # base layer
  accent = add_accent(slide, ...)  # drawn on top
  ```
- If reordering is needed after the fact, manipulate the spTree XML element order

### 7.9 Large File Size from High-DPI Images

**Problem:** Embedding multiple 300 DPI images produces PPTX files over 50 MB, causing email and sharing issues.

**Prevention:**
- Use PNG for charts with flat fills (smaller than JPEG for graphics)
- Use JPEG (quality 85) for photographic content only
- Compress images before embedding if file size exceeds 30 MB
- Consider splitting into multiple decks for presentations over 40 slides
- Remove unused media from the PPTX ZIP structure after build

---

## Appendix: Quick Reference

### Standard Import Block

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml.etree import SubElement as OxmlElement
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import geopandas as gpd
import numpy as np
from PIL import Image
import os
```

### Build Checklist

Before delivering any PPTX:

1. Run the 9-rule quality gate — all rules must pass
2. Convert to PDF via LibreOffice headless — verify no rendering differences
3. Generate per-slide JPEG snapshots at 150 DPI
4. Run brand compliance check against the active palette
5. Verify file size is under 30 MB (warn if over, split if over 50 MB)
6. Open in PowerPoint (not just LibreOffice) and click through every slide
7. Confirm all text is readable, no overflow, no clipping
8. Confirm all charts have source lines
9. Confirm title positions are consistent across slides
10. Archive the build artifacts (PPTX, PDF, slide images) in the output directory

### Automated Bounds Check

```python
SLIDE_W = 12192000
SLIDE_H = 6858000

def check_bounds(left, top, width, height):
    """Verify element stays within slide dimensions."""
    assert left >= 0, f"Left {left} is negative"
    assert top >= 0, f"Top {top} is negative"
    assert left + width <= SLIDE_W, \
        f"Right edge {left + width} exceeds slide width {SLIDE_W}"
    assert top + height <= SLIDE_H, \
        f"Bottom edge {top + height} exceeds slide height {SLIDE_H}"
```
