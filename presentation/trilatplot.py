import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

from PyQt5.QtCore import pyqtSignal, QObject

from simulation import station
from simulation import SandboxScenario


class TrilatPlot(QObject):
    anchors_changed = pyqtSignal()
    tags_changed = pyqtSignal()
    measurements_changed = pyqtSignal()

    STATION_DOT_SIZE = 100
    STATION_COLOR = 'blue'
    CIRCLE_LINESTYLE = 'dotted'
    VIEWPORT_PADDING = 5.0
    LABEL_OFFSET = 1

    def __init__(self, window, scenario):
        super().__init__()
        self.window = window
        self.scenario = scenario
        self.display_config = self.window.display_config

        self.dragging_point = None
        self.fig, self.ax_trilat = plt.subplots(figsize=(6, 4))

        self.anchor_plots = []
        self.anchor_scatter = None
        self.circle_pairs = []
        self.tag_estimate_scatter = None

        self.anchor_pair_lines = []
        self.anchor_pair_texts = []
        self.tag_anchor_lines = []
        self.tag_anchor_texts = []
        self.tag_name_texts = []
        self.anchor_name_texts = []
        self.position_error_lines = []

        self.lines_plot = []

        self.border_rectangle_patch = None

        self.sandbox_tag = next((tag for tag in self.scenario.get_tag_list() if tag.name == "SANDBOX_TAG"), None)
        if self.sandbox_tag:
            self.tag_truth_plot = self.ax_trilat.scatter(self.scenario.tag_truth.position()[0], self.scenario.tag_truth.position()[1], c='green', s=self.STATION_DOT_SIZE, picker=True)
            self.tag_truth_plot.set_visible(self.display_config.showTagTruth)
        else:
            self.tag_truth_plot = None
        self.tag_estimate_plots = []
        for _ in self.scenario.get_tag_list():
            plot, = self.ax_trilat.plot([], [], 'rx', markersize=10)
            self.tag_estimate_plots.append(plot)

        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        self.fig.canvas.mpl_connect('resize_event', self._on_resize)

        self.init_artists()


    def update_anchors(self):
        anchor_positions = self.scenario.anchor_positions()

        # Update or create the anchor scatter
        if self.anchor_scatter is None:
            if len(anchor_positions) > 0:
                offsets = np.array(anchor_positions)
                self.anchor_scatter = self.ax_trilat.scatter(offsets[:, 0], offsets[:, 1], c=self.STATION_COLOR, s=self.STATION_DOT_SIZE, picker=True)
            else:
                # create an empty 2D offsets array to avoid matplotlib IndexError
                empty_offsets = np.empty((0, 2))
                self.anchor_scatter = self.ax_trilat.scatter([], [], c=self.STATION_COLOR, s=self.STATION_DOT_SIZE, picker=True)
        else:
            if len(anchor_positions) > 0:
                self.anchor_scatter.set_offsets(np.array(anchor_positions))
            else:
                # matplotlib expects a (N,2) array; provide empty shape to avoid indexing errors
                self.anchor_scatter.set_offsets(np.empty((0, 2)))
        self.anchor_scatter.set_visible(self.display_config.showAnchors)

        # Ensure there are circle pairs for each anchor; create if missing
        if len(self.circle_pairs) < len(anchor_positions):
            for i in range(len(self.circle_pairs), len(anchor_positions)):
                c1 = Circle((0, 0), 0, edgecolor=self.STATION_COLOR, facecolor='none', fill=False, linestyle=self.CIRCLE_LINESTYLE, linewidth=1.0, zorder=1)
                c2 = Circle((0, 0), 0, edgecolor=self.STATION_COLOR, facecolor='none', fill=False, linestyle=self.CIRCLE_LINESTYLE, linewidth=1.0, zorder=1)
                c1.set_visible(False)
                c2.set_visible(False)
                self.ax_trilat.add_patch(c1)
                self.ax_trilat.add_patch(c2)
                self.circle_pairs.append((c1, c2))

        # If there are more circle_pairs than anchors (after removals), hide extras
        for idx, (c1, c2) in enumerate(self.circle_pairs):
            if idx < len(anchor_positions):
                c1.set_visible(True)
                c2.set_visible(True)
                c1.set_center(anchor_positions[idx])
                c2.set_center(anchor_positions[idx])
            else:
                c1.set_visible(False)
                c2.set_visible(False)

        # Keep anchor name texts in sync (hide extras)
        for idx in range(len(anchor_positions), len(self.anchor_name_texts)):
            try:
                self.anchor_name_texts[idx].set_visible(False)
            except Exception:
                pass

    def update_data(self, anchors=False, tags=False, measurements=False):

        anchor_positions = self.scenario.anchor_positions()
        title = self.scenario.name

        tag_positions = self.scenario.tag_positions()
        reference_tag = None
        if self.sandbox_tag is not None:
            reference_tag = self.sandbox_tag
        else:
            tags = self.scenario.get_tag_list()
            if len(tags) > 0:
                reference_tag = tags[0]

        if reference_tag is not None:
            try:
                distances_truth = reference_tag.distances()
            except Exception:
                distances_truth = self.scenario.tag_truth.distances()
        else:
            distances_truth = self.scenario.tag_truth.distances()

        # Update tag estimate scatter offsets
        if self.tag_estimate_scatter is not None:
            if len(tag_positions) > 0:
                self.tag_estimate_scatter.set_offsets(np.array(tag_positions))
            else:
                self.tag_estimate_scatter.set_offsets(np.empty((0, 2)))
            self.tag_estimate_scatter.set_visible(self.display_config.showTags)

        # Update anchor scatter offsets
        if self.anchor_scatter is not None:
            if len(anchor_positions) > 0:
                self.anchor_scatter.set_offsets(np.array(anchor_positions))
            else:
                self.anchor_scatter.set_offsets(np.empty((0, 2)))
            self.anchor_scatter.set_visible(self.display_config.showAnchors)

        if self.scenario.tag_truth:
            self.tag_truth_plot.set_offsets([self.scenario.tag_truth.position()])
            self.tag_truth_plot.set_visible(self.display_config.showTagTruth)

        # Update anchor circles: control visibility and radius explicitly. Use visibility toggling
        if self.display_config.showAnchorCircles:
            for i, (bigger_circle, smaller_circle) in enumerate(self.circle_pairs):
                if i < len(anchor_positions):
                    bigger_circle.set_visible(True)
                    smaller_circle.set_visible(True)
                    bigger_circle.set_center(anchor_positions[i])
                    bigger_circle.set_radius(distances_truth[i] + self.scenario.sigma)
                    smaller_circle.set_center(anchor_positions[i])
                    smaller_circle.set_radius(max(0.0, distances_truth[i] - self.scenario.sigma))
                else:
                    bigger_circle.set_visible(False)
                    smaller_circle.set_visible(False)
        else:
            for (bigger_circle, smaller_circle) in self.circle_pairs:
                bigger_circle.set_visible(False)
                smaller_circle.set_visible(False)

        # Update or create reusable line/text artists for anchor-anchor pairs
        num_anchor_pairs = max(0, len(anchor_positions) * (len(anchor_positions) - 1) // 2)
        # ensure enough line artists
        while len(self.anchor_pair_lines) < num_anchor_pairs:
            l, = self.ax_trilat.plot([], [], 'b--', alpha=0.5)
            self.anchor_pair_lines.append(l)
            t = self.ax_trilat.text(0, 0, '', ha='center', va='center')
            t.set_visible(False)
            self.anchor_pair_texts.append(t)

        pair_idx = 0
        for i in range(len(anchor_positions)):
            for j in range(i + 1, len(anchor_positions)):
                if self.display_config.showBetweenAnchorsLines:
                    xdata = [anchor_positions[i][0], anchor_positions[j][0]]
                    ydata = [anchor_positions[i][1], anchor_positions[j][1]]
                    line = self.anchor_pair_lines[pair_idx]
                    line.set_xdata(xdata)
                    line.set_ydata(ydata)
                    line.set_visible(True)
                else:
                    self.anchor_pair_lines[pair_idx].set_visible(False)

                xm = (anchor_positions[i][0] + anchor_positions[j][0]) / 2
                ym = (anchor_positions[i][1] + anchor_positions[j][1]) / 2
                distance = np.linalg.norm(anchor_positions[i] - anchor_positions[j])

                if self.display_config.showBetweenAnchorsLabels:
                    t = self.anchor_pair_texts[pair_idx]
                    t.set_text(f"{distance:.2f}")
                    t.set_position((xm, ym))
                    t.set_visible(True)
                else:
                    self.anchor_pair_texts[pair_idx].set_visible(False)

                pair_idx += 1

        # Hide any leftover anchor-pair artists that are no longer needed
        for idx in range(pair_idx, len(self.anchor_pair_lines)):
            try:
                self.anchor_pair_lines[idx].set_visible(False)
            except Exception:
                pass
        for idx in range(pair_idx, len(self.anchor_pair_texts)):
            try:
                self.anchor_pair_texts[idx].set_visible(False)
            except Exception:
                pass

        # Update or create reusable tag-anchor line/text artists
        needed_tag_anchor = len(tag_positions) * len(anchor_positions)
        while len(self.tag_anchor_lines) < needed_tag_anchor:
            l, = self.ax_trilat.plot([], [], 'r--', alpha=0.5)
            self.tag_anchor_lines.append(l)
            t = self.ax_trilat.text(0, 0, '', ha='center', va='center')
            t.set_visible(False)
            self.tag_anchor_texts.append(t)

        ta_idx = 0
        for ti, tag_position in enumerate(tag_positions):
            for ai, anchor_position in enumerate(anchor_positions):
                if self.display_config.showTagAnchorLines:
                    xdata = [anchor_position[0], tag_position[0]]
                    ydata = [anchor_position[1], tag_position[1]]
                    line = self.tag_anchor_lines[ta_idx]
                    line.set_xdata(xdata)
                    line.set_ydata(ydata)
                    line.set_visible(True)
                else:
                    self.tag_anchor_lines[ta_idx].set_visible(False)

                if self.display_config.showTagAnchorLabels:
                    xm = (anchor_position[0] + tag_position[0]) / 2
                    ym = (anchor_position[1] + tag_position[1]) / 2
                    distance = np.linalg.norm(anchor_position - tag_position)
                    t = self.tag_anchor_texts[ta_idx]
                    t.set_text(f"{distance:.2f}")
                    t.set_position((xm, ym))
                    t.set_visible(True)
                else:
                    self.tag_anchor_texts[ta_idx].set_visible(False)

                ta_idx += 1

        # Hide any leftover tag-anchor artists that are no longer needed
        for idx in range(ta_idx, len(self.tag_anchor_lines)):
            try:
                self.tag_anchor_lines[idx].set_visible(False)
            except Exception:
                pass
        for idx in range(ta_idx, len(self.tag_anchor_texts)):
            try:
                self.tag_anchor_texts[idx].set_visible(False)
            except Exception:
                pass

        # Update/create tag name texts
        while len(self.tag_name_texts) < len(tag_positions):
            t = self.ax_trilat.text(0, 0, '', ha='center', va='bottom', color='red')
            t.set_visible(False)
            self.tag_name_texts.append(t)

        for i, tag_pos in enumerate(tag_positions):
            x, y = tag_pos
            name = self.scenario.get_tag_list()[i].name
            label_text = self._generate_label_text(name, x, y, show_name=self.display_config.showTagNames, show_coords=self.display_config.showTagCoordinates)
            if label_text:
                t = self.tag_name_texts[i]
                t.set_text(label_text)
                t.set_position((x + self.LABEL_OFFSET, y + self.LABEL_OFFSET))
                t.set_bbox(dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
                t.set_visible(True)
            else:
                self.tag_name_texts[i].set_visible(False)

        # Hide any extra tag name texts beyond current tags
        for idx in range(len(tag_positions), len(self.tag_name_texts)):
            try:
                self.tag_name_texts[idx].set_visible(False)
            except Exception:
                pass

        # Update/create anchor name texts
        while len(self.anchor_name_texts) < len(anchor_positions):
            t = self.ax_trilat.text(0, 0, '', ha='center', va='center')
            t.set_visible(False)
            self.anchor_name_texts.append(t)

        for i in range(len(anchor_positions)):
            x, y = anchor_positions[i]
            name = self.scenario.get_anchor_list()[i].name
            label_text = self._generate_label_text(name, x, y, show_name=self.display_config.showAnchorNames, show_coords=self.display_config.showAnchorCoordinates)
            if label_text:
                t = self.anchor_name_texts[i]
                t.set_text(label_text)
                t.set_position((x + self.LABEL_OFFSET, y + self.LABEL_OFFSET))
                t.set_bbox(dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
                t.set_visible(True)
            else:
                self.anchor_name_texts[i].set_visible(False)

        # Hide any extra anchor name texts beyond current anchors
        for idx in range(len(anchor_positions), len(self.anchor_name_texts)):
            try:
                self.anchor_name_texts[idx].set_visible(False)
            except Exception:
                pass

        # Update position error lines
        while len(self.position_error_lines) < len(tag_positions):
            l, = self.ax_trilat.plot([], [], 'r-', linewidth=2)
            self.position_error_lines.append(l)

        for i, tag_pos in enumerate(tag_positions):
            if self.display_config.showPositionErrorLines and self.scenario.tag_truth:
                truth_pos = self.scenario.tag_truth.position()
                xdata = [truth_pos[0], tag_pos[0]]
                ydata = [truth_pos[1], tag_pos[1]]
                self.position_error_lines[i].set_xdata(xdata)
                self.position_error_lines[i].set_ydata(ydata)
                self.position_error_lines[i].set_visible(True)
            else:
                self.position_error_lines[i].set_visible(False)

        # Hide extras
        for idx in range(len(tag_positions), len(self.position_error_lines)):
            try:
                self.position_error_lines[idx].set_visible(False)
            except Exception:
                pass

        # Ensure trilat plot keeps equal XY scaling (expand X-range if needed)
        try:
            self.update_viewport()
        except Exception:
            pass

        # Update legend
        self.update_legend()

        # Update border rectangle visibility
        if self.border_rectangle_patch:
            self.border_rectangle_patch.set_visible(self.display_config.showBorderRectangle)

    def update_viewport(self):
        """Update the viewport (xlim, ylim) based on all station positions with padding."""
        if self.display_config.useBorderRectangleForViewport and self.scenario.border_rectangle:
            # Use border rectangle for viewport
            rect = self.scenario.border_rectangle
            padding = self.VIEWPORT_PADDING
            xlim = (rect['min_x'] - padding, rect['max_x'] + padding)
            ylim = (rect['min_y'] - padding, rect['max_y'] + padding)
        else:
            # Use extrema of positions
            all_positions = [self.scenario.tag_truth.position()] + list(self.scenario.anchor_positions()) + list(self.scenario.tag_positions())
            if all_positions:
                all_positions = np.array(all_positions)
                min_x, max_x = all_positions[:, 0].min(), all_positions[:, 0].max()
                min_y, max_y = all_positions[:, 1].min(), all_positions[:, 1].max()
                padding = self.VIEWPORT_PADDING
                xlim = (min_x - padding, max_x + padding)
                ylim = (min_y - padding, max_y + padding)
        self.ax_trilat.set_xlim(xlim)
        self.ax_trilat.set_ylim(ylim)
        # Ensure equal aspect ratio to prevent distortion
        self.ax_trilat.set_aspect('equal', adjustable='box')
        self._adjust_trilat_aspect()

    def redraw(self):
        """Trigger a canvas redraw."""
        try:
            self.fig.canvas.draw_idle()
        except Exception:
            # best-effort
            pass

    def init_artists(self):
        # Remove any existing artists from previous scenarios so switching
        # scenarios doesn't leave stale lines/texts/patches on the axes.
        try:
            # remove scatter artists
            if getattr(self, 'anchor_scatter', None) is not None:
                try:
                    self.anchor_scatter.remove()
                except Exception:
                    pass
                self.anchor_scatter = None

            if getattr(self, 'tag_estimate_scatter', None) is not None:
                try:
                    self.tag_estimate_scatter.remove()
                except Exception:
                    pass
                self.tag_estimate_scatter = None

            if getattr(self, 'tag_truth_plot', None) is not None:
                try:
                    self.tag_truth_plot.remove()
                except Exception:
                    pass
                self.tag_truth_plot = None

            # remove line and text artists
            for lst_name in ('anchor_pair_lines', 'anchor_pair_texts', 'tag_anchor_lines', 'tag_anchor_texts', 'tag_name_texts', 'anchor_name_texts', 'position_error_lines'):
                for art in getattr(self, lst_name, []) or []:
                    try:
                        art.remove()
                    except Exception:
                        pass
                setattr(self, lst_name, [])

            # remove circle patches
            for pair in getattr(self, 'circle_pairs', []) or []:
                try:
                    pair[0].remove()
                except Exception:
                    pass
                try:
                    pair[1].remove()
                except Exception:
                    pass
            self.circle_pairs = []

            # remove border rectangle patch
            if getattr(self, 'border_rectangle_patch', None):
                try:
                    self.border_rectangle_patch.remove()
                except Exception:
                    pass
                self.border_rectangle_patch = None
        except Exception:
            # best-effort: ignore any cleanup errors
            pass

        # Create fresh scatter artists (empty) which the rest of the code expects
        if self.anchor_scatter is None:
            self.anchor_scatter = self.ax_trilat.scatter([], [], c=self.STATION_COLOR, s=self.STATION_DOT_SIZE, picker=True)
            self.anchor_scatter.set_visible(self.display_config.showAnchors)

        if self.tag_estimate_scatter is None:
            self.tag_estimate_scatter = self.ax_trilat.scatter([], [], c='red', marker='x')
            self.tag_estimate_scatter.set_visible(self.display_config.showTags)

        try:
            pos = self.scenario.tag_truth.position()
            self.tag_truth_plot = self.ax_trilat.scatter(pos[0], pos[1], c='green', s=self.STATION_DOT_SIZE, picker=True)
            self.tag_truth_plot.set_visible(self.display_config.showTagTruth)
        except Exception:
            self.tag_truth_plot = None

        # Reset internal lists used to store reusable artists
        self.anchor_pair_lines = []
        self.anchor_pair_texts = []
        self.tag_anchor_lines = []
        self.tag_anchor_texts = []
        self.tag_name_texts = []
        self.anchor_name_texts = []
        self.position_error_lines = []

        self.ax_trilat.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

        self.ax_trilat.set_title(self.scenario.name)
        self.ax_trilat.set_xlabel('x (m)')
        self.ax_trilat.set_ylabel('y (m)')

        # Create legend
        legend_elements = []
        if self.display_config.showLegendAnchors and self.anchor_scatter:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.STATION_COLOR, markersize=8, label='Anchors'))
        if self.display_config.showLegendTags and self.tag_estimate_scatter:
            legend_elements.append(plt.Line2D([0], [0], marker='x', color='w', markerfacecolor='red', markersize=8, label='Tags'))
        if self.display_config.showLegendTagTruth and self.tag_truth_plot:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Tag Truth'))
        
        if legend_elements:
            self.ax_trilat.legend(handles=legend_elements, loc='upper right')

        # Create border rectangle if available
        if self.scenario.border_rectangle:
            rect = self.scenario.border_rectangle
            width = rect['max_x'] - rect['min_x']
            height = rect['max_y'] - rect['min_y']
            self.border_rectangle_patch = Rectangle((rect['min_x'], rect['min_y']), width, height,
                                                   edgecolor='black', facecolor='none', linewidth=2, zorder=0)
            self.ax_trilat.add_patch(self.border_rectangle_patch)
            self.border_rectangle_patch.set_visible(self.display_config.showBorderRectangle)
        else:
            self.border_rectangle_patch = None

        self.update_viewport()

        # Trigger a redraw to reflect the cleared/rebuilt artists
        try:
            self.fig.canvas.draw_idle()
        except Exception:
            pass

    def update_legend(self):
        """Update the legend based on current display config."""
        # Remove existing legend
        if self.ax_trilat.get_legend():
            self.ax_trilat.get_legend().remove()
        
        # Create new legend
        legend_elements = []
        if self.display_config.showLegendAnchors and self.anchor_scatter:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.STATION_COLOR, markersize=8, label='Anchors'))
        if self.display_config.showLegendTags and self.tag_estimate_scatter:
            legend_elements.append(plt.Line2D([0], [0], marker='x', color='w', markerfacecolor='red', markersize=8, label='Tags'))
        if self.display_config.showLegendTagTruth and self.tag_truth_plot:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Tag Truth'))
        if self.display_config.showLegendBorder and self.border_rectangle_patch:
            legend_elements.append(plt.Rectangle((0, 0), 1, 1, edgecolor='black', facecolor='none', linewidth=2, label='Border'))
        
        if legend_elements:
            self.ax_trilat.legend(handles=legend_elements, loc='upper right')
        else:
            # Remove legend if no elements
            if self.ax_trilat.get_legend():
                self.ax_trilat.get_legend().remove()

    def _on_resize(self, event):
        """Matplotlib resize event handler: adjust trilat axis so x/y units stay proportional."""
        try:
            self._adjust_trilat_aspect()
            # redraw after adjustment
            self.fig.canvas.draw_idle()
        except Exception:
            pass

    def _adjust_trilat_aspect(self):
        """Adjust the trilat axis x-limits so that one unit in x equals one unit in y on screen.

        Keeps the current y-limits and expands/contracts the x-limits based on the
        pixel aspect ratio of the trilat axis.
        """
        # Get current y-range
        ymin, ymax = self.ax_trilat.get_ylim()
        yrange = ymax - ymin

        # Get axis bounding box in figure pixels
        try:
            fig_w, fig_h = self.fig.canvas.get_width_height()
            bbox = self.ax_trilat.get_position()
            ax_w_px = bbox.width * fig_w
            ax_h_px = bbox.height * fig_h
            if ax_h_px <= 0:
                return
            # Required x-range so that px per unit matches in x and y
            xrange_needed = yrange * (ax_w_px / ax_h_px)

            # Center x around current center
            xmin, xmax = self.ax_trilat.get_xlim()
            xmid = 0.5 * (xmin + xmax)
            new_xmin = xmid - 0.5 * xrange_needed
            new_xmax = xmid + 0.5 * xrange_needed
            self.ax_trilat.set_xlim(new_xmin, new_xmax)
            # Ensure equal aspect so circles look circular
            try:
                self.ax_trilat.set_aspect('equal', adjustable='box')
            except Exception:
                pass
        except Exception:
            # best-effort: ignore errors
            pass

    def add_anchor(self, x, y):
        anchor_name = f"Anchor {len(self.scenario.get_anchor_list()) + 1}"
        self.scenario.stations.append(station.Anchor([x, y], anchor_name))
        self.anchors_changed.emit()

    def remove_anchor(self, index):
        anchor_to_remove = self.scenario.get_anchor_list()[index]
        self.scenario.remove_station(anchor_to_remove)
        self.anchors_changed.emit()

    def on_mouse_press(self, event):
        if event.inaxes is None:
            return

        if event.button == 3 and self.display_config.rightClickAnchors:
            # Check hit on anchor scatter (reused artist)
            if self.anchor_scatter is not None:
                contains, info = self.anchor_scatter.contains(event)
                if contains:
                    inds = info.get('ind', [])
                    if len(inds) > 0:
                        i = int(inds[0])
                        self.remove_anchor(i)
                        return
            # If no anchor hit, add a new one
            self.add_anchor(event.xdata, event.ydata)
            return

        # Check for anchor hit to start dragging
        if self.anchor_scatter is not None:
            contains, info = self.anchor_scatter.contains(event)
            if contains:
                inds = info.get('ind', [])
                if len(inds) > 0:
                    i = int(inds[0])
                    if self.display_config.dragAnchors:
                        self.dragging_point = self.scenario.get_anchor_list()[i]
                    return
        if self.tag_truth_plot:
            contains, _ = self.tag_truth_plot.contains(event)
            if contains:
                self.dragging_point = self.scenario.tag_truth

    def on_mouse_release(self, event):
        if self.dragging_point is not None:
            # Finalize: emit anchors_changed if dragging anchor, tags_changed if dragging tag
            if isinstance(self.dragging_point, station.Anchor):
                self.anchors_changed.emit()
            else:
                self.tags_changed.emit()
        self.dragging_point = None

    def on_mouse_move(self, event):
        if self.dragging_point is None or event.inaxes is None:
            return

        if isinstance(self.dragging_point, station.Anchor):
            x, y = event.xdata, event.ydata
            self.dragging_point.update_position([x, y])
            self.anchors_changed.emit()
        elif self.dragging_point is not None:
            # If dragging tag truth
            x, y = event.xdata, event.ydata
            self.dragging_point.update_position([x, y])
            if self.sandbox_tag:
                self.scenario.generate_measurements(self.sandbox_tag, self.scenario.tag_truth)
            self.tags_changed.emit()

    def request_refresh(self, anchors=False, tags=False, measurements=False):
        """Request a coalesced refresh. Multiple calls within
        _refresh_interval_ms will be merged into a single update.
        """
        self._pending_refresh["anchors"] = self._pending_refresh["anchors"] or anchors
        self._pending_refresh["tags"] = self._pending_refresh["tags"] or tags
        self._pending_refresh["measurements"] = self._pending_refresh["measurements"] or measurements
        if not self._refresh_timer.isActive():
            self._refresh_timer.start(self._refresh_interval_ms)

    def _on_refresh_timer(self):
        flags = self._pending_refresh.copy()
        # reset pending flags
        self._pending_refresh = {"anchors": False, "tags": False, "measurements": False}

        # Emit signals for each changed type
        if flags.get("anchors"):
            self.anchors_changed.emit()
        if flags.get("tags"):
            self.tags_changed.emit()
        if flags.get("measurements"):
            self.measurements_changed.emit()

    def _generate_label_text(self, name, x, y, show_name=False, show_coords=False, scenario_name=None):
        parts = []
        if show_name:
            parts.append(name)
        if show_coords:
            parts.append(f"({x:.2f}, {y:.2f})")
        if scenario_name and (show_name or show_coords):
            parts.append(f"({scenario_name})")
        return "\n".join(parts) if parts else ""