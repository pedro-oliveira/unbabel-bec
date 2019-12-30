#!/usr/bin/env python

import argparse
from google.cloud import pubsub_v1
import json


def subscribe(project_id, subscription_name):
    """ Receives messages from a Pub/Sub subscription. """
    client = pubsub_v1.SubscriberClient()
    # create a fully qualified identifier in the form of
    # `projects/{project_id}/subscriptions/{subscription_name}`
    subscription_path = client.subscription_path(
        project_id, subscription_name)

    def callback(message):
        json_str = message.data.decode('utf-8')
        json_dict = json.loads(json_str)
        print('Received message {} with ID {}\n'.format(
            json_dict, message.message_id))
        message.ack()

    streaming_pull_future = client.subscribe(subscription_path,
                                             callback=callback)
    print('Subscribed for messages on {} ...\n'.format(subscription_path))

    # calling result() on StreamingPullFuture keeps the main thread from
    # exiting while messages get processed in the callbacks.
    try:
        streaming_pull_future.result()
    except:
        streaming_pull_future.cancel()


def run():
    """ Main entry point, runs the subscriber process. """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('project_id', help='Google Cloud project ID')
    parser.add_argument('subscription_name', help='Pub/Sub subscription name')
    args = parser.parse_args()

    subscribe(args.project_id, args.subscription_name)


if __name__ == '__main__':
    run()
