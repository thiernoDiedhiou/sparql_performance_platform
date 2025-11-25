"""
Script de diagnostic pour vérifier les insights de performance
"""

import pandas as pd
import numpy as np

# Simulation des données du screenshot
data = {
    'engine': ['Jena Fuseki', 'Virtuoso'],
    'query_name': ['Simple - Cours disponibles', 'Simple - Cours disponibles'],
    'execution_time': [0.01560521, 0.02367878],
    'success': [True, True]
}

df = pd.DataFrame(data)

print("=" * 80)
print("DIAGNOSTIC DES INSIGHTS DE PERFORMANCE")
print("=" * 80)
print()

print("Données brutes:")
print(df)
print()

# Performance moyenne par moteur
print("-" * 80)
print("1. PERFORMANCE MOYENNE PAR MOTEUR")
print("-" * 80)
avg_by_engine = df.groupby('engine')['execution_time'].mean()
print(avg_by_engine)
print()

# Moteur le plus performant (temps le plus faible)
best_engine = avg_by_engine.idxmin()
worst_engine = avg_by_engine.idxmax()

print(f"✅ Moteur le PLUS performant (temps MIN): {best_engine} ({avg_by_engine[best_engine]:.8f}s)")
print(f"❌ Moteur le MOINS performant (temps MAX): {worst_engine} ({avg_by_engine[worst_engine]:.8f}s)")
print()

# Calcul de l'écart de performance
print("-" * 80)
print("2. CALCUL DE L'ÉCART DE PERFORMANCE")
print("-" * 80)

performance_gap = avg_by_engine[worst_engine] / avg_by_engine[best_engine]
gap_percent = (performance_gap - 1) * 100

print(f"Ratio: {avg_by_engine[worst_engine]:.8f} / {avg_by_engine[best_engine]:.8f} = {performance_gap:.4f}")
print(f"Écart en %: ({performance_gap:.4f} - 1) × 100 = {gap_percent:.2f}%")
print()

# Autre méthode de calcul (différence absolue)
abs_diff = avg_by_engine[worst_engine] - avg_by_engine[best_engine]
abs_diff_percent_worst = (abs_diff / avg_by_engine[worst_engine]) * 100
abs_diff_percent_best = (abs_diff / avg_by_engine[best_engine]) * 100

print("Méthodes alternatives:")
print(f"  - Différence absolue: {abs_diff:.8f}s")
print(f"  - % par rapport au MOINS performant: {abs_diff_percent_worst:.2f}%")
print(f"  - % par rapport au PLUS performant: {abs_diff_percent_best:.2f}%")
print()

# Stabilité
print("-" * 80)
print("3. STABILITÉ DES PERFORMANCES")
print("-" * 80)
stability = df.groupby('engine')['execution_time'].std()
print(stability)
print()
print(f"Plus stable: {stability.idxmin()}")
print(f"Moins stable: {stability.idxmax()}")
print()

# Insights finaux
print("=" * 80)
print("INSIGHTS FINAUX (comme dans l'application)")
print("=" * 80)
insights = {
    'best_engine': best_engine,
    'worst_engine': worst_engine,
    'performance_gap': performance_gap,
    'most_stable': stability.idxmin(),
    'least_stable': stability.idxmax()
}

print(f"✅ Meilleur moteur: {insights['best_engine']}")
print(f"❌ Moins performant: {insights['worst_engine']}")
print(f"📊 Écart de performance: {gap_percent:.1f}% plus lent pour le moteur le moins performant")
print(f"🎯 Plus stable: {insights['most_stable']}")
print(f"📊 Moins stable: {insights['least_stable']}")
print()

print("=" * 80)
print("RÉSULTAT ATTENDU")
print("=" * 80)
print(f"Le message devrait être: 'Moteur le plus performant: {best_engine}'")
print(f"Si l'interface affiche 'Virtuoso', il y a un bug dans le filtrage ou l'affichage.")
print()
