import util


# Class which calculates each word's relevance score relatively to its location on the page.
class Score(object):
    # Scores by relevance:
    CONST_TITLE_POINTS = 18  # Found in title.

    CONST_DESCRIPTION_POINTS = 12  # Found in description.

    CONST_H1_POINTS = 7  # Found in heading 1.

    CONST_H2_POINTS = 6  # Found in heading 2.

    CONST_H3_POINTS = 5  # Found in heading 3.

    CONST_P_POINTS = 4  # Found in paragraph.

    # We could except these words from index, but we're gonna decrement their score by 1/10.
    # Basically, STOP_WORDS are very common words like prepositions and conjunctions.
    CONST_STOP_WORDS = {"a", "an", "the", "and", "for", "nor", "but", "or", "yet", "so", "though", "although", "while",
                        "if", "unless", "else", "until", "lest", "after", "before", "soon", "once", "since", "till",
                        "what", "whatever", "whatsoever", "which", "whichever", "when", "whenever", "who", "whoever",
                        "whom", "whomever", "whose", "where", "wherever" "that", "than", "why", "rather", "whether",
                        "as",
                        "whereas", "because", "how", "both", "just", "hardly", "scarcely", "either", "neither", "then",
                        "not", "with", "also", "seldom", "besides", "furthermore", "moreover", "likewise", "however",
                        "nevertheless", "nonetheless", "still", "instead", "otherwise", "hence", "meanwhile",
                        "therefore",
                        "thus", "albeit", "about", "above", "across", "after", "against", "along", "among", "around",
                        "at", "behind", "below", "in", "of", "by", "is", "on", "it", "be", "was", "has", "to",

                        "y", "e", "ni", "que", "pero", "mas", "aunque", "sino", "siquiera", "o", "u", "sea", "ya", "no",
                        "ni", "pues", "porque", "puesto", "como", "más", "así", "luego", "tan", "tanto", "conque",
                        "cuando",
                        "mientras", "cuanto", "antes", "después", "a", "ante", "bajo", "cabe", "con", "contra", "de",
                        "desde",
                        "en", "entre", "hacia", "hasta", "para", "por", "según", "sin", "so", "sobre", "tras",
                        "durante",
                        "mediante", "excepto", "salvo", "incluso", "menos", "debajo", "delante", "dentro", "cerca",
                        "alrededor",
                        "al", "del", "encima", "enfrente", "junto", "lejos", "pesar", "embargo", "el", "la", "los",
                        "las", "atrás",
                        "un", "una", "unos", "unas", "algún", "alguna", "algunos", "algunas"}

    # We can add span, a, div content if necessary.

    # Initialization of the class.
    def __init__(self, soup, page_id):
        self.soup = soup                # Take soup utility.
        self.page_id = page_id          # Page's identification number.
        self.words_weight = {}          # Dictionary with the page's words and their corresponding weights.
        self.title = ""                 # Title of the page.
        '''
            We need to call the following methods directly in the constructor 
            so as to execute them when we call the class calc_score.
        '''
        self.calc_title()               # Calculates score of title.
        self.calc_description()         # Calculates score of description of the page.
        self.calc_h1()                  # Calculates score of header 1 of the page.
        self.calc_h2()                  # Calculates score of header 2 of the page.
        self.calc_h3()                  # Calculates score of header 3 of the page.
        self.calc_p()                   # Calculates score of paragraph of the page.
        # self.list_words()             # Prints out the words found on a page and their score.

    # Gets the title of the page.
    def get_title(self):
        return util.clean_words(self.title)
        #  return self.title

    # Method which calculates the score given a string.
    def calc(self, input_str, points):
        # Trivial case when there are no words.
        if input_str is None:
            return
        try:
            clear = util.clean_words(input_str)  # Clean the words from "litter".
            words = clear.split(" ")             # Split the string into several words.
            # We check for every word of the string.
            for word in words:
                if word == '':
                    continue
                sum_points = self.words_weight.get(word)  # Initially set to 0, we will accumulate the score.
                if word in self.CONST_STOP_WORDS:         # If the word is actually a STOP WORD...
                    x = points * 0.1
                else:
                    x = points
                if sum_points is None:
                    self.words_weight[word] = x
                else:
                    self.words_weight[word] += x
        except ValueError as e:
            print(e)

    def calc_title(self):
        if self.soup.title is not None:
            self.calc(self.soup.title.string, self.CONST_TITLE_POINTS)
            self.title = self.soup.title.string

    def calc_description(self):
        meta = self.soup.find("meta", attrs={"name": "description"}) # html <meta name = description>.
        if meta is not None and 'content' in meta:
            self.calc(meta["content"], self.CONST_DESCRIPTION_POINTS)

    def calc_h1(self):
        h1_list = self.soup.find_all("h1")
        for h1 in h1_list:
            self.calc(h1.string, self.CONST_H1_POINTS)

    def calc_h2(self):
        h2_list = self.soup.find_all("h2")
        for h2 in h2_list:
            self.calc(h2.string, self.CONST_H2_POINTS)

    def calc_h3(self):
        h3_list = self.soup.find_all("h3")
        for h3 in h3_list:
            self.calc(h3.string, self.CONST_H3_POINTS)

    def calc_p(self):
        p_list = self.soup.find_all("p")
        for p in p_list:
            self.calc(p.string, self.CONST_P_POINTS)

    # Print the words with their corresponding weights.
    def list_words(self):
        print("Points rate")
        print(self.words_weight)

    def get_result(self):
        result = {}
        for word in self.words_weight:
            '''
                We store in the "result" dictionary each word, where each "word" is also a dictionary, with the 
                following fields:
                word = {(identification number of page): word's score rounded to 2 decimals}
                We need the identification number to know to which page does belong this word since we could have 
                distinct pages with the same word.
            '''
            result[word] = {self.page_id: round(self.words_weight.get(word), 2)}
        return result
