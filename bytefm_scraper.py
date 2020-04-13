# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
import csv
from datetime import datetime, timedelta
import logging.config
import os
import time

from downloader import Downloader, DownloaderException
from html_parser import HTMLParser


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'propagate': True,
        }
    }
})

log = logging.getLogger('bytefm_scraper')
BASE_URL = 'https://www.byte.fm'


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


def urls_generator(start_date, end_date):
    while start_date <= end_date:
        url = BASE_URL + '/programm/' + start_date.strftime('%Y-%m-%d')
        start_date +=timedelta(days=1)
        yield url


def is_program_link(link):
    if link.count('/') > 3 and 'sendungen' in link:
        return True
    return False


def get_output_writer(output_dir, start_date, end_date, radio_show=None):
    filename = '_'.join(
        ['bytefm', radio_show or '', start_date.strftime('%Y-%m-%d'),
          end_date.strftime('%Y-%m-%d')]
    )
    outfile = os.path.join(output_dir, filename + '.csv')
    header = ["program", "date", "title", "artist", "album", "label"]
    writer = csv.DictWriter(
        open(outfile, 'w'), fieldnames=header, lineterminator='\n')
    writer.writeheader()
    return writer, outfile


def main(args):
    output_dir = args.output_dir
    start_date = args.start_date
    end_date = args.end_date
    radio_show = args.radio_show

    writer, outfile = get_output_writer(output_dir, start_date, end_date,
                                        radio_show)
    html_parser = HTMLParser()
    CustomDownloader = Downloader()
    for url in urls_generator(start_date, end_date):
        log.info('Downloading {url}'.format(url=url))
        start_time = time.time()
        try:
            html_page = CustomDownloader(url)
        except DownloaderException as e:
            log.warning(e)
            continue
        for link in html_parser.get_links(html_page):
            if not is_program_link(link):
                continue
            program = link.split('/')[2]
            date = link.split('/')[3]
            if radio_show and radio_show not in link:
                continue
            sub_url = BASE_URL + link
            try:
                sub_html_page = CustomDownloader(sub_url)
            except DownloaderException as e:
                log.warning(e)
                continue
            for song in html_parser.get_program_songs(sub_html_page):
                song['program'] = program
                song['date'] = date
                writer.writerow(song)
        log.info("Scraped in {} seconds.".format(time.time() - start_time))

    log.info('Out file ready in: {}'.format(outfile))

if __name__ == '__main__':
    args = get_args()

    logging.getLogger('').setLevel(args.log_level)

    main(args)
