import os
import json
import datetime
import xml.sax.saxutils as saxutils

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

def render_heatmap_svg(json_path="data/contributions.json", output_path="contrib-heatmap.svg"):
    if not os.path.exists(json_path):
        print(f"Data file '{json_path}' not found. Running fetch_contributions.py first...")
        import fetch_contributions
        fetch_contributions.main()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    total_contributions = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)

    # Canvas dimensions
    width = 860
    height = 240

    cell_size = 11
    cell_gap = 3.5
    cell_step = cell_size + cell_gap

    start_x = 42
    start_y = 52

    # Group days into weeks (53 columns x 7 rows)
    # Map dates to grid positions
    grid_cells = []
    month_labels = []

    last_month = None

    # Calculate week columns
    if days:
        first_date = datetime.datetime.strptime(days[0]["date"], "%Y-%m-%d")
        for idx, day in enumerate(days):
            dt = datetime.datetime.strptime(day["date"], "%Y-%m-%d")
            
            # Days since start
            delta_days = (dt - first_date).days
            col = delta_days // 7
            row = (dt.weekday() + 1) % 7  # 0=Sun, 1=Mon, ..., 6=Sat

            if col >= 53:
                break

            # Pick color level (0..5)
            cnt = day["count"]
            lvl = day["level"]
            if cnt > 12:
                lvl = 5  # Neon highlight for top end

            lvl = max(0, min(lvl, len(PALETTE) - 1))
            color = PALETTE[lvl]

            grid_cells.append({
                "col": col,
                "row": row,
                "date": day["date"],
                "count": cnt,
                "color": color,
                "level": lvl
            })

            # Check for month label at top of column
            m_str = dt.strftime("%b")
            if m_str != last_month and row == 0 and col < 52:
                month_labels.append({"col": col, "label": m_str})
                last_month = m_str

    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg_lines.append('<defs>')
    svg_lines.append('  <style>')
    svg_lines.append('    .bg { fill: #0d1117; rx: 8px; ry: 8px; stroke: #30363d; stroke-width: 1px; }')
    svg_lines.append('    .header-dot { rx: 50%; ry: 50%; }')
    svg_lines.append('    .title-bar { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 11px; fill: #8b949e; font-weight: 600; }')
    svg_lines.append('    .label { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 10px; fill: #7d8590; }')
    svg_lines.append('    .stats-text { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 11.5px; fill: #c9d1d9; font-weight: 500; }')
    svg_lines.append('    .highlight-val { fill: #39d353; font-weight: 700; }')
    
    # CSS Keyframes for diagonal slide-down reveal animation
    svg_lines.append('    @keyframes diagReveal {')
    svg_lines.append('      0% { opacity: 0; transform: translate(-4px, -6px) scale(0.7); }')
    svg_lines.append('      60% { opacity: 1; transform: translate(0.5px, 0.5px) scale(1.05); }')
    svg_lines.append('      100% { opacity: 1; transform: translate(0, 0) scale(1); }')
    svg_lines.append('    }')
    svg_lines.append('    .day-cell { opacity: 0; animation: diagReveal 0.3s ease-out forwards; transform-origin: center; }')
    
    svg_lines.append('  </style>')
    svg_lines.append('</defs>')

    # Background card
    svg_lines.append(f'<rect width="{width}" height="{height}" class="bg" />')

    # Terminal Header bar
    svg_lines.append('<circle cx="16" cy="16" r="5" fill="#ff5f56" />')
    svg_lines.append('<circle cx="32" cy="16" r="5" fill="#ffbd2e" />')
    svg_lines.append('<circle cx="48" cy="16" r="5" fill="#27c93f" />')
    svg_lines.append('<text x="66" y="19" class="title-bar">Skedare240507@github ~ ./contributions.sh</text>')
    svg_lines.append(f'<line x1="0" y1="30" x2="{width}" y2="30" stroke="#21262d" stroke-width="1" />')

    # Day labels (Mon, Wed, Fri)
    day_name_y = {1: start_y + 1 * cell_step + 9, 3: start_y + 3 * cell_step + 9, 5: start_y + 5 * cell_step + 9}
    svg_lines.append(f'<text x="14" y="{day_name_y[1]}" class="label">Mon</text>')
    svg_lines.append(f'<text x="14" y="{day_name_y[3]}" class="label">Wed</text>')
    svg_lines.append(f'<text x="14" y="{day_name_y[5]}" class="label">Fri</text>')

    # Month labels
    for ml in month_labels:
        mx = start_x + ml["col"] * cell_step
        svg_lines.append(f'<text x="{mx:.1f}" y="{start_y - 8}" class="label">{ml["label"]}</text>')

    # Grid boxes
    for cell in grid_cells:
        cx = start_x + cell["col"] * cell_step
        cy = start_y + cell["row"] * cell_step
        
        # Diagonal stagger delay based on col + row
        delay = (cell["col"] + cell["row"]) * 0.015 + 0.1
        
        rect_svg = (
            f'<rect class="day-cell" x="{cx:.1f}" y="{cy:.1f}" width="{cell_size}" height="{cell_size}" '
            f'fill="{cell["color"]}" rx="2.5" ry="2.5" style="animation-delay: {delay:.3f}s;">'
            f'<title>{cell["count"]} contributions on {cell["date"]}</title>'
            f'</rect>'
        )
        svg_lines.append(rect_svg)

    # Footer: Stats text & Legend
    footer_y = start_y + 7 * cell_step + 28

    # Left footer stats
    stats_str = f'{total_contributions:,} contributions in the last year'
    svg_lines.append(f'<text x="18" y="{footer_y}" class="stats-text"><tspan class="highlight-val">{total_contributions:,}</tspan> contributions in the last year <tspan fill="#484f58">|</tspan> Streak: <tspan class="highlight-val">{current_streak}d</tspan> (max <tspan class="highlight-val">{longest_streak}d</tspan>)</text>')

    # Right footer legend (Less -> More)
    legend_end_x = width - 20
    leg_box_size = 10
    leg_gap = 3
    
    # "More" text
    svg_lines.append(f'<text x="{legend_end_x - 30}" y="{footer_y}" class="label">More</text>')
    
    # Legend color boxes
    cur_x = legend_end_x - 38 - len(PALETTE) * (leg_box_size + leg_gap)
    for p_color in reversed(PALETTE):
        cur_x -= (leg_box_size + leg_gap)
        svg_lines.append(f'<rect x="{cur_x:.1f}" y="{footer_y - 9}" width="{leg_box_size}" height="{leg_box_size}" fill="{p_color}" rx="2" ry="2" />')

    # "Less" text
    svg_lines.append(f'<text x="{cur_x - 28:.1f}" y="{footer_y}" class="label">Less</text>')

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
    print(f"Generated heatmap SVG at '{output_path}'")

if __name__ == "__main__":
    render_heatmap_svg()
