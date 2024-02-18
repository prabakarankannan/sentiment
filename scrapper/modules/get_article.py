import datetime
import json
import os
import nltk
from django.utils import timezone
from django.conf import settings
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from newsplease import NewsPlease
from scrapper.models import Article
from scrapper.modules.helpers import topic_extract, translate_text, search_keywords
from scrapper.modules.openai_connetor import openai_extract_info
from cleantext import clean

nltk.data.path.append(os.path.join(settings.BASE_DIR, 'storage'))
try:
    sia = SentimentIntensityAnalyzer()
except LookupError:
    nltk.download("vader_lexicon", download_dir=os.path.join(settings.BASE_DIR, 'storage'))
    sia = SentimentIntensityAnalyzer()


class WebScraper:
    """

        {
      "authors": [],
      "date_download": null,
      "date_modify": null,
      "date_publish": "2017-07-17 17:03:00",
      "description": "Russia has called on Ukraine to stick to the Minsk peace process [news-please will extract the whole text but in this example file we needed to cut off here because of copyright laws].",
      "filename": "https%3A%2F%2Fwww.rt.com%2Fnews%2F203203-ukraine-russia-troops-border%2F.json",
      "image_url": "https://img.rt.com/files/news/31/9c/30/00/canada-russia-troops-buildup-.si.jpg",
      "language": "en",
      "localpath": null,
      "source_domain": "www.rt.com",
      "maintext": "Russia has called on Ukraine to stick to the Minsk peace process [news-please will extract the whole text but in this example file we needed to cut off here because of copyright laws].",
      "title": "Moscow to Kiev: Stick to Minsk ceasefire, stop making false \u2018invasion\u2019 claims",
      "title_page": null,
      "title_rss": null,
      "url": "https://www.rt.com/news/203203-ukraine-russia-troops-border/"
    }
    """
    def __init__(self, target_keywords):
        self.target_keywords = target_keywords
        print("scrapping articles")

    def get_data_from_web(self, url):
        try:
            article = NewsPlease.from_url(url)
            source_title = article.title
            source_content = str(article.description) + "\n\n" + str(article.maintext)
            keywords = search_keywords(source_content=source_content, source_title=source_title,
                                       title=url, target_keywords=self.target_keywords)
            return article, source_title, source_content, keywords
        except Exception as e:
            print("unable to scrape given url error in newsplease package : ", e)
            return None, None, None, None

    def translate_content(self, source_content):
        content_list = []
        for each_content in source_content.split("\n"):
            if each_content.strip():
                en = self.translate_text(each_content.strip())
                if en:
                    content_list.append(en)
                else:
                    content_2 = []
                    for each_content_2 in each_content.split("."):
                        en_2 = self.translate_text(each_content_2.strip())
                        if en_2:
                            content_2.append(en_2)

                    content_list.append(".".join(content_2))

        return "\n".join(content_list)

    @staticmethod
    def translate_text(text):
        try:
            return translate_text(text=text, target_language='en')
        except Exception as e:
            print("Unable to translate text:", e)
            return None

    def process_content(self, source_title, source_content):
        try:
            title = self.translate_text(source_title)
            content = self.translate_content(source_content)
            return title, content
        except Exception as e:
            print(f"Error in processing content: {e}")
            return self.clean_text(source_title), self.clean_text(source_content)

    @staticmethod
    def clean_text(text):
        try:
            return clean(str(text),
                         fix_unicode=True,  # fix various unicode errors
                         to_ascii=True,  # transliterate to closest ASCII representation
                         lower=True,
                         no_emails=True,  # remove emails
                         no_urls=True,  # remove urls
                         normalize_whitespace=True).strip(" ")
        except Exception as e:
            print(f"Error in cleaning text: {e}")
            return None

    def analyze_sentiment(self, text):
        try:
            sentiment = sia.polarity_scores(text)
            sentiment_compound = sentiment["compound"]
            sentiment_neu = sentiment["neu"]
            sentiment_neg = sentiment["neg"]
            sentiment_pos = sentiment["pos"]
            return sentiment_compound, sentiment_neu, sentiment_neg, sentiment_pos
        except Exception as e:
            print("error in sentiment analysis : ", e)
            return None, None, None, None

    def get_data_from_openai(self, resp):
        try:
            text_obj = {"keywords": str(resp['keywords']), "title": str(resp['title']), "content": str(resp['content'].split("\n\n")[0])}
            resp_openai = openai_extract_info(text_obj=text_obj)
            first_index = resp_openai.find('{')
            last_index = resp_openai.rfind('}')
            resp_openai = resp_openai[first_index:last_index+1]
            resp_dict = json.loads(resp_openai)
            resp_dict['people'] = [i.get('people') for i in resp_dict['people_sentiment'] if i.get('people')]
            resp_dict['keywords'] = [i.get('keyword') for i in resp_dict['keywords_sentiment'] if i.get('keyword')]

            return resp_dict
        except Exception as e:
            print(f"Error in openai : {e}")
            return {}

    def get_article(self, url):
        exists = Article.objects.filter(source_url=url).exists()
        if exists:
            print("This url already exists and scrapped before --> ", url)
            return {}
        print(f"fetching news for {url}")
        article, source_title, source_content, keywords = self.get_data_from_web(url)
        if not all([article, source_title, source_content, keywords]):
            return {}
        print(f"fetched")
        print(f"processing news translation")

        title, content = self.process_content(source_title=source_title, source_content=source_content)
        print(f"done")
        print(f"openai analysis")

        resp_openai = self.get_data_from_openai({
            "title": title,
            "content": content,
            "keywords": keywords
        })
        print(f"done")

        if resp_openai.get('overall_sentiment', None):
            sentiment_compound = float(resp_openai['overall_sentiment'])
        else:
            sentiment_compound, sentiment_neu, sentiment_neg, sentiment_pos = self.analyze_sentiment(
                str(title) + " | " + str(content))

        date_publish = article.date_publish if article.date_publish else datetime.datetime.now()
        date_publish = timezone.make_aware(date_publish, timezone=timezone.get_current_timezone())
        return {
            "author": article.authors if article.authors else [],
            "publication": article.source_domain if article.source_domain else None,
            "category": resp_openai.get("category", []),
            "location": resp_openai.get("locations", []),
            "country": resp_openai.get("country", []),
            "state": resp_openai.get("state", []),
            "city": resp_openai.get("city", []),
            "keywords": keywords,
            "tags": resp_openai.get("tags", []),
            "people": resp_openai.get("people", []),
            "people_sentiment": resp_openai.get("people_sentiment", []),
            "keywords_sentiment": resp_openai.get("keywords_sentiment", []),
            "title": title,
            "content": content,
            "source_title": source_title,
            "source_content": source_content,
            "source_language": article.language if article.language else None,
            "source_url": url,
            "image_url": article.image_url if article.image_url else None,
            "sentiment_compound": sentiment_compound,
            "date_publish": date_publish,
            "is_tweet": False
        }

# Usage
# scraper = WebScraper()
# result = scraper.get_article('https://example.com')