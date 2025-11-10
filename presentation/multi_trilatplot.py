import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

from PyQt5.QtCore import QObject

from simulation import station


class MultiTrilatPlot(QObject):
    """Plot showing all loaded scenarios overlaid in a single plot, similar to TrilatPlot."""

    STATION_DOT_SIZE = 100
    STATION_COLOR = 'blue'
    CIRCLE_LINESTYLE = 'dotted'
    VIEWPORT_PADDING = 5.0
    LABEL_OFFSET = 1

    def __init__(self, window, scenarios):
        super().__init__()
        self.window = window
        self.scenarios = scenarios
        self.display_config = self.window.display_config

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        self.ax.set_title("Multi-Scenario Trilateration Plot")
        self.ax.set_xlabel('x (m)')
        self.ax.set_ylabel('y (m)')
        self.ax.set_aspect('equal', adjustable='box')

        # Create legend
        legend_elements = []
        if self.display_config.showLegendAnchors:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Anchors'))
        if self.display_config.showLegendTags:
            legend_elements.append(plt.Line2D([0], [0], marker='x', color='w', markerfacecolor='red', markersize=8, label='Tags'))
        if self.display_config.showLegendTagTruth:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Tag Truth'))
        
        if legend_elements:
            self.ax.legend(handles=legend_elements, loc='upper right', fontsize='small')

        # Initialize artists for each scenario
        self.anchor_scatters = []
        self.tag_scatters = []
        self.tag_truth_scatters = []
        self.circle_pairs_list = []
        self.anchor_pair_lines_list = []
        self.anchor_pair_texts_list = []
        self.tag_anchor_lines_list = []
        self.tag_anchor_texts_list = []
        self.tag_name_texts_list = []
        self.anchor_name_texts_list = []
        self.position_error_lines_list = []
        self.border_patches = []
        self.tag_truth_texts = []

        linestyles = ['solid', 'dashed', 'dashdot', 'dotted']
        colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']

        for i, scenario in enumerate(scenarios):
            linestyle = linestyles[i % len(linestyles)]
            # All anchors blue, as in TrilatPlot
            color = 'blue'

            # Initialize empty artists
            anchor_scatter = self.ax.scatter([], [], c='blue', s=self.STATION_DOT_SIZE, marker='o')
            tag_scatter = self.ax.scatter([], [], c='red', marker='x')
            tag_truth_scatter = self.ax.scatter([], [], c='green', s=self.STATION_DOT_SIZE)

            self.anchor_scatters.append(anchor_scatter)
            self.tag_scatters.append(tag_scatter)
            self.tag_truth_scatters.append(tag_truth_scatter)

            self.circle_pairs_list.append([])
            self.anchor_pair_lines_list.append([])
            self.anchor_pair_texts_list.append([])
            self.tag_anchor_lines_list.append([])
            self.tag_anchor_texts_list.append([])
            self.tag_name_texts_list.append([])
            self.anchor_name_texts_list.append([])
            self.position_error_lines_list.append([])
            self.tag_truth_texts.append(None)

            # Border rectangle black, as in TrilatPlot
            if scenario.border_rectangle:
                rect = scenario.border_rectangle
                width = rect['max_x'] - rect['min_x']
                height = rect['max_y'] - rect['min_y']
                border_patch = Rectangle((rect['min_x'], rect['min_y']), width, height,
                                         edgecolor='black', facecolor='none', linewidth=2, linestyle='solid', zorder=0)
                self.ax.add_patch(border_patch)
                border_patch.set_visible(self.display_config.showBorderRectangle)
                self.border_patches.append(border_patch)
            else:
                self.border_patches.append(None)

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Update all artists with current scenario data."""
        for i, scenario in enumerate(self.scenarios):
            anchor_scatter = self.anchor_scatters[i]
            tag_scatter = self.tag_scatters[i]
            tag_truth_scatter = self.tag_truth_scatters[i]

            anchor_positions = scenario.anchor_positions()
            tag_positions = scenario.tag_positions()

            # Update anchors
            if len(anchor_positions) > 0:
                anchor_scatter.set_offsets(np.array(anchor_positions))
            else:
                anchor_scatter.set_offsets(np.empty((0, 2)))
            anchor_scatter.set_visible(self.display_config.showAnchors)

            # Update tags
            if len(tag_positions) > 0:
                tag_scatter.set_offsets(np.array(tag_positions))
            else:
                tag_scatter.set_offsets(np.empty((0, 2)))
            tag_scatter.set_visible(self.display_config.showTags)

            # Update tag truth
            if scenario.tag_truth:
                tag_truth_scatter.set_offsets([scenario.tag_truth.position()])
                tag_truth_scatter.set_visible(self.display_config.showTagTruth)

                # Update tag truth label
                pos = scenario.tag_truth.position()
                if self.tag_truth_texts[i] is None:
                    self.tag_truth_texts[i] = self.ax.text(0, 0, '', ha='center', va='center', color='green')
                name = scenario.get_tag_list()[0].name if scenario.get_tag_list() else scenario.tag_truth.name or 'Tag Truth'
                label_text = self._generate_label_text(name, pos[0], pos[1], show_name=True, show_coords=self.display_config.showTagCoordinates, scenario_name=scenario.name)
                self.tag_truth_texts[i].set_text(label_text)
                self.tag_truth_texts[i].set_position((pos[0] + self.LABEL_OFFSET, pos[1] + self.LABEL_OFFSET))
                self.tag_truth_texts[i].set_bbox(dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
                self.tag_truth_texts[i].set_visible(self.display_config.showTagTruth and self.display_config.showTagTruthLabels)
            else:
                tag_truth_scatter.set_visible(False)
                if self.tag_truth_texts[i]:
                    self.tag_truth_texts[i].set_visible(False)

            # Update circles
            circle_pairs = self.circle_pairs_list[i]
            linestyle = ['solid', 'dashed', 'dashdot', 'dotted'][i % 4]
            if self.display_config.showAnchorCircles and scenario.tag_truth:
                distances_truth = scenario.tag_truth.distances()
                # Ensure enough circles
                while len(circle_pairs) < len(anchor_positions):
                    c1 = Circle((0, 0), 0, edgecolor='blue', facecolor='none', fill=False, linestyle=linestyle, linewidth=1.0, zorder=1, alpha=0.7)
                    c2 = Circle((0, 0), 0, edgecolor='blue', facecolor='none', fill=False, linestyle=linestyle, linewidth=1.0, zorder=1, alpha=0.7)
                    self.ax.add_patch(c1)
                    self.ax.add_patch(c2)
                    circle_pairs.append((c1, c2))

                for j, (c1, c2) in enumerate(circle_pairs):
                    if j < len(anchor_positions):
                        c1.set_visible(True)
                        c2.set_visible(True)
                        c1.set_center(anchor_positions[j])
                        c1.set_radius(distances_truth[j] + scenario.sigma)
                        c2.set_center(anchor_positions[j])
                        c2.set_radius(max(0.0, distances_truth[j] - scenario.sigma))
                    else:
                        c1.set_visible(False)
                        c2.set_visible(False)
            else:
                for c1, c2 in circle_pairs:
                    c1.set_visible(False)
                    c2.set_visible(False)

            # Update anchor pair lines and texts
            anchor_pair_lines = self.anchor_pair_lines_list[i]
            anchor_pair_texts = self.anchor_pair_texts_list[i]
            num_pairs = len(anchor_positions) * (len(anchor_positions) - 1) // 2
            while len(anchor_pair_lines) < num_pairs:
                l, = self.ax.plot([], [], 'b--', alpha=0.5)
                anchor_pair_lines.append(l)
                t = self.ax.text(0, 0, '', ha='center', va='center')
                anchor_pair_texts.append(t)

            pair_idx = 0
            for a in range(len(anchor_positions)):
                for b in range(a + 1, len(anchor_positions)):
                    if self.display_config.showBetweenAnchorsLines:
                        xdata = [anchor_positions[a][0], anchor_positions[b][0]]
                        ydata = [anchor_positions[a][1], anchor_positions[b][1]]
                        anchor_pair_lines[pair_idx].set_xdata(xdata)
                        anchor_pair_lines[pair_idx].set_ydata(ydata)
                        anchor_pair_lines[pair_idx].set_visible(True)
                    else:
                        anchor_pair_lines[pair_idx].set_visible(False)

                    if self.display_config.showBetweenAnchorsLabels:
                        xm = (anchor_positions[a][0] + anchor_positions[b][0]) / 2
                        ym = (anchor_positions[a][1] + anchor_positions[b][1]) / 2
                        distance = np.linalg.norm(anchor_positions[a] - anchor_positions[b])
                        anchor_pair_texts[pair_idx].set_text(f"{distance:.2f}")
                        anchor_pair_texts[pair_idx].set_position((xm, ym))
                        anchor_pair_texts[pair_idx].set_visible(True)
                    else:
                        anchor_pair_texts[pair_idx].set_visible(False)
                    pair_idx += 1

            # Hide extras
            for idx in range(pair_idx, len(anchor_pair_lines)):
                anchor_pair_lines[idx].set_visible(False)
                anchor_pair_texts[idx].set_visible(False)

            # Update tag-anchor lines and texts
            tag_anchor_lines = self.tag_anchor_lines_list[i]
            tag_anchor_texts = self.tag_anchor_texts_list[i]
            num_ta = len(tag_positions) * len(anchor_positions)
            while len(tag_anchor_lines) < num_ta:
                l, = self.ax.plot([], [], 'r--', alpha=0.5)
                tag_anchor_lines.append(l)
                t = self.ax.text(0, 0, '', ha='center', va='center')
                tag_anchor_texts.append(t)

            ta_idx = 0
            for ti, tag_pos in enumerate(tag_positions):
                for ai, anchor_pos in enumerate(anchor_positions):
                    if self.display_config.showTagAnchorLines:
                        xdata = [anchor_pos[0], tag_pos[0]]
                        ydata = [anchor_pos[1], tag_pos[1]]
                        tag_anchor_lines[ta_idx].set_xdata(xdata)
                        tag_anchor_lines[ta_idx].set_ydata(ydata)
                        tag_anchor_lines[ta_idx].set_visible(True)
                    else:
                        tag_anchor_lines[ta_idx].set_visible(False)

                    if self.display_config.showTagAnchorLabels:
                        xm = (anchor_pos[0] + tag_pos[0]) / 2
                        ym = (anchor_pos[1] + tag_pos[1]) / 2
                        distance = np.linalg.norm(anchor_pos - tag_pos)
                        tag_anchor_texts[ta_idx].set_text(f"{distance:.2f}")
                        tag_anchor_texts[ta_idx].set_position((xm, ym))
                        tag_anchor_texts[ta_idx].set_visible(True)
                    else:
                        tag_anchor_texts[ta_idx].set_visible(False)
                    ta_idx += 1

            # Hide extras
            for idx in range(ta_idx, len(tag_anchor_lines)):
                tag_anchor_lines[idx].set_visible(False)
                tag_anchor_texts[idx].set_visible(False)

            # Update tag names
            tag_name_texts = self.tag_name_texts_list[i]
            while len(tag_name_texts) < len(tag_positions):
                t = self.ax.text(0, 0, '', ha='center', va='center', color='red')
                tag_name_texts.append(t)

            for j, tag_pos in enumerate(tag_positions):
                x, y = tag_pos
                name = scenario.get_tag_list()[j].name
                label_text = self._generate_label_text(name, x, y, show_name=self.display_config.showTagNames, show_coords=self.display_config.showTagCoordinates, scenario_name=scenario.name)
                if label_text:
                    tag_name_texts[j].set_text(label_text)
                    tag_name_texts[j].set_position((x + self.LABEL_OFFSET, y + self.LABEL_OFFSET))
                    tag_name_texts[j].set_bbox(dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
                    tag_name_texts[j].set_visible(True)
                else:
                    tag_name_texts[j].set_visible(False)

            for idx in range(len(tag_positions), len(tag_name_texts)):
                tag_name_texts[idx].set_visible(False)

            # Update anchor names
            anchor_name_texts = self.anchor_name_texts_list[i]
            while len(anchor_name_texts) < len(anchor_positions):
                t = self.ax.text(0, 0, '', ha='center', va='center')
                anchor_name_texts.append(t)

            for j in range(len(anchor_positions)):
                x, y = anchor_positions[j]
                name = scenario.get_anchor_list()[j].name
                label_text = self._generate_label_text(name, x, y, show_name=self.display_config.showAnchorNames, show_coords=self.display_config.showAnchorCoordinates, scenario_name=scenario.name)
                if label_text:
                    anchor_name_texts[j].set_text(label_text)
                    anchor_name_texts[j].set_position((x + self.LABEL_OFFSET, y + self.LABEL_OFFSET))
                    anchor_name_texts[j].set_bbox(dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
                    anchor_name_texts[j].set_visible(True)
                else:
                    anchor_name_texts[j].set_visible(False)

            for idx in range(len(anchor_positions), len(anchor_name_texts)):
                anchor_name_texts[idx].set_visible(False)

            # Update position error lines
            position_error_lines = self.position_error_lines_list[i]
            while len(position_error_lines) < len(tag_positions):
                l, = self.ax.plot([], [], 'r-', linewidth=2)
                position_error_lines.append(l)

            for j, tag_pos in enumerate(tag_positions):
                if self.display_config.showPositionErrorLines and scenario.tag_truth:
                    truth_pos = scenario.tag_truth.position()
                    xdata = [truth_pos[0], tag_pos[0]]
                    ydata = [truth_pos[1], tag_pos[1]]
                    position_error_lines[j].set_xdata(xdata)
                    position_error_lines[j].set_ydata(ydata)
                    position_error_lines[j].set_visible(True)
                else:
                    position_error_lines[j].set_visible(False)

            # Hide extras
            for idx in range(len(tag_positions), len(position_error_lines)):
                position_error_lines[idx].set_visible(False)

            # Border
            if self.border_patches[i]:
                self.border_patches[i].set_visible(self.display_config.showBorderRectangle)

        # Update viewport over all scenarios
        self._update_viewport()

        # Update legend
        self.update_legend()

    def _update_viewport(self):
        """Update viewport based on all positions from all scenarios or border rectangles if option is set."""
        if self.display_config.useBorderRectangleForViewport:
            # Use union of all border rectangles
            min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
            has_border = False
            for scenario in self.scenarios:
                if scenario.border_rectangle:
                    rect = scenario.border_rectangle
                    min_x = min(min_x, rect['min_x'])
                    max_x = max(max_x, rect['max_x'])
                    min_y = min(min_y, rect['min_y'])
                    max_y = max(max_y, rect['max_y'])
                    has_border = True
            if has_border:
                padding = self.VIEWPORT_PADDING
                xlim = (min_x - padding, max_x + padding)
                ylim = (min_y - padding, max_y + padding)
            else:
                # Fallback to positions
                all_positions = []
                for scenario in self.scenarios:
                    all_positions.extend(scenario.anchor_positions())
                    all_positions.extend(scenario.tag_positions())
                    if scenario.tag_truth:
                        all_positions.append(scenario.tag_truth.position())
                if all_positions:
                    all_positions = np.array(all_positions)
                    min_x, max_x = all_positions[:, 0].min(), all_positions[:, 0].max()
                    min_y, max_y = all_positions[:, 1].min(), all_positions[:, 1].max()
                    padding = self.VIEWPORT_PADDING
                    xlim = (min_x - padding, max_x + padding)
                    ylim = (min_y - padding, max_y + padding)
                else:
                    xlim = (-10, 10)
                    ylim = (-10, 10)
        else:
            # Use extrema of all positions
            all_positions = []
            for scenario in self.scenarios:
                all_positions.extend(scenario.anchor_positions())
                all_positions.extend(scenario.tag_positions())
                if scenario.tag_truth:
                    all_positions.append(scenario.tag_truth.position())
            if all_positions:
                all_positions = np.array(all_positions)
                min_x, max_x = all_positions[:, 0].min(), all_positions[:, 0].max()
                min_y, max_y = all_positions[:, 1].min(), all_positions[:, 1].max()
                padding = self.VIEWPORT_PADDING
                xlim = (min_x - padding, max_x + padding)
                ylim = (min_y - padding, max_y + padding)
            else:
                xlim = (-10, 10)
                ylim = (-10, 10)
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

    def update_legend(self):
        """Update the legend based on current display config."""
        # Remove existing legend
        if self.ax.get_legend():
            self.ax.get_legend().remove()
        
        # Create new legend
        legend_elements = []
        if self.display_config.showLegendAnchors:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Anchors'))
        if self.display_config.showLegendTags:
            legend_elements.append(plt.Line2D([0], [0], marker='x', color='w', markerfacecolor='red', markersize=8, label='Tags'))
        if self.display_config.showLegendTagTruth:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Tag Truth'))
        if self.display_config.showLegendBorder and any(self.border_patches):
            legend_elements.append(plt.Rectangle((0, 0), 1, 1, edgecolor='black', facecolor='none', linewidth=2, label='Border'))
        
        if legend_elements:
            self.ax.legend(handles=legend_elements, loc='upper right', fontsize='small')
        else:
            # Remove legend if no elements
            if self.ax.get_legend():
                self.ax.get_legend().remove()

    def redraw(self):
        """Trigger a canvas redraw."""
        try:
            self.fig.canvas.draw_idle()
        except Exception:
            pass

    def _generate_label_text(self, name, x, y, show_name=False, show_coords=False, scenario_name=None):
        parts = []
        if show_name:
            parts.append(name)
        if show_coords:
            parts.append(f"({x:.2f}, {y:.2f})")
        if scenario_name and (show_name or show_coords):
            parts.append(f"({scenario_name})")
        return "\n".join(parts) if parts else ""