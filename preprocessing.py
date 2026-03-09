import csv

def parse_row(line):

    cols = next(csv.reader([line]))

    if len(cols) < 15:
        return None

    try:
        return {
            "vehicle_id": int(cols[0]),
            "frame_id": int(cols[1]),
            "local_x": float(cols[4]),
            "local_y": float(cols[5]),
            "velocity": float(cols[11]),
            "acceleration": float(cols[12]),
            "lane_id": int(cols[13]),
            "preceding": int(cols[14]),
        }

    except ValueError:
        return None
    
def remove_invalid(row):
    if row is None:
        return False

    if row["velocity"] < 0 or row["velocity"] > 120:
        return False
        
    if row["acceleration"] < -30 or row["acceleration"] > 30:
        return False
            
    return True
    
def segment_filter(row):
    return 100 <= row["local_y"] <= 500
    
    
