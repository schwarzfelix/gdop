import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.gridspec as gridspec

from PyQt5.QtCore import QTimer

from simulation import station


class TrilatPlot:

    STATION_DOT_SIZE = 100
    STATION_COLOR = 'blue'
    CIRCLE_LINESTYLE = 'dotted'

    def __init__(self, window):
        self.window = window
        self.scenario = self.window.scenario
        self.display_config = self.window.display_config

        self.dragging_point = None

        self.fig = plt.figure(figsize=(6, 4))
        gs = gridspec.GridSpec(1, 2, width_ratios=[4, 1])
        self.ax_trilat = plt.subplot(gs[0])
        self.ax_gdop = plt.subplot(gs[1])

        self.ax_trilat.set_xlim(-15, 15)
        self.ax_trilat.set_ylim(-15, 15)

        self.anchor_plots = []
        # single scatter for anchors (PathCollection) to update offsets efficiently
        self.anchor_scatter = None
        # circle patches, two per anchor
        self.circle_pairs = []
        # single scatter for tag estimates
        self.tag_estimate_scatter = None

        # reusable line and text artist caches
        self.anchor_pair_lines = []
        self.anchor_pair_texts = []
        self.tag_anchor_lines = []
        self.tag_anchor_texts = []
        self.tag_name_texts = []
        self.anchor_name_texts = []
        # fallback list for miscellaneous artists
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

        # A short single-shot timer to coalesce frequent refresh requests
        # (e.g. during dragging or streaming) so we don't redraw the plot
        # on every event. Requests set flags and the timer triggers a single
        # update for the accumulated changes.
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._on_refresh_timer)
        self._refresh_interval_ms = 40  # ~25 FPS refresh cap
        self._pending_refresh = {"anchors": False, "tags": False, "measurements": False}


    def update_anchors(self):
        anchor_positions = self.scenario.anchor_positions()

        # Update or create the anchor scatter
        if self.anchor_scatter is None:
            if len(anchor_positions) > 0:
                offsets = np.array(anchor_positions)
                self.anchor_scatter = self.ax_trilat.scatter(offsets[:, 0], offsets[:, 1], c=self.STATION_COLOR, s=self.STATION_DOT_SIZE, picker=True)
            else:
                self.anchor_scatter = self.ax_trilat.scatter([], [], c=self.STATION_COLOR, s=self.STATION_DOT_SIZE, picker=True)
        else:
            if len(anchor_positions) > 0:
                self.anchor_scatter.set_offsets(np.array(anchor_positions))
            else:
                self.anchor_scatter.set_offsets([])

        # Ensure there are circle pairs for each anchor; create if missing
        if len(self.circle_pairs) < len(anchor_positions):
            for i in range(len(self.circle_pairs), len(anchor_positions)):
                c1 = Circle((0, 0), 0, color=self.STATION_COLOR, fill=False, linestyle=self.CIRCLE_LINESTYLE)
                c2 = Circle((0, 0), 0, color=self.STATION_COLOR, fill=False, linestyle=self.CIRCLE_LINESTYLE)
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

    def update_plot(self):
        anchor_positions = self.scenario.anchor_positions()
        distances_truth = self.scenario.tag_truth.distances(scenario=self.scenario)
        tag_positions = self.scenario.tag_positions()

        # Update tag estimate scatter: use a single scatter for all tags
        if self.tag_estimate_scatter is None:
            if len(tag_positions) > 0:
                arr = np.array(tag_positions)
                self.tag_estimate_scatter = self.ax_trilat.scatter(arr[:, 0], arr[:, 1], c='red', marker='x')
            else:
                self.tag_estimate_scatter = self.ax_trilat.scatter([], [], c='red', marker='x')
        else:
            if len(tag_positions) > 0:
                self.tag_estimate_scatter.set_offsets(np.array(tag_positions))
            else:
                self.tag_estimate_scatter.set_offsets([])

        # Update anchor scatter offsets (if using anchor_scatter)
        if self.anchor_scatter is not None and len(anchor_positions) > 0:
            self.anchor_scatter.set_offsets(np.array(anchor_positions))
        elif self.anchor_scatter is not None:
            self.anchor_scatter.set_offsets([])

        if self.tag_truth_plot:
            self.tag_truth_plot.set_offsets([self.scenario.tag_truth.position()])

        if self.display_config.showAnchorCircles:
            for i, (bigger_circle, smaller_circle) in enumerate(self.circle_pairs):
                if i < len(anchor_positions):
                    bigger_circle.set_center(anchor_positions[i])
                    bigger_circle.set_radius(distances_truth[i] + self.scenario.sigma)
                    smaller_circle.set_center(anchor_positions[i])
                    smaller_circle.set_radius(max(0.0, distances_truth[i] - self.scenario.sigma))
                else:
                    bigger_circle.set_radius(0)
                    smaller_circle.set_radius(0)
        else:
            for (bigger_circle, smaller_circle) in self.circle_pairs:
                bigger_circle.set_radius(0)
                smaller_circle.set_radius(0)

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

        if self.display_config.showGDOP:
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

        self.ax_trilat.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

        self.fig.canvas.draw_idle()

    def add_anchor(self, x, y):
        anchor_name = f"Anchor {len(self.scenario.get_anchor_list()) + 1}"
        self.scenario.stations.append(station.Anchor([x, y], anchor_name))
        # Anchor list changed — request a full UI update (tabs + plot)
        self.window.update_all()

    def remove_anchor(self, index):
        anchor_to_remove = self.scenario.get_anchor_list()[index]
        self.scenario.remove_station(anchor_to_remove)
        self.window.update_all()

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
            # Finalize: full UI update (tabs + plot)
            self.window.update_all()
        self.dragging_point = None

    def on_mouse_move(self, event):
        if self.dragging_point is None or event.inaxes is None:
            return

        if not isinstance(self.dragging_point, station.Anchor):
            return

        x, y = event.xdata, event.ydata
        self.dragging_point.update_position([x, y])
        if self.sandbox_tag:
            self.scenario.generate_measurements(self.sandbox_tag, self.scenario.tag_truth)
        # During dragging, avoid full tab updates on every mouse move —
        # coalesce frequent plot refreshes instead.
        self.request_refresh(tags=True, measurements=True)

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

        # If anchors changed, ensure the anchor artists are rebuilt/updated
        if flags.get("anchors"):
            try:
                self.update_anchors()
            except Exception:
                # best-effort: keep UI responsive even if anchor update fails
                pass

        # Update the rest of the plot (tag estimates, lines, labels, circles)
        try:
            self.update_plot()
        except Exception:
            pass