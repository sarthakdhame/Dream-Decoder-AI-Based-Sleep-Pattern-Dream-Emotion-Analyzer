import matplotlib.pyplot as plt


def generate_time_taken_chart(output_path: str = "simple_time_analysis.png") -> None:
    """Generate and save a line chart for Dream Decoder pipeline time analysis."""
    steps = [
        "Dream Input",
        "Validation",
        "NLP Processing",
        "AI Interpretation",
        "Insight Generation",
        "Storage",
        "Display",
    ]

    # Time taken per step in seconds.
    time_taken = [2, 1, 3, 5, 2, 1, 1]

    plt.figure(figsize=(10, 5))
    plt.plot(steps, time_taken, marker="o", linewidth=2)

    plt.title("Time Taken")
    plt.xlabel("Dream Decoder Process")
    plt.ylabel("Total Time Taken (sec)")

    for i, value in enumerate(time_taken):
        plt.text(i, value, str(value), ha="center", va="bottom")

    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.show()


if __name__ == "__main__":
    generate_time_taken_chart()
