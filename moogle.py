import pickle
import operator
import SpiderBot


#############################################################################
# Common part
#############################################################################


def authors():
    """Returns a string with the name of the authors of the work."""
    return "Margarita Geleta"


#############################################################################
# Crawler
#############################################################################


def store(db, filename):
    with open(filename, "wb") as f:
        print("store", filename)
        pickle.dump(db, f)
        print("done")


def crawler(url, maxdist):
    spider = SpiderBot.SpiderBot()
    spider.set_maxdist(maxdist) # Set maxdist variable.
    spider.parse(url) # Start crawling.
    return spider.get_urls(), spider.get_titles(), spider.get_index() # Return dictionaries with urls, titles and words.


#############################################################################
# Answer
#############################################################################


def load(filename):
    """Reads an object from file filename and returns it."""
    with open(filename, "rb") as f:
        print("load", filename)
        db = pickle.load(f)
        print("done")
        return db

# The answer function needs a database with words and a query (the word given by user):
def answer(db, query):
    # From the database we extract these 3 fields given in dictionaries.
    """ Remember:  In the SpiderBot class we had...
     self.index = {}                     # Spider's dictionary of words, page's id and scores.
     self.urls = {}                      # Spider's dictionary of url's.
     self.titles = {}                    # Spider's dictionary of pages' titles.
    """
    urls, titles, index = db
    # The query can contain more than one word, therefore we split:
    query_words = query.split(" ")
    query_words_count = len(query_words)  # How many query words.

    accordance_factor = {}
    total_scores = {}
    ac_total_scores = {}

    for query_word in query_words:
        # We take all the pages that contain the query (their id numbers).
        scores = index.get(query_word)
        ################################
        # In case the word is not found in the database.
        if index.get(query_word) is None:
             continue
        ################################
        for page_id in scores:
            '''
            We define an accordance factor: as much words from the query the page does contains, its priority increases 
            according to an accordance factor. 
            '''
            if page_id not in accordance_factor:
                accordance_factor[page_id] = 1
            else:
                accordance_factor[page_id] += 1
            if page_id not in total_scores:
                total_scores[page_id] = scores.get(page_id)
            else:
                total_scores[page_id] += scores.get(page_id)
    for page_id in total_scores:
        ac_total_scores[page_id] = total_scores[page_id] * (accordance_factor[page_id] / query_words_count)
    sorted_scores = sorted(ac_total_scores.items(), key=operator.itemgetter(1))
    sorted_scores.reverse()  # sort the scores.
    result = []  # Now we store the final result.
    for page in sorted_scores:
        ''' The structure of the search result for a given query is as follows:
        [{title1, url1, score1}, {title2, url2, score2}, ... , {titleN, urlN, scoreN}]
        It is a sorted list in order of the priority of the scores.
        '''
        result.append({
            "title": titles[page[0]],
            "url": urls[page[0]],
            "score": round(page[1], 2),
        })

    return result
