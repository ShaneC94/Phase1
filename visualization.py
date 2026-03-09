import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
import os

os.makedirs("plots", exist_ok=True)

PROJECT_ID = "YOUR_PROJECT_ID"
DATASET = "YOUR_DATASET"
TABLE = "YOUR_TABLE"


def load_scenarios():

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT *
    WHERE scenario IN ('hard_braking','lane_change')
    FROM `{PROJECT_ID}.{DATASET}.{TABLE}`
    """

    df = client.query(query).to_dataframe()

    return df


def load_trajectory():

    df = pd.read_csv("gs://pro-router-485514-f9-ngsim-bucket/trajectories-0805am-0820am.csv")
    
    return df

def plot_lane_change(df):

    plt.figure(figsize=(8,5))

    for vid, group in df.groupby("Vehicle_ID"):

        group = group.sort_values("Frame_ID")

        if (group["Lane_ID"].diff() != 0).any():
            plt.plot(group["Frame_ID"], group["Lane_ID"], alpha=0.6)

    plt.xlabel("Frame")
    plt.ylabel("Lane ID")
    plt.title("Lane Change Scenario")

    plt.tight_layout()
    plt.savefig("plots/lane_change.png")
    plt.close()


def plot_braking(df):

    plt.figure(figsize=(8,5))

    plt.plot(df["frame_id"], df["velocity"])

    plt.xlabel("Frame")
    plt.ylabel("Velocity")
    plt.title("Hard Braking Scenario")

    plt.savefig("plots/braking.png")


def plot_trajectory(df):

    plt.figure(figsize=(10,6))

    plt.scatter(df["Local_X"], df["Local_Y"], s=1)

    plt.xlabel("Local X")
    plt.ylabel("Local Y")
    plt.title("Vehicle Trajectories")

    plt.savefig("plots/trajectory.png")


def main():

    scenarios = load_scenarios()
    trajectory = load_trajectory()

    braking = scenarios[scenarios["scenario"] == "hard_braking"]

    if not braking.empty:
        plot_braking(braking)

    plot_lane_change(trajectory)

    plot_trajectory(trajectory)


if __name__ == "__main__":
    main()
