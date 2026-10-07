import os
import xml.sax.saxutils as saxutils

def generate_info_card(output_path="info-card.svg"):
    is_static = os.environ.get("STATIC") == "1"
    
    width = 490
    height = 490

    # Data rows for Neofetch card
    rows = [
        ("Sahil", "Skedare240507", "#58a6ff", True),  # Header title
        ("----------------------------------", "", "#484f58", False),
        ("OS", "macOS / Arch Linux x86_64", "#79c0ff", False),
        ("Host", "GitHub Profile Terminal v2.4", "#79c0ff", False),
        ("Kernel", "6.12.0-custom-mainline", "#79c0ff", False),
        ("Uptime", "8+ years in software & algorithms", "#79c0ff", False),
        ("Shell", "zsh 5.9 (x86_64-apple-darwin)", "#79c0ff", False),
        ("Now", "Building animated SVG engines & AI tools", "#ff7b72", False),
        ("Prev", "Full-Stack Software Engineer & Systems Architect", "#d2a8ff", False),
        ("Stack", "Python, TypeScript, React, Rust, Go, Docker", "#7ee787", False),
        ("Highlights", "Creator of CLI tools & Open-Source SVG Art", "#ffa657", False),
    ]

    palette_colors = ["#161b22", "#ff7b72", "#7ee787", "#ffa657", "#79c0ff", "#d2a8ff", "#58a6ff", "#c9d1d9"]

    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg_lines.append('<defs>')
    svg_lines.append('  <style>')
    svg_lines.append('    .bg { fill: #0d1117; rx: 8px; ry: 8px; stroke: #30363d; stroke-width: 1px; }')
    svg_lines.append('    .title-bar { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 11px; fill: #8b949e; font-weight: 600; }')
    svg_lines.append('    .prompt-text { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; fill: #58a6ff; font-weight: 600; }')
    svg_lines.append('    .key { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12.5px; font-weight: 700; }')
    svg_lines.append('    .value { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12.5px; fill: #c9d1d9; }')
    svg_lines.append('    .header-user { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 15px; font-weight: 800; fill: #58a6ff; }')
    
    if not is_static:
        svg_lines.append('    @keyframes fadeInUp {')
        svg_lines.append('      from { opacity: 0; transform: translateY(6px); }')
        svg_lines.append('      to { opacity: 1; transform: translateY(0); }')
        svg_lines.append('    }')
        svg_lines.append('    .animated-row { opacity: 0; animation: fadeInUp 0.4s ease-out forwards; }')
    else:
        svg_lines.append('    .animated-row { opacity: 1; }')
        
    svg_lines.append('  </style>')
    svg_lines.append('</defs>')

    # Card background
    svg_lines.append(f'<rect width="{width}" height="{height}" class="bg" />')
    
    # Header bar
    svg_lines.append('<circle cx="16" cy="16" r="5" fill="#ff5f56" />')
    svg_lines.append('<circle cx="32" cy="16" r="5" fill="#ffbd2e" />')
    svg_lines.append('<circle cx="48" cy="16" r="5" fill="#27c93f" />')
    svg_lines.append('<text x="66" y="19" class="title-bar">Skedare240507@github ~ neofetch</text>')
    svg_lines.append(f'<line x1="0" y1="30" x2="{width}" y2="30" stroke="#21262d" stroke-width="1" />')

    # Neofetch prompt line
    svg_lines.append('<g class="animated-row" style="animation-delay: 0.05s;">')
    svg_lines.append('<text x="18" y="52" class="prompt-text">Skedare240507@github</text>')
    svg_lines.append('<text x="162" y="52" class="value"><tspan fill="#8b949e">:</tspan><tspan fill="#79c0ff">~</tspan><tspan fill="#8b949e">$</tspan> neofetch --user Skedare240507</text>')
    svg_lines.append('</g>')

    # Rows printing
    start_y = 78
    row_height = 28

    for i, (key, val, color, is_header) in enumerate(rows):
        y_pos = start_y + i * row_height
        delay = (i + 2) * 0.08
        delay_attr = f'style="animation-delay: {delay:.2f}s;"' if not is_static else ''
        
        svg_lines.append(f'<g class="animated-row" {delay_attr}>')
        if is_header:
            svg_lines.append(f'  <text x="18" y="{y_pos}" class="header-user">{saxutils.escape(key)}<tspan fill="#c9d1d9">@</tspan>{saxutils.escape(val)}</text>')
        elif key.startswith("---"):
            svg_lines.append(f'  <text x="18" y="{y_pos}" fill="{color}" font-family="monospace" font-size="12px">{key}</text>')
        else:
            svg_lines.append(f'  <text x="18" y="{y_pos}" class="key" fill="{color}">{saxutils.escape(key)}</text>')
            svg_lines.append(f'  <text x="110" y="{y_pos}" class="key" fill="#8b949e">:&amp;</text>')
            svg_lines.append(f'  <text x="125" y="{y_pos}" class="value">{saxutils.escape(val)}</text>')
        svg_lines.append('</g>')

    # Neofetch color palette block at bottom
    palette_y = start_y + len(rows) * row_height + 10
    delay = (len(rows) + 2) * 0.08
    delay_attr = f'style="animation-delay: {delay:.2f}s;"' if not is_static else ''
    
    svg_lines.append(f'<g class="animated-row" {delay_attr}>')
    block_width = 24
    block_height = 14
    start_x = 18
    for idx, c in enumerate(palette_colors):
        x = start_x + idx * (block_width + 6)
        svg_lines.append(f'  <rect x="{x}" y="{palette_y}" width="{block_width}" height="{block_height}" fill="{c}" rx="2" ry="2" stroke="#30363d" stroke-width="1" />')
    svg_lines.append('</g>')

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
    print(f"Generated info card SVG at '{output_path}'")

if __name__ == "__main__":
    generate_info_card("info-card.svg")
