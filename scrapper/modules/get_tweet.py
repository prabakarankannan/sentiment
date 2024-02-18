import datetime
import json
import os
import nltk
from django.utils import timezone
from django.conf import settings
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from newsplease import NewsPlease
from scrapper.models import Article
from scrapper.modules.helpers import topic_extract, translate_text, search_keywords, get_target_keywords, detect_language, translate_text_v2
from scrapper.modules.openai_connetor import openai_extract_info
from cleantext import clean

nltk.data.path.append(os.path.join(settings.BASE_DIR, 'storage'))
try:
    sia = SentimentIntensityAnalyzer()
except LookupError:
    nltk.download("vader_lexicon", download_dir=os.path.join(settings.BASE_DIR, 'storage'))
    sia = SentimentIntensityAnalyzer()


class ProcessTweet:
    def __init__(self, target_keywords, target_states):
        self.target_keywords = target_keywords
        self.target_states = target_states
        self.source_language = 'auto'

    def find_keywords(self, source_content, target_keywords):
        try:
            keywords = search_keywords(source_content=source_content, source_title="",
                                       title="", target_keywords=target_keywords)
            print("keuwords found", keywords)
            return keywords
        except Exception as e:
            print(" error in find keyword package : ", e)
            return []

    def translate_content(self, source_content):
        content_list = []
        for each_content in source_content.split("\n"):
            if each_content.strip():
                trans_text = self.translate_text(each_content.strip())
                self.source_language = trans_text['source_language']
                translated_text = trans_text['translated_text']
                en = translated_text
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
            trans_text = translate_text_v2(text=text, target_language='en')
            return trans_text
        except Exception as e:
            print("Unable to translate text:", e)
            return None

    def process_content(self, source_content):
        try:
            content = self.translate_content(source_content)
            return content
        except Exception as e:
            print(f"Error in processing content: {e}")
            return self.clean_text(source_content)

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
            text_obj = {"keywords": str(resp['keywords']), "content": str(resp['content'].split("\n\n")[0])}
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

    def get_tweets(self, tweet_obj):
        url = tweet_obj.get('source_url', None)
        if url is None:
            print("source url not found")
            return {}
        exists = Article.objects.filter(source_url=url, is_tweet=True).exists()
        if exists:
            print("This url already exists and scrapped before --> ", url)
            return {}
        print("processing tweet")
        source_content = tweet_obj.get("source_content")

        keywords = self.find_keywords(source_content=source_content, target_keywords=self.target_keywords)
        if not keywords:
            keywords = tweet_obj.get("keywords", [])

        print("translating content")
        content = self.process_content(source_content=tweet_obj.get('source_content', None))
        resp_openai = self.get_data_from_openai({
            "content": content,
            "keywords": keywords
        })
        print("translation done")

        if resp_openai.get('overall_sentiment', None):
            sentiment_compound = float(resp_openai['overall_sentiment'])
        else:
            sentiment_compound, sentiment_neu, sentiment_neg, sentiment_pos = self.analyze_sentiment(str(content))

        date_publish = tweet_obj.get("date_publish")
        if date_publish:
            # date_string = "Nov 17, 2023 · 1:53 AM UTC"
            # Define the format of the date string
            date_format = "%b %d, %Y · %I:%M %p %Z"

            # Parse the string into a naive datetime object
            naive_datetime = datetime.datetime.strptime(date_publish, date_format)

            # Convert the naive datetime to a timezone-aware datetime
            date_publish = timezone.make_aware(naive_datetime, timezone=timezone.utc)
        else:
            date_publish = timezone.make_aware(datetime.datetime.now(), timezone=timezone.get_current_timezone())
        print("process complete")
        return {
            "author": [tweet_obj.get("author")] if tweet_obj.get("author") else [],
            "publication": tweet_obj.get("publication") if tweet_obj.get("publication") else None,
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
            "title": None,
            "content": content,
            "source_title": None,
            "source_content": source_content,
            "source_language": self.source_language if self.source_language else None,
            "source_url": url,
            "image_url": None,
            "sentiment_compound": sentiment_compound,
            "date_publish": date_publish,
            "is_tweet": True
        }

# Usage
# scraper = WebScraper()
# result = scraper.get_article('https://example.com')