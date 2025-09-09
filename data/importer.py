"""
CSV Import module for GDOP application.
Pure data processing for importing measurement data from CSV files.
No UI components - just business logic.
"""

import pandas as pd
from typing import List, Optional, Tuple
import os
import json

from data.csv import read_workspace_csvs
from simulation.station import Anchor, Tag
from simulation import measurements


def get_available_scenarios(workspace_dir: str = "workspace") -> Tuple[List[str], Optional[str]]:
    """
    Get list of available scenarios from CSV files.
    
    Args:
        workspace_dir: Directory containing CSV files
        
    Returns:
        Tuple of (scenario_list, error_message)
    """
    try:
        df = read_workspace_csvs(workspace_dir)
        
        if df.empty:
            return [], f"No CSV measurement files found in '{workspace_dir}' directory."
        
        scenarios = df['scenario'].unique().tolist()
        
        if not scenarios:
            return [], "No scenario data found in CSV files."
        
        return scenarios, None
        
    except Exception as e:
        return [], f"Error reading CSV files: {str(e)}"


def get_scenario_data(scenario_name: str, workspace_dir: str = "workspace") -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Get CSV data for a specific scenario.
    
    Args:
        scenario_name: Name of the scenario to load
        workspace_dir: Directory containing CSV files
        
    Returns:
        Tuple of (dataframe, error_message)
    """
    try:
        df = read_workspace_csvs(workspace_dir)
        
        if df.empty:
            return None, f"No CSV files found in '{workspace_dir}'"
        
        scenario_data = df[df['scenario'] == scenario_name].copy()
        
        if scenario_data.empty:
            return None, f"No measurement data found for scenario '{scenario_name}'"
        
        return scenario_data, None
        
    except Exception as e:
        return None, f"Error loading scenario data: {str(e)}"


def import_scenario_data(scenario_obj, scenario_name: str, workspace_dir: str = "workspace") -> Tuple[bool, str]:
    """
    Import CSV data for a scenario into the scenario object.
    
    Args:
        scenario_obj: The scenario object to update
        scenario_name: Name of the scenario to import
        workspace_dir: Directory containing CSV files
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Load scenario configuration from JSON
        scenario_path = os.path.join(workspace_dir, scenario_name, "scenario.json")
        if not os.path.exists(scenario_path):
            return False, f"Scenario configuration file not found: {scenario_path}"
        
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
        
        # Get scenario data
        scenario_data, error = get_scenario_data(scenario_name, workspace_dir)
        if error:
            return False, error
        
        # Process the data
        processed_count = _process_measurement_data(scenario_obj, scenario_data, scenario_name)
        
        return True, f"Successfully imported {len(scenario_data)} measurements from scenario '{scenario_name}'."
        
    except Exception as e:
        return False, f"An error occurred while importing CSV data: {str(e)}"


def validate_scenario_for_import(scenario_obj) -> Tuple[bool, str]:
    """
    Validate that a scenario object is ready for import.
    
    Args:
        scenario_obj: The scenario object to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    existing_anchors = scenario_obj.get_anchor_list()
    existing_tags = scenario_obj.get_tag_list()
    
    if not existing_tags and len(existing_anchors) < 2:
        return False, "Scenario must have at least 2 anchor stations or 1 tag to import measurements"
    
    return True, ""


def _process_measurement_data(scenario_obj, scenario_data: pd.DataFrame, scenario_name: str):
    """
    Process the imported measurement data and update the scenario.
    
    Args:
        scenario_obj: The scenario object to update
        scenario_data: DataFrame containing the measurement data for the scenario
        scenario_name: Name of the imported scenario
    """
    # Expected columns (mapped from CSV headers)
    # Based on the actual CSV format: time(ms), true_range(m), est._range(m), std_dev(m), ap-ssid
    expected_cols = ['time(ms)', 'true_range(m)', 'est._range(m)', 'std_dev(m)', 'ap-ssid']
    
    # Use existing anchor stations as measurement anchors for imported data
    existing_anchors = scenario_obj.get_anchor_list()
    
    # Get tags from the loaded scenario
    existing_tags = scenario_obj.get_tag_list()
    if not existing_tags:
        print("Warning: No tags found in scenario configuration. Measurements require at least one tag.")
        return
    
    target_tag = existing_tags[0]  # Use first tag from JSON configuration
    
    # Process measurements - group by timestamp to create measurement sets
    processed_count = 0
    
    for _, row in scenario_data.iterrows():
        try:
            # Get estimated range (the main measurement value)
            estimated_range = row.get('est._range(m)', 0.0)
            
            if estimated_range <= 0:
                continue  # Skip invalid measurements
            
            # Use the AP name to determine which anchor this measurement corresponds to
            ap_name = row.get('ap-ssid', 'Unknown_AP')
            
            # Find a matching anchor station (by name similarity or use first available)
            anchor_station = None
            for anchor in existing_anchors:
                if ap_name.lower() in anchor.name().lower() or anchor.name().lower() in ap_name.lower():
                    anchor_station = anchor
                    break
            
            # If no matching anchor found, use the first available anchor
            if not anchor_station and existing_anchors:
                anchor_station = existing_anchors[0]
            
            if anchor_station and anchor_station != target_tag:
                # Add measurement between anchor and tag
                station_pair = frozenset([anchor_station, target_tag])
                scenario_obj.measurements.update_relation(station_pair, estimated_range)
                processed_count += 1
                
        except Exception as e:
            print(f"Warning: Failed to process measurement row: {e}")
            continue
    
    print(f"Processed {processed_count} measurements from {len(scenario_data)} rows in scenario '{scenario_name}'")
    print(f"Total measurement relations: {len(scenario_obj.measurements.relation)}")