from omimpy import OMIMScrapper
from pprint import pprint

scrapper = OMIMScrapper()
results = scrapper.start_search("p53")
#pprint(results,indent=4)
scrapper.read_entries(results['entries'][1:2])