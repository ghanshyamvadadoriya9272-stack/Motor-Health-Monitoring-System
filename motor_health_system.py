"""
Motor Health Monitoring System using Fuzzy Logic & Genetic Programming
Core Computational Engine
"""

import numpy as np
import pandas as pd
import random

# Membership functions
def trap(x, a, b, c, d):
    """Trapezoidal membership function."""
    if x <= a or x >= d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if a < x < b:
        return (x - a) / (b - a) if b != a else 1.0
    return (d - x) / (d - c) if d != c else 1.0

def trimf(x, a, b, c):
    """Triangular membership function."""
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    return (x - a) / (b - a) if x < b else (c - x) / (c - b)

def current_memberships(x):
    """Fuzzification for Current (0-20 A)."""
    return {
        'Low': trap(x, 0, 0, 5, 10),
        'Medium': trimf(x, 5, 10, 15),
        'High': trap(x, 10, 15, 20, 20)
    }

def temp_memberships(x):
    """Fuzzification for Temperature (25-100 °C)."""
    return {
        'Low': trap(x, 25, 25, 35, 50),
        'Medium': trimf(x, 40, 62.5, 85),
        'High': trap(x, 75, 90, 100, 100)
    }

def vib_memberships(x):
    """Fuzzification for Vibration (0-10 mm/s)."""
    return {
        'Low': trap(x, 0, 0, 2, 4),
        'Medium': trimf(x, 2.5, 5, 7.5),
        'High': trap(x, 6, 8, 10, 10)
    }

levels = ['Low', 'Medium', 'High']

def rule_output(c, t, v):
    """
    Expert Rule Base mapping 3 inputs (27 combinations).
    Severity score: Low=0, Medium=1, High=2
    Total severity:
      sev <= 1: Normal (score 20)
      sev <= 3: Warning (score 50)
      sev >= 4: Critical (score 80)
    """
    sev_map = {'Low': 0, 'Medium': 1, 'High': 2}
    sev = sev_map[c] + sev_map[t] + sev_map[v]
    if sev <= 1:
        return 'Normal', 20
    if sev <= 3:
        return 'Warning', 50
    return 'Critical', 80

def fuzzy_predict(current, temp, vib, inclusive_warning=False):
    """
    Predict motor health score and condition.
    inclusive_warning:
      If True (PPT specification), score <= 65 is classified as 'Warning' (e.g. Test 5 -> Warning).
      If False (strict notebook condition), score < 65 is Warning and score >= 65 is Critical.
    """
    cm = current_memberships(current)
    tm = temp_memberships(temp)
    vm = vib_memberships(vib)
    
    num = 0.0
    den = 0.0
    fired = []
    
    for c in levels:
        for t in levels:
            for v in levels:
                w = min(cm[c], tm[t], vm[v])
                if w > 0:
                    lab, score_val = rule_output(c, t, v)
                    num += w * score_val
                    den += w
                    fired.append({
                        'current_level': c,
                        'temp_level': t,
                        'vib_level': v,
                        'weight': round(w, 4),
                        'label': lab,
                        'score_val': score_val
                    })
                    
    score = num / den if den else 20.0
    
    if score < 35:
        lab = 'Normal'
    elif inclusive_warning:
        lab = 'Warning' if score <= 65 else 'Critical'
    else:
        lab = 'Warning' if score < 65 else 'Critical'
        
    return lab, score, fired

def get_maintenance_suggestion(condition):
    """Returns maintenance protocol recommendation based on condition."""
    suggestions = {
        'Normal': 'Motor operating within safe parameters. Continue standard routine inspection schedule.',
        'Warning': 'Abnormal stress detected. Schedule preventive inspection; check bearing lubrication, load, and thermal dissipation.',
        'Critical': 'Severe anomaly detected! Initiate immediate emergency shutdown; inspect bearings, windings, and shaft alignment.'
    }
    return suggestions.get(condition, 'Unknown condition')

# Test cases defined in Phase 4
TEST_CASES = [
    (1, 3.0, 30.0, 1.0),
    (2, 5.5, 42.0, 2.0),
    (3, 7.5, 50.0, 3.0),
    (4, 10.0, 60.0, 4.0),
    (5, 12.5, 68.0, 4.2),
    (6, 14.0, 72.0, 5.5),
    (7, 15.5, 80.0, 6.5),
    (8, 17.0, 88.0, 7.8),
    (9, 18.5, 95.0, 9.0),
    (10, 19.5, 98.0, 9.8),
    (11, 8.0, 90.0, 8.0),
    (12, 4.0, 85.0, 7.0)
]

def run_all_tests(inclusive_warning=False):
    """Runs all 12 milestone test cases and returns a DataFrame."""
    rows = []
    for test_id, c, t, v in TEST_CASES:
        cond, score, _ = fuzzy_predict(c, t, v, inclusive_warning=inclusive_warning)
        rows.append({
            'Test': test_id,
            'Current (A)': c,
            'Temperature (°C)': t,
            'Vibration (mm/s)': v,
            'Health Score': round(score, 2),
            'Condition': cond
        })
    return pd.DataFrame(rows)

def run_genetic_programming(generations=25, pop_size=30, seed=42):
    """
    Executes Genetic Programming rule optimization.
    Returns:
      history: list of best fitness per generation
      initial_fitness: float
      best_fitness: float
      initial_chrom: list of ints
      best_chrom: list of ints
      rule_keys: list of (c, t, v)
    """
    random.seed(seed)
    np.random.seed(seed)
    
    def synthetic_label(c, t, v):
        risk = 0.5 * (c / 20.0) + 0.3 * ((t - 25.0) / 75.0) + 0.2 * (v / 10.0)
        return 0 if risk < 0.35 else (1 if risk < 0.65 else 2)
        
    train = [(random.uniform(0, 20), random.uniform(25, 100), random.uniform(0, 10)) for _ in range(180)]
    y = [synthetic_label(*x) for x in train]
    rule_keys = [(c, t, v) for c in levels for t in levels for v in levels]
    
    def chromosome_predict(chrom, c, t, v):
        cm = current_memberships(c)
        tm = temp_memberships(t)
        vm = vib_memberships(v)
        ws, vals = [], []
        for i, (cl, tl, vl) in enumerate(rule_keys):
            w = min(cm[cl], tm[tl], vm[vl])
            if w > 0:
                ws.append(w)
                vals.append(chrom[i])
        return int(round(np.average(vals, weights=ws))) if ws else 0
        
    def fitness(chrom):
        return sum(chromosome_predict(chrom, *x) == yy for x, yy in zip(train, y)) / len(train)
        
    initial = [rule_output(*k)[1] // 30 for k in rule_keys]
    initial_fit = fitness(initial)
    
    pop = [initial[:]]
    for _ in range(pop_size - 1):
        ch = initial[:]
        for j in range(27):
            if random.random() < 0.18:
                ch[j] = random.randrange(3)
        pop.append(ch)
        
    history = []
    for gen in range(generations):
        scored = sorted([(fitness(ch), ch) for ch in pop], reverse=True, key=lambda z: z[0])
        history.append(scored[0][0])
        elites = [ch for _, ch in scored[:6]]
        new_pop = [e[:] for e in elites]
        while len(new_pop) < pop_size:
            p1, p2 = random.choice(elites), random.choice(elites)
            cut = random.randrange(1, 27)
            child = p1[:cut] + p2[cut:]
            for j in range(27):
                if random.random() < 0.06:
                    child[j] = random.randrange(3)
            new_pop.append(child)
        pop = new_pop
        
    best_fit, best_chrom = max((fitness(ch), ch) for ch in pop)
    return {
        'history': history,
        'initial_fitness': initial_fit,
        'best_fitness': best_fit,
        'initial_chrom': initial,
        'best_chrom': best_chrom,
        'rule_keys': rule_keys
    }

if __name__ == '__main__':
    print("--- Phase 4 Test Results ---")
    df = run_all_tests()
    print(df.to_string(index=False))
    print("\n--- Sample PPT Test Case (12.5 A, 68 °C, 4.2 mm/s) ---")
    lab_strict, score, fired = fuzzy_predict(12.5, 68, 4.2, inclusive_warning=False)
    lab_ppt, _, _ = fuzzy_predict(12.5, 68, 4.2, inclusive_warning=True)
    print(f"Health Score: {score:.2f}")
    print(f"Strict condition (< 65): {lab_strict}")
    print(f"PPT specification (<= 65): {lab_ppt}")
