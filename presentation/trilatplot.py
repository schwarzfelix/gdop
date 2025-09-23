import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.gridspec as gridspec

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

    def __init__(self, window, scenario):
        super().__init__()
        self.window = window
        self.scenario = scenario
        self.display_config = self.window.display_config

        self.dragging_point = None

        self.fig = plt.figure(figsize=(6, 4))
        gs = gridspec.GridSpec(1, 2, width_ratios=[4, 1])
        self.ax_trilat = plt.subplot(gs[0])
        self.ax_gdop = plt.subplot(gs[1])

        self.ax_trilat.set_xlim(-15, 15)
        self.ax_trilat.set_ylim(-15, 15)

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

        self.lines_plot = []

        self.sandbox_tag = next((tag for tag in self.scenario.get_tag_list() if tag.name() == "SANDBOX_TAG"), None)
        if self.sandbox_tag:
            self.tag_truth_plot = self.ax_trilat.scatter(self.scenario.tag_truth.position()[0], self.scenario.tag_truth.position()[1], c='green', s=self.STATION_DOT_SIZE, picker=True)
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

        # Update anchor scatter offsets
        if self.anchor_scatter is not None:
            if len(anchor_positions) > 0:
                self.anchor_scatter.set_offsets(np.array(anchor_positions))
            else:
                self.anchor_scatter.set_offsets(np.empty((0, 2)))

        # check if the scenario is a sandbox scenario with tag_truth
        if isinstance(self.scenario, SandboxScenario) and self.scenario.tag_truth:
            self.tag_truth_plot.set_offsets([self.scenario.tag_truth.position()])

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

        # Update GDOP bar chart if visible
        if self.display_config.showGDOP:
            try:
                # Ensure the axis is visible when GDOP is enabled
                try:
                    self.ax_gdop.set_visible(True)
                except Exception:
                    pass
                self.ax_gdop.clear()
                tags = self.scenario.get_tag_list()
                gdop_values = [tag.dilution_of_precision() for tag in tags]
                x_pos = range(len(gdop_values))
                self.ax_gdop.bar(x_pos, gdop_values, color="orange")
                self.ax_gdop.set_ylim(0, 12)
                self.ax_gdop.set_xticks(x_pos)
                self.ax_gdop.set_xticklabels([tag.name() for tag in tags], rotation=90)
                for i, gdop in enumerate(gdop_values):
                    self.ax_gdop.text(i, gdop, f"{gdop:.2f}", ha="center")
            except Exception:
                # best-effort: ignore plotting errors
                pass
        else:
            # When GDOP display is off, hide the GDOP axis so it's not visible
            try:
                self.ax_gdop.clear()
                self.ax_gdop.set_visible(False)
            except Exception:
                pass

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
            if self.display_config.showTagLabels:
                t = self.tag_name_texts[i]
                t.set_text(self.scenario.get_tag_list()[i].name())
                t.set_position((tag_pos[0], tag_pos[1]))
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
            if self.display_config.showAnchorLabels:
                t = self.anchor_name_texts[i]
                t.set_text(self.scenario.get_anchor_list()[i].name())
                t.set_position((anchor_positions[i][0], anchor_positions[i][1]))
                t.set_visible(True)
            else:
                self.anchor_name_texts[i].set_visible(False)

        # Hide any extra anchor name texts beyond current anchors
        for idx in range(len(anchor_positions), len(self.anchor_name_texts)):
            try:
                self.anchor_name_texts[idx].set_visible(False)
            except Exception:
                pass

        # Ensure trilat plot keeps equal XY scaling (expand X-range if needed)
        try:
            self._adjust_trilat_aspect()
        except Exception:
            pass

    def redraw(self):
        """Trigger a canvas redraw."""
        try:
            self.fig.canvas.draw_idle()
        except Exception:
            # best-effort
            pass

    def init_artists(self):

        if self.anchor_scatter is None:
            self.anchor_scatter = self.ax_trilat.scatter([], [], c=self.STATION_COLOR, s=self.STATION_DOT_SIZE, picker=True)

        if self.tag_estimate_scatter is None:
            self.tag_estimate_scatter = self.ax_trilat.scatter([], [], c='red', marker='x')

        self.anchor_pair_lines = []
        self.anchor_pair_texts = []
        self.tag_anchor_lines = []
        self.tag_anchor_texts = []
        self.tag_name_texts = []
        self.anchor_name_texts = []

        if self.display_config.showGDOP:
            self.ax_gdop.set_visible(True)
            self.ax_gdop.clear()
            tags = self.scenario.get_tag_list()
            gdop_values = [tag.dilution_of_precision() for tag in tags]
            x_pos = range(len(gdop_values))
            self.ax_gdop.bar(x_pos, gdop_values, color="orange")
            self.ax_gdop.set_ylim(0, 12)
            self.ax_gdop.set_xticks(x_pos)
            self.ax_gdop.set_xticklabels([tag.name() for tag in tags], rotation=90)
            for i, gdop in enumerate(gdop_values):
                self.ax_gdop.text(i, gdop, f"{gdop:.2f}", ha="center")
        else:
            self.ax_gdop.clear()
            self.ax_gdop.set_visible(False)

        self.ax_trilat.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

        self.ax_trilat.set_title(self.scenario.name)
        self._adjust_trilat_aspect()

        self.fig.canvas.draw_idle()

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