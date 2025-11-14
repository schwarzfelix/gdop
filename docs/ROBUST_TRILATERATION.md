# Robuste Trilateration - Implementierung

## Problem

Der klassische Least-Squares Trilaterationsalgorithmus versagt bei schlechter Anker-Geometrie:

**Beispiel: Szenario 4-4A-PD-V3**
- Messungen: alle < 16m
- Klassische Lösung: Position bei [-6.92, -17.62] → ~28m von allen Ankern entfernt ❌
- **Grund**: 3 der 4 Anker (BLUE, GREEN, ORANGE) liegen exakt auf einer Geraden
- Konditionszahl der Matrix: 150 → kleine Messfehler werden um Faktor 150 verstärkt!

## Lösung

Drei alternative Trilaterationsmethoden wurden implementiert:

### 1. `classical` (Standard)
- Klassisches Least-Squares Verfahren
- **Vorteile**: Schnell, analytische Lösung
- **Nachteile**: Versagt bei kollinearen Ankern
- **Verwendung**: Nur bei guter Anker-Geometrie

### 2. `best_subset` (Empfohlen)
- Wählt automatisch die beste 3-Anker-Kombination basierend auf Konditionszahl
- Prüft alle C(n,3) Kombinationen und wählt die mit bestem Residuum
- **Vorteile**: 
  - Robust gegen kollineare Anker
  - Automatische Filterung schlechter Geometrie
  - Im Test: 0.31m Fehler statt 36.67m!
- **Nachteile**: Etwas langsamer (aber vernachlässigbar für <10 Anker)
- **Verwendung**: Standard für reale Szenarien

### 3. `nonlinear` (Experimentell)
- Nonlineare Optimierung mit Schwerpunkt als Startpunkt
- Benötigt scipy
- **Vorteile**: Robust, nutzt alle Anker
- **Nachteile**: Kann in lokalen Minima landen
- **Verwendung**: Als Fallback oder zum Vergleich

## Verwendung

### In der GUI

1. Öffne den **Display Tab**
2. Erweitere **Trilateration Options**
3. Wähle die gewünschte Methode aus dem Dropdown
4. Änderungen werden sofort auf alle Tags angewendet

### Im Code

```python
from simulation.scenario import Scenario
from simulation.station import Tag

scenario = Scenario("MyScenario")
# ... Anker und Messungen hinzufügen ...

# Methode festlegen
scenario.trilateration_method = "best_subset"  # oder "classical", "nonlinear"

# Tag-Position wird automatisch mit der gewählten Methode berechnet
tag = Tag(scenario, "MyTag")
position = tag.position()
```

### Direkte Verwendung

```python
from simulation.geometry import trilateration_robust, check_anchor_geometry
import numpy as np

anchors = np.array([[0,0], [10,0], [5,10], [5,0]])
distances = np.array([5.0, 5.0, 5.0, 5.0])

# Geometrie prüfen
geometry_info = check_anchor_geometry(anchors)
if geometry_info['is_collinear']:
    print("Warnung: Anker sind fast kollinear!")

# Robuste Trilateration
position, metadata = trilateration_robust(anchors, distances, method="best_subset")

print(f"Position: {position}")
print(f"Verwendete Anker: {metadata['anchor_subset']}")
print(f"Konditionszahl: {metadata['condition_number']:.1f}")
print(f"Residuum: {metadata['residual']:.2f}m")
```

## Testergebnisse

**Szenario 4-4A-PD-V3** (3 kollineare Anker):

| Methode     | Positionsfehler | Verbesserung |
|-------------|-----------------|--------------|
| classical   | 36.67m          | -            |
| best_subset | 0.31m           | **+36.36m**  |
| nonlinear   | 20.48m          | +16.19m      |

## Implementation Details

- `simulation/geometry.py`: `trilateration_robust()` und `check_anchor_geometry()`
- `simulation/scenario.py`: `trilateration_method` Property
- `simulation/station.py`: `Tag.position()` berücksichtigt Methode vom Scenario
- `presentation/displayconfig.py`: `trilaterationMethod` Config
- `presentation/tabs/display_tab.py`: UI-Auswahl
- Tests: `simulation/test_trilateration_robust.py`

## Empfehlungen

1. **Standard-Einstellung**: `best_subset` für reale Messungen verwenden
2. **Geometrie-Check**: Bei hohen Positionsfehlern zuerst die Anker-Geometrie prüfen
3. **GDOP-Monitoring**: Hohe GDOP-Werte (>10) deuten auf schlechte Geometrie hin
4. **Anker-Platzierung**: 
   - Keine 3+ Anker auf einer Linie
   - Tag sollte innerhalb des Anker-Polygons liegen
   - Möglichst große Dreiecke/Vierecke bilden
