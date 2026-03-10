import numpy as np

WINDOW_SIZE = 50  # ~5 seconds (NGSIM = 10Hz)


def detect_scenario(window):

    velocities = [r["velocity"] for r in window]

    if len(velocities) > 1:

        accel = np.diff(velocities) / 0.1

        strong_brake_frames = np.sum(accel < -4)

        velocity_drop = velocities[0] - velocities[-1]

        if strong_brake_frames >= 3 and velocity_drop > 5:
            return "hard_braking"

    # lane change
    lane_ids = [r["lane_id"] for r in window]

    if len(set(lane_ids)) > 1:
        return "lane_change"

    # car following
    lead = window[0].get("preceding", 0)

    if lead > 0:

        if len(set(lane_ids)) == 1:

            if np.std(velocities) < 2:
                return "car_following"

    return "normal_driving"


def generate_scenarios(vehicle_rows):

    scenarios = []

    if len(vehicle_rows) < WINDOW_SIZE:
        return scenarios

    for start in range(0, len(vehicle_rows) - WINDOW_SIZE, WINDOW_SIZE):

        window = vehicle_rows[start:start + WINDOW_SIZE]

        label = detect_scenario(window)

        scenarios.append({
            "ego_vehicle": window[0]["vehicle_id"],
            "start_frame": window[0]["frame_id"],
            "end_frame": window[-1]["frame_id"],
            "scenario_label": label
        })

    return scenarios
