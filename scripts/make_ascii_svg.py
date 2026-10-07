import os
import sys
import xml.sax.saxutils as saxutils
import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)

def image_to_ascii(img_path, cols=96, rows=52):
    """Downsamples image and maps pixel brightness to ASCII characters."""
    img = Image.open(img_path).convert('L')
    img_resized = img.resize((cols, rows), Image.Resampling.LANCZOS)
    arr = np.array(img_resized)

    ascii_rows = []
    ramp_len = len(RAMP)
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            val = arr[r, c]
            # 255 (white/bright) -> 0 index (space)
            # 0 (black/dark) -> max index (@)
            idx = int((1.0 - (val / 255.0)) * (ramp_len - 1))
            idx = max(0, min(idx, ramp_len - 1))
            row_chars.append(RAMP[idx])
        ascii_rows.append("".join(row_chars))
    return ascii_rows

def generate_ascii_svg(ascii_rows, output_path="avi-ascii.svg"):
    cols = len(ascii_rows[0])
    rows = len(ascii_rows)

    # Dimensions layout
    font_size = 7.5
    char_width = 3.65
    line_height = 8.5
    padding_x = 14
    padding_y = 36
    
    width = int(cols * char_width + padding_x * 2)
    height = int(rows * line_height + padding_y + 15)

    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="370" height="{int(370 * height / width)}">')
    
    # Styles
    svg_lines.append('<defs>')
    svg_lines.append('  <style>')
    svg_lines.append('    .bg { fill: #0d1117; rx: 8px; ry: 8px; stroke: #30363d; stroke-width: 1px; }')
    svg_lines.append('    .header-dot { rx: 50%; ry: 50%; }')
    svg_lines.append('    .title { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 11px; fill: #8b949e; font-weight: 600; }')
    svg_lines.append('    .ascii-text { font-family: "Fira Code", "Cascadia Code", Consolas, "Courier New", monospace; font-size: 7.5px; fill: #c9d1d9; letter-spacing: 0px; whitespace: pre; }')
    svg_lines.append('    .cursor { fill: #58a6ff; }')
    svg_lines.append('  </style>')

    # ClipPaths for horizontal row wipe animation
    row_dur = 0.07  # wipe duration per row in seconds
    row_stagger = 0.045  # delay between rows
    
    total_content_width = width - padding_x * 2
    
    for i in range(rows):
        y_pos = padding_y + i * line_height
        delay = i * row_stagger
        svg_lines.append(f'  <clipPath id="clip-row-{i}">')
        svg_lines.append(f'    <rect x="{padding_x}" y="{y_pos - 1}" width="0" height="{line_height + 2}">')
        svg_lines.append(f'      <animate attributeName="width" from="0" to="{total_content_width}" dur="{row_dur}s" begin="{delay:.3f}s" fill="freeze" />')
        svg_lines.append('    </rect>')
        svg_lines.append('  </clipPath>')

    svg_lines.append('</defs>')

    # Background card
    svg_lines.append(f'<rect width="{width}" height="{height}" class="bg" />')
    
    # Terminal title bar header
    svg_lines.append('<!-- Terminal Header -->')
    svg_lines.append('<circle cx="16" cy="16" r="5" fill="#ff5f56" />')
    svg_lines.append('<circle cx="32" cy="16" r="5" fill="#ffbd2e" />')
    svg_lines.append('<circle cx="48" cy="16" r="5" fill="#27c93f" />')
    svg_lines.append(f'<text x="66" y="19" class="title">sahil-ascii.portrait</text>')
    svg_lines.append(f'<line x1="0" y1="30" x2="{width}" y2="30" stroke="#21262d" stroke-width="1" />')

    # Render ASCII rows with SMIL horizontal wipe & trailing cursor
    svg_lines.append('<!-- ASCII Art Rows -->')
    for i, row in enumerate(ascii_rows):
        escaped_row = saxutils.escape(row)
        y_pos = padding_y + (i + 1) * line_height - 2
        delay = i * row_stagger
        
        # Row text clipped to wipe rect
        svg_lines.append(f'<text x="{padding_x}" y="{y_pos:.1f}" class="ascii-text" clip-path="url(#clip-row-{i})">{escaped_row}</text>')
        
        # Block cursor riding the wipe edge
        svg_lines.append(f'<rect class="cursor" y="{y_pos - line_height + 2:.1f}" width="5" height="7.5" opacity="1">')
        svg_lines.append(f'  <animate attributeName="x" from="{padding_x}" to="{padding_x + total_content_width}" dur="{row_dur}s" begin="{delay:.3f}s" fill="freeze" />')
        svg_lines.append(f'  <animate attributeName="opacity" from="1" to="0" begin="{delay + row_dur:.3f}s" dur="0.01s" fill="freeze" />')
        svg_lines.append('</rect>')

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
    print(f"Generated ASCII SVG portrait at '{output_path}'")

if __name__ == "__main__":
    if not os.path.exists("source-prepped.png"):
        print("source-prepped.png not found. Running prep_photo.py first...")
        import prep_photo
        prep_photo.prep_photo("source-photo.jpg")
    
    rows = image_to_ascii("source-prepped.png")
    generate_ascii_svg(rows, "sahil-ascii.svg")
