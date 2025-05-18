import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.gridspec as gridspec

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

        self.ax_trilat.set_xlim(-5, 15)
        self.ax_trilat.set_ylim(-5, 15)

        self.anchor_plots = []
        self.circle_pairs = []
        self.lines_plot = []

        self.tag_truth_plot = self.ax_trilat.scatter(self.scenario.tag_truth.position()[0], self.scenario.tag_truth.position()[1], c='green', s=self.STATION_DOT_SIZE, picker=True)
        self.tag_estimate_plot, = self.ax_trilat.plot([], [], 'rx', markersize=10)
        self.tag_plots = []

        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        self.update_anchors()
        self.update_plot()


    def update_anchors(self):

        anchor_positions = self.scenario.anchor_positions()

        for plot in self.anchor_plots + self.lines_plot:
            plot.remove()

        for circle_pair in self.circle_pairs:
            circle_pair[0].remove()
            circle_pair[1].remove()
        
        self.anchor_plots = [self.ax_trilat.scatter(x, y, c=self.STATION_COLOR, s=self.STATION_DOT_SIZE, picker=True) for x, y in anchor_positions]

        self.circle_pairs = [
            (
                self.ax_trilat.add_patch(Circle((x, y), 0, color=self.STATION_COLOR, fill=False, linestyle=self.CIRCLE_LINESTYLE)),
                self.ax_trilat.add_patch(Circle((x, y), 0, color=self.STATION_COLOR, fill=False, linestyle=self.CIRCLE_LINESTYLE)),
            )
            for x, y in anchor_positions
        ]

    def update_plot(self):

        anchor_positions = self.scenario.anchor_positions()
        distances_estimate = self.scenario.tag_estimate.distances()
        distances_truth = self.scenario.tag_truth.distances(scenario=self.scenario)
        estimate_position = self.scenario.tag_estimate.position()
        gdop = self.scenario.tag_estimate.dilution_of_precision()
        tags = self.scenario.get_tag_list()

        for i, plot in enumerate(self.tag_plots):
            plot.remove()
        self.tag_plots = [self.ax_trilat.scatter(x, y, c='red', s=self.STATION_DOT_SIZE, picker=True) for x, y in [tag.position() for tag in tags]]

        self.tag_estimate_plot.set_xdata([estimate_position[0]])
        self.tag_estimate_plot.set_ydata([estimate_position[1]])

        for i, plot in enumerate(self.anchor_plots):
            plot.set_offsets([anchor_positions[i]])
        self.tag_truth_plot.set_offsets([self.scenario.tag_truth.position()])

        if self.display_config.showAnchorCircles:
            for i, (bigger_circle, smaller_circle) in enumerate(self.circle_pairs):
                bigger_circle.set_center(anchor_positions[i])
                bigger_circle.set_radius(distances_truth[i] + self.scenario.sigma)

                smaller_circle.set_center(anchor_positions[i])
                smaller_circle.set_radius(distances_truth[i] - self.scenario.sigma)
        else:
            for i, (bigger_circle, smaller_circle) in enumerate(self.circle_pairs):
                bigger_circle.set_radius(0)
                smaller_circle.set_radius(0)

        for line in self.lines_plot:
            try:
                line.remove()
            except:
                pass
        self.lines_plot = []

        for i in range(len(anchor_positions)):
            for j in range(i + 1, len(anchor_positions)):
                if self.display_config.showBetweenAnchorsLines:
                    line, = self.ax_trilat.plot(
                        [anchor_positions[i][0], anchor_positions[j][0]],
                        [anchor_positions[i][1], anchor_positions[j][1]],
                        'b--', alpha=0.5
                    )
                    self.lines_plot.append(line)


                xm = (anchor_positions[i][0] + anchor_positions[j][0]) / 2
                ym = (anchor_positions[i][1] + anchor_positions[j][1]) / 2
                distance = np.linalg.norm(anchor_positions[i] - anchor_positions[j])

                if self.display_config.showBetweenAnchorsLabels:
                    t = self.ax_trilat.text(xm, ym, f"{distance:.2f}", ha='center', va='center')
                    self.lines_plot.append(t)

        for anchor_position in anchor_positions:
            if self.display_config.showTagAnchorLines:
                line, = self.ax_trilat.plot(
                    [anchor_position[0], estimate_position[0]],
                    [anchor_position[1], estimate_position[1]],
                    'r--', alpha=0.5
                )
                self.lines_plot.append(line)

            xm = (anchor_position[0] + estimate_position[0]) / 2
            ym = (anchor_position[1] + estimate_position[1]) / 2
            distance = np.linalg.norm(anchor_position - estimate_position)

            if self.display_config.showTagAnchorLabels:
                t = self.ax_trilat.text(xm, ym, f"{distance:.2f}", ha='center', va='center')
                self.lines_plot.append(t)

        if self.display_config.showAnchorLabels:
            for i in range(len(self.scenario.get_anchor_list())):
                name = self.ax_trilat.text(anchor_positions[i][0], anchor_positions[i][1], self.scenario.get_anchor_list()[i].name(), ha='center', va='center')
                self.lines_plot.append(name)

        self.ax_gdop.clear()
        self.ax_gdop.bar(["GDOP"], [gdop], color="orange")
        self.ax_gdop.set_ylim(0, 12)
        self.ax_gdop.set_xticks([0])
        self.ax_gdop.set_xticklabels(["GDOP"])
        self.ax_gdop.text(0, gdop, f"{gdop:.2f}", ha="center")

        self.ax_trilat.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

        self.fig.canvas.draw_idle()

    def add_anchor(self, x, y):
        anchor_name = f"Anchor {len(self.scenario.get_anchor_list()) + 1}"
        self.scenario.stations.append(station.Anchor([x, y], anchor_name))
        self.update_anchors()
        self.update_plot()

    def remove_anchor(self, index):
        self.scenario.stations.remove(self.scenario.get_anchor_list()[index])
        self.update_anchors()
        self.update_plot()

    def on_mouse_press(self, event):
        if event.inaxes is None:
            return

        if event.button == 3:
            for i, plot in enumerate(self.anchor_plots):
                contains, _ = plot.contains(event)
                if contains:
                    self.remove_anchor(i)
                    return
            self.add_anchor(event.xdata, event.ydata)
            return

        for i, plot in enumerate(self.anchor_plots):
            contains, _ = plot.contains(event)
            if contains:
                self.dragging_point = self.scenario.get_anchor_list()[i]
                return
        contains, _ = self.tag_truth_plot.contains(event)
        if contains:
            self.dragging_point = self.scenario.tag_truth

    def on_mouse_release(self, event):
        if self.dragging_point is not None:
            self.window.update_all()
        self.dragging_point = None

    def on_mouse_move(self, event):
        if self.dragging_point is None or event.inaxes is None:
            return

        if not isinstance(self.dragging_point, station.Anchor):
            return

        x, y = event.xdata, event.ydata
        self.dragging_point.update_position([x, y])
        self.scenario.generate_measurements(self.scenario.tag_estimate, self.scenario.tag_truth)
        self.update_plot()