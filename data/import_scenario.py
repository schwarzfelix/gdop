"""
Scenario Import module for GDOP application.
Handles loading scenario configurations from JSON files.
"""

import os
import json
from simulation.station import Anchor, Tag
from simulation import measurements
import logging

_LOG = logging.getLogger(__name__)


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
            _LOG.warning("Scenario configuration file not found: %s", scenario_path)
            return False
        
        with open(scenario_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing stations and reset measurements before creating Tag objects
        scenario_obj.stations = []
        # Initialize a fresh Measurements container so Tags created below
        # will reference the new measurements instance
        scenario_obj.measurements = measurements.Measurements()

        for st in data.get('stations', []):
            name = st['name']
            typ = st['type']
            if typ == 'ANCHOR':
                pos = st['position']
                # pass the scenario into Anchor so methods that expect it can use it
                scenario_obj.stations.append(Anchor(pos, name, scenario_obj))
            elif typ == 'TAG':
                # Tags don't have fixed positions - they are calculated from measurements
                # TODO streamline getting position from json
                pos = st.get('position', None)
                if pos is not None:
                    scenario_obj.tag_truth = Anchor(pos, 'TAG_TRUTH', scenario_obj)
                else:
                    scenario_obj.tag_truth = None
                    
                scenario_obj.stations.append(Tag(scenario_obj, name))

        # Load optional border rectangle
        rectangle_data = data.get('rectangle')
        if rectangle_data:
            scenario_obj.border_rectangle = {
                'min_x': rectangle_data['min_x'],
                'max_x': rectangle_data['max_x'],
                'min_y': rectangle_data['min_y'],
                'max_y': rectangle_data['max_y']
            }

        return True
        
    except Exception as e:
        _LOG.exception("Error loading scenario from JSON: %s", e)
        return False
