from bs4 import BeautifulSoup
import urllib2

OMIM_BASE_URL = "https://omim.org"
OMIM_SEARCH_PREFIX = "search"
OMIM_ENTRY_PREFIX = "entry"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"


class OMIMScrapper(object):

    def __init__(self,start=1,limit=20):
        self.start = start
        self.limit = limit

    def read(self, url):
        """
        This function reads the given url and return its contents without any further processing
        :param url: The url to read and return its contents
        :return:
        """
        request = urllib2.Request(url,headers={
            'User-Agent' : USER_AGENT
        })
        opener = urllib2.build_opener()
        response = opener.open(request)
        return None if response is None else response.read()

    def search(self,query):
        """
        This function is the entry point for OMIM Scrapping process , It searches OMIM against the query
        :param query: The query to search against OMIM
        :return: Python dictionary with found information or raises Exception
        https://omim.org/search/?index=entry&sort=score+desc%2C+prefix_sort+desc&start=1&limit=20&search=p53
        """
        query_path = "?index=entry&sort=score+desc%2C+prefix_sort+desc&start={start}&limit={limit}&search={query}".format(start=self.start,limit=self.limit,query=query)
        url = "/".join([OMIM_BASE_URL,OMIM_SEARCH_PREFIX,query_path])
        contents = self.read(url)
        if contents is None:
            raise Exception("No Response has been Received.")
        bs = BeautifulSoup(contents,'html.parser')
        return bs



    def generate_entries(self,content):
        """
        This function takes Beautiful Soup Object which represents the HTML response of the page that is required to be scrapped in order to generate entries from it.
        :param content: The beautiful soup object
        :return: Python dictionary representation for the corresponding OMIM Gene Entries
        """
        pass
