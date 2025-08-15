import multiprocessing
import random
import re
from typing import List, Union

import pandas as pd
from icecream import ic

from elemental_tools.Jarvis.tools.translation import Translation
from time import sleep
from bs4 import BeautifulSoup
from requests import get

from elemental_tools.file_system.download import search_csv_download_and_load
from elemental_tools.logger import Logger


class ScrapeSelectors:

    class Google:

        description_first: str = """//*[@id="kp-wp-tab-overview"]/div[1]/div/div/div/div/div/div[2]/div/span"""


def _req(term, results, lang, start, proxies, timeout):
    def get_useragent():
        return random.choice(_useragent_list)

    _useragent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'
    ]

    resp = get(
        url="https://www.google.com/search",
        headers={
            "User-Agent": get_useragent()
        },
        params={
            "q": term,
            "num": results + 2,  # Prevents multiple requests
            "hl": lang,
            "start": start,
        },
        proxies=proxies,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def google_search(term, num_results=10, lang="en", proxy=None, advanced=False, sleep_interval=0, timeout=5):
    """Search the Google search engine"""

    escaped_term = term.replace(" ", "+")

    # Proxy
    proxies = None
    if proxy:
        if proxy.startswith("https"):
            proxies = {"https": proxy}
        else:
            proxies = {"http": proxy}

    # Fetch
    start = 0
    while start < num_results:
        # Send request
        resp = _req(escaped_term, num_results - start,
                    lang, start, proxies, timeout)

        # Parse
        soup = BeautifulSoup(resp.text, "html.parser")
        result_block = soup.find_all("div", attrs={"class": "g"})
        for result in result_block:

            # Find link, title, description
            link = result.find("a", href=True)
            title = result.find("h3")
            description_box = result.find(
                "div", {"style": "-webkit-line-clamp:2"})
            if description_box:
                description = description_box.text
                if link and title and description:
                    start += 1

                    if advanced:
                        yield SearchResult(link["href"], title.text, description)
                    else:
                        yield link["href"]
        sleep(sleep_interval)


class WebSearch:
    timeout: int
    content: str = None
    result_limit: int
    language: str
    result: Union[List[SearchResult], list] = []
    debug: bool = True
    _log = Logger(app_name="Elemental-Tools", owner='web-search').log

    def __init__(self, content: str, language: str = 'en', result_limit: int = 25, timeout: int = 10):
        self._log('info', f'Initializing WebSearch', debug=self.debug)

        self.content = content
        self.result_limit = result_limit
        self.timeout = timeout
        self.language = language

        self._search_prefixes = {
            "what_is": "What is ",
            "who_is": "Who is ",
            "how_to": "How to ",
            "csv": "csv with "
        }

        # Translate Search Prefixes to the Desired Language
        if language != self.language:
            self._log('info', f'Translating Search Prefixes', debug=self.debug)

            for p_name, prefix in self._search_prefixes:
                self._search_prefixes[p_name] = Translation(source=self.language, target=language)

            self._log('success', f'Search Prefixes Translated', debug=self.debug)

            self.language = language

        self._log('success', f'WebSearch Initialized!', debug=self.debug)

    def examples(self, ignore: Union[list, None] = None):
        self._log('info', f'Generating Examples of {self.content}', debug=self.debug)

        _s_content = f"{self._search_prefixes['csv']} {self.content}"
        merged_df = None  # Initialize an empty DataFrame for concatenation

        if ignore is None:
            ignore = ['.pdf']

        self._log('info', f'Google Lookup for Datasets...', debug=self.debug)

        g_lookup_links = list(google_search(_s_content, num_results=self.result_limit, advanced=False, timeout=self.timeout))
        g_lookup_result_count = len(g_lookup_links)

        if g_lookup_result_count:
            self._log('success', f'Google Lookup Result Found: {g_lookup_result_count}', debug=self.debug)
        else:
            self._log('alert', f'Google Lookup Result Not Found!')

        for link in g_lookup_links:
            pattern = r'.+?(?:' + '|'.join(ignore) + r')$'
            self._log('info', f'Checking Link: {link}', debug=self.debug)
            if not len(re.findall(pattern, link)):
                #try:
                self._log('info', f'Downloading Content Link: {link}', debug=self.debug)
                csv_df = search_csv_download_and_load(link, self.debug)
                self._log('success', f'Content Downloaded!', debug=self.debug)
                if merged_df is None and csv_df is not None:
                    self._log('info', f'Creating Model Dataframe: {csv_df}', debug=self.debug)
                    merged_df = csv_df
                    self._log('success', f'Model Dataframe Created!', debug=self.debug)
                elif csv_df is not None:
                    self._log('info', f'Merging to Model Dataframe: {csv_df.head()}', debug=self.debug)
                    # Perform a left merge with the existing merged DataFrame
                    merged_df = pd.merge(merged_df, csv_df, how='left', on=list(merged_df.columns),
                                         suffixes=('', '_new'))
                    # Drop duplicate columns
                    merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]
                    self._log('success', f'Model Dataframe Merged!', debug=self.debug)
                #except Exception as e:
                #    self._log('critical-error', f'Model Dataframe Exited With Exception: {str(e)}', debug=self.debug)
                #    pass
            else:
                self._log('alert', f'Irrelevant link: {link}', debug=self.debug)

        # Now merged_df contains the concatenated DataFrame

        return merged_df

    def what_is(self):
        _s_content = f"{self._search_prefixes['what_is']} {self.content}"
        yield google_search(_s_content, num_results=self.result_limit, advanced=True, timeout=self.timeout)

    def who_is(self):
        _s_content = f"{self._search_prefixes['who_is']} {self.content}"
        yield google_search(_s_content, num_results=self.result_limit, advanced=True, timeout=self.timeout)

    def how_to(self):
        _s_content = f"{self._search_prefixes['how_to']} {self.content}"
        yield google_search(_s_content, num_results=self.result_limit, advanced=True, timeout=self.timeout)
