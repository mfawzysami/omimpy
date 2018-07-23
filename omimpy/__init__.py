from bs4 import BeautifulSoup
import urllib2
import re

OMIM_BASE_URL = "https://omim.org"
OMIM_SEARCH_PREFIX = "search"
OMIM_ENTRY_PREFIX = "entry"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
OMIM_REGEX_TOTAL_ENTRIES_PATTERN = 'Results: [0-9,]* entries'
OMIM_REGEX_ENTRIES_PATTERN = '^/entry/[0-9]+(\?|\&)([^=]+)\=([^&]+)'
OMIM_REGEX_GENEMAP_PATTERN = "^/geneMap/*"


class OMIMScrapper(object):
    def __init__(self, start=1, limit=20):
        self.start = start
        self.limit = limit
        self.total = limit
        self.resultSet = {}

    def __read(self, url):
        """
        PRIVATE
        This function reads the given url and return its contents without any further processing
        :param url: The url to read and return its contents
        :return:
        """
        request = urllib2.Request(url, headers={
            'User-Agent': USER_AGENT
        })
        opener = urllib2.build_opener()
        response = opener.open(request)
        return None if response is None else response.read()

    def start_search(self, query, start=1, limit=20):
        self.start = start
        self.limit = limit
        contents = self.__search(query)
        if contents is None:
            raise Exception("Unknown Error Occured.")
        return self.get_entries(contents)

    def get_entries(self, contents):
        self.resultSet['entries'] = []
        for entry in self.__generate_entries(contents):
            if entry.get('mim_number',None) is not None:
                self.resultSet['entries'].append(entry)

        self.resultSet['total'] = self.total
        self.resultSet['size'] = len(self.resultSet['entries'])
        return self.resultSet

    def __search(self, query):
        """
        PRIVATE
        This function is the entry point for OMIM Scrapping process , It searches OMIM against the query
        :param query: The query to search against OMIM
        :return: Python dictionary with found information or raises Exception
        https://omim.org/search/?index=entry&sort=score+desc%2C+prefix_sort+desc&start=1&limit=20&search=p53
        """
        query_path = "?index=entry&sort=score+desc%2C+prefix_sort+desc&start={start}&limit={limit}&search={query}".format(
            start=self.start, limit=self.limit, query=query)
        url = "/".join([OMIM_BASE_URL, OMIM_SEARCH_PREFIX, query_path])
        contents = self.__read(url)
        if contents is None:
            raise Exception("No Response has been Received.")
        bs = BeautifulSoup(contents, 'html.parser')
        return bs

    def __generate_entries(self, content):
        """
        PRIVATE
        This function takes Beautiful Soup Object which represents the HTML response of the page that is required to be scrapped in order to generate entries from it.
        :param content: The beautiful soup object
        :return: A Tuple (MIM Number , Link Text , Link href)
        """
        if not isinstance(content, BeautifulSoup):
            raise Exception(
                "Content Parameter to Function generate_entries should be a BeautifulSoup Object. Aborting.")
        # First get the total number of resultSet returned
        rs = content.find_all('div', text=re.compile(OMIM_REGEX_TOTAL_ENTRIES_PATTERN))
        if len(rs) <= 0:
            self.total = 0
        elif len(rs) > 0:
            entries_count_txt = rs[0].get_text().strip()
            entries_count_txt = entries_count_txt.replace('Results:', '')
            entries_count_txt = entries_count_txt.replace('entries', '')
            entries_count_txt = entries_count_txt.replace(' ', '')
            entries_count_txt = entries_count_txt.replace('.', '')
            entries_count_txt = entries_count_txt.replace(',', '')
            self.total = int(entries_count_txt) or 0
        links = content.find_all('a', href=re.compile(OMIM_REGEX_ENTRIES_PATTERN))
        if len(links) <= 0:
            yield None
        else:
            for link in links:
                link_text = ''.join([x for x in link.get_text(strip=['\t', '\n', '*', '%'])])
                link_href = link.get('href')
                mim_number = None
                mim_matches = re.findall('[0-9]+', link_href)
                if len(mim_matches) > 0:
                    mim_number = mim_matches[0] or None
                locus = None
                siblings = link.parent.find_all('a',href=re.compile(OMIM_REGEX_GENEMAP_PATTERN))
                if len(siblings) > 0:
                    locus = siblings[0].get_text().strip()
                temp_el = link.parent.find_next('a',target='_blank')
                coordinates = temp_el.get_text().strip() if temp_el is not None else None
                coordinates_link = temp_el.get('href')
                yield {
                    'mim_number' : mim_number,
                    'link_text' : link_text.replace('*','').replace('#','').replace('%','').replace('$',''),
                    'link_href' : link_href,
                    'locus' : locus,
                    'coordinates' : coordinates,
                    'coords_link' : coordinates_link
                }
