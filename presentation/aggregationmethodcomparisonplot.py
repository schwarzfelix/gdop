"""
Aggregation Method Comparison Plot for GDOP Analysis.

This plot compares position errors across different aggregation methods
(newest, lowest, mean, median) by reimporting all scenarios with each method
and calculating the resulting position error. Scenarios are grouped by arrangement
(first 4 characters) with each bar representing a specific scenario colored by its
aggregation method.
"""

import matplotlib.pyplot as plt
import numpy as np
from data.importer import import_scenario
from collections import defaultdict


class AggregationMethodComparisonPlot:
    """Plot comparing position errors for different aggregation methods."""

    def __init__(self, parent, scenarios):
        """Initialize the aggregation method comparison plot.
        
        Args:
            parent: Parent widget
            scenarios: List of currently loaded scenarios
        """
        self.parent = parent
        self.scenarios = scenarios
        self.fig, self.ax = plt.subplots(figsize=(14, 7))
        
    def update_data(self):
        """Update plot data by reimporting scenarios with different aggregation methods."""
        self.ax.clear()
        
        if not self.scenarios:
            self.ax.text(0.5, 0.5, 'No scenarios loaded', 
                        ha='center', va='center', transform=self.ax.transAxes)
            return
        
        # Define aggregation methods to compare
        agg_methods = ['newest', 'lowest', 'mean', 'median']
        colors = {'newest': '#1f77b4', 'lowest': '#ff7f0e', 'mean': '#2ca02c', 'median': '#d62728'}
        
        # Group scenarios by arrangement and collect data
        arrangement_scenarios = defaultdict(list)
        
        for scenario in self.scenarios:
            # Skip sandbox scenario
            if scenario.name == "SandboxScenario":
                continue
            
            # Extract arrangement (first 4 characters)
            if len(scenario.name) >= 4:
                arrangement = scenario.name[:4]
            else:
                arrangement = 'Other'
            
            arrangement_scenarios[arrangement].append(scenario)
        
        # Sort arrangements
        arrangements = sorted(arrangement_scenarios.keys())
        
        if not arrangements:
            self.ax.text(0.5, 0.5, 'No valid scenarios to compare', 
                        ha='center', va='center', transform=self.ax.transAxes)
            return
        
        # Prepare data for plotting
        bar_positions = []
        bar_heights = []
        bar_colors = []
        bar_labels = []
        tick_positions = []
        tick_labels = []
        
        current_pos = 0
        group_width = 0.8
        
        for arrangement in arrangements:
            scenarios_in_group = arrangement_scenarios[arrangement]
            num_scenarios = len(scenarios_in_group)
            
            # Calculate positions for this group
            if num_scenarios > 0:
                scenario_width = group_width / num_scenarios
                group_start = current_pos
                
                for i, scenario in enumerate(scenarios_in_group):
                    # Get the aggregation method used for this scenario
                    agg_method = getattr(scenario, 'aggregation_method', 'lowest')
                    if agg_method is None:
                        agg_method = 'lowest'
                    
                    # Get the original trilateration method
                    original_trilat_method = getattr(scenario, 'trilateration_method', 'classical')
                    
                    # Calculate position error with the scenario's aggregation method
                    try:
                        # Reimport with the same method
                        success, message, temp_scenario = import_scenario(
                            scenario.name, 
                            workspace_dir="workspace", 
                            agg_method=agg_method
                        )
                        
                        if success and temp_scenario:
                            temp_scenario.trilateration_method = original_trilat_method
                            tags = temp_scenario.get_tag_list()
                            if tags:
                                error = tags[0].position_error()
                                if error is None:
                                    error = 0.0
                            else:
                                error = 0.0
                        else:
                            error = 0.0
                    except Exception as e:
                        print(f"Error processing {scenario.name}: {e}")
                        error = 0.0
                    
                    # Add bar
                    pos = group_start + i * scenario_width + scenario_width / 2
                    bar_positions.append(pos)
                    bar_heights.append(error)
                    bar_colors.append(colors.get(agg_method, '#888888'))
                    bar_labels.append(f"{scenario.name}\n({agg_method})")
                
                # Add tick for group center
                tick_positions.append(group_start + group_width / 2)
                tick_labels.append(arrangement)
                
                # Move to next group
                current_pos += group_width + 0.3
        
        if not bar_positions:
            self.ax.text(0.5, 0.5, 'No data to display', 
                        ha='center', va='center', transform=self.ax.transAxes)
            return
        
        # Plot bars
        bars = self.ax.bar(bar_positions, bar_heights, width=group_width/max(len(arrangement_scenarios[arr]) for arr in arrangements),
                          color=bar_colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Add value labels on bars
        for pos, height in zip(bar_positions, bar_heights):
            if height > 0:
                self.ax.text(pos, height, f'{height:.2f}',
                           ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # Customize plot
        self.ax.set_xlabel('Arrangement', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Position Error (m)', fontsize=12, fontweight='bold')
        self.ax.set_title('Position Error by Aggregation Method (Grouped by Arrangement)', 
                         fontsize=14, fontweight='bold')
        self.ax.set_xticks(tick_positions)
        self.ax.set_xticklabels(tick_labels)
        
        # Create legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=colors[method], label=method.capitalize(), alpha=0.8) 
                          for method in agg_methods]
        self.ax.legend(handles=legend_elements, title='Aggregation Method', loc='upper right')
        
        self.ax.grid(True, alpha=0.3, axis='y')
        self.fig.tight_layout()
    
    def redraw(self):
        """Redraw the plot."""
        self.fig.canvas.draw()

