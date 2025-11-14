"""
Trilateration Method Comparison Plot for GDOP Analysis.

This plot compares position errors across different trilateration methods
(classical, best_subset, nonlinear) by applying each method to all loaded scenarios
and calculating the resulting position error. Scenarios are grouped by arrangement
(first 4 characters) with each bar representing a specific scenario colored by its
trilateration method.
"""

import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


class TrilaterationMethodComparisonPlot:
    """Plot comparing position errors for different trilateration methods."""

    def __init__(self, parent, scenarios):
        """Initialize the trilateration method comparison plot.
        
        Args:
            parent: Parent widget
            scenarios: List of currently loaded scenarios
        """
        self.parent = parent
        self.scenarios = scenarios
        self.fig, self.ax = plt.subplots(figsize=(14, 7))
        
    def update_data(self):
        """Update plot data by calculating position errors with different trilateration methods."""
        self.ax.clear()
        
        if not self.scenarios:
            self.ax.text(0.5, 0.5, 'No scenarios loaded', 
                        ha='center', va='center', transform=self.ax.transAxes)
            return
        
        # Define trilateration methods to compare
        trilat_methods = ['classical', 'best_subset', 'nonlinear']
        colors = {'classical': '#1f77b4', 'best_subset': '#ff7f0e', 'nonlinear': '#2ca02c'}
        
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
                    # Get the trilateration method used for this scenario
                    trilat_method = getattr(scenario, 'trilateration_method', 'classical')
                    
                    # Calculate position error with the scenario's trilateration method
                    try:
                        # Temporarily set method (already set, but make sure)
                        original_method = scenario.trilateration_method
                        scenario.trilateration_method = trilat_method
                        
                        # Calculate position error for first tag
                        tags = scenario.get_tag_list()
                        if tags:
                            error = tags[0].position_error()
                            if error is None:
                                error = 0.0
                        else:
                            error = 0.0
                        
                        # Restore original method (though it should be the same)
                        scenario.trilateration_method = original_method
                        
                    except Exception as e:
                        print(f"Error processing {scenario.name}: {e}")
                        error = 0.0
                        try:
                            scenario.trilateration_method = original_method
                        except:
                            pass
                    
                    # Add bar
                    pos = group_start + i * scenario_width + scenario_width / 2
                    bar_positions.append(pos)
                    bar_heights.append(error)
                    bar_colors.append(colors.get(trilat_method, '#888888'))
                    bar_labels.append(f"{scenario.name}\n({trilat_method})")
                
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
        bars = self.ax.bar(bar_positions, bar_heights, 
                          width=group_width/max(len(arrangement_scenarios[arr]) for arr in arrangements),
                          color=bar_colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Add value labels on bars
        for pos, height in zip(bar_positions, bar_heights):
            if height > 0:
                self.ax.text(pos, height, f'{height:.2f}',
                           ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # Customize plot
        self.ax.set_xlabel('Arrangement', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Position Error (m)', fontsize=12, fontweight='bold')
        self.ax.set_title('Position Error by Trilateration Method (Grouped by Arrangement)', 
                         fontsize=14, fontweight='bold')
        self.ax.set_xticks(tick_positions)
        self.ax.set_xticklabels(tick_labels)
        
        # Create legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=colors[method], 
                                label=method.replace('_', ' ').title(), 
                                alpha=0.8) 
                          for method in trilat_methods]
        self.ax.legend(handles=legend_elements, title='Trilateration Method', loc='upper right')
        
        self.ax.grid(True, alpha=0.3, axis='y')
        self.fig.tight_layout()
    
    def redraw(self):
        """Redraw the plot."""
        self.fig.canvas.draw()

