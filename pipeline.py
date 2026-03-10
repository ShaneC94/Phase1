import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import argparse
from scenarios import generate_scenarios


def parse_csv(line):

    cols = line.split(",")

    # skip malformed rows
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

    except:
        return None


class DetectScenarios(beam.DoFn):

    def process(self, element):

        vehicle_id, rows = element

        rows = sorted(rows, key=lambda r: r["frame_id"])

        scenarios = generate_scenarios(rows)

        for s in scenarios:
            yield s


def run():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output_table", required=True)

    args, beam_args = parser.parse_known_args()

    pipeline_options = PipelineOptions(
        beam_args,
        save_main_session=True
    )

    with beam.Pipeline(options=pipeline_options) as p:

        (
            p
            | "Read CSV" >> beam.io.ReadFromText(args.input, skip_header_lines=1)

            | "Parse CSV" >> beam.Map(parse_csv)

            | "Remove bad rows" >> beam.Filter(lambda x: x is not None)

            | "Key by vehicle" >> beam.Map(lambda x: (x["vehicle_id"], x))

            | "Group by vehicle" >> beam.GroupByKey()

            | "Detect Scenarios" >> beam.ParDo(DetectScenarios())

            | "Write BQ" >> beam.io.WriteToBigQuery(
                args.output_table,
                schema={
                    "fields": [
                        {"name": "ego_vehicle", "type": "INTEGER"},
                        {"name": "start_frame", "type": "INTEGER"},
                        {"name": "end_frame", "type": "INTEGER"},
                        {"name": "scenario_label", "type": "STRING"},
                    ]
                },
                write_disposition="WRITE_APPEND",
                create_disposition="CREATE_IF_NEEDED",
            )
        )


if __name__ == "__main__":
    run()
