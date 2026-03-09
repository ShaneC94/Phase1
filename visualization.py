import pandas as pd
import matplotlib.pyplot as plt


def plot_lane_change(df):

    plt.figure(figsize=(8,5))

    for vid, group in df.groupby("vehicle_id"):
        plt.plot(group["frame_id"], group["local_x"])

    plt.xlabel("Frame")
    plt.ylabel("Local_X")
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

    df = pd.read_csv("scenario_output.csv")

    braking = df[df["scenario"] == "hard_braking"]

    plot_braking(braking)


if __name__ == "__main__":
    main()