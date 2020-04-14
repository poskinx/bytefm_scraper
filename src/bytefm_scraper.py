# -*- coding: utf-8 -*-
import csv
from datetime import timedelta
import os
import time

from common import log
from downloader import Downloader, DownloaderException
from html_parser import HTMLParser
from mongo_cache import MongoCache


class ByteFMScraper():
    def __init__(
            self, output_dir, start_date, end_date, chosen_program=None,
            use_cache=False):
        self.output_dir = output_dir
        self.start_date = start_date
        self.end_date = end_date
        self.chosen_program = chosen_program

        self.base_url = 'https://www.byte.fm'
        self.header = ["program", "date", "title", "artist", "album", "label"]
        self.parser = HTMLParser()
        if use_cache:
            cache = MongoCache()
        else:
            cache = None
        self.Downloader = Downloader(cache=cache)

    def get_songs(self, html_page):
        for link in self.parser.get_links(html_page):
            if not self._is_program_link(link):
                continue
            program = link.split('/')[2]
            date = link.split('/')[3]
            if self.chosen_program and self.chosen_program not in link:
                continue
            sub_url = self.base_url + link
            try:
                sub_html_page = self.Downloader(sub_url)
            except DownloaderException as e:
                log.warning(e)
                continue
            for song in self.parser.get_program_songs(sub_html_page):
                song['program'] = program
                song['date'] = date
                yield song

    def run(self):
        output_file = self._get_output_file_name_path()
        with open(output_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.header,
                                    lineterminator='\n')
            writer.writeheader()
            for url in self._url_generator():
                log.info('Getting data from {url}'.format(url=url))
                start_time = time.time()
                try:
                    html_page = self.Downloader(url)
                except DownloaderException as e:
                    log.warning(e)
                    continue
                for song in self.get_songs(html_page):
                    writer.writerow(song)
                log.info("Done in {} seconds."
                         .format(time.time() - start_time))

        log.info('Out file ready in: {}'.format(output_file))

    def _get_output_file_name_path(self):
        if self.chosen_program:
            filename = '_'.join(['bytefm', self.chosen_program,
                                 self.start_date.strftime('%Y-%m-%d'),
                                 self.end_date.strftime('%Y-%m-%d')])
        else:
            filename = '_'.join(['bytefm',
                                 self.start_date.strftime('%Y-%m-%d'),
                                 self.end_date.strftime('%Y-%m-%d')])

        return os.path.join(self.output_dir, filename + '.csv')

    def _is_program_link(self, link):
        if link.count('/') > 3 and 'sendungen' in link:
            return True
        return False

    def _url_generator(self):
        while self.start_date <= self.end_date:
            url = '/'.join([self.base_url, 'programm',
                            self.start_date.strftime('%Y-%m-%d')])
            self.start_date += timedelta(days=1)
            yield url
