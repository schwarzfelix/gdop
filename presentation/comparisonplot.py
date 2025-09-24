import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from PyQt5.QtCore import pyqtSignal, QObject, QTimer

from simulation import SandboxScenario


class ComparisonPlot(QObject):
    anchors_changed = pyqtSignal()
    tags_changed = pyqtSignal()
    measurements_changed = pyqtSignal()

    def __init__(self, window, app_scenarios):
        super().__init__()
        self.window = window
        self.scenarios = app_scenarios
        self.display_config = self.window.display_config

        # simple figure with two subplots: left = per-scenario metric bars, right = overlay scatter of tag estimates
        self.fig = plt.figure(figsize=(6, 4))
        gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
        self.ax_metrics = plt.subplot(gs[0])
        self.ax_compare = plt.subplot(gs[1])

        # internal artists
        self.metric_bars = None
        self.compare_scatters = []  # one scatter per scenario

        # Refresh coalescing like TrilatPlot
        self._refresh_interval_ms = 80
        self._pending_refresh = {"anchors": False, "tags": False, "measurements": False}
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._on_refresh_timer)

        self.init_artists()

    def init_artists(self):
        # clear axes
        try:
            self.ax_metrics.clear()
            self.ax_compare.clear()
        except Exception:
            pass

        # create empty bars
        self.metric_bars = self.ax_metrics.bar([], [])
        self.ax_metrics.set_title('Scenario metrics')
        self.ax_metrics.set_ylabel('Mean error')

        # create empty scatter for each scenario
        self.compare_scatters = []
        for _ in self.scenarios:
            sc = self.ax_compare.scatter([], [], alpha=0.7)
            self.compare_scatters.append(sc)

        self.ax_compare.set_title('Tag estimates overlay')
        self.ax_compare.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

        try:
            self.fig.canvas.draw_idle()
        except Exception:
            pass

    def update_anchors(self):
        # comparison plot doesn't show anchors explicitly, but keep API consistent
        pass

    def update_data(self, anchors=False, tags=False, measurements=False):
        # Compute a simple per-scenario metric: mean distance error between tag_estimate and tag_truth (where available)
        scenario_names = [s.name for s in self.scenarios]
        mean_errors = []
        for s in self.scenarios:
            errs = []
            tags = s.get_tag_list()
            # if sandbox scenario, compare tag_truth to sandbox tag
            for tag in tags:
                try:
                    est_pos = tag.estimate_position()
                    # find a truth position if sandbox
                    if isinstance(s, SandboxScenario) and getattr(s, 'tag_truth', None):
                        truth = s.tag_truth.position()
                        errs.append(np.linalg.norm(np.array(est_pos) - np.array(truth)))
                except Exception:
                    pass
            if len(errs) > 0:
                mean_errors.append(float(np.mean(errs)))
            else:
                mean_errors.append(0.0)

        # update metrics bar chart
        try:
            self.ax_metrics.clear()
            x_pos = range(len(scenario_names))
            self.ax_metrics.bar(x_pos, mean_errors, color='C2')
            self.ax_metrics.set_xticks(x_pos)
            self.ax_metrics.set_xticklabels(scenario_names, rotation=90)
            self.ax_metrics.set_ylim(0, max(1.0, max(mean_errors) * 1.2 if len(mean_errors) > 0 else 1.0))
            for i, v in enumerate(mean_errors):
                self.ax_metrics.text(i, v, f"{v:.2f}", ha='center', va='bottom')
        except Exception:
            pass

        # update compare scatter: for each scenario, plot tag estimates
        try:
            self.ax_compare.clear()
            for si, s in enumerate(self.scenarios):
                tag_positions = []
                for tag in s.get_tag_list():
                    try:
                        pos = tag.estimate_position()
                        tag_positions.append(pos)
                    except Exception:
                        pass
                if len(tag_positions) > 0:
                    arr = np.array(tag_positions)
                    self.ax_compare.scatter(arr[:, 0], arr[:, 1], alpha=0.7, label=s.name)
            self.ax_compare.legend(loc='best', fontsize='small')
            self.ax_compare.set_aspect('equal', adjustable='box')
        except Exception:
            pass

    def redraw(self):
        try:
            self.fig.canvas.draw_idle()
        except Exception:
            pass

    def request_refresh(self, anchors=False, tags=False, measurements=False):
        self._pending_refresh["anchors"] = self._pending_refresh["anchors"] or anchors
        self._pending_refresh["tags"] = self._pending_refresh["tags"] or tags
        self._pending_refresh["measurements"] = self._pending_refresh["measurements"] or measurements
        if not self._refresh_timer.isActive():
            self._refresh_timer.start(self._refresh_interval_ms)

    def _on_refresh_timer(self):
        flags = self._pending_refresh.copy()
        self._pending_refresh = {"anchors": False, "tags": False, "measurements": False}
        if flags.get('anchors'):
            self.anchors_changed.emit()
        if flags.get('tags'):
            self.tags_changed.emit()
        if flags.get('measurements'):
            self.measurements_changed.emit()
