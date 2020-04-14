# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
from datetime import datetime
import logging.config
import os

from src.bytefm_scraper import ByteFMScraper
from src.common import log


class ArgumentValidator(object):
    """Validators to use for ``argparse`` command line arguments
    """
    @staticmethod
    def valid_path(p):
        if not os.path.exists(p):
            raise argparse.ArgumentTypeError('Invalid path: {}'.format(p))
        return p

    @staticmethod
    def valid_date(d):
        dt = None
        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']:
            try:
                dt = datetime.strptime(d, fmt)
            except ValueError as e:
                raise argparse.ArgumentTypeError(
                    'Invalid date {}: {}'
                    .format(str(d), e)
                )
            return dt


def get_args():
    parser = argparse.ArgumentParser(
        description='Byte FM scraper.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--output-dir',
        type=ArgumentValidator.valid_path,
        required=True,
        help='Directory to write output file.'
    )
    parser.add_argument(
        '--start-date',
        type=ArgumentValidator.valid_date,
        required=True,
        help='Start date. Date format: YYYY-MM-DD.'
    )
    parser.add_argument(
        '--end-date',
        type=ArgumentValidator.valid_date,
        required=True,
        help='End date. Date format: YYYY-MM-DD.'
    )
    parser.add_argument(
        '--radio-show',
        type=str,
        default=None,
        help='Radio show name to crawl.'
    )
    parser.add_argument(
        '--log_level',
        default='INFO',
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
        help=(
            "Set the logging output level. "
        )
    )
    args = parser.parse_args()
    return args


def main(args):
    output_dir = args.output_dir
    start_date = args.start_date
    end_date = args.end_date
    radio_show = args.radio_show

    bytefm_scraper = ByteFMScraper(
        output_dir, start_date, end_date, radio_show)
    bytefm_scraper.run()


if __name__ == '__main__':
    args = get_args()

    logging.getLogger('').setLevel(args.log_level)

    main(args)
