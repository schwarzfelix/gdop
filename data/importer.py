"""
Import module for GDOP application.
Handles importing measurement data from CSV files and scenario configurations from JSON files.
Pure data processing - no UI components.
"""

import pandas as pd
from typing import List, Optional, Tuple
import logging

_LOG = logging.getLogger(__name__)

from data.import_measurements import read_workspace_csvs
from data.import_scenario import load_scenario_from_json


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


def import_scenario_data(scenario_obj, scenario_name: str, workspace_dir: str = "workspace", agg_method: str = "lowest") -> Tuple[bool, str]:
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
        if not load_scenario_from_json(scenario_obj, scenario_name, workspace_dir):
            return False, f"Failed to load scenario configuration for '{scenario_name}'"

        # Get scenario data
        scenario_data, error = get_scenario_data(scenario_name, workspace_dir)
        if error:
            return False, error

        # Process the data (aggregate per AP based on agg_method)
        processed_count = _process_measurement_data(scenario_obj, scenario_data, scenario_name, agg_method=agg_method)

        return True, f"Successfully imported {processed_count} measurements (agg={agg_method}) from scenario '{scenario_name}'."

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
    # It's not required that the current scenario already contains anchors or tags.
    # The JSON scenario descriptor in the workspace should provide the station definitions
    # that will be loaded during import. Keep this check permissive but return a
    # helpful message if the scenario object is malformed (missing expected API).
    try:
        _ = scenario_obj.get_anchor_list()
        _ = scenario_obj.get_tag_list()
    except Exception:
        return False, "Scenario object does not implement required station accessors"

    # Allow import to proceed; the importer will warn if the CSV data or JSON config
    # lacks required information at processing time.
    return True, ""


def _process_measurement_data(scenario_obj, scenario_data: pd.DataFrame, scenario_name: str, agg_method: str = "lowest"):
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
        _LOG.warning("No tags found in scenario configuration. Measurements require at least one tag.")
        return
    
    target_tag = existing_tags[0]  # Use first tag from JSON configuration
    
    # Aggregate measurements per AP (ap-ssid) according to agg_method
    processed_count = 0

    # Ensure the key columns exist
    if 'ap-ssid' not in scenario_data.columns or 'est._range(m)' not in scenario_data.columns:
        _LOG.warning("Input data missing required columns 'ap-ssid' or 'est._range(m)'.")
        return 0

    # Prepare aggregation
    # Filter out invalid ranges
    valid_df = scenario_data.copy()
    valid_df = valid_df[pd.to_numeric(valid_df['est._range(m)'], errors='coerce').notnull()]
    valid_df['est_range'] = pd.to_numeric(valid_df['est._range(m)'], errors='coerce')
    valid_df = valid_df[valid_df['est_range'] > 0]

    if valid_df.empty:
        _LOG.info("No valid measurements to import for scenario '%s'", scenario_name)
        return 0

    # Define aggregation function
    agg_method = (agg_method or "newest").lower()
    if agg_method not in ("newest", "lowest", "mean", "median"):
        _LOG.warning("Unknown aggregation method '%s', defaulting to 'newest'.", agg_method)
        agg_method = "newest"

    aggregated = None
    if agg_method == "newest":
        # assume there is a timestamp column 'time(ms)'; pick the row with max time per ap-ssid
        if 'time(ms)' in valid_df.columns:
            valid_df['time_ms'] = pd.to_numeric(valid_df['time(ms)'], errors='coerce')
            aggregated = valid_df.sort_values('time_ms').groupby('ap-ssid', sort=False).last()
        else:
            # fallback to last occurrence
            aggregated = valid_df.groupby('ap-ssid', sort=False).last()
    elif agg_method == "lowest":
        aggregated = valid_df.groupby('ap-ssid', sort=False)['est_range'].min().to_frame()
    elif agg_method == "mean":
        aggregated = valid_df.groupby('ap-ssid', sort=False)['est_range'].mean().to_frame()
    elif agg_method == "median":
        aggregated = valid_df.groupby('ap-ssid', sort=False)['est_range'].median().to_frame()

    # Normalize aggregated to a DataFrame with est_range column and ap-ssid as index
    if isinstance(aggregated, pd.Series):
        aggregated = aggregated.to_frame('est_range')
    if 'est_range' not in aggregated.columns:
        # In case 'last' produced full rows, extract est_range
        if 'est_range' in valid_df.columns and 'est._range(m)' in valid_df.columns:
            aggregated['est_range'] = aggregated.get('est_range') if 'est_range' in aggregated.columns else aggregated['est._range(m)']

    # Iterate aggregated results and add measurements
    for ap_ssid, row in aggregated.iterrows():
        try:
            estimated_range = float(row['est_range'])

            # Find a matching anchor station (by name similarity or use first available)
            ap_name = ap_ssid if isinstance(ap_ssid, str) else str(ap_ssid)
            anchor_station = None
            for anchor in existing_anchors:
                try:
                    if ap_name.lower() in anchor.name().lower() or anchor.name().lower() in ap_name.lower():
                        anchor_station = anchor
                        break
                except Exception:
                    continue

            # If no matching anchor found, use the first available anchor
            if not anchor_station and existing_anchors:
                anchor_station = existing_anchors[0]

            if anchor_station and anchor_station != target_tag:
                station_pair = frozenset([anchor_station, target_tag])
                scenario_obj.measurements.update_relation(station_pair, estimated_range)
                processed_count += 1

        except Exception as e:
            _LOG.warning("Failed to process aggregated measurement for '%s': %s", ap_ssid, e)
            continue
    _LOG.info("Processed %d aggregated measurements (method=%s) for scenario '%s'", processed_count, agg_method, scenario_name)
    _LOG.info("Total measurement relations: %d", len(scenario_obj.measurements.relation))
    return processed_count