import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

from preprocessing import parse_row, remove_invalid, segment_filter
from scenarios import detect_hard_braking, detect_car_following


schema = """
vehicle_id:INTEGER,
frame_id:INTEGER,
scenario:STRING,
velocity:FLOAT,
acceleration:FLOAT,
lane_id:INTEGER
"""


class ScenarioDetection(beam.DoFn):

    def process(self, row):

        brake = detect_hard_braking(row)
        if brake:
            yield brake

        follow = detect_car_following(row)
        if follow:
            yield follow


def run(argv=None, save_main_session=True):

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
        help="Input CSV file in GCS"
    )

    parser.add_argument(
        "--output_table",
        required=True,
        help="BigQuery output table PROJECT:DATASET.TABLE"
    )

    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(pipeline_args)

    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

    with beam.Pipeline(options=pipeline_options) as p:

        rows = (
            p
            | "Read NGSIM" >> beam.io.ReadFromText(
                known_args.input,
                skip_header_lines=1
            )
            | "Parse Rows" >> beam.Map(parse_row)
            | "Remove Parse Failures" >> beam.Filter(lambda x: x is not None)
            | "Remove Invalid" >> beam.Filter(remove_invalid)
            | "Segment Filter" >> beam.Filter(segment_filter)
        )

        scenarios = (
            rows
            | "Detect Scenarios" >> beam.ParDo(ScenarioDetection())
        )

        formatted = (
            scenarios
            | "Format Output" >> beam.Map(lambda r: {
                "vehicle_id": r["vehicle_id"],
                "frame_id": r["frame_id"],
                "scenario": r["scenario"],
                "velocity": r["velocity"],
                "acceleration": r["acceleration"],
                "lane_id": r["lane_id"]
            })
        )

        formatted | "Write to BigQuery" >> beam.io.WriteToBigQuery(
            known_args.output_table,
            schema=schema,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
        )


if __name__ == "__main__":
    run()
