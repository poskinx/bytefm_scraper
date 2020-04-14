import random
import time

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from fake_useragent import UserAgent

from common import log


class DownloaderException(Exception):
        pass


class Downloader():
    def __init__(
            self, retries=3, backoff_factor=0.5,
            status_forcelist=(500, 502, 504), cache=None, proxies=None):
        session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        self.proxies = proxies
        self._session = session
        self.cache = cache

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                # url is not available in cache
                pass
            else:
                if self.num_retries > 0 and 500 <= result['code'] < 600:
                    # Server error so ignore result from cache and re-download.
                    result = None
        if result is None:
            # Result was not loaded from cache so still need to download.
            result = self.download(url)
            if self.cache:
                # save result to cache
                self.cache[url] = result
        return result['html']

    def download(self, url):
        # Get random user-agent for each http request
        self._session.headers.update({'User-Agent': UserAgent().random})
        if self.proxies:
            proxy = random.choice(self.proxies)
            proxyDict = dict(https=proxy, http=proxy)
            self._session.headers.update(proxies=proxyDict)
        log.debug('Delaying request between 0 and 9 seconds ...')
        time.sleep(random.randint(0, 9))  # avoid crashing the server
        try:
            response = self._session.get(url)
        except requests.exceptions.ConnectionError as e:
            raise DownloaderException(e)
        return {'html': response.content, 'code': response.status_code}
