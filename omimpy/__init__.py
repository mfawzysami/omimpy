from bs4 import BeautifulSoup
import urllib2

OMIM_BASE_URL = "https://omim.org"
OMIM_SEARCH_PREFIX = "search/"
OMIM_ENTRY_PREFIX = "entry/"


class OMIMScrapper(object):
    def __init__(self):
        pass

    def read(self, url):
        """
        This function reads the given url and return its contents without any further processing
        :param url: The url to read and return its contents
        :return:
        """
        response = urllib2.urlopen(url)
        return None if response is None else response.read()

    def search(self,query):
        """
        This function is the entry point for OMIM Scrapping process , It searches OMIM against the query
        :param query: The query to search against OMIM
        :return: Python dictionary with found information or raises Exception
        """
        pass

    def generate_entries(self,content):
        """
        This function takes Beautiful Soup Object which represents the HTML response of the page that is required to be scrapped in order to generate entries from it.
        :param content: The beautiful soup object
        :return: Python dictionary representation for the corresponding OMIM Gene Entries
        """
        pass
