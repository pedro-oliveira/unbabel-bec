#!/usr/bin/env python

"""
The Batch workflow of the Backend Engineering Challenge.
"""

from __future__ import absolute_import, division

import argparse
from datetime import datetime
import logging

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

# from code import JsonCoder, AddTimestampDoFn
import json
import time


class JsonCoder(object):
    """A JSON coder interpreting each line as a JSON string. """

    def encode(self, x):
        json_obj = json.dumps(x)
        encoded_json = json_obj.encode('utf-8')
        return encoded_json

    def decode(self, x):
        json_obj = x.decode('utf-8')
        d = json.loads(json_obj)
        return d


class AddTimestampDoFn(beam.DoFn):
    """
    This DoFn subclass adds the TimestampedValue to each element based on the
    'timestamp' field that exists within each element.
    """

    def process(self, element):
        """
        Sets this element's TimestampedValue with the respective timestamp value
        included in the element.

        :param element: the PCollection element to add the TimestampdValued.
        :return: the TimestampedValued associated with this element.
        """
        # get the timestamp from this element's timestamp information
        ts_format = '%Y-%m-%d %H:%M:%S.%f'
        evt_ts_str = element['timestamp']
        evt_datetime = datetime.strptime(evt_ts_str, ts_format)
        # datetime.timestamp() only from py3.3 onwards
        evt_ts = time.mktime(evt_datetime.timetuple())
        # set the current element with the specified TimestampedValue
        yield beam.window.TimestampedValue(element, evt_ts)


def events_aggregation(window_events):
    (key, events) = window_events
    duration_lst = [e['duration'] for e in events]
    total_duration = sum(duration_lst)
    nr_events = len(events)
    avg_duration = total_duration/nr_events
    return key, total_duration, nr_events, avg_duration


class FormatDoFn(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam,
                timestamp=beam.DoFn.TimestampParam):
        ts_format = '%Y-%m-%d %H:%M:%S'
        window_end = window.end.to_utc_datetime().strftime(ts_format)
        key, total_duration, nr_events, avg_duration = element
        return [{'date': window_end,
                 'total_duration': total_duration,
                 'nr_events': nr_events,
                 'average_delivery_time': avg_duration}]


def run(argv=None, save_main_session=True):
    """Main entry point; defines and runs the BEC pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_file',
        default='gs://unbabel-bec/events.jsonl',
        help='Input file to process.'
    )
    parser.add_argument(
        '--output_file',
        required=True,
        help='Output file to write results to.'
    )
    parser.add_argument(
        '--window_size',
        required=False,
        type=int,
        default=600,
        help='Window size (in seconds) to apply to metrics calculations.'
    )
    parser.add_argument(
        '--window_period',
        required=False,
        type=int,
        default=60,
        help='Window period (in seconds) to apply to metrics calculations.'
    )
    known_args, pipeline_args = parser.parse_known_args(argv)

    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    p = beam.Pipeline(options=pipeline_options)

    # Read the text file[pattern] into a PCollection.
    lines = p | 'read' >> ReadFromText(known_args.input_file, coder=JsonCoder())

    counts = (lines
              | 'Add timestamp' >> beam.ParDo(AddTimestampDoFn())
              | 'Add dummy key' >> beam.Map(lambda x: (None, x))
              | 'SlidingWindow' >> beam.WindowInto(
                beam.window.SlidingWindows(size=known_args.window_size,
                                           period=known_args.window_period))
              | 'Group' >> beam.GroupByKey()
              | 'Aggregate' >> beam.Map(events_aggregation))

    output = counts | 'Format' >> beam.ParDo(FormatDoFn())

    # Write the output using a "Write" transform that has side effects.
    output | 'write' >> WriteToText(known_args.output_file, coder=JsonCoder())

    # run the pipeline
    result = p.run()
    result.wait_until_finish()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
