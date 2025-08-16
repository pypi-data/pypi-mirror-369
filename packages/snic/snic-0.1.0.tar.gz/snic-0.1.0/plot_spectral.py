import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import argparse
from typing import List, Tuple

# Import the Rust-bound function
from snic import stream_matches_from


def generate_colors(n):
    """Generate n visually distinct colors."""
    return plt.cm.viridis(np.linspace(0, 1, n))


def calculate_strides(matchups):
    """Calculate strides for each matchup."""
    return [abs(m[0] - m[1]) for m in matchups]


def categorize_strides(strides, base):
    """Categorize strides into hierarchical levels."""
    max_level = int(np.log2(max(strides))) + 1
    categories = np.zeros(len(strides), dtype=int)
    for i, stride in enumerate(strides):
        categories[i] = max_level - int(np.log2(stride)) - 1
    return categories, max_level


def create_matchup_array(matchups: List[Tuple[int, ...]], network_size: int):
    """Create and return the main matchup array and participation array."""
    matchup_array = np.array(matchups)
    participation_array = np.zeros((network_size, len(matchups)), dtype=bool)
    for i, matchup in enumerate(matchups):
        participation_array[matchup, i] = True
    return matchup_array, participation_array


def plot_snic_spectrum(
    matchups: List[Tuple[int, ...]], network_size: int, match_size: int
):
    """Create the improved SNIC Temporal Matchup Spectrum visualization."""
    matchup_array, participation_array = create_matchup_array(matchups, network_size)

    # Calculate strides and categorize them
    strides = calculate_strides(matchups)
    stride_categories, max_level = categorize_strides(strides, match_size)

    # Create color maps
    element_colors = generate_colors(network_size)
    element_cmap = LinearSegmentedColormap.from_list(
        "element_colors", element_colors, N=network_size
    )
    stride_colors = plt.cm.YlOrRd(np.linspace(0.2, 0.8, max_level))
    stride_cmap = LinearSegmentedColormap.from_list(
        "stride_colors", stride_colors, N=max_level
    )

    # Calculate element frequencies
    frequencies = np.sum(participation_array, axis=1)

    # Create the main figure
    fig = plt.figure(figsize=(20, 15))
    gs = fig.add_gridspec(4, 2, width_ratios=[20, 1], height_ratios=[1, 3, 1, 1])

    # Stride hierarchy visualization
    ax_stride = fig.add_subplot(gs[0, 0])
    stride_img = ax_stride.imshow(
        [stride_categories], aspect="auto", cmap=stride_cmap, interpolation="nearest"
    )
    ax_stride.set_yticks([])
    ax_stride.set_title("Stride Hierarchy")

    # Main spectrum
    ax_spectrum = fig.add_subplot(gs[1, 0], sharex=ax_stride)
    spectrum = ax_spectrum.imshow(
        matchup_array.T, aspect="auto", cmap=element_cmap, interpolation="nearest"
    )
    ax_spectrum.set_title("SNIC Temporal Matchup Spectrum")
    ax_spectrum.set_xlabel("Matchup Index")
    ax_spectrum.set_ylabel("Position in Matchup")

    # Participation tracking
    ax_participation = fig.add_subplot(gs[2, 0], sharex=ax_spectrum)
    ax_participation.imshow(
        participation_array, aspect="auto", cmap="binary", interpolation="nearest"
    )
    ax_participation.set_xlabel("Matchup Index")
    ax_participation.set_ylabel("Element Index")

    # Mark first appearances
    first_appearances = np.argmax(participation_array, axis=1)
    ax_participation.scatter(
        first_appearances, range(network_size), color="red", s=20, marker="o"
    )

    # Stride line plot
    ax_stride_plot = fig.add_subplot(gs[3, 0], sharex=ax_spectrum)
    ax_stride_plot.plot(strides, color="blue", alpha=0.7)
    ax_stride_plot.set_yscale("log")
    ax_stride_plot.set_ylabel("Stride (log scale)")
    ax_stride_plot.set_xlabel("Matchup Index")

    # Colorbars
    cbar_element = plt.colorbar(spectrum, cax=fig.add_subplot(gs[1, 1]))
    cbar_element.set_label("Element Index")

    cbar_stride = plt.colorbar(stride_img, cax=fig.add_subplot(gs[0, 1]))
    cbar_stride.set_label("Stride Level")
    cbar_stride.set_ticks(range(max_level))
    cbar_stride.set_ticklabels([f"2^{max_level-i-1}" for i in range(max_level)])

    # Frequency bar chart
    ax_frequency = fig.add_subplot(gs[2:, 1])
    ax_frequency.barh(range(network_size), frequencies, align="center")
    ax_frequency.set_title("Participation Frequency")
    ax_frequency.set_xlabel("Frequency")

    plt.tight_layout()
    return fig


def main(network_size: int, match_size: int, output_file: str = None):
    """Main function to generate matchups, create and show/save the visualization."""

    # Generate matchups using the Rust-bound function
    matchups = list(stream_matches_from(network_size, match_size))

    fig = plot_snic_spectrum(matchups, network_size, match_size)

    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Visualization saved to {output_file}")
    else:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Visualize SNIC matchups with hierarchical stride"
    )
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
