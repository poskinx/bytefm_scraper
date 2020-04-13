from bs4 import BeautifulSoup

class HTMLParser():
    def get_links(self, html_page):
        '''
        For a given html page, parses its content using BeautifulSoup,
        extracts all links and yields them one bye one.
        '''
        soup = BeautifulSoup(html_page, 'html.parser')
        for link in soup.find_all("a"):
            yield link.get('href')


    def get_program_songs(self, html_page):
        """
        Yields data (artist, title, album, label) from songs
        of the program to parse.
        """
        soup = BeautifulSoup(html_page, 'html.parser')
        attrs = {'class': 'show-playlist__song'}
        for data in soup.find_all("td", attrs=attrs):
            try:
                raw_artist = ''.join(data.find('b').previous_siblings)
            except AttributeError as e:
                # Not song data.
                continue
            if not raw_artist:
                # Not song data.
                continue
            try:
                raw_title = data.find('b').text
            except AttributeError as e:
                # Not song data.
                continue
            try:
                raw_text = ''.join(data.find('br').next_siblings)
                raw_album = raw_text.split(' / ')[0]
                raw_label = '|'.join(raw_text.split('/')[1:len(raw_text)])
            except ValueError as e:
                logging.debug(e)
                raw_album = ''.join(data.find('br').next_siblings)
                raw_label = ''
            except AttributeError as e:
                # Album and Label not available.
                raw_album = ''
                raw_label = ''
            data = dict(
                artist=self._cleaner(raw_artist),
                title=self._cleaner(raw_title),
                album=self._cleaner(raw_album),
                label=self._cleaner(raw_label)
            )
            yield data

    def _cleaner(self, text):
        """
        Removes undesired characters from text.
        """
        text = text.replace('/', '')
        text = text.replace('"', '')
        text = text.strip()
        return text
