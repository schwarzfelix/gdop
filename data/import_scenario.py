"""
Scenario Import module for GDOP application.
Handles loading scenario configurations from JSON files.
"""

import os
import json
from simulation.station import Anchor, Tag
from simulation import measurements


def load_scenario_from_json(scenario_obj, scenario_name: str, workspace_dir: str = "workspace") -> bool:
    """
    Load scenario configuration from JSON file and update the scenario object.
    
    Args:
        scenario_obj: The scenario object to update
        scenario_name: Name of the scenario
        workspace_dir: Directory containing scenario files
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load scenario configuration from JSON
        scenario_path = os.path.join(workspace_dir, scenario_name, "scenario.json")
        if not os.path.exists(scenario_path):
            print(f"Scenario configuration file not found: {scenario_path}")
            return False
        
        with open(scenario_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing stations and load from JSON
        scenario_obj.stations = []
        for st in data.get('stations', []):
            name = st['name']
            typ = st['type']
            if typ == 'ANCHOR':
                pos = st['position']
                scenario_obj.stations.append(Anchor(pos, name))
            elif typ == 'TAG':
                # Tags don't have fixed positions - they are calculated from measurements
                scenario_obj.stations.append(Tag(scenario_obj, name))
        
        # Clear existing measurements
        scenario_obj.measurements = measurements.Measurements()
        
        return True
        
    except Exception as e:
        print(f"Error loading scenario from JSON: {str(e)}")
        return False
