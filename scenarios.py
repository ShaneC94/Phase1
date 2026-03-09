from collections import defaultdict


def detect_hard_braking(row):

    if row["acceleration"] < -10:
        row["scenario"] = "hard_braking"
        return row

    return None


def detect_car_following(row):

    if row["preceding"] != 0:
        row["scenario"] = "car_following"
        return row

    return None


def detect_lane_change(vehicle_records):

    vehicle_records = sorted(vehicle_records, key=lambda x: x["frame_id"])

    lane_changes = []

    previous_lane = vehicle_records[0]["lane_id"]

    for row in vehicle_records:

        if row["lane_id"] != previous_lane:

            row["scenario"] = "lane_change"
            lane_changes.append(row)

        previous_lane = row["lane_id"]

    return lane_changes


def group_by_vehicle(records):

    vehicles = defaultdict(list)

    for r in records:
        vehicles[r["vehicle_id"]].append(r)

    return vehicles