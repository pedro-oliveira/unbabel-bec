#!/usr/bin/env python

"""
The Streaming workflow of the Backend Engineering Challenge.
"""

from __future__ import absolute_import, division

import argparse
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.options.pipeline_options import StandardOptions

from code import JsonCoder, AddTimestampDoFn

JSON_CODER = JsonCoder()
NR_DECIMALS = 2


def events_aggregation(window_events):
    (client_name, events) = window_events
    duration_lst = [e['duration'] for e in events]
    nr_words_lst = [e['nr_words'] for e in events]
    total_duration = sum(duration_lst)
    total_nr_words = sum(nr_words_lst)
    nr_events = len(events)
    average_delivery_time = total_duration / nr_events
    translation_speed_lst = [w/d for d, w in zip(duration_lst, nr_words_lst)]
    slowest_translation = min(translation_speed_lst)
    return {'client_name': client_name,
            'nr_events': nr_events,
            'total_nr_words': total_nr_words,
            'slowest_translation': round(slowest_translation, NR_DECIMALS),
            'average_delivery_time': round(average_delivery_time, NR_DECIMALS)}


def is_translation_delivered(event):
    return event['event_name'] == 'translation_delivered'


def event_by_client(event):
    client_name = event['client_name']
    return client_name, event


class FormatDoFn(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam,
                timestamp=beam.DoFn.TimestampParam):
        ts_format = '%Y-%m-%d %H:%M:%S'
        # window_start = window.start.to_utc_datetime().strftime(ts_format)
        window_end = window.end.to_utc_datetime().strftime(ts_format)
        # ts_datetime = datetime.utcfromtimestamp(timestamp)
        # ts_str = ts_datetime.strftime(ts_format)
        element['date'] = window_end
        return [element]


def run(argv=None, save_main_session=True):
    """Build and run the pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output_topic', required=True,
        help=('Output PubSub topic of the form '
              '"projects/<PROJECT>/topics/<TOPIC>".'))
    parser.add_argument(
        '--window_size',
        required=False,
        type=int,
        default=600,
        help='Window size (in seconds) to apply to metrics calculations'
    )
    parser.add_argument(
        '--window_period',
        required=False,
        type=int,
        default=60,
        help='Window period (in seconds) to apply to metrics calculations'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--input_topic',
        help=('Input PubSub topic of the form '
              '"projects/<PROJECT>/topics/<TOPIC>".'))
    group.add_argument(
        '--input_subscription',
        help=('Input PubSub subscription of the form '
              '"projects/<PROJECT>/subscriptions/<SUBSCRIPTION>."'))
    known_args, pipeline_args = parser.parse_known_args(argv)

    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    pipeline_options.view_as(StandardOptions).streaming = True
    p = beam.Pipeline(options=pipeline_options)

    # Read from PubSub into a PCollection.
    if known_args.input_subscription:
        messages = p | beam.io.ReadFromPubSub(
            subscription=known_args.input_subscription)

    else:
        messages = p | beam.io.ReadFromPubSub(topic=known_args.input_topic)

    lines = messages | 'Decode' >> beam.Map(lambda x: JSON_CODER.decode(x))

    counts = (lines
              | 'Filter' >> beam.Filter(is_translation_delivered)
              | 'Add timestamp' >> beam.ParDo(AddTimestampDoFn())
              | 'Set key' >> beam.Map(event_by_client)
              | 'SlidingWindow' >> beam.WindowInto(
                beam.window.SlidingWindows(size=known_args.window_size,
                                           period=known_args.window_period))
              | 'Group' >> beam.GroupByKey()
              | 'Aggregate' >> beam.Map(events_aggregation))

    output = (counts
              | 'Format' >> beam.ParDo(FormatDoFn())
              | 'Encode' >> beam.Map(lambda x: JSON_CODER.encode(x))
              .with_output_types(bytes))

    # Write the output using a "Write" transform that has side effects.
    output | beam.io.WriteToPubSub(known_args.output_topic)

    # run the pipeline
    result = p.run()
    result.wait_until_finish()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
