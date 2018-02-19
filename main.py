#!/usr/bin/env python3

import argparse
import logging as log
import os
import pandas as pd

from distutils.version import LooseVersion
from itertools import islice

from CsvInfoWriter import CsvInfoWriter
from NugetCatalog import NugetCatalog
from NugetRecommender import NugetRecommender

INFOS_FILENAME = 'package_infos.csv'
PAGES_LIMIT = 1

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        help="Print debug information",
        action='store_const', dest='log_level', const=log.DEBUG,
        default=log.WARNING
    )
    return parser.parse_args()

def write_infos_file():
    if not os.path.isfile(INFOS_FILENAME) or os.getenv('REFRESH_PACKAGE_INFOS') == '1':
        catalog = NugetCatalog()
        with CsvInfoWriter(filename=INFOS_FILENAME) as writer:
            writer.write_header()
            for page in islice(catalog.all_pages, PAGES_LIMIT):
                for package in page.packages:
                    writer.write_info(package.info)

def read_infos_file():
    df = pd.read_csv(INFOS_FILENAME, dtype={
        'authors': str,
        'description': str,
        'id': str,
        'is_prerelease': bool,
        'listed': bool,
        'summary': str,
        'tags': str,
        'version': str
    }, na_filter=False)

    # Remove entries with the same id, keeping the one with the highest version
    df = df.drop_duplicates(subset='id', keep='last').reset_index(drop=True)
    return df

def main():
    args = parse_args()
    log.basicConfig(level=args.log_level)

    write_infos_file()
    df = read_infos_file()

    nr = NugetRecommender()
    nr.fit(df)
    recs = nr.predict(top_n=3)

    head = list(recs.items())[:50]
    print('\n'.join(map(str, head)))

if __name__ == '__main__':
    main()
