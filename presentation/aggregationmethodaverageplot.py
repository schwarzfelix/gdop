"""
Aggregation Method Average Plot for GDOP Analysis.

This plot shows the average position error for each aggregation method
across all loaded scenarios. Each bar represents one aggregation method
with the mean position error calculated by reimporting all scenarios
with that specific method.
"""

import matplotlib.pyplot as plt
import numpy as np
from data.importer import import_scenario
from presentation.plot_colors import AGG_METHOD_COLORS, POSITION_ERROR


class AggregationMethodAveragePlot:
    """Plot showing average position error per aggregation method."""

    def __init__(self, parent, scenarios):
        """Initialize the aggregation method average plot.
        
        Args:
            parent: Parent widget
            scenarios: List of currently loaded scenarios
        """
        self.parent = parent
        self.scenarios = scenarios
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        
    def update_data(self):
        """Update plot data by calculating average position error per method."""
        self.ax.clear()
        
        if not self.scenarios:
            self.ax.text(0.5, 0.5, 'No scenarios loaded', 
                        ha='center', va='center', transform=self.ax.transAxes)
            return
        
        # Define aggregation methods to compare
        agg_methods = ['newest', 'lowest', 'mean', 'median']
        
        # Filter out sandbox scenario
        valid_scenarios = [s for s in self.scenarios if s.name != "SandboxScenario"]
        
        if not valid_scenarios:
            self.ax.text(0.5, 0.5, 'No valid scenarios to compare', 
                        ha='center', va='center', transform=self.ax.transAxes)
            return
        
        # Calculate average position error for each aggregation method
        method_errors = {}
        method_counts = {}
        
        for agg_method in agg_methods:
            errors = []
            
            for scenario in valid_scenarios:
                # Get the original trilateration method
                original_trilat_method = getattr(scenario, 'trilateration_method', 'classical')
                
                try:
                    # Reimport with this aggregation method
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
                            if error is not None:
                                errors.append(error)
                except Exception as e:
                    print(f"Error processing {scenario.name} with {agg_method}: {e}")
            
            # Calculate average
            if errors:
                method_errors[agg_method] = np.mean(errors)
                method_counts[agg_method] = len(errors)
            else:
                method_errors[agg_method] = 0.0
                method_counts[agg_method] = 0
        
        # Prepare data for plotting
        methods = list(method_errors.keys())
        avg_errors = [method_errors[m] for m in methods]
        bar_colors = [AGG_METHOD_COLORS[m] for m in methods]
        
        # Create bar plot
        x_pos = np.arange(len(methods))
        bars = self.ax.bar(x_pos, avg_errors, color=bar_colors, 
                          edgecolor='black', linewidth=1.5, width=0.6)
        
        # Add value labels on bars
        for i, (pos, height, method) in enumerate(zip(x_pos, avg_errors, methods)):
            count = method_counts[method]
            self.ax.text(pos, height, f'{height:.2f}m\n(n={count})',
                       ha='center', va='bottom')
        
        # Customize plot
        self.ax.set_xlabel('Aggregation Method')
        self.ax.set_ylabel('Average Position Error (m)')
        self.ax.set_title('Average Position Error by Aggregation Method')
        self.ax.set_xticks(x_pos)
        self.ax.set_xticklabels([m.capitalize() for m in methods])
        
        # Add grid
        self.ax.grid(True, alpha=0.3, axis='y')
        self.ax.set_axisbelow(True)
        
        # Set y-axis to start from 0
        self.ax.set_ylim(bottom=0)
        
        # Add total sample count info
        total_samples = sum(method_counts.values())
        self.fig.text(0.5, 0.02, f'Total measurements across all methods: {total_samples}', ha='center')
        
        self.fig.tight_layout(rect=[0, 0.05, 1, 1])  # Leave space for info text
    
    def redraw(self):
        """Redraw the plot."""
        self.fig.canvas.draw()
