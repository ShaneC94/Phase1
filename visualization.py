import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import os
from google.cloud import bigquery

PROJECT = "<PROJECT_ID>"
DATASET = "ngsim_dataset"
TABLE = "scenarios"

RAW_DATA = "gs://<BUCKET_NAME>/trajectories-0805am-0820am.csv"
LOCAL_FILE = "trajectories.csv"

PLOT_DIR = "plots"
os.makedirs(PLOT_DIR, exist_ok=True)

MAX_FRAME = 4000

plt.style.use("seaborn-v0_8-whitegrid")


def load_scenarios():

    client = bigquery.Client()

    query = f"""
    SELECT * FROM `{PROJECT}.{DATASET}.{TABLE}`
    """

    df = client.query(query).to_dataframe()

    print("Loaded scenarios:", len(df))

    return df


def load_raw():

    if not os.path.exists(LOCAL_FILE):

        print("Downloading raw trajectory data from GCS...")

        subprocess.run([
            "gsutil",
            "cp",
            RAW_DATA,
            LOCAL_FILE
        ], check=True)

    raw = pd.read_csv(LOCAL_FILE, low_memory=False)

    raw = raw.rename(columns={
        "Vehicle_ID": "vehicle_id",
        "Frame_ID": "frame_id",
        "Local_X": "local_x",
        "Local_Y": "local_y",
        "v_Vel": "velocity",
        "Lane_ID": "lane_id",
        "Preceding": "preceding"
    })

    raw = raw[raw["frame_id"] <= MAX_FRAME]

    print("Loaded rows:", len(raw))

    return raw


def plot_trajectories(raw):

    print("Generating trajectory overview...")

    vehicles = raw["vehicle_id"].drop_duplicates().sample(
        min(300, raw["vehicle_id"].nunique()),
        random_state=42
    )

    subset = raw[raw["vehicle_id"].isin(vehicles)]

    plt.figure(figsize=(12,6))

    for vid, group in subset.groupby("vehicle_id"):

        plt.plot(
            group["local_x"],
            group["local_y"],
            linewidth=1,
            alpha=0.4
        )

    lane_width = 12
    min_x = raw["local_x"].min()

    for lane in range(8):

        x = min_x + lane * lane_width

        plt.axvline(
            x=x,
            color="black",
            linestyle="--",
            linewidth=0.8,
            alpha=0.4
        )

    plt.title("Vehicle Trajectories (Sample of Traffic Flow)")
    plt.xlabel("Lateral Position (ft)")
    plt.ylabel("Longitudinal Position (ft)")

    plt.tight_layout()

    plt.savefig(f"{PLOT_DIR}/trajectories.png", dpi=300)

    plt.show()


def plot_lane_changes(raw, scenarios):

    print("Generating lane change visualization...")

    lane = scenarios[scenarios["scenario_label"] == "lane_change"]

    if len(lane) == 0:
        return

    samples = lane.sample(
        min(15, len(lane)),
        random_state=42
    )

    plt.figure(figsize=(10,6))

    for _, row in samples.iterrows():

        data = raw[
            (raw["vehicle_id"] == row["ego_vehicle"]) &
            (raw["frame_id"] >= row["start_frame"]) &
            (raw["frame_id"] <= row["end_frame"])
        ].copy()

        if data.empty:
            continue

        data = data.sort_values("frame_id")

        if data["velocity"].mean() < 5:
            continue

        data["relative_frame"] = data["frame_id"] - data["frame_id"].iloc[0]
        data["time_sec"] = data["relative_frame"] / 10

        lanes = data["lane_id"].values
        times = data["time_sec"].values

        for i in range(1, len(lanes)):

            if lanes[i] != lanes[i-1]:

                color = "blue" if lanes[i] > lanes[i-1] else "orange"

                plt.step(
                    [times[i-1], times[i]],
                    [lanes[i-1], lanes[i]],
                    where="post",
                    linewidth=2,
                    color=color,
                    alpha=0.9
                )

    plt.plot([], [], color="blue", label="Right lane change")
    plt.plot([], [], color="orange", label="Left lane change")

    plt.title("Lane Change Transitions")
    plt.xlabel("Time within Scenario Window (seconds)")
    plt.ylabel("Lane ID")

    plt.yticks(range(1,8))

    plt.legend()

    plt.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()

    plt.savefig(f"{PLOT_DIR}/lane_change.png", dpi=300)

    plt.show()


def plot_braking(raw, scenarios):

    print("Generating hard braking visualization...")

    brake = scenarios[scenarios["scenario_label"] == "hard_braking"]

    if len(brake) == 0:
        return

    samples = brake.sample(
        min(15, len(brake)),
        random_state=42
    )

    plt.figure(figsize=(10,6))

    for _, row in samples.iterrows():

        data = raw[
            (raw["vehicle_id"] == row["ego_vehicle"]) &
            (raw["frame_id"] >= row["start_frame"]) &
            (raw["frame_id"] <= row["end_frame"])
        ].copy()

        if data.empty:
            continue

        data = data.sort_values("frame_id")

        if data["velocity"].mean() < 5:
            continue

        data["relative_frame"] = data["frame_id"] - data["frame_id"].iloc[0]
        data["time_sec"] = data["relative_frame"] / 10

        data["acceleration"] = data["velocity"].diff() / 0.1

        plt.plot(
            data["time_sec"],
            data["velocity"],
            linewidth=1.3,
            alpha=0.8
        )

        hard_brake = data[data["acceleration"] <= -3]

        plt.scatter(
            hard_brake["time_sec"],
            hard_brake["velocity"],
            color="red",
            s=25
        )

    plt.title("Hard Braking Scenarios")
    plt.xlabel("Time within Scenario Window (seconds)")
    plt.ylabel("Velocity (m/s)")

    plt.grid(True, linestyle="--", alpha=0.3)

    plt.tight_layout()

    plt.savefig(f"{PLOT_DIR}/hard_braking.png", dpi=300)

    plt.show()


def plot_following(raw, scenarios):

    print("Generating car-following visualization...")

    follow = scenarios[scenarios["scenario_label"] == "car_following"]

    if len(follow) == 0:
        return

    samples = follow.sample(
        min(15, len(follow)),
        random_state=42
    )

    plt.figure(figsize=(10,6))

    for _, row in samples.iterrows():

        data = raw[
            (raw["vehicle_id"] == row["ego_vehicle"]) &
            (raw["frame_id"] >= row["start_frame"]) &
            (raw["frame_id"] <= row["end_frame"])
        ].copy()

        if data.empty:
            continue

        data = data.sort_values("frame_id")

        if data["velocity"].mean() < 5:
            continue

        data["relative_frame"] = data["frame_id"] - data["frame_id"].iloc[0]
        data["time_sec"] = data["relative_frame"] / 10

        plt.plot(
            data["time_sec"],
            data["velocity"],
            linewidth=1.2,
            alpha=0.7
        )

    plt.title("Car-Following Velocity Profiles")
    plt.xlabel("Time within Scenario Window (seconds)")
    plt.ylabel("Velocity (m/s)")

    plt.grid(True, linestyle="--", alpha=0.3)

    plt.tight_layout()

    plt.savefig(f"{PLOT_DIR}/car_following.png", dpi=300)

    plt.show()


def plot_scenario_distribution(scenarios):

    print("Generating scenario distribution plot...")

    counts = scenarios["scenario_label"].value_counts()

    plt.figure(figsize=(6,4))

    counts.plot(kind="bar")

    plt.title("Scenario Distribution")
    plt.xlabel("Scenario Type")
    plt.ylabel("Count")

    plt.tight_layout()

    plt.savefig(f"{PLOT_DIR}/scenario_distribution.png", dpi=300)

    plt.show()


def main():

    scenarios = load_scenarios()

    raw = load_raw()

    plot_trajectories(raw)

    plot_lane_changes(raw, scenarios)

    plot_braking(raw, scenarios)

    plot_following(raw, scenarios)

    plot_scenario_distribution(scenarios)


if __name__ == "__main__":
    main()

