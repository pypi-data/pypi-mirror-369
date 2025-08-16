import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import argparse
from itertools import combinations

from snic import stream_matches_from


class SNICVisualizer:
    def __init__(self, network_size, match_size):
        self.network_size = network_size
        self.match_size = match_size
        self.matchups = list(stream_matches_from(network_size, match_size))

        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_aspect("equal")
        self.setup_plot()

    def setup_plot(self):
        self.ax.set_xlim(-1.1, 1.1)
        self.ax.set_ylim(-1.1, 1.1)
        self.ax.axis("off")

        # Plot network elements
        theta = np.linspace(0, 2 * np.pi, self.network_size, endpoint=False)
        self.x = np.cos(theta)
        self.y = np.sin(theta)
        self.ax.scatter(self.x, self.y, c="black", s=10, zorder=3)

        # Setup for matchup arcs
        self.arcs = []

    def draw_arc(self, start, end):
        start_x, start_y = self.x[start], self.y[start]
        end_x, end_y = self.x[end], self.y[end]

        # Calculate the midpoint
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2

        # Calculate the vector from start to end
        dx = end_x - start_x
        dy = end_y - start_y

        # Calculate the distance between points
        distance = np.sqrt(dx**2 + dy**2)

        # Calculate the perpendicular vector
        perp_x = -dy
        perp_y = dx

        # Normalize the perpendicular vector
        length = np.sqrt(perp_x**2 + perp_y**2)
        perp_x /= length
        perp_y /= length

        # Calculate the control point
        # Increase the base curvature and make it less dependent on distance
        base_curvature = 0.1  # Increased base curvature
        distance_factor = 0.7  # Reduced impact of distance
        curvature_factor = base_curvature + distance_factor * distance

        # Move the control point towards the center
        center_pull = 0.3  # Adjust this to pull arcs more towards the center
        ctrl_x = mid_x * (1 - center_pull) + curvature_factor * perp_x
        ctrl_y = mid_y * (1 - center_pull) + curvature_factor * perp_y

        # Ensure the control point stays inside the circle
        ctrl_length = np.sqrt(ctrl_x**2 + ctrl_y**2)
        if ctrl_length > 0.95:  # Slightly reduced to keep arcs inside
            ctrl_x *= 0.95 / ctrl_length
            ctrl_y *= 0.95 / ctrl_length

        # Create the path
        path = Path(
            [(start_x, start_y), (ctrl_x, ctrl_y), (end_x, end_y)],
            [Path.MOVETO, Path.CURVE3, Path.CURVE3],
        )

        patch = PathPatch(
            path,
            facecolor="none",
            edgecolor="black",
            alpha=0.5,
            linewidth=0.5,
            zorder=2,
        )
        self.ax.add_patch(patch)
        return patch

    def animate(self, frame):
        if frame < len(self.matchups):
            matchup = self.matchups[frame]
            for points in combinations(matchup, 2):
                arc = self.draw_arc(*points)
                self.arcs.append(arc)

            # Highlight the most recent matchup
            for arc in self.arcs[-len(matchup) + 1 :]:
                arc.set_alpha(0.8)

        # Fade older arcs
        for arc in self.arcs[: -self.match_size + 1]:
            arc.set_alpha(max(0.1, arc.get_alpha() * 0.99))

        return self.arcs

    def create_animation(self):
        frames = len(self.matchups) + 10
        interval = max(
            20, min(100, 5000 // self.network_size)
        )  # Adjust speed based on network size
        return FuncAnimation(
            self.fig,
            self.animate,
            frames=frames,
            interval=interval,
            blit=True,
            repeat=False,
        )


def main(network_size, match_size, output_file=None):
    visualizer = SNICVisualizer(network_size, match_size)
    anim = visualizer.create_animation()

    plt.title(
        f"SNIC Matchup Visualization\nNetwork Size: {network_size}, Match Size: {match_size}"
    )

    if output_file:
        anim.save(output_file, writer="pillow", fps=30)
        print(f"Animation saved to {output_file}")
    else:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize SNIC matchups")
    parser.add_argument(
        "network_size", type=int, help="Total number of elements in the network"
    )
    parser.add_argument(
        "match_size", type=int, help="Number of elements in each matchup"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (if not provided, display interactively)",
    )

    args = parser.parse_args()

    main(args.network_size, args.match_size, args.output)
