from omimpy import OMIMScrapper
import pprint

scrapper = OMIMScrapper()
results = scrapper.start_search("p53")
scrapper.read_entries(results['entries'][1:2])