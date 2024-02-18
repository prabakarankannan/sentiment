import os

import pandas as pd
import yake
from googletrans import Translator
from scrapper.models import Keyword, TargetURL, Article, Project, People
from cleantext import clean
from urllib.parse import urlparse
import pandas as pd
from django.conf import settings
from datetime import datetime
from api.helpers import get_current_time


STOPWORDS = {
"0o", "0s", "3a", "3b", "3d", "6b", "6o", "a", "a1", "a2", "a3", "a4", "ab", "able", "about", "above", "abst", "ac", "accordance", "according", "accordingly", "across", "act", "actually", "ad", "added", "adj", "ae", "af", "affected", "affecting", "affects", "after", "afterwards", "ag", "again", "against", "ah", "ain", "ain't", "aj", "al", "all", "allow", "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "ao", "ap", "apart", "apparently", "appear", "appreciate", "appropriate", "approximately", "ar", "are", "aren", "arent", "aren't", "arise", "around", "as", "a's", "aside", "ask", "asking", "associated", "at", "au", "auth", "av", "available", "aw", "away", "awfully", "ax", "ay", "az", "b", "b1", "b2", "b3", "ba", "back", "bc", "bd", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "bi", "bill", "biol", "bj", "bk", "bl", "bn", "both", "bottom", "bp", "br", "brief", "briefly", "bs", "bt", "bu", "but", "bx", "by", "c", "c1", "c2", "c3", "ca", "call", "came", "can", "cannot", "cant", "can't", "cause", "causes", "cc", "cd", "ce", "certain", "certainly", "cf", "cg", "ch", "changes", "ci", "cit", "cj", "cl", "clearly", "cm", "c'mon", "cn", "co", "com", "come", "comes", "con", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn", "couldnt", "couldn't", "course", "cp", "cq", "cr", "cry", "cs", "c's", "ct", "cu", "currently", "cv", "cx", "cy", "cz", "d", "d2", "da", "date", "dc", "dd", "de", "definitely", "describe", "described", "despite", "detail", "df", "di", "did", "didn", "didn't", "different", "dj", "dk", "dl", "do", "does", "doesn", "doesn't", "doing", "don", "done", "don't", "down", "downwards", "dp", "dr", "ds", "dt", "du", "due", "during", "dx", "dy", "e", "e2", "e3", "ea", "each", "ec", "ed", "edu", "ee", "ef", "effect", "eg", "ei", "eight", "eighty", "either", "ej", "el", "eleven", "else", "elsewhere", "em", "empty", "en", "end", "ending", "enough", "entirely", "eo", "ep", "eq", "er", "es", "especially", "est", "et", "et-al", "etc", "eu", "ev", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "ey", "f", "f2", "fa", "far", "fc", "few", "ff", "fi", "fifteen", "fifth", "fify", "fill", "find", "fire", "first", "five", "fix", "fj", "fl", "fn", "fo", "followed", "following", "follows", "for", "former", "formerly", "forth", "forty", "found", "four", "fr", "from", "front", "fs", "ft", "fu", "full", "further", "furthermore", "fy", "g", "ga", "gave", "ge", "get", "gets", "getting", "gi", "give", "given", "gives", "giving", "gj", "gl", "go", "goes", "going", "gone", "got", "gotten", "gr", "greetings", "gs", "gy", "h", "h2", "h3", "had", "hadn", "hadn't", "happens", "hardly", "has", "hasn", "hasnt", "hasn't", "have", "haven", "haven't", "having", "he", "hed", "he'd", "he'll", "hello", "help", "hence", "her", "here", "hereafter", "hereby", "herein", "heres", "here's", "hereupon", "hers", "herself", "hes", "he's", "hh", "hi", "hid", "him", "himself", "his", "hither", "hj", "ho", "home", "hopefully", "how", "howbeit", "however", "how's", "hr", "hs", "http", "hu", "hundred", "hy", "i", "i2", "i3", "i4", "i6", "i7", "i8", "ia", "ib", "ibid", "ic", "id", "i'd", "ie", "if", "ig", "ignored", "ih", "ii", "ij", "il", "i'll", "im", "i'm", "immediate", "immediately", "importance", "important", "in", "inasmuch", "inc", "indeed", "index", "indicate", "indicated", "indicates", "information", "inner", "insofar", "instead", "interest", "into", "invention", "inward", "io", "ip", "iq", "ir", "is", "isn", "isn't", "it", "itd", "it'd", "it'll", "its", "it's", "itself", "iv", "i've", "ix", "iy", "iz", "j", "jj", "jr", "js", "jt", "ju", "just", "k", "ke", "keep", "keeps", "kept", "kg", "kj", "km", "know", "known", "knows", "ko", "l", "l2", "la", "largely", "last", "lately", "later", "latter", "latterly", "lb", "lc", "le", "least", "les", "less", "lest", "let", "lets", "let's", "lf", "like", "liked", "likely", "line", "little", "lj", "ll", "ll", "ln", "lo", "look", "looking", "looks", "los", "lr", "ls", "lt", "ltd", "m", "m2", "ma", "made", "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means", "meantime", "meanwhile", "merely", "mg", "might", "mightn", "mightn't", "mill", "million", "mine", "miss", "ml", "mn", "mo", "more", "moreover", "most", "mostly", "move", "mr", "mrs", "ms", "mt", "mu", "much", "mug", "must", "mustn", "mustn't", "my", "myself", "n", "n2", "na", "name", "namely", "nay", "nc", "nd", "ne", "near", "nearly", "necessarily", "necessary", "need", "needn", "needn't", "needs", "neither", "never", "nevertheless", "new", "next", "ng", "ni", "nine", "ninety", "nj", "nl", "nn", "no", "nobody", "non", "none", "nonetheless", "noone", "nor", "normally", "nos", "not", "noted", "nothing", "novel", "now", "nowhere", "nr", "ns", "nt", "ny", "o", "oa", "ob", "obtain", "obtained", "obviously", "oc", "od", "of", "off", "often", "og", "oh", "oi", "oj", "ok", "okay", "ol", "old", "om", "omitted", "on", "once", "one", "ones", "only", "onto", "oo", "op", "oq", "or", "ord", "os", "ot", "other", "others", "otherwise", "ou", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "ow", "owing", "own", "ox", "oz", "p", "p1", "p2", "p3", "page", "pagecount", "pages", "par", "part", "particular", "particularly", "pas", "past", "pc", "pd", "pe", "per", "perhaps", "pf", "ph", "pi", "pj", "pk", "pl", "placed", "please", "plus", "pm", "pn", "po", "poorly", "possible", "possibly", "potentially", "pp", "pq", "pr", "predominantly", "present", "presumably", "previously", "primarily", "probably", "promptly", "proud", "provides", "ps", "pt", "pu", "put", "py", "q", "qj", "qu", "que", "quickly", "quite", "qv", "r", "r2", "ra", "ran", "rather", "rc", "rd", "re", "readily", "really", "reasonably", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "research-articl", "respectively", "resulted", "resulting", "results", "rf", "rh", "ri", "right", "rj", "rl", "rm", "rn", "ro", "rq", "rr", "rs", "rt", "ru", "run", "rv", "ry", "s", "s2", "sa", "said", "same", "saw", "say", "saying", "says", "sc", "sd", "se", "sec", "second", "secondly", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "sf", "shall", "shan", "shan't", "she", "shed", "she'd", "she'll", "shes", "she's", "should", "shouldn", "shouldn't", "should've", "show", "showed", "shown", "showns", "shows", "si", "side", "significant", "significantly", "similar", "similarly", "since", "sincere", "six", "sixty", "sj", "sl", "slightly", "sm", "sn", "so", "some", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "sp", "specifically", "specified", "specify", "specifying", "sq", "sr", "ss", "st", "still", "stop", "strongly", "sub", "substantially", "successfully", "such", "sufficiently", "suggest", "sup", "sure", "sy", "system", "sz", "t", "t1", "t2", "t3", "take", "taken", "taking", "tb", "tc", "td", "te", "tell", "ten", "tends", "tf", "th", "than", "thank", "thanks", "thanx", "that", "that'll", "thats", "that's", "that've", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "thered", "therefore", "therein", "there'll", "thereof", "therere", "theres", "there's", "thereto", "thereupon", "there've", "these", "they", "theyd", "they'd", "they'll", "theyre", "they're", "they've", "thickv", "thin", "think", "third", "this", "thorough", "thoroughly", "those", "thou", "though", "thoughh", "thousand", "three", "throug", "through", "throughout", "thru", "thus", "ti", "til", "tip", "tj", "tl", "tm", "tn", "to", "together", "too", "took", "top", "toward", "towards", "tp", "tq", "tr", "tried", "tries", "truly", "try", "trying", "ts", "t's", "tt", "tv", "twelve", "twenty", "twice", "two", "tx", "u", "u201d", "ue", "ui", "uj", "uk", "um", "un", "under", "unfortunately", "unless", "unlike", "unlikely", "until", "unto", "uo", "up", "upon", "ups", "ur", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using", "usually", "ut", "v", "va", "value", "various", "vd", "ve", "ve", "very", "via", "viz", "vj", "vo", "vol", "vols", "volumtype", "vq", "vs", "vt", "vu", "w", "wa", "want", "wants", "was", "wasn", "wasnt", "wasn't", "way", "we", "wed", "we'd", "welcome", "well", "we'll", "well-b", "went", "were", "we're", "weren", "werent", "weren't", "we've", "what", "whatever", "what'll", "whats", "what's", "when", "whence", "whenever", "when's", "where", "whereafter", "whereas", "whereby", "wherein", "wheres", "where's", "whereupon", "wherever", "whether", "which", "while", "whim", "whither", "who", "whod", "whoever", "whole", "who'll", "whom", "whomever", "whos", "who's", "whose", "why", "why's", "wi", "widely", "will", "willing", "wish", "with", "within", "without", "wo", "won", "wonder", "wont", "won't", "words", "world", "would", "wouldn", "wouldnt", "wouldn't", "www", "x", "x1", "x2", "x3", "xf", "xi", "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y", "y2", "yes", "yet", "yj", "yl", "you", "youd", "you'd", "you'll", "your", "youre", "you're", "yours", "yourself", "yourselves", "you've", "yr", "ys", "yt", "z", "zero", "zi", "zz",
}
STOPWORDS_v1 = {"|", "today","india","'", "none",':', "can", "]", "[", ")", "(", ";", ",", ".", 'doing', '—', '-', '_', 'at', '”', 'could', 'mr.', ',', '.', '?', '"', '/', 'haven', 'themselves', 'mustn', 'won', 'out', 'will', 'himself', 'its', 'can', 'both', 'yours', 'once', "needn't", 'hasn', 'more', 'yourselves', 'he', 'again', 'no', "isn't", 'she', 'herself', 'but', 'myself', 'ourselves', 'just', "it's", 'yourself', 'what', 'y', 'ain', 'ours', 'weren', 'own', "you've", 'now', 'that', 'any', "don't", 'being', "shouldn't", 'having', 's', 'off', 'each', 'through', 'few', 'at', 'wouldn', 'me', "that'll", 'against', 'd', 'been', 'all', 'than', 'on', "you'd", 'is', 'or', 'by', 'isn', 'for', "weren't", 'a', 'am', 'then', 'some', 'before', 'down', "couldn't", 'them', 're', 'him', 'aren', "doesn't", 'so', 'which', "hadn't", 'did', "shan't", 'over', 'hers', 'into', 'theirs', 've', 'm', 'further', 'my', 'an', 'when', 'our', 'of', 'in', 'very', 'don', "aren't", "didn't", 'be', 'too', 'whom', 'during', 'where', 'have', 'with', "she's", 'wasn', 'are', 't', "mustn't", 'above', 'itself', 'does', 'who', 'why', 'while', 'not', 'their', 'this', 'if', 'same', "should've", 'after', 'hadn', 'didn', 'you', 'about', 'how', 'it', 'had', 'o', 'here', 'other', 'under', 'until', 'most', 'we', 'your', 'because', 'and', 'has', 'i', 'ma', 'll', 'they', 'shan', 'his', "haven't", 'was', 'up', 'from', 'those', 'couldn', "won't", 'needn', 'her', 'mightn', 'to', 'should', "mightn't", 'doesn', 'were', "wasn't", 'shouldn', "wouldn't", 'the', 'do', "you'll", 'as', 'between', 'nor', 'these', 'there', 'below', 'such', "hasn't", "you're", 'only'}
STOPWORDS_v1.update(STOPWORDS)


def save_file(data, is_tweet, project_name):
    # dateandtime = get_current_time()
    # if is_tweet:
    #     filename = os.path.join(settings.BASE_DIR, 'media', str(dateandtime) + f"___{project_name}__tweets__.csv")
    # else:
    #     filename = os.path.join(settings.BASE_DIR, 'media', str(dateandtime) + f"___{project_name}__news__.csv")
    #
    # df = pd.DataFrame(data)
    # df.to_csv(filename, index=False)
    pass


def vacuum_db():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("VACUUM")
    connection.close()


def topic_extract(text):
    kw_extractor = yake.KeywordExtractor(top=5, stopwords=STOPWORDS_v1)
    keywords = kw_extractor.extract_keywords(text)

    ll = set()
    for kw, v in keywords:
        ll.add(kw)
    # print(a, ll)
    return ll


def get_word_freq(df):
    df = df.fillna("")

    # Same results.

    df['text'] = df['tags'].apply(
        lambda x: ', '.join([word for word in x if word.lower() not in STOPWORDS_v1]))
    # print(df)
    res = df.text.str.split(expand=True).stack().value_counts()
    # print(res.to_frame())
    kwd = pd.DataFrame(res).reset_index()
    kwd.columns = ['text', 'value']
    return kwd


def detect_language(text):
    translator = Translator()
    a = translator.detect(text)
    if a._response.status_code == 200:
        if a.confidence > 0.75:
            return a.lang
        else:
            return 'auto'
    else:
        return 'auto'


def translate_text(text, target_language='en'):
    translator = Translator()
    translated_text = translator.translate(text, scr=detect_language(text), dest=target_language)

    if 'en' in detect_language(translated_text.text):
        return translated_text.text
    else:
        return None


def translate_text_v2(text, target_language='en'):
    translator = Translator()
    source_language = detect_language(text)
    translated_text = translator.translate(text, scr=detect_language(text), dest=target_language)
    return {"source_language":source_language, "translated_text":translated_text.text}


def search_keywords(content="", title="", source_content="", source_title="", target_keywords=[]):
    if source_title:
        source_title = clean(str(source_title),
                      fix_unicode=True,  # fix various unicode errors
                      to_ascii=True,  # transliterate to closest ASCII representation
                      lower=True,
                      no_emails=True,
                      no_urls=True,
                      normalize_whitespace=True).strip(" ")

    if source_content:
        source_content = clean(str(source_content),
                        fix_unicode=True,  # fix various unicode errors
                        to_ascii=True,  # transliterate to closest ASCII representation
                        lower=True,
                        no_emails=True,
                        no_urls=True,
                        normalize_whitespace=True).strip(" ")
    try:
        print("searching keywords")
        # print(all_keywords)
        if content:
            keywords = [kw for kw in target_keywords if kw in content]
        elif source_content:
            keywords = [kw for kw in target_keywords if kw in source_content]
        else:
            keywords = []

        if title:
            keywords = keywords + [kw for kw in target_keywords if kw in title]
        elif source_content:
            keywords = keywords + [kw for kw in target_keywords if kw in source_title]
        else:
            keywords = []
        print(keywords)
    except Exception as e:
        print("Error in keyword search : ", e)
        keywords = []

    return list(set(keywords))


def extract_domain_without_www(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        domain = parsed_url.netloc
        if domain.startswith("www."):
            return domain[4:]
        return domain
    else:
        return None


def get_target_urls():
    return TargetURL.objects.filter(is_active=True).values(
        'url', 'selector')


def get_target_keywords():
    return Keyword.objects.filter(is_enable=True).values_list('name', flat=True)


def get_project_details():
    projects = Project.objects.all()
    project_details = []

    for project in projects:
        keywords = list(project.keyword.values_list('name', flat=True))
        states = list(project.state.values_list('name', flat=True))

        project_info = {
            'name': project.name,
            'keywords': keywords,
            'states': states,
        }
        project_details.append(project_info)

    return project_details


def resync_keyword():
    main_list = set()

    keywords_list = Keyword.objects.filter(is_enable=True)

    for article in Article.objects.all():
        for keyword in keywords_list:
            if keyword not in article.keywords.all():
                if (
                        (article.title and keyword.name.lower() in article.title.lower()) or
                        (article.content and keyword.name.lower() in article.content.lower()) or
                        (article.source_title and keyword.name.lower() in article.source_title.lower()) or
                        (article.source_content and keyword.name.lower() in article.source_content.lower())
                ) or keyword.name.lower() in [ppl.name.lower() for ppl in article.people.all()]:
                    article.keywords.add(keyword)
                    main_list.add(keyword.name)
    return main_list


def resync_people():
    main_list = set()

    people_list = People.objects.filter()

    for article in Article.objects.all():
        for people in people_list:
            if people not in article.people.all():
                if (
                        (article.title and people.name.lower() in article.title.lower()) or
                        (article.content and people.name.lower() in article.content.lower()) or
                        (article.source_title and people.name.lower() in article.source_title.lower()) or
                        (article.source_content and people.name.lower() in article.source_content.lower())
                ) or people.name.lower() in [kw.name.lower() for kw in article.keywords.all()]:
                    article.people.add(people)
                    main_list.add(people.name)
    return main_list


