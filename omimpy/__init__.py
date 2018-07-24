from bs4 import BeautifulSoup
import urllib2
import re
from lxml import etree, html
import traceback

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

    def read(self, url):
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

    def read_entries(self, entries):
        shallowcopy = [x for x in entries]
        try:
            self.resultSet['entries'] = []
            if len(entries) <= 0:
                raise Exception("Entries should not be None")
            for entry in shallowcopy:
                link_href = entry.get('link_href', None)
                mim_number = entry.get('mim_number', None)
                if not link_href or not mim_number:
                    continue
                full_url = ''.join([OMIM_BASE_URL, link_href])
                entry_details = self.read(full_url)
                obj = self.read_single_entry_page(entry_details)
                if obj is None:
                    continue
                entry.update(obj)
                self.resultSet['entries'].append(entry)

            return self.resultSet


        except Exception as e:
            print (e.message)
            print (traceback.format_exc())
            self.resultSet['entries'] = shallowcopy
            return

    def read_single_entry_page(self, entry_page):
        try:
            if not entry_page:
                return
            gene_phenotype = {}
            main_div = self.find_by_xpath(entry_page,
                                          '//*[@id="content"]/div[contains(@class, "hidden-print")]/div[2]/div[3]')
            if not main_div or len(main_div) <= 0:
                return
            main_div = main_div[0]
            gene_phenotype['omim_type'] = main_div.xpath('div[1]/div[1]/div[2]/span/span/span/strong/text()')[0].strip()

            if main_div.xpath('.//*[@id="textFold"]'):
                text_infos = main_div.xpath('.//*[@id="textFold"]/span/p/text()')
                gene_phenotype['text'] = ''
                for text in text_infos:
                    gene_phenotype['text'] += "{0}\n".format(text.strip())

            # Get Description Fold
            if main_div.xpath('.//*[@id="descriptionFold"]'):
                text_infos = main_div.xpath('.//*[@id="descriptionFold"]/span/p/text()')
                gene_phenotype['description'] = ''
                for text in text_infos:
                    gene_phenotype['description'] += "{0}\n".format(text.strip())

            # Get Cloning Fold
            if main_div.xpath('.//*[@id="cloningFold"]'):
                text_infos = main_div.xpath('.//*[@id="cloningFold"]/span/p/text()')
                gene_phenotype['cloning'] = ''
                for text in text_infos:
                    gene_phenotype['cloning'] += "{0}\n".format(text.strip())

            # Get Gene Function Fold
            if main_div.xpath('.//*[@id="geneFunctionFold"]'):
                text_infos = main_div.xpath('.//*[@id="geneFunctionFold"]/span/p/text()')
                gene_phenotype['functions'] = ''
                for text in text_infos:
                    gene_phenotype['functions'] += "{0}\n".format(text.strip())

            # Get Gene Structure
            if main_div.xpath('.//*[@id="geneStructureFold"]'):
                text_infos = main_div.xpath('.//*[@id="geneStructureFold"]/span/p/text()')
                gene_phenotype['structure'] = ''
                for text in text_infos:
                    gene_phenotype['structure'] += "{0}\n".format(text.strip())

            # Get Mapping
            if main_div.xpath('.//*[@id="mappingFold"]'):
                text_infos = main_div.xpath('.//*[@id="mappingFold"]/span/p/text()')
                gene_phenotype['mapping'] = ''
                for text in text_infos:
                    gene_phenotype['mapping'] += "{0}\n".format(text.strip())

            # Get References
            if main_div.xpath('.//*[@id="referencesFold"]'):
                text_infos = main_div.xpath('.//*[@id="referencesFold"]/span/p/text()')
                gene_phenotype['references'] = ''
                for text in text_infos:
                    gene_phenotype['references'] += "{0}\n".format(text.strip())

            if main_div.xpath('.//table[contains(@class, "small")]'):
                gene_phenotype['relations'] = []
                tr = main_div.xpath('.//table[contains(@class, "small")]/tbody/tr')
                for tb_record in tr:
                    phenotype = {}
                    if len(main_div.xpath('.//table[contains(@class, "small")]')[0].xpath('.//td[@rowspan]')) > 0:
                        phenotype['location'] = main_div.xpath('.//table[contains(@class, "small")]')[0].xpath(
                            './/td[@rowspan]')[0].xpath('span/a/text()')[0].strip()
                    else:
                        phenotype['location'] = tb_record.xpath('td')[0].xpath('span/a/text()').extract_first().strip()
                    if len(tb_record.xpath('.//td[@rowspan]')) > 0:
                        index = 1
                    else:
                        index = 0
                    phenotype['phenotype'] = tb_record.xpath('td')[index].xpath('span/text()')[0].strip()
                    phenotype['pheno_mim'] = tb_record.xpath('td')[(index + 1)].xpath(
                        'span/a/text()')[0].strip() if len(tb_record.xpath('td')[(index + 1)].xpath(
                        'span/a/text()')) > 0 else "N/A"
                    if phenotype['pheno_mim']:
                        phenotype['pheno_mim'] = phenotype['pheno_mim'].strip()
                    else:
                        phenotype['pheno_mim'] = tb_record.xpath('td')[(index + 1)].xpath(
                            'span/a/text()').extract_first().strip()

                    if len(tb_record.xpath('td')[(index + 2)].xpath('span/abbr/text()')) > 0:
                        phenotype['inherit'] = tb_record.xpath('td')[(index + 2)].xpath('span/abbr/text()')[0].strip()
                        if phenotype['inherit']:
                            phenotype['inherit'] = phenotype['inherit'].strip()
                    else:
                        phenotype['inherit'] = 'N/A'
                    phenotype['mapping_key'] = tb_record.xpath('td')[(index + 3)].xpath(
                        'span/abbr/text()')[0].strip()
                    if len(tb_record.xpath('td')) > (index + 4):
                        phenotype['gene_related'] = tb_record.xpath('td')[(index + 4)].xpath(
                            'span/abbr/text()')[0].strip()
                    if len(tb_record.xpath('td')) > (index + 5):
                        phenotype['gene_mim'] = tb_record.xpath('td')[(index + 5)].xpath(
                            'span/abbr/text()')[0].strip()
                    gene_phenotype['relations'].append(phenotype)

            return gene_phenotype



        except Exception as e:
            print  (e.message)
            print (traceback.format_exc())
            return




    def find_by_xpath(self, element_source, xpath_expression):
        root = html.fromstring(element_source)
        return root.xpath(xpath_expression)

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
            if entry.get('mim_number', None) is not None:
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
        contents = self.read(url)
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
                siblings = link.parent.find_all('a', href=re.compile(OMIM_REGEX_GENEMAP_PATTERN))
                if len(siblings) > 0:
                    locus = siblings[0].get_text().strip()
                temp_el = link.parent.find_next('a', target='_blank')
                coordinates = temp_el.get_text().strip() if temp_el is not None else None
                coordinates_link = temp_el.get('href')
                yield {
                    'mim_number': mim_number,
                    'link_text': link_text.replace('*', '').replace('#', '').replace('%', '').replace('$', ''),
                    'link_href': link_href,
                    'locus': locus,
                    'coordinates': coordinates,
                    'coords_link': coordinates_link
                }
