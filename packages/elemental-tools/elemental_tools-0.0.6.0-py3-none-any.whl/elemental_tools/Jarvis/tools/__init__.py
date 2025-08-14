from itertools import product
from elemental_tools.logger import Logger
import numpy as np
import random
import spacy
from typing import Any
import re
from dateutil.parser import parse as date_parser
from nltk.corpus import wordnet
from numpy import ndarray

logger = Logger(app_name='brainiac', owner='tools', destination=None).log

# Load spacy and their models for the program standard language
try:
    nlp_models = spacy.load('en_core_web_md')
except:
    spacy.cli.download("en_core_web_md")
    nlp_models = spacy.load('en_core_web_md')


class MessageStats:
    msg = None
    subject = None
    tenses = None
    verbs = None
    verbs_tenses = None
    verbs_future = None
    verbs_past = None
    verbs_present = None

    def __init__(self, msg: str):
        self.msg = msg.lower()
        self.msg_model = nlp_models(msg)
        self.get_verbs()
        self.get_verbs_tenses()
        self.get_subject()
        self.get_tenses()

    def get_verbs(self):
        self.verbs = [token for token in self.msg_model if token.pos_ == "VERB"]
        self.verbs_present = [token.text for token in self.msg_model if
                              token.morph.get("Tense") == "PRESENT" and token.pos_ == "VERB"]
        self.verbs_future = [token for token in self.msg_model if token.text in ["will", "shall"]]
        self.verbs_past = [token for token in self.msg_model if
                           token.morph.get("Tense") == "PAST" and token.pos_ == "VERB"]
        return self.verbs

    def get_verbs_tenses(self):
        self.verbs_tenses = [token.morph.get("Tense") for token in self.verbs if token.pos_ == "VERB"]
        return self.verbs_tenses

    def get_tenses(self):
        self.tenses = [token.morph.get("Tense") for token in self.msg_model if token.pos_ == "VERB"]
        return self.tenses

    def get_subject(self):
        self.subject = [token for token in self.msg_model if "subj" in token.dep_]
        return self.subject


class Tools:
    data = None
    questions = np.array(["what", "what's", "how", "when", "what about", "who", "why", 'can', 'do'])
    present = np.array(["is", "are"])
    past = np.array(["was", "were"])
    person = np.array(["me", "you", "he", "she", "it", "i", "my"])
    numbers = range(100)
    cryptos = ["BTC", "LTC", "ETH", "NEO", "BNB", "QTUM", "EOS", "SNT", "BNT", "GAS", "BCC", "USDT", "HSR", "OAX",
               "DNT", "MCO", "ICN", "ZRX", "OMG", "WTC", "YOYO", "LRC", "TRX", "SNGLS", "STRAT", "BQX", "FUN", "KNC",
               "CDT", "XVG", "IOTA", "SNM", "LINK", "CVC", "TNT", "REP", "MDA", "MTL", "SALT", "NULS", "SUB", "STX",
               "MTH", "ADX", "ETC", "ENG", "ZEC", "AST", "GNT", "DGD", "BAT", "DASH", "POWR", "BTG", "REQ", "XMR",
               "EVX", "VIB", "ENJ", "VEN", "ARK", "XRP", "MOD", "STORJ", "KMD", "RCN", "EDO", "DATA", "DLT", "MANA",
               "PPT", "RDN", "GXS", "AMB", "ARN", "BCPT", "CND", "GVT", "POE", "BTS", "FUEL", "XZC", "QSP", "LSK",
               "BCD", "TNB", "ADA", "LEND", "XLM", "CMT", "WAVES", "WABI", "GTO", "ICX", "OST", "ELF", "AION", "WINGS",
               "BRD", "NEBL", "NAV", "VIBE", "LUN", "TRIG", "APPC", "CHAT", "RLC", "INS", "PIVX", "IOST", "STEEM",
               "NANO", "AE", "VIA", "BLZ", "SYS", "RPX", "NCASH", "POA", "ONT", "ZIL", "STORM", "XEM", "WAN", "WPR",
               "QLC", "GRS", "CLOAK", "LOOM", "BCN", "TUSD", "ZEN", "SKY", "THETA", "IOTX", "QKC", "AGI", "NXS", "SC",
               "NPXS", "KEY", "NAS", "MFT", "DENT", "IQ", "ARDR", "HOT", "VET", "DOCK", "POLY", "VTHO", "ONG", "PHX",
               "HC", "GO", "PAX", "RVN", "DCR", "USDC", "MITH", "BCHABC", "BCHSV", "REN", "BTT", "USDS", "FET", "TFUEL",
               "CELR", "MATIC", "ATOM", "PHB", "ONE", "FTM", "BTCB", "USDSB", "CHZ", "COS", "ALGO", "ERD", "DOGE",
               "BGBP", "DUSK", "ANKR", "WIN", "TUSDB", "COCOS", "PERL", "TOMO", "BUSD", "BAND", "BEAM", "HBAR", "XTZ",
               "NGN", "DGB", "NKN", "GBP", "EUR", "KAVA", "RUB", "UAH", "ARPA", "TRY", "CTXC", "AERGO", "BCH", "TROY",
               "BRL", "VITE", "FTT", "AUD", "OGN", "DREP", "BULL", "BEAR", "ETHBULL", "ETHBEAR", "XRPBULL", "XRPBEAR",
               "EOSBULL", "EOSBEAR", "TCT", "WRX", "LTO", "ZAR", "MBL", "COTI", "BKRW", "BNBBULL", "BNBBEAR", "HIVE",
               "STPT", "SOL", "IDRT", "CTSI", "CHR", "BTCUP", "BTCDOWN", "HNT", "JST", "FIO", "BIDR", "STMX", "MDT",
               "PNT", "COMP", "IRIS", "MKR", "SXP", "SNX", "DAI", "ETHUP", "ETHDOWN", "ADAUP", "ADADOWN", "LINKUP",
               "LINKDOWN", "DOT", "RUNE", "BNBUP", "BNBDOWN", "XTZUP", "XTZDOWN", "AVA", "BAL", "YFI", "SRM", "ANT",
               "CRV", "SAND", "OCEAN", "NMR", "LUNA", "IDEX", "RSR", "PAXG", "WNXM", "TRB", "EGLD", "BZRX", "WBTC",
               "KSM", "SUSHI", "YFII", "DIA", "BEL", "UMA", "EOSUP", "TRXUP", "EOSDOWN", "TRXDOWN", "XRPUP", "XRPDOWN",
               "DOTUP", "DOTDOWN", "NBS", "WING", "SWRV", "LTCUP", "LTCDOWN", "CREAM", "UNI", "OXT", "SUN", "AVAX",
               "BURGER", "BAKE", "FLM", "SCRT", "XVS", "CAKE", "SPARTA", "UNIUP", "UNIDOWN", "ALPHA", "ORN", "UTK",
               "NEAR", "VIDT", "AAVE", "FIL", "SXPUP", "SXPDOWN", "INJ", "FILDOWN", "FILUP", "YFIUP", "YFIDOWN", "CTK",
               "EASY", "AUDIO", "BCHUP", "BCHDOWN", "BOT", "AXS", "AKRO", "HARD", "KP3R", "RENBTC", "SLP", "STRAX",
               "UNFI", "CVP", "BCHA", "FOR", "FRONT", "ROSE", "HEGIC", "AAVEUP", "AAVEDOWN", "PROM", "BETH", "SKL",
               "GLM", "SUSD", "COVER", "GHST", "SUSHIUP", "SUSHIDOWN", "XLMUP", "XLMDOWN", "DF", "JUV", "PSG", "BVND",
               "GRT", "CELO", "TWT", "REEF", "OG", "ATM", "ASR", "1INCH", "RIF", "BTCST", "TRU", "DEXE", "CKB", "FIRO",
               "LIT", "PROS", "VAI", "SFP", "FXS", "DODO", "AUCTION", "UFT", "ACM", "PHA", "TVK", "BADGER", "FIS", "OM",
               "POND", "ALICE", "DEGO", "BIFI", "LINA"]
    currency = ['r$']
    wishes = np.array(['want', 'like', 'wish'])
    others = np.array(['do', '"', "'"])
    conjunctions = np.array(['the', 'of', 'with', 'without', 'be'])
    junk = np.concatenate((questions, present, wishes, person, conjunctions, others), axis=0)
    months = np.array(
        ["jan", "january", "feb", "february", "mar", "march", "apr", "april", "may", "jun", "june", "jul", "july",
         "aug", "august", "sep", "september", "oct", "october", "nov", "november", "dec", "december"])

    def get_syn_list(self, word: str):
        synonyms = []
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())

        synonyms = list(set(synonyms))
        return np.array(synonyms)

    def get_random_syn(self, word: str):
        syn_list = self.get_syn_list(word)
        return random.choice(syn_list)

    def get_questions(self, syns: list):
        result = []

        for syn in syns:
            for q in self.questions:
                result.append(q + " " + syn)

        result = list(set(result))
        result = np.array(result)

        return result

    def get_currency_symbols(self, currency: str):
        c = currency.lower()
        s = ['$']

        if c == "usd":
            s = ['usd', '$']
        elif c == "brl":
            s = ['brl', 'r$']

        return s

    def get_amounts(self, currency: str):
        result = []
        currency_symbol = self.get_currency_symbols(currency)
        for s in currency_symbol:
            result += [f"{s}{n}" for n in self.numbers]
        result += [f"{n}k" for n in self.numbers] + [f"{n}k" for n in self.numbers]
        result = list(set(result))
        return np.array(result)

    def generate_combinations(self, *args):
        # Generate all combinations of the arguments separated by a space
        combinations = list(set([' '.join(x) for x in set(product(*args))]))
        return np.array(combinations)

    def to_nlp(self, models, ndarray: np.ndarray):
        unique_values = []
        seen_values = set()

        for item in ndarray:
            model_result = models(str(item))
            if model_result not in seen_values:
                unique_values.append(model_result)
                seen_values.add(model_result)

        return unique_values

    def is_junk(self, word: str):
        # logger('error', f'Searching for {word} in junk: {self.junk}')

        if len(np.where(self.junk == word)[0]):
            # logger('error', f'Word {word} is junk!')
            return True
        # logger('error', f'Word {word} is not junk...')
        return False

    def add_junk(self, word: str):
        # logger('error', f"adding {word} with type: {type(word)} to junk : {self.junk}")
        _array = np.array([word])
        self.junk = np.concatenate((_array, self.junk), axis=0)
        # logger('error', f"junk after addition {self.junk}")
        return self.junk

    def retrieve_dates(self, nlp_model):
        # Initialize a list to store date expressions
        date_expressions = []
        for token in nlp_model:
            # Check if the token is a date-related word
            if token.text.lower() in ["jan", "january", "feb", "february", "mar", "march", "apr", "april", "may", "jun",
                                      "june", "jul", "july", "aug", "august", "sep", "september", "oct", "october",
                                      "nov", "november", "dec", "december"]:
                # Translate date-related words to English
                date_expressions.append(token.text)
            elif re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', token.text):
                # Match standard date formats (dd/mm/yyyy or mm/dd/yyyy)
                date_expressions.append(token.text)

        parsed_dates = [date_parser(date) for date in date_expressions]
        return parsed_dates

    def retrieve_amounts(self, text: str):

        def get_currency():
            currency_symbols = re.findall(r'[$€¥£]', text)

        def adapted_value(amount: str):

            k_count = 1
            if 'k' in amount:
                k_count = 0
            for e in amount:
                if e == 'k':
                    k_count += 1000
            try:
                result = float(re.sub(r'[A-Za-z]', '', amount))
                result = float(result * k_count)
            except:
                result = None
            return result

        # print(f"Retrieving amount from text: {text}")
        # Regular expression patterns for money expressions

        money_pattern = r'(?:r?\$|R\$)?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?\s*[Kk]?)'

        # Find money expressions in the input text
        money_matches = re.findall(money_pattern, text)
        # print(f"first: {money_matches}")
        if not len(money_matches):
            number_pattern = r'[0-9]'
            money_matches = re.findall(number_pattern, text)
            # print(f"sec: {money_matches}")

        return max([float(adapted_value(str(match))) for match in money_matches])


    def codes_and_languages(self):
        codes_and_languages = {
            '+55': 'pt',
            '55': 'pt',

            '+54': 'es',
            '54': 'es',

            '+1': 'en',
            '1': 'en',
        }
        return codes_and_languages

    def clean_phone(self, phone):
        _result = phone
        _result = _result.replace(' ', '')
        _result = _result.replace('-', '')
        return _result


class BrainiacRequest:
    output_function: Any = None

    message = None
    message_model = None
    message_stats = None
    message_model_lemma = None
    threshold_args: float = 0.50

    _garbage = set()

    class skill:
        _id: str
        name: str
        function: Any
        suggestion_title: str = None
        parameters: dict = {}
        examples: np.ndarray = np.array([])
        examples_lemmas: np.ndarray = np.array([])
        args: dict = {}
        depends = None
        authorized: bool = False
        result = None
        exception = None
        confidence = float = -1.0
        keywords: np.ndarray = np.array([])

        def __init__(self):
            for example in self.examples:
                ex_verbs = MessageStats(example.text).verbs
                self.keywords = np.concatenate((np.array(ex_verbs), self.keywords), axis=0)

    def add_garbage(self, garbage_index: tuple):
        self._garbage.add(garbage_index)

    def is_garbage(self, garbage_index: tuple):
        return garbage_index in self._garbage

    def __init__(self):
        self.rt = Tools()


def multi_split(input_string, delimiters):
    # Create a regular expression pattern using the provided delimiters
    pattern = '|'.join(map(re.escape, delimiters))

    # Use re.split with the pattern to split the input string
    result = re.split(pattern, input_string)

    return result


def extract_and_remove_quoted_content(input_string):
    # Find and store content within double quotes
    double_quotes_content = re.findall(r'"([^"]*)"', input_string)

    # Remove content within double quotes
    clean_string = re.sub(r'"([^"]*)"', '""', input_string)

    # Find and store content within single quotes
    single_quotes_content = re.findall(r"'([^']*)'", clean_string)

    # Remove content within single quotes
    clean_string = re.sub(r"'([^']*)'", "''", clean_string)

    return clean_string.strip(), double_quotes_content + single_quotes_content


