import urllib3
import Score
from urllib.parse import urlparse
from urllib.parse import urlsplit
from urllib.parse import urljoin
from urllib3 import exceptions
from bs4 import BeautifulSoup

# Ignore warnings: when a request is made to an HTTPS URL without certificate verification enabled.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Crawling-through-Web spider.
class SpiderBot:
    def __init__(self):
        self.maxdist = 0                    # maxdist is the maximum depth of the crawling process.
        self.iterator = 0                   # Shows on which iteration we are currently in the crawling process.
        self.visited = []                   # List with visited pages.
        self.http = urllib3.PoolManager()   # To make requests, http://urllib3.readthedocs.io/en/latest/user-guide.html.
        self.index = {}                     # Spider's dictionary of words, page's id and scores.
        self.urls = {}                      # Spider's dictionary of url's.
        self.titles = {}                    # Spider's dictionary of pages' titles.

    # Setter for crawling maxdist.
    def set_maxdist(self, maxdist):
        self.maxdist = maxdist

    def get_index(self):
        return self.index

    def get_urls(self):
        return self.urls

    def get_titles(self):
        return self.titles

    # Add the url to visited URL's list.
    def add_visited(self, url):
        if not self.is_visited(url):
            self.visited.append(url)

    # Check whether URL has already been visited.
    def is_visited(self, url):
        return url in self.visited

    # Check whether URL is absolute.
    @staticmethod
    def is_absolute(url):
        # https://stackoverflow.com/questions/8357098/how-can-i-check-if-a-url-is-absolute-using-python
        # netloc => Network Location Part.
        return bool(urlparse(url).netloc)

    # Get base URL.
    @staticmethod
    def base_url(url):  # MUST BE ABSOLUTE
        parsed_url = urlsplit(url)
        # [0] => URL scheme specifier. Examples os schemes: http, https, mailto, ftp and so on.
        # [1] => netloc, Network Location Part
        return parsed_url[0] + "://" + parsed_url[1]

    # Normalize URL.
    @staticmethod
    def normalize_url(url):
        # https://stackoverflow.com/questions/10893374/python-confusions-with-urljoin
        absolute = urljoin(SpiderBot.base_url(url), url)
        # rstrip to remove the last slash.
        return absolute.rstrip("/")

    # Prints out useful info.
    def print_info(self):
        print("Iteration:", self.iterator)
        print("Indexed pages:", len(self.visited))

    # Will merge all the particular dictionaries from all pages into a unique dictionary.
    def merge_index(self, dictionary):
        for word in dictionary:
            if word not in self.index:
                self.index[word] = dictionary[word]
            else:
                self.index[word].update(dictionary[word])

    # Recursive page parse.
    def parse(self, url, depth=1):
        self.iterator += 1
        self.print_info()
        print("-------------------------------------")
        print("Request:", url)
        print("\tDepth:", depth)
        base_url = self.base_url(url)
        try:
            print("\t\tResponse sent")
            '''
            That's just the way Python has its syntax. Once you exit a try-block because of an exception, 
            there is no way back in.
            https://stackoverflow.com/questions/19522990/python-catch-exception-and-continue-try-block
            '''
            # We request a given url, set timeout to 1.
            response = self.http.request('GET', url, timeout=urllib3.Timeout(connect=1, read=1))
            self.add_visited(url)
            print("\t\tStatus received:", response.status)
            if response.status != 200:  # Status code 200: OK, the request was fulfilled. No response is 204
                return

            # https://stackoverflow.com/questions/23714383/what-are-all-the-possible-values-for-http-content-type-header
            content_type = response.getheader("Content-Type")
            if "text/html" not in content_type:
                print(content_type)
                return

            # BeautifulSoup in action: extract html and calculate the score of the words.
            soup = BeautifulSoup(response.data, "html.parser")
            calc = Score.Score(soup, self.iterator)
            self.merge_index(calc.get_result())  # get_result() returns a dictionary with words with id pages and scores
            self.urls[self.iterator] = url  # Save the urls in a url's dictionary with the iterator (its id number).
            self.titles[self.iterator] = calc.get_title()  # Save the titles in the titles' dictionary.

            # Find the links from the current url to execute DEPTH-FIRST SEARCH.
            for link in soup.find_all("a"):
                href = link.get("href")
                if href is None or link is None:
                    continue
                normalized_url = self.normalize_url(href)
                # If the scheme is the one we need (like mailto, stp...).
                if (urlparse(normalized_url)).scheme not in ["", "http", "https"]:
                    continue
                # If the page has already been visited.
                if self.is_visited(normalized_url):
                    continue
                # If url is of type /../... (not absolute), join with absolute.
                if href[0:1] == "/" and href[1:2] != "/":
                    href = urljoin(base_url, href)
                if self.is_absolute(href):
                    print("\t\t\t Accessing to ", href)
                    if self.is_visited(href):
                        print("\t\t\t but has been already visited.")
                        continue
                    next_depth = depth + 1  # Going deeper...
                    if next_depth <= self.maxdist:
                        self.parse(href, next_depth)  # ... with the new url.
                        print("\t\t\t Going back.")

        # EXCEPTIONS:
        except exceptions.MaxRetryError as e:
            print(e)
        except exceptions.LocationValueError as e:
            print(e)
        except UnicodeEncodeError as e:
            print(e)
        except exceptions.ConnectTimeoutError as e:
            print(e)
        except exceptions.ReadTimeoutError as e:
            print(e)
        except exceptions.ConnectionError as e:
            print(e)
        finally:  # we add the url to the list of visited url's.
            self.add_visited(url)
