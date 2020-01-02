#!/usr/bin/env python

import argparse
from datetime import datetime
import json
import numpy as np
from random import randint
import time
import uuid

from google.cloud import pubsub_v1

# language codes used for generating test sets
languages = ['en', 'pt', 'es', 'fr', 'it']
nr_languages = len(languages)

# translation event names and probabilities
event_names = ['translation_failed', 'translation_canceled',
               'translation_delivered']
event_probabilities = [0.05, 0.05, 0.9]


def generate_evt(client_name, max_nr_words, max_duration):
    """
    Generates a dict with a random translation event for the specified client.
    This can be used to construct test sets, and by 'publisher agents' that
    simulate translation events to be published.

    Notes:
    - source_language and target_language can be the same (but we don't care
    for the purpose of this application).

    :param client_name: the client name requesting the random translation event.
    :param max_nr_words: the maximum number of words that a random
    translation will have. The number of words of the translations will
    range from 1 to max_nr_words.
    :param max_duration: the maximum duration in seconds that a random
    translation will have. The duration of the translations will range from 1 to
    max_duration.
    :return: A dict with a randomly generated translation event.
    """
    evt_datetime = datetime.utcnow()
    evt_dict = {
        'timestamp': evt_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
        'translation_id': str(uuid.uuid4()),
        'source_language': languages[randint(0, nr_languages - 1)],
        'target_language': languages[randint(0, nr_languages - 1)],
        'client_name': client_name,
        'event_name': np.random.choice(event_names, p=event_probabilities),
        'nr_words': randint(1, max_nr_words),
        'duration': randint(1, max_duration)
    }
    return evt_dict


def get_callback(api_future, data):
    """ Wrap message data in the context of the callback function. """
    def callback(api_future):
        try:
            print("Published message {} with ID {}".format(
                data, api_future.result()))
        except Exception:
            print("A problem occurred when publishing {}: {}\n".format(
                data, api_future.exception()))
            raise
    return callback


def publish(project_id, topic_name, message):
    """ Publishes a message to a Pub/Sub topic. """
    client = pubsub_v1.PublisherClient()
    # create a fully qualified identifier in the form of
    # `projects/{project_id}/topics/{topic_name}`
    topic_path = client.topic_path(project_id, topic_name)

    # data sent to Cloud Pub/Sub must be a bytestring
    data = message.encode('utf-8')

    # when you publish a message, the client returns a future
    api_future = client.publish(topic_path, data=data)
    api_future.add_done_callback(get_callback(api_future, data))

    # keep the main thread from exiting while the message future gets resolved
    # in the background.
    while api_future.running():
        time.sleep(0.5)


def run():
    """ Main entry point, runs the publisher process. """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('project_id', help='Google Cloud project ID')
    parser.add_argument('topic_name', help='Pub/Sub topic name')
    parser.add_argument('client_name', help='Client name')
    parser.add_argument('-w',
                        '--max_nr_words',
                        required=False,
                        type=int,
                        default=200,
                        help='Maximum number of words in a translation')
    parser.add_argument('-d',
                        '--max_duration',
                        required=False,
                        type=int,
                        default=60,
                        help='Maximum duration (in seconds) of a translation')
    parser.add_argument('-s',
                        '--max_sleep_time',
                        required=False,
                        type=int,
                        default=180,
                        help='Maximum time (in seconds) between translations')
    args = parser.parse_args()

    print('Started publisher for client {}'.format(args.client_name))
    while True:
        sleep_time = randint(1, args.max_sleep_time)
        print('Waiting {} seconds before generating event.'.format(sleep_time))
        time.sleep(sleep_time)

        # generate random translation event, serialize to JSON str and publish
        event = generate_evt(args.client_name, args.max_nr_words,
                             args.max_duration)
        message = json.dumps(event)
        publish(args.project_id, args.topic_name, message)


if __name__ == '__main__':
    run()
