"""
Debug script to test trilateration method synchronization.
Run this from the Python REPL in the app to verify the method is being used.
"""

import sys
sys.path.insert(0, '/Users/schwarzf/Projects/schwarzfelix/gdop')

from simulation.scenario import Scenario
from simulation.station import Anchor, Tag
import numpy as np

# Create test scenario (4-4A-PD-V3)
scenario = Scenario("Debug_Test")

# Add anchors
scenario.stations.append(Anchor([3.50, 8.50], 'FTM_PINK'))
scenario.stations.append(Anchor([0.00, 11.00], 'FTM_BLUE'))
scenario.stations.append(Anchor([16.00, 0.00], 'FTM_GREEN'))
scenario.stations.append(Anchor([8.00, 5.50], 'FTM_ORANGE'))

# Add tag
tag = Tag(scenario, 'N10P')
scenario.stations.append(tag)

# Set tag truth
scenario.tag_truth.update_position([16.00, 11.00])

# Add measurements
anchors = scenario.get_anchor_list()
distances = [12.75, 16.0, 15.0, 9.71]

for anchor, distance in zip(anchors, distances):
    pair = frozenset([anchor, tag])
    scenario.measurements.update_relation(pair, distance)

print("\n" + "="*70)
print("TRILATERATION METHOD TEST")
print("="*70)

methods = ["classical", "best_subset", "nonlinear"]
truth = scenario.tag_truth.position()

for method in methods:
    print(f"\n--- Method: {method} ---")
    scenario.trilateration_method = method
    print(f"Scenario method set to: {scenario.trilateration_method}")
    
    pos = tag.position()
    error = np.linalg.norm(pos - truth)
    
    print(f"Computed position: {pos}")
    print(f"Truth position:    {truth}")
    print(f"Error:             {error:.2f}m")
    
    if method == "classical":
        if error > 30:
            print("✓ Classical fails as expected (high error)")
        else:
            print("⚠️  Classical should have high error!")
    elif method == "best_subset":
        if error < 1:
            print("✓ Best_subset works correctly (low error)")
        else:
            print("⚠️  Best_subset should have low error!")

print("\n" + "="*70)
print("If you see '✓' for all tests, the synchronization is working!")
print("="*70 + "\n")
