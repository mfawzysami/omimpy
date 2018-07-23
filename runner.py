from omimpy import OMIMScrapper
import pprint

scrapper = OMIMScrapper()
results = scrapper.start_search("p53",start=2)
print pprint.pprint(results)