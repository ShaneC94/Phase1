import csv


def parse_row(line):


    cols = next(csv.reader([line]))

    if len(cols) < 15:
        return None

    try:
        return {
            "vehicle_id": int(cols[0]),
            "frame_id": int(cols[1]),

            # vehicle position
            "local_x": float(cols[4]),
            "local_y": float(cols[5]),

            # motion
            "velocity": float(cols[11]),
            "acceleration": float(cols[12]),

            # lane + nearby vehicles
            "lane_id": int(cols[13]),
            "preceding": int(cols[14]),
        }

    except Exception:
        return None


def remove_invalid(row):

    if row is None:
        return False

    velocity = row["velocity"]
    acceleration = row["acceleration"]

    # filter unrealistic speeds
    if velocity < 0 or velocity > 120:
        return False

    # filter unrealistic acceleration values
    if acceleration < -30 or acceleration > 30:
        return False

    return True


def segment_filter(row):

    y = row["local_y"]

    return 100 <= y <= 500
