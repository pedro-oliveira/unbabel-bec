#!/usr/bin/env python

import argparse
import pandas as pd
from tabulate import tabulate


def pprint_df(df, title=None, showindex=True):
    """
    Print the specified pandas.DataFrame (df) in a 'pretty' format.

    :param df the pandas.DataFrame to be printed.
    :param title the text to be printed before the df serving as a caption.
    :param showindex optional parameter indicating whether the index of the df
    should be printed or not. By default is set to True.
    """
    if title is not None:
        print(title)
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=showindex))


def run():
    """
    Reads the specified input file into a pandas.DataFrame and sorts the
    DataFrame by timestamp. Assumption that we can load the file contents into
    memory. The input file should be in the jsonlines format, i.e., a JSON
    object per line.
    """

    # parse the input file from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='input_file', help='Input file to sort')
    args = parser.parse_args()

    # read the jsonlines file into a pandas.DataFrame and sort by timestamp
    data = pd.read_json(args.input_file, orient='records', lines=True)
    data_sorted = data.sort_values(by='date')
    pprint_df(data_sorted, showindex=False)


if __name__ == '__main__':
    run()
