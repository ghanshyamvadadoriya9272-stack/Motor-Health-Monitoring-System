"""
Script to generate:
- gp_optimization.png
- simulator_test_01.png to simulator_test_12.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from motor_health_system import (
    fuzzy_predict, current_memberships, temp_memberships, vib_memberships,
    get_maintenance_suggestion, TEST_CASES, run_genetic_programming
)

# Set high DPI and styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 0.8

def generate_gp_plot(output_path='gp_optimization.png'):
    print("Running Genetic Programming Optimization...")
    res = run_genetic_programming(generations=25, pop_size=30, seed=42)
    history = res['history']
    init_fit = res['initial_fitness']
    best_fit = res['best_fitness']
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#1e293b')
    
    gens = list(range(1, 26))
    ax.plot(gens, history, color='#38bdf8', linewidth=2.5, marker='o', 
            markersize=6, markerfacecolor='#38bdf8', markeredgecolor='#0284c7', label='Best Fitness (Generation)')
    
    # Fill area under curve
    ax.fill_between(gens, history, min(history) - 0.05, color='#38bdf8', alpha=0.12)
    
    # Reference line for initial baseline
    ax.axhline(init_fit, color='#f43f5e', linestyle='--', linewidth=1.8, 
               label=f'Initial Heuristic Baseline ({init_fit*100:.1f}%)')
    
    # Highlight maximum convergence
    max_idx = history.index(max(history))
    ax.scatter([gens[max_idx]], [history[max_idx]], color='#22c55e', s=140, zorder=5, label=f'Peak Fitness ({best_fit*100:.1f}%)')
    
    ax.annotate(f'Peak Accuracy: {best_fit*100:.1f}%\n(Gen {gens[max_idx]})', 
                xy=(gens[max_idx], history[max_idx]),
                xytext=(gens[max_idx] - 6, history[max_idx] - 0.05),
                arrowprops=dict(facecolor='#22c55e', shrink=0.08, width=1.5, headwidth=7),
                color='#f8fafc', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#064e3b', edgecolor='#22c55e', alpha=0.9))
    
    ax.set_title('Genetic Programming — Fuzzy Rule Base Optimization\nMotor Health Monitoring System (Milestone-3)', 
                 fontsize=14, fontweight='bold', color='#f8fafc', pad=15)
    ax.set_xlabel('Generation', fontsize=12, fontweight='bold', color='#94a3b8')
    ax.set_ylabel('Classification Fitness (Accuracy)', fontsize=12, fontweight='bold', color='#94a3b8')
    ax.set_xlim(0.5, 25.5)
    ax.set_ylim(0.65, 0.95)
    ax.set_xticks(range(1, 26, 2))
    
    ax.tick_params(colors='#94a3b8', labelsize=10)
    ax.grid(True, color='#334155', linestyle=':', alpha=0.6)
    
    # Summary box
    info_text = (
        f"Population Size: 30\n"
        f"Chromosome Length: 27 rules\n"
        f"Crossover: Single-point\n"
        f"Mutation Rate: 0.06\n"
        f"Initial Fitness: {init_fit:.3f} ({init_fit*100:.1f}%)\n"
        f"Optimized Fitness: {best_fit:.3f} ({best_fit*100:.1f}%)\n"
        f"Net Gain: +{(best_fit - init_fit)*100:.1f}%"
    )
    ax.text(0.03, 0.35, info_text, transform=ax.transAxes, fontsize=9.5,
            verticalalignment='top', color='#e2e8f0', family='monospace',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#0f172a', edgecolor='#475569', alpha=0.95))
    
    legend = ax.legend(facecolor='#0f172a', edgecolor='#475569', labelcolor='#f8fafc', loc='lower right', fontsize=10)
    legend.get_frame().set_alpha(0.9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated {output_path} successfully.")

def generate_simulator_card(test_id, current, temp, vib, output_path):
    cond_strict, score, fired = fuzzy_predict(current, temp, vib, inclusive_warning=False)
    cond_ppt, _, _ = fuzzy_predict(current, temp, vib, inclusive_warning=True)
    
    # Palette definition
    bg_main = '#0f172a'
    card_bg = '#1e293b'
    border_color = '#334155'
    text_white = '#f8fafc'
    text_muted = '#94a3b8'
    
    if score < 35:
        theme_color = '#10b981' # emerald
        status_text = 'NORMAL'
        badge_bg = '#064e3b'
    elif score < 65:
        theme_color = '#f59e0b' # amber
        status_text = 'WARNING'
        badge_bg = '#78350f'
    else:
        # score >= 65
        if test_id == 5:
            theme_color = '#f59e0b' if cond_ppt == 'Warning' else '#ef4444'
            status_text = 'WARNING (PPT) / CRITICAL'
            badge_bg = '#78350f' if cond_ppt == 'Warning' else '#7f1d1d'
        else:
            theme_color = '#ef4444' # red
            status_text = 'CRITICAL'
            badge_bg = '#7f1d1d'
            
    suggestion = get_maintenance_suggestion('Warning' if (test_id == 5 and cond_ppt == 'Warning') else cond_strict)
    
    fig = plt.figure(figsize=(11, 7), dpi=180)
    fig.patch.set_facecolor(bg_main)
    
    # Main grid
    gs = fig.add_gridspec(3, 2, height_ratios=[0.22, 0.42, 0.36], width_ratios=[1.1, 0.9], 
                          left=0.05, right=0.95, top=0.94, bottom=0.06, hspace=0.35, wspace=0.25)
    
    # 1. Header Box across top
    ax_hdr = fig.add_subplot(gs[0, :])
    ax_hdr.set_facecolor(card_bg)
    ax_hdr.axis('off')
    # Draw border
    rect = patches.FancyBboxPatch((0.01, 0.05), 0.98, 0.9, boxstyle="round,pad=0.02,rounding_size=0.03", 
                                  facecolor=card_bg, edgecolor=border_color, linewidth=1.5)
    ax_hdr.add_patch(rect)
    
    ax_hdr.text(0.04, 0.65, f"MOTOR HEALTH MONITORING SYSTEM — SIMULATOR TEST #{test_id:02d}", 
                fontsize=14, fontweight='bold', color=text_white, transform=ax_hdr.transAxes)
    ax_hdr.text(0.04, 0.25, f"Phase 4 Industrial Diagnostic Simulation  |  Fuzzy Logic & Genetic Programming", 
                fontsize=9.5, color=text_muted, transform=ax_hdr.transAxes)
    
    # Health status badge in header
    badge = patches.FancyBboxPatch((0.72, 0.18), 0.24, 0.64, boxstyle="round,pad=0.02,rounding_size=0.04",
                                  facecolor=badge_bg, edgecolor=theme_color, linewidth=2.0)
    ax_hdr.add_patch(badge)
    ax_hdr.text(0.84, 0.50, status_text, fontsize=12, fontweight='bold', color=theme_color,
                ha='center', va='center', transform=ax_hdr.transAxes)
    
    # 2. Left Middle: Input Parameters & Fuzzified Memberships
    ax_inputs = fig.add_subplot(gs[1, 0])
    ax_inputs.set_facecolor(card_bg)
    for spine in ax_inputs.spines.values():
        spine.set_color(border_color)
    ax_inputs.set_title("Input Sensor Readings & Fuzzification", fontsize=11, fontweight='bold', color=text_white, pad=8)
    
    cm = current_memberships(current)
    tm = temp_memberships(temp)
    vm = vib_memberships(vib)
    
    ax_inputs.axis('off')
    # Draw custom bars for 3 sensors
    sensors = [
        ("Current (A)", current, 0, 20, "A", cm, 0.72),
        ("Temperature (°C)", temp, 25, 100, "°C", tm, 0.42),
        ("Vibration (mm/s)", vib, 0, 10, "mm/s", vm, 0.12)
    ]
    
    for name, val, vmin, vmax, unit, mems, ypos in sensors:
        pct = (val - vmin) / (vmax - vmin)
        ax_inputs.text(0.02, ypos + 0.14, f"{name}: {val:.1f} {unit}", fontsize=10, fontweight='bold', 
                       color=text_white, transform=ax_inputs.transAxes)
        # Background bar
        bg_bar = patches.Rectangle((0.02, ypos + 0.05), 0.96, 0.06, facecolor='#334155', edgecolor='none')
        ax_inputs.add_patch(bg_bar)
        # Active progress bar
        bar_color = '#38bdf8' if 'Current' in name else ('#fb923c' if 'Temp' in name else '#a855f7')
        act_bar = patches.Rectangle((0.02, ypos + 0.05), 0.96 * max(0.01, min(1.0, pct)), 0.06, 
                                    facecolor=bar_color, edgecolor='none')
        ax_inputs.add_patch(act_bar)
        
        # Membership labels
        m_str = f"μ_Low: {mems['Low']:.2f} | μ_Med: {mems['Medium']:.2f} | μ_High: {mems['High']:.2f}"
        ax_inputs.text(0.02, ypos - 0.04, m_str, fontsize=8.5, color='#cbd5e1', family='monospace',
                       transform=ax_inputs.transAxes)
        
    # 3. Right Middle: Defuzzified Health Score Gauge & Meter
    ax_score = fig.add_subplot(gs[1, 1])
    ax_score.set_facecolor(card_bg)
    for spine in ax_score.spines.values():
        spine.set_color(border_color)
    ax_score.set_title("Defuzzified Health Score", fontsize=11, fontweight='bold', color=text_white, pad=8)
    ax_score.axis('off')
    
    # Draw circular or horizontal meter
    ax_score.text(0.5, 0.75, f"{score:.2f}", fontsize=28, fontweight='bold', color=theme_color,
                  ha='center', va='center', transform=ax_score.transAxes)
    ax_score.text(0.5, 0.58, "OUT OF 100", fontsize=9, fontweight='bold', color=text_muted,
                  ha='center', va='center', transform=ax_score.transAxes)
    
    # Progress gauge bar
    g_bg = patches.Rectangle((0.1, 0.40), 0.8, 0.09, facecolor='#334155', edgecolor='none')
    ax_score.add_patch(g_bg)
    g_val = patches.Rectangle((0.1, 0.40), 0.8 * (score / 100.0), 0.09, facecolor=theme_color, edgecolor='none')
    ax_score.add_patch(g_val)
    
    # Zones marks
    ax_score.text(0.1, 0.28, "0 (Normal)", fontsize=7.5, color='#10b981', transform=ax_score.transAxes)
    ax_score.text(0.38, 0.28, "35 (Warning)", fontsize=7.5, color='#f59e0b', transform=ax_score.transAxes)
    ax_score.text(0.65, 0.28, "65 (Critical)", fontsize=7.5, color='#ef4444', transform=ax_score.transAxes)
    ax_score.text(0.85, 0.28, "100", fontsize=7.5, color='#94a3b8', transform=ax_score.transAxes)
    
    if test_id == 5:
        ax_score.text(0.5, 0.12, "NOTE: Score 65.0 is Warning in PPT (<=65)\nand Critical under strict condition (<65)", 
                      fontsize=7.5, color='#fbbf24', ha='center', va='center', transform=ax_score.transAxes)
    else:
        ax_score.text(0.5, 0.12, f"Condition Category: {cond_strict.upper()}", 
                      fontsize=8.5, fontweight='bold', color=text_white, ha='center', va='center', transform=ax_score.transAxes)
        
    # 4. Bottom Left: Active Fuzzy Rules Fired
    ax_rules = fig.add_subplot(gs[2, 0])
    ax_rules.set_facecolor(card_bg)
    for spine in ax_rules.spines.values():
        spine.set_color(border_color)
    ax_rules.set_title("Active Fuzzy Rules Fired", fontsize=11, fontweight='bold', color=text_white, pad=8)
    ax_rules.axis('off')
    
    y_r = 0.82
    ax_rules.text(0.02, y_r, "RULE COMBINATION                       WEIGHT    CONSEQUENCE", 
                  fontsize=8, fontweight='bold', color='#94a3b8', family='monospace', transform=ax_rules.transAxes)
    y_r -= 0.15
    for r in fired[:4]:
        c_desc = f"I:{r['current_level'][:3]} & T:{r['temp_level'][:3]} & V:{r['vib_level'][:3]}"
        w_desc = f"{r['weight']:.2f}"
        con_col = '#10b981' if r['label'] == 'Normal' else ('#f59e0b' if r['label'] == 'Warning' else '#ef4444')
        ax_rules.text(0.02, y_r, f"{c_desc:<28} {w_desc:<8}", fontsize=8.5, color='#e2e8f0', family='monospace', transform=ax_rules.transAxes)
        ax_rules.text(0.68, y_r, f"{r['label']} ({r['score_val']})", fontsize=8.5, fontweight='bold', color=con_col, family='monospace', transform=ax_rules.transAxes)
        y_r -= 0.18
        
    # 5. Bottom Right: Maintenance Directive & Action Protocol
    ax_rec = fig.add_subplot(gs[2, 1])
    ax_rec.set_facecolor(card_bg)
    for spine in ax_rec.spines.values():
        spine.set_color(border_color)
    ax_rec.set_title("Operational Maintenance Protocol", fontsize=11, fontweight='bold', color=text_white, pad=8)
    ax_rec.axis('off')
    
    # Recommendation text
    ax_rec.text(0.05, 0.78, "PRESCRIPTION:", fontsize=9, fontweight='bold', color='#38bdf8', transform=ax_rec.transAxes)
    ax_rec.text(0.05, 0.52, suggestion, fontsize=9, color='#e2e8f0', wrap=True, transform=ax_rec.transAxes)
    
    # Status indicator pill
    pill = patches.FancyBboxPatch((0.05, 0.12), 0.90, 0.22, boxstyle="round,pad=0.02,rounding_size=0.03",
                                 facecolor='#0f172a', edgecolor=theme_color, linewidth=1.2)
    ax_rec.add_patch(pill)
    ax_rec.text(0.50, 0.23, f"DECISION STATUS: {status_text}", fontsize=9, fontweight='bold', color=theme_color,
                ha='center', va='center', transform=ax_rec.transAxes)
    
    plt.savefig(output_path, dpi=180, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated {output_path}")

def generate_all_test_cards():
    for test_id, c, t, v in TEST_CASES:
        out_name = f"simulator_test_{test_id:02d}.png"
        generate_simulator_card(test_id, c, t, v, out_name)

if __name__ == '__main__':
    generate_gp_plot()
    generate_all_test_cards()
