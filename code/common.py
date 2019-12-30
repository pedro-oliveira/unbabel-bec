import json
import time
from datetime import datetime

import apache_beam as beam


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
