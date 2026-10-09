"""
Motor Health Monitoring System - Standalone Desktop GUI (Tkinter)
Milestone-3 Submission | Roll: 240280109042
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from motor_health_system import (
    fuzzy_predict, current_memberships, temp_memberships, vib_memberships,
    get_maintenance_suggestion, TEST_CASES, run_genetic_programming
)

class MotorHealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor Health Monitoring System — Milestone 3")
        self.root.geometry("1100x720")
        self.root.configure(bg="#0f172a")

        self.inclusive_warning = tk.BooleanVar(value=True)
        self.current_val = tk.DoubleVar(value=12.5)
        self.temp_val = tk.DoubleVar(value=68.0)
        self.vib_val = tk.DoubleVar(value=4.2)

        self._setup_styles()
        self._build_ui()
        self.update_diagnostics()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#0f172a', foreground='#f8fafc', font=('Segoe UI', 9))
        style.configure('TFrame', background='#0f172a')
        style.configure('Card.TFrame', background='#1e293b', relief='flat')
        style.configure('TLabel', background='#1e293b', foreground='#f8fafc', font=('Segoe UI', 9))
        style.configure('Header.TLabel', background='#0f172a', foreground='#38bdf8', font=('Segoe UI', 15, 'bold'))
        style.configure('SubHeader.TLabel', background='#0f172a', foreground='#94a3b8', font=('Segoe UI', 9))
        style.configure('Title.TLabel', background='#1e293b', foreground='#38bdf8', font=('Segoe UI', 10, 'bold'))
        style.configure('TCheckbutton', background='#0f172a', foreground='#fbbf24', font=('Segoe UI', 9))

    def _build_ui(self):
        # Header
        hdr_frame = ttk.Frame(self.root)
        hdr_frame.pack(fill='x', padx=15, pady=(10, 5))
        ttk.Label(hdr_frame, text="MOTOR HEALTH MONITORING SYSTEM", style='Header.TLabel').pack(anchor='w')
        ttk.Label(hdr_frame, text="Milestone-3 Submission • Fuzzy Logic & Genetic Programming • Roll: 240280109042", style='SubHeader.TLabel').pack(anchor='w')

        # PPT Banner & Mode Toggle
        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill='x', padx=15, pady=5)
        chk = ttk.Checkbutton(top_bar, text="PPT Mode (Score <= 65 is Warning; e.g. Test 5 -> Warning)",
                              variable=self.inclusive_warning, command=self.update_diagnostics)
        chk.pack(side='left')

        # Main Layout: 2 Columns
        main_paned = ttk.PanedWindow(self.root, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=15, pady=10)

        # Left Column: Inputs & Test Suite
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Inputs Card
        in_card = ttk.Frame(left_frame, style='Card.TFrame', padding=12)
        in_card.pack(fill='x', pady=(0, 10))
        ttk.Label(in_card, text="SENSOR TELEMETRY INPUTS", style='Title.TLabel').pack(anchor='w', pady=(0, 10))

        # Current Slider
        self._create_slider(in_card, "Current (Electrical Load)", self.current_val, 0.0, 20.0, "A")
        # Temp Slider
        self._create_slider(in_card, "Temperature (Stator)", self.temp_val, 25.0, 100.0, "°C")
        # Vib Slider
        self._create_slider(in_card, "Vibration (ISO 10816)", self.vib_val, 0.0, 10.0, "mm/s")

        # Test Cases Table
        tbl_card = ttk.Frame(left_frame, style='Card.TFrame', padding=12)
        tbl_card.pack(fill='both', expand=True)
        ttk.Label(tbl_card, text="PHASE 4 TEST CASES (Click to load)", style='Title.TLabel').pack(anchor='w', pady=(0, 6))

        cols = ('ID', 'Current', 'Temp', 'Vib', 'Score', 'Cond')
        self.tree = ttk.Treeview(tbl_card, columns=cols, show='headings', height=8)
        self.tree.heading('ID', text='#')
        self.tree.heading('Current', text='I (A)')
        self.tree.heading('Temp', text='T (°C)')
        self.tree.heading('Vib', text='V (mm/s)')
        self.tree.heading('Score', text='Score')
        self.tree.heading('Cond', text='Condition')

        self.tree.column('ID', width=30, anchor='center')
        self.tree.column('Current', width=55, anchor='center')
        self.tree.column('Temp', width=55, anchor='center')
        self.tree.column('Vib', width=65, anchor='center')
        self.tree.column('Score', width=60, anchor='center')
        self.tree.column('Cond', width=80, anchor='center')

        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        self._populate_tree()

        # Right Column: Diagnostics & Fired Rules
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        diag_card = ttk.Frame(right_frame, style='Card.TFrame', padding=15)
        diag_card.pack(fill='x', pady=(0, 10))
        ttk.Label(diag_card, text="DIAGNOSTIC HEALTH ASSESSMENT", style='Title.TLabel').pack(anchor='w')

        # Score Display
        self.score_label = tk.Label(diag_card, text="65.00", font=('JetBrains Mono', 32, 'bold'),
                                    bg='#1e293b', fg='#f59e0b')
        self.score_label.pack(pady=(5, 0))
        ttk.Label(diag_card, text="HEALTH SCORE (0 - 100)", style='SubHeader.TLabel').pack()

        # Condition Banner
        self.cond_banner = tk.Label(diag_card, text="WARNING", font=('Segoe UI', 13, 'bold'),
                                    bg='#78350f', fg='#fbbf24', relief='solid', bd=1, padx=12, pady=6)
        self.cond_banner.pack(fill='x', pady=10)

        # Suggestion
        self.sugg_label = tk.Label(diag_card, text="", wraplength=450, justify='left',
                                   bg='#1e293b', fg='#e2e8f0', font=('Segoe UI', 9))
        self.sugg_label.pack(fill='x', pady=5)

        # Fired Rules Card
        rules_card = ttk.Frame(right_frame, style='Card.TFrame', padding=12)
        rules_card.pack(fill='both', expand=True)
        ttk.Label(rules_card, text="ACTIVE FIRED RULES", style='Title.TLabel').pack(anchor='w', pady=(0, 6))

        self.rules_txt = tk.Text(rules_card, bg='#0f172a', fg='#cbd5e1', font=('Consolas', 9),
                                 height=7, relief='flat', padx=8, pady=8)
        self.rules_txt.pack(fill='both', expand=True)

    def _create_slider(self, parent, label_text, var, from_val, to_val, unit):
        box = ttk.Frame(parent, style='Card.TFrame')
        box.pack(fill='x', pady=4)
        top = ttk.Frame(box, style='Card.TFrame')
        top.pack(fill='x')
        ttk.Label(top, text=label_text).pack(side='left')
        v_lbl = ttk.Label(top, text=f"{var.get():.1f} {unit}", font=('Segoe UI', 9, 'bold'))
        v_lbl.pack(side='right')

        def on_slide(val):
            v_lbl.config(text=f"{float(val):.1f} {unit}")
            self.update_diagnostics()

        scale = ttk.Scale(box, from_=from_val, to=to_val, variable=var, command=on_slide)
        scale.pack(fill='x', pady=2)

    def _populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        inc = self.inclusive_warning.get()
        for t_id, c, t, v in TEST_CASES:
            cond, score, _ = fuzzy_predict(c, t, v, inclusive_warning=inc)
            self.tree.insert('', 'end', values=(t_id, f"{c:.1f}", f"{t:.0f}", f"{v:.1f}", f"{score:.2f}", cond))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])['values']
        self.current_val.set(float(vals[1]))
        self.temp_val.set(float(vals[2]))
        self.vib_val.set(float(vals[3]))
        self.update_diagnostics()

    def update_diagnostics(self):
        c = self.current_val.get()
        t = self.temp_val.get()
        v = self.vib_val.get()
        inc = self.inclusive_warning.get()

        cond, score, fired = fuzzy_predict(c, t, v, inclusive_warning=inc)
        self.score_label.config(text=f"{score:.2f}")

        if cond == 'Normal':
            self.score_label.config(fg='#10b981')
            self.cond_banner.config(text="NORMAL", bg='#064e3b', fg='#34d399')
        elif cond == 'Warning':
            self.score_label.config(fg='#f59e0b')
            self.cond_banner.config(text="WARNING", bg='#78350f', fg='#fbbf24')
        else:
            self.score_label.config(fg='#ef4444')
            self.cond_banner.config(text="CRITICAL", bg='#7f1d1d', fg='#f87171')

        self.sugg_label.config(text="Recommendation: " + get_maintenance_suggestion(cond))

        # Format Fired Rules
        self.rules_txt.delete('1.0', tk.END)
        self.rules_txt.insert(tk.END, f"{'Rule Antecedents':<32} {'Weight':<8} {'Output'}\n")
        self.rules_txt.insert(tk.END, "-" * 55 + "\n")
        for r in fired:
            c_str = f"I:{r['current_level']} & T:{r['temp_level']} & V:{r['vib_level']}"
            self.rules_txt.insert(tk.END, f"{c_str:<32} {r['weight']:<8.3f} {r['label']} ({r['score_val']})\n")

def main():
    root = tk.Tk()
    app = MotorHealthApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
