"""
Zentrale Farbkonfiguration für alle GDOP-Diagramme.

Diese Datei definiert einheitliche Farben für konsistente Darstellung
über alle Visualisierungen hinweg.
"""

# Metriken
DISTANCE_ERROR = '#FF6B6B'      # Distanzfehler - helles Rot
STD_DEVIATION = '#9B59B6'       # Standardabweichung - Lila
POSITION_ERROR = '#C0392B'      # Positionsfehler - dunkleres kräftiges Rot
TAG_TRUTH_GDOP = '#FF8C00'      # Tag Truth GDOP - Orange (DarkOrange)

# Varianten
PD_COLOR = '#3498DB'            # PD - Blau
FW_COLOR = '#E74C3C'            # FW - kräftiges Rot

# Anchor Count
ANCHOR_3A = '#5DADE2'           # 3A - Hellblau
ANCHOR_4A = '#1F618D'           # 4A - Dunkelblau

# Aggregationsmethoden (Grün-/Türkis-Abstufungen)
AGG_METHOD_COLORS = {
    'newest': '#48C9B0',        # Türkis
    'lowest': '#45B39D',        # Grünlich-Türkis
    'mean': '#16A085',          # Dunkles Türkis
    'median': '#138D75'         # Sehr dunkles Türkis/Grün
}

# Trilaterationsmethoden (Gelblich-grüne Abstufungen)
TRILAT_METHOD_COLORS = {
    'classical': '#ABEBC6',     # Helles gelblich-grün
    'best_subset': '#82E0AA',   # Mittleres grün
    'nonlinear': '#58D68D'      # Kräftiges grün (eher gelblich)
}

# Standard Matplotlib-Stil beibehalten
# (keine Änderungen an Schriftart, Größe etc. - Matplotlib Standard)
