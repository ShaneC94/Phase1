import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery


PROJECT_ID = "pro-router-485514-f9"
DATASET = "ngsim"
TABLE = "scenarios"


def load_data():

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET}.{TABLE}`
    LIMIT 5000
    """

    df = client.query(query).to_dataframe()

    return df


def plot_lane_change(df):

    plt.figure(figsize=(8,5))

    for vid, group in df.groupby("vehicle_id"):
        plt.plot(group["frame_id"], group["lane_id"])

    plt.xlabel("Frame")
    plt.ylabel("Lane ID")
    plt.title("Lane Change Scenario")

    plt.show()


def plot_braking(df):

    plt.figure(figsize=(8,5))

    plt.plot(df["frame_id"], df["velocity"])

    plt.xlabel("Frame")
    plt.ylabel("Velocity")
    plt.title("Hard Braking Scenario")

    plt.show()


def plot_trajectory(df):

    plt.figure(figsize=(10,6))

    plt.scatter(df["local_x"], df["local_y"], s=1)

    plt.xlabel("Local X")
    plt.ylabel("Local Y")
    plt.title("Vehicle Trajectories")

    plt.show()


def main():

    df = load_data()

    braking = df[df["scenario"] == "hard_braking"]
    lane_change = df[df["scenario"] == "lane_change"]

    if not braking.empty:
        plot_braking(braking)

    if not lane_change.empty:
        plot_lane_change(lane_change)

    plot_trajectory(df)


if __name__ == "__main__":
    main()
