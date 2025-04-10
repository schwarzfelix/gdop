import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider

import geometry
import station
import simulation


class GdopPlot:
    def __init__(self, localization: simulation.Simulation, show=True):
        self.localization = localization
        self.dragging_point = None
        self.fire_shots = False

        self.fig = plt.figure(figsize=(6, 4))
        gs = gridspec.GridSpec(1, 3, width_ratios=[4, 1, 1])

        self.ax_main = plt.subplot(gs[0])
        self.ax_main.set_xlim(-5, 15)
        self.ax_main.set_ylim(-5, 15)

        self.anchor_plots = []
        self.circle_plots = []
        self.circle_plots2 = []
        self.lines_plot = []
        self.update_anchors()

        self.tag_truth_plot = self.ax_main.scatter(self.localization.tag_truth.position()[0], self.localization.tag_truth.position()[1], c='green', s=100, picker=True)
        self.tag_estimate_plot, = self.ax_main.plot([], [], 'rx', markersize=10)
        self.shots_plot = self.ax_main.scatter([], [], c='red', s=5, alpha=0.5)

        self.ax_bar = plt.subplot(gs[1])
        ax_settings = plt.subplot(gs[2])

        self.slider = Slider(ax_settings, 'σ', 0, 5, valinit=self.localization.sigma, orientation='vertical')
        self.slider.on_changed(self.update_plot)

        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        self.fig.canvas.manager.set_window_title('Trilateration')
        self.update_plot()

        if show:
            plt.show()

    def update_anchors(self):
        for plot in self.anchor_plots:
            plot.remove()
        for circle in self.circle_plots + self.circle_plots2:
            circle.remove()
        for line in self.lines_plot:
            line.remove()
        
        self.anchor_plots = [self.ax_main.scatter(x, y, c='blue', s=100, picker=True) for x, y in self.localization.anchor_positions()]
        self.circle_plots = [self.ax_main.add_patch(Circle((x, y), 0, color='blue', fill=False, linestyle='dotted')) for x, y in self.localization.anchor_positions()]
        self.circle_plots2 = [self.ax_main.add_patch(Circle((x, y), 0, color='blue', fill=False, linestyle='dotted')) for x, y in self.localization.anchor_positions()]

    def update_plot(self, val=None):
        if val is not None:
            self.localization.sigma = val

        distances = self.localization.euclidean_distances()
        estimate_position = self.localization.tag_estimate.position()
        dop = self.localization.dilution_of_precision()


        self.tag_estimate_plot.set_xdata([estimate_position[0]])
        self.tag_estimate_plot.set_ydata([estimate_position[1]])

        if self.fire_shots:
            shot_positions = [self.localization.tag_estimate.position() + np.random.normal(0, self.localization.sigma, 2) for _ in range(100)]
            self.shots_plot.set_offsets(shot_positions)
        else:
            self.shots_plot.set_offsets(estimate_position)

        for i, plot in enumerate(self.anchor_plots):
            plot.set_offsets([self.localization.anchor_positions()[i]])
        self.tag_truth_plot.set_offsets([self.localization.tag_truth.position()])

        for i, circle in enumerate(self.circle_plots):
            circle.set_center(self.localization.anchor_positions()[i])
            circle.set_radius(distances[i] + self.localization.sigma)

        for i, circle in enumerate(self.circle_plots2):
            circle.set_center(self.localization.anchor_positions()[i])
            circle.set_radius(distances[i] - self.localization.sigma)

        # Entferne vorherige Linien
        for line in self.lines_plot:
            try:
                line.remove()
            except:
                pass
        self.lines_plot = []

        for i in range(len(self.localization.anchor_positions())):
            for j in range(i + 1, len(self.localization.anchor_positions())):
                line, = self.ax_main.plot(
                    [self.localization.anchor_positions()[i][0], self.localization.anchor_positions()[j][0]],
                    [self.localization.anchor_positions()[i][1], self.localization.anchor_positions()[j][1]],
                    'b--', alpha=0.5
                )
                self.lines_plot.append(line)


                xm = (self.localization.anchor_positions()[i][0] + self.localization.anchor_positions()[j][0]) / 2
                ym = (self.localization.anchor_positions()[i][1] + self.localization.anchor_positions()[j][1]) / 2
                distance = np.linalg.norm(self.localization.anchor_positions()[i] - self.localization.anchor_positions()[j])
                t = self.ax_main.text(xm, ym, f"{distance:.2f}", ha='center', va='center')
                self.lines_plot.append(t)

        for anchor_position in self.localization.anchor_positions():
            line, = self.ax_main.plot(
                [anchor_position[0], estimate_position[0]],
                [anchor_position[1], estimate_position[1]],
                'r--', alpha=0.5
            )
            self.lines_plot.append(line)

            xm = (anchor_position[0] + estimate_position[0]) / 2
            ym = (anchor_position[1] + estimate_position[1]) / 2
            distance = np.linalg.norm(anchor_position - estimate_position)
            t = self.ax_main.text(xm, ym, f"{distance:.2f}", ha='center', va='center')
            self.lines_plot.append(t)

        for i in range(len(self.localization.anchors)):
            name = self.ax_main.text(self.localization.anchor_positions()[i][0], self.localization.anchor_positions()[i][1], self.localization.anchors[i].name(), ha='center', va='center')
            self.lines_plot.append(name)

        self.ax_bar.clear()
        self.ax_bar.bar(["DOP"], [dop], color="orange")
        self.ax_bar.set_ylim(0, 12)
        self.ax_bar.set_xticks([0])
        self.ax_bar.set_xticklabels(["DOP"])
        self.ax_bar.set_title("DOP")
        self.ax_bar.text(0, dop, f"{dop:.2f}", ha="center")

        self.fig.canvas.draw_idle()

    def add_anchor(self, x, y):
        anchor_name = f"Anchor {len(self.localization.anchors) + 1}"
        self.localization.anchors.append(station.Anchor([x, y], anchor_name))
        self.update_anchors()
        self.update_plot()

    def remove_anchor(self, index):
        self.localization.anchors.pop(index)
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
                self.dragging_point = ('anchor', i)
                return
        contains, _ = self.tag_truth_plot.contains(event)
        if contains:
            self.dragging_point = ('tag_truth', None)

    def on_mouse_release(self, event):
        if self.dragging_point is not None:
            self.print_angles()
        self.dragging_point = None

    def on_mouse_move(self, event):
        if self.dragging_point is None or event.inaxes is None:
            return
        x, y = event.xdata, event.ydata
        if self.dragging_point[0] == 'anchor' and (self.localization.anchor_positions()[self.dragging_point[1]][0] != x or self.localization.anchor_positions()[self.dragging_point[1]][1] != y):
            self.localization.anchors[self.dragging_point[1]].position()[:] = [x, y]
        elif self.dragging_point[0] == 'tag_truth' and (self.localization.tag_truth.position()[0] != x or self.localization.tag_truth.position()[1] != y):
            self.localization.tag_truth.position()[:] = [x, y]
        else:
            return
        self.localization.update_measurements()
        self.update_plot()

    def on_key_press(self, event):
        if event.key == 'm':
            self.fire_shots = not self.fire_shots
            print(f"Shots: {'On' if self.fire_shots else 'Off'}")
        self.update_plot()

    def print_angles(self):
        #print("---------------------------------")
        #for i in range(len(self.localization.anchor_positions())):
        #    for j in range(i + 1, len(self.localization.anchor_positions())):
        #        angle = geometry.angle_vectors(self.localization.anchor_positions()[i] - self.localization.tag_truth.position(), self.localization.anchor_positions()[j] - self.localization.tag_truth.position())
        #        print(f"Angle between {self.localization.anchors[i].name()} and {self.localization.anchors[j].name()}: {angle:.2f}°")

        angles_text = ""
        for i in range(len(self.localization.anchor_positions())):
            for j in range(i + 1, len(self.localization.anchor_positions())):
                angle = geometry.angle_vectors(self.localization.anchor_positions()[i] - self.localization.tag_truth.position(), self.localization.anchor_positions()[j] - self.localization.tag_truth.position())
                angles_text += f"Angle between {self.localization.anchors[i].name()} and {self.localization.anchors[j].name()}: {angle:.2f}°\n"

        self.window.angle_text.setText(angles_text)