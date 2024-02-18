import random

from django.shortcuts import render
from django.db.models import Count, Q
from django.db.models.functions import Trunc
from rest_framework import viewsets
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.utils.text import slugify
from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse
from rest_framework import status
from api.serializers import SentimentTrendSerializer, KeywordSerializer, TargetURLSerializer
from datetime import datetime, timedelta
from django.utils import timezone
from scrapper.models import Keyword, TargetURL, Article, Publication, State, City, Tag, KeywordSentiment, \
    PeopleSentiment, People
import pandas as pd
import json
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import action
from rest_framework import viewsets, filters
from api.helpers import human_format, datetime_to_hour, convert_to_unix_datetime
from django.db.models import F, Value, CharField
from django.db.models.functions import Cast, Concat
from django.db.models import Count, Case, When, IntegerField
from django.db.models import Avg, Case, When, Value, F, IntegerField, FloatField, ExpressionWrapper
from django.db.models.functions import TruncHour
from django.db.models import F
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Max
from django.utils import timezone
from django.template.defaultfilters import timesince
import pandas as pd
from datetime import datetime, timezone
from .helpers import get_current_time


def index(request):
    # Step 1: Get counts and data
    # total_news_website = TargetURL.objects.filter(is_active=True).values_list('domain', flat=True).distinct()
    # unique_domain_count = len(total_news_website)
    articles_queryset = Article.objects.filter(keywords__is_enable=True)
    total_news_scrapped = articles_queryset.filter(is_tweet=False).count()
    total_tweets_scrapped = articles_queryset.filter(is_tweet=True).count()

    top_states = articles_queryset.values('state__name').annotate(volume=Count('id')).order_by('-volume')[0]

    top_state_name = str(top_states['state__name']).title()
    # total_active_keywords = Keyword.objects.filter(is_enable=True).count()

    # Step 2: Get all active keywords
    # active_keywords = Keyword.objects.filter(is_enable=True)
    keyword_data = []
    # Assuming KeywordSentiment is the name of your model
    keyword_sentiment_averages = KeywordSentiment.objects.filter(keyword__is_enable=True).values('keyword__name').annotate(
        overall_avg_percent=ExpressionWrapper(
            (Avg('sentiment_score') + 1) * 50,  # Map [-1, 1] to [0, 100]
            output_field=FloatField()
        )
    )

    for keyword_sentiment_average in keyword_sentiment_averages:
        keyword_name = keyword_sentiment_average['keyword__name']
        article_keyword = Article.objects.filter(keywords__name=keyword_name)
        if article_keyword.exists():
            total_count = article_keyword.count()
            overall_avg_percent = keyword_sentiment_average['overall_avg_percent']

            # print(f"Keyword: {keyword_name}")
            keyword_sentiments = KeywordSentiment.objects.filter(keyword__name=keyword_name)
            avg_positive = keyword_sentiments.filter(sentiment_score__gt=0, sentiment_score__lte=1).aggregate(
                avg_positive=Avg('sentiment_score'))['avg_positive'] or 0
            avg_negative = keyword_sentiments.filter(sentiment_score__gte=-1, sentiment_score__lt=0).aggregate(
                avg_negative=Avg('sentiment_score'))['avg_negative'] or 0
            avg_neutral = keyword_sentiments.filter(sentiment_score=0).aggregate(avg_neutral=Avg('sentiment_score'))[
                              'avg_neutral'] or 0

            keyword_info = {
                "keyword": keyword_name,
                "overall_avg_percent":overall_avg_percent,
                "avg_positive":avg_positive,
                "avg_negative":avg_negative,
                "avg_neutral":avg_neutral,
                "total_volume": total_count
            }

            # print(keyword.name, positive, negative, neutral, keyword_info['sentiment'], max_sentiment)
            # keyword_data.append(keyword_info)

            # Step 5: Get the last recent hour of each keyword
            if article_keyword.exists():
                last_hour = article_keyword.filter(keywords__is_enable=True).order_by('-created_on').values('created_on').first()['created_on']
                keyword_info[
                    'recent_scrapped'] = f'{int((get_current_time() - last_hour).total_seconds() / 3600)} hours ago'
            else:
                keyword_info['recent_scrapped'] = 'No data yet'

            keyword_data.append(keyword_info)

    keyword_data_table = sorted(keyword_data, key=lambda x: x['avg_positive'], reverse=True)

    df = pd.DataFrame(keyword_data_table)
    df = df.round(2)
    keyword_data_table = df.to_dict(orient="records")

    # people_data = []
    # # Assuming KeywordSentiment is the name of your model
    # people_sentiment_averages = PeopleSentiment.objects.values('people__name').annotate(
    #     overall_avg_percent=ExpressionWrapper(
    #         (Avg('sentiment_score') + 1) * 50,  # Map [-1, 1] to [0, 100]
    #         output_field=FloatField()
    #     )
    # )
    #
    # for people_sentiment_average in people_sentiment_averages:
    #     people_name = people_sentiment_average['people__name']
    #     # print(people_name)
    #     article_people = Article.objects.filter(people__name=people_name)
    #     if article_people.exists():
    #         people_total_count = article_people.count()
    #         people_overall_avg_percent = people_sentiment_average['overall_avg_percent']
    #
    #         # print(f"Keyword: {people_name}")
    #         people_sentiments = PeopleSentiment.objects.filter(people__name=people_name)
    #         people_avg_positive = people_sentiments.filter(sentiment_score__gt=0, sentiment_score__lte=1).aggregate(
    #             people_avg_positive=Avg('sentiment_score'))['people_avg_positive'] or 0
    #         people_avg_negative = people_sentiments.filter(sentiment_score__gte=-1, sentiment_score__lt=0).aggregate(
    #             people_avg_negative=Avg('sentiment_score'))['people_avg_negative'] or 0
    #         people_avg_neutral = people_sentiments.filter(sentiment_score=0).aggregate(
    #             people_avg_neutral=Avg('sentiment_score'))[
    #                           'people_avg_neutral'] or 0
    #
    #         people_info = {
    #             "people": people_name.strip(),
    #             "people_avg_positive":people_avg_positive,
    #             "people_avg_neutral":people_avg_neutral,
    #             "people_avg_negative":people_avg_negative,
    #             "people_overall_avg_percent":people_overall_avg_percent,
    #             "people_total_volume": people_total_count
    #         }
    #
    #         # print(keyword.name, positive, negative, neutral, keyword_info['sentiment'], max_sentiment)
    #         # keyword_data.append(keyword_info)
    #
    #         # Step 5: Get the last recent hour of each keyword
    #         if article_people.exists():
    #             last_hour = article_people.order_by('-created_on').values('created_on').first()['created_on']
    #             people_info[
    #                 'people_recent_scrapped'] = f'{int((get_current_time() - last_hour).total_seconds() / 3600)} hours ago'
    #         else:
    #             people_info['people_recent_scrapped'] = 'No data yet'
    #
    #         people_data.append(people_info)
    #
    # people_data_table = sorted(people_data, key=lambda x: x['people_total_volume'], reverse=True)
    #
    # people_df = pd.DataFrame(people_data_table)
    # people_df = people_df.round(2)
    # people_data_table = people_df.to_dict(orient="records")[:10]
    #
    # keyword_sentiment = {"label": json.dumps(df['keyword'].tolist()), "positive": df['positive'].tolist(),
    #                     "negative": df['negative'].tolist(), "neutral": df['neutral'].tolist()}


    # Step 6: Process sentiment-wise data
    # label, positive_data, negative_data, neutral_data = [], [], [], []
    #
    # for keyword_info in keyword_data_table[:6]:
    #     articles = KeywordSentiment.objects.filter(keyword__name=keyword_info['keyword'])
    #     if articles.exists():
    #         positive_data.append(articles.filter(sentiment_score__gt=0).count())
    #         negative_data.append(articles.filter(sentiment_score__lt=0).count())
    #         neutral_data.append(articles.filter(sentiment_score=0).count())
    #         label.append(keyword_info['keyword'].title())
    #
    # keyword_sentiment = {"label": json.dumps(label), "positive": positive_data, "negative": negative_data,
    #                      "neutral": neutral_data}

    # # Get the top people with the most articles
    # top_people = People.objects.annotate(num_articles=Count('article')).order_by('-num_articles')[:6]
    #
    # # Extract names from the queryset
    # top_people_names = [person.name for person in top_people]
    #
    # people_label, people_positive_data, people_negative_data, people_neutral_data = [], [], [], []
    #
    # for people_name in top_people_names:
    #     articles = PeopleSentiment.objects.filter(people__name=people_name)
    #     if articles.exists():
    #         people_positive_count = articles.filter(sentiment_score__gt=0).count()
    #         people_negative_count = articles.filter(sentiment_score__lt=0).count()
    #         people_neutral_count = articles.filter(sentiment_score=0).count()
    #
    #         ppl_total_count = people_positive_count + people_negative_count + people_neutral_count
    #         ppl_positive = int((people_positive_count / ppl_total_count) * 100)
    #         ppl_negative = int((people_negative_count / ppl_total_count) * 100)
    #         ppl_neutral = int((people_neutral_count / ppl_total_count) * 100)
    #
    #         people_positive_data.append(ppl_positive)
    #         people_negative_data.append(ppl_negative)
    #         people_neutral_data.append(ppl_neutral)
    #         people_label.append(people_name.title())
    #
    # people_sentiment = {"label": json.dumps(people_label), "positive": people_positive_data,
    #                     "negative": people_negative_data, "neutral": people_neutral_data}

    # Step 8: Prepare context
    context = {
        "total_volume": total_news_scrapped + total_tweets_scrapped,
        'total_news_scrapped': total_news_scrapped,
        'total_tweets_scrapped': total_tweets_scrapped,
        'top_state_name': top_state_name,
        "keyword_data_table": keyword_data_table,
        # "people_data_table":people_data_table
        # "keyword_sentiment_graph": keyword_sentiment,
        # "people_sentiment_graph": people_sentiment,
        # add more data as needed
    }

    return render(request, 'django-website/index.html', context)


def realtime_page(request):
    # Calculate the start time for the last 6 hours
    six_hours_ago = get_current_time() - timedelta(hours=6)
    articles_queryset = Article.objects.filter(
        created_on__gte=six_hours_ago,
    )
    # news, tweet, facebook count
    news_count = articles_queryset.filter(is_tweet=False).count()
    tweet_count = articles_queryset.filter(is_tweet=True).count()
    total_volume = articles_queryset.count()

    facebook_count = 0

    # Calculate the counts and graphs for each keyword
    keyword_data = []
    # Assuming KeywordSentiment is the name of your model
    keyword_sentiment_averages = KeywordSentiment.objects.filter(
        article__created_on__gte=six_hours_ago, keyword__is_enable=True
    ).values('keyword__name').annotate(
        overall_avg=Avg('sentiment_score', output_field=FloatField()),
        overall_avg_percent=ExpressionWrapper(
            (Avg('sentiment_score') + 1) * 50,  # Map [-1, 1] to [0, 100]
            output_field=FloatField()
        )
    )

    for keyword_sentiment_average in keyword_sentiment_averages:
        keyword_name = keyword_sentiment_average['keyword__name']
        total_count = articles_queryset.filter(keywords__name=keyword_name)
        if total_count.exists():
            total_count = total_count.count()
            overall_avg_percent = keyword_sentiment_average['overall_avg_percent']
            overall_avg = keyword_sentiment_average['overall_avg']

            # print(f"Keyword: {keyword_name}")
            keyword_sentiments = KeywordSentiment.objects.filter(keyword__name=keyword_name)
            avg_positive = keyword_sentiments.filter(sentiment_score__gt=0, sentiment_score__lte=1).aggregate(
                avg_positive=Avg('sentiment_score'))['avg_positive'] or 0
            avg_negative = keyword_sentiments.filter(sentiment_score__gte=-1, sentiment_score__lt=0).aggregate(
                avg_negative=Avg('sentiment_score'))['avg_negative'] or 0
            avg_neutral = keyword_sentiments.filter(sentiment_score=0).aggregate(avg_neutral=Avg('sentiment_score'))[
                              'avg_neutral'] or 0

            keyword_info = {
                "keyword": keyword_name,
                "overall_avg_percent":overall_avg_percent,
                "overall_avg":overall_avg,
                "avg_positive":avg_positive,
                "avg_negative":avg_negative,
                "avg_neutral":avg_neutral,
                "total_count": total_count
            }

            keyword_data.append(keyword_info)

    keyword_data_table = sorted(keyword_data, key=lambda x: x['avg_positive'], reverse=True)

    df = pd.DataFrame(keyword_data_table)
    df = df.round(2)
    keyword_data_table = df.to_dict(orient='records')

    keyword_counts = articles_queryset.prefetch_related('keywords') \
        .values('keywords__name') \
        .annotate(keyword_count=Count('id', filter=Q(keywords__isnull=False))) \
        .order_by('-keyword_count')

    # Similarly, count the occurrences for other fields, and add the filter condition
    # location_counts = articles_queryset.prefetch_related('location') \
    #     .values('location__name') \
    #     .annotate(location_count=Count('id', filter=Q(location__isnull=False))) \
    #     .order_by('-location__name')

    state_counts = articles_queryset.prefetch_related('state') \
        .values('state__name') \
        .annotate(state_count=Count('id', filter=Q(state__isnull=False))) \
        .order_by('-state__name')

    # city_counts = articles_queryset.prefetch_related('city') \
    #     .values('city__name') \
    #     .annotate(city_count=Count('id', filter=Q(city__isnull=False))) \
    #     .order_by('-city__name')

    # country_counts = articles_queryset.prefetch_related('country') \
    #     .values('country__name') \
    #     .annotate(country_count=Count('id', filter=Q(country__isnull=False))) \
    #     .order_by('-country__name')

    tags_counts = articles_queryset.prefetch_related('tags') \
        .values('tags__name') \
        .annotate(tags_count=Count('id', filter=Q(tags__isnull=False))) \
        .order_by('-tags__name')

    people_counts = articles_queryset.prefetch_related('people') \
        .values('people__name') \
        .annotate(people_count=Count('id', filter=Q(people__isnull=False))) \
        .order_by('-people__name')

    keyword_data_count = [{"key": entry['keywords__name'].replace("'", ""), "value": entry['keyword_count']} for entry
                          in keyword_counts
                          if
                          entry['keywords__name'] is not None and entry['keyword_count'] is not None]

    # location_data = [{"key": entry['location__name'].replace("'", ""), "value": entry['location_count']} for entry in
    #                  location_counts if
    #                  entry['location__name'] is not None and entry['location_count'] is not None]

    state_data = [{"key": entry['state__name'].replace("'", ""), "value": entry['state_count']} for entry in
                  state_counts if
                  entry['state__name'] is not None and entry['state_count'] is not None]

    # city_data = [{"key": entry['city__name'].replace("'", ""), "value": entry['city_count']} for entry in city_counts if
    #              entry['city__name'] is not None and entry['city_count'] is not None]

    # country_data = [{"key": entry['country__name'].replace("'", ""), "value": entry['country_count']} for entry in
    #                 country_counts if
    #                 entry['country__name'] is not None and entry['country_count'] is not None]
    tags_data = [{"key": entry['tags__name'].replace("'", ""), "value": entry['tags_count']} for entry in tags_counts if
                 entry['tags__name'] is not None and entry['tags_count'] is not None]
    people_data = [{"key": entry['people__name'].replace("'", ""), "value": entry['people_count']} for entry in
                   people_counts if
                   entry['people__name'] is not None and entry['people_count'] is not None]
    # category_data = [{"key": entry['category__name'].replace("'", ""), "value": entry['category_count']} for entry in
    #                  category_counts if
    #                  entry['category__name'] is not None and entry['category_count'] is not None]
    # author_data = [{"key": entry['author__name'].replace("'", ""), "value": entry['author_count']} for entry in author_counts if
    #                entry['author__name'] is not None and entry['author_count'] is not None]

    # context = {}

    data_dict = {
        'keywords': keyword_data_count,
        # 'locations': location_data,
        'states': state_data,
        # 'cities': city_data,
        # 'countries': country_data,
        'tags': tags_data,
        'people': people_data,
        # 'categories': category_data,
        # 'authors': author_data
    }

    all_words = []
    for key, data in data_dict.items():
        if data:
            all_words += data

    all_words = sorted(all_words, key=lambda x: x['value'], reverse=True)


    context = {
        "cards": {
            "news_count": news_count,
            "tweet_count": tweet_count,
            "facebook_count": facebook_count,
            "total_count": total_volume
        },
        "word_cloud": json.dumps(all_words[:200]) if all_words else json.dumps(["No data found in last 6 hours"]),
        "table": keyword_data_table,
        "pie_chart": {
            "keyword": df['keyword'].tolist() if "keyword" in df.columns else [],
            "positive": df['positive'].tolist() if "positive" in df.columns else [],
            "negative": df['negative'].tolist() if "negative" in df.columns else [],
            "neutral": df['neutral'].tolist() if "neutral" in df.columns else []
        }
    }
    # print(all_words[:20])
    return render(request, 'django-website/realtime.html', context)


def keywords_page(request):
    # Calculate the start time for the last 6 hours
    keyword_obj = Keyword.objects.all()
    active_kw_count = keyword_obj.filter(is_enable=True).count()
    inactive_kw_count = keyword_obj.filter(is_enable=False).count()
    total_kw_count = keyword_obj.count()

    top_keywords = Article.objects.values('keywords__name').annotate(volume=Count('id')).order_by('-volume')[0]
    top_keyword_name = str(top_keywords['keywords__name']).title()

    context = {
        "active_kw_count":active_kw_count,
        "inactive_kw_count":inactive_kw_count,
        "total_kw_count":total_kw_count,
        "top_keyword_name":top_keyword_name
    }

    return render(request, 'django-website/keywords.html', context)


def historic_page(request):
    # Calculate the start time for the last 6 hours
    context = {
        # "active_kw_count":active_kw_count,
        # "inactive_kw_count":inactive_kw_count,
        # "total_kw_count":total_kw_count,
        # "top_keyword_name":top_keyword_name
    }

    return render(request, 'django-website/historic.html', context)


def targeted_area_page(request):
    state_dict = {
        'uttar pradesh': 'IN-UP',
        'maharashtra': 'IN-MH',
        'bihar': 'IN-BR',
        'west bengal': 'IN-WB',
        'madhya pradesh': 'IN-MP',
        'tamil nadu': 'IN-TN',
        'rajasthan': 'IN-RJ',
        'karnataka': 'IN-KA',
        'gujarat': 'IN-GJ',
        'andhra pradesh': 'IN-AP',
        'orissa': 'IN-OR',
        'telangana': 'IN-TG',
        'kerala': 'IN-KL',
        'jharkhand': 'IN-JH',
        'assam': 'IN-AS',
        'punjab': 'IN-PB',
        'chhattisgarh': 'IN-CT',
        'haryana': 'IN-HR',
        'jammu and kashmir': 'IN-JK',
        'uttarakhand': 'IN-UT',
        'himachal pradesh': 'IN-HP',
        'tripura': 'IN-TR',
        'meghalaya': 'IN-ML',
        'manipur': 'IN-MN',
        'nagaland': 'IN-NL',
        'goa': 'IN-GA',
        'arunachal pradesh': 'IN-AR',
        'mizoram': 'IN-MZ',
        'sikkim': 'IN-SK',
        'delhi': 'IN-DL',
        'puducherry': 'IN-PY',
        'chandigarh': 'IN-CH',
        'andaman and nicobar islands': 'IN-AN',
        'dadra and nagar haveli': 'IN-DN',
        'daman and diu': 'IN-DD',
        'lakshadweep': 'IN-LD'
    }

    # Calculate the start time for the last 6 hours
    state_article_counts = Article.objects.values('state__name').annotate(volume=Count('id')).order_by('-volume')

    # Create the output format
    output_format = [['State Code', 'State', 'Volume']]

    for state_count in state_article_counts:
        state_name = str(state_count['state__name']).title()
        state_code = state_dict.get(state_name.lower(), None)

        if state_code is None:
            # If the state code is not in the dictionary, generate it
            state_code = "IN-" + slugify(state_name)[:3].upper()

        volume = state_count['volume']
        output_format.append([state_code, state_name, volume])

    context = {"state_volume": output_format}

    return render(request, 'django-website/target-area.html', context)


def realtime_page_jquery(request):
    # Calculate the start time for the last 6 hours
    six_hours_ago = get_current_time() - timedelta(hours=6)
    articles_queryset = Article.objects.filter(
        created_on__gte=six_hours_ago,
    )
    # news, tweet, facebook count
    news_count = articles_queryset.filter(is_tweet=False).count()
    tweet_count = articles_queryset.filter(is_tweet=True).count()
    total_volume = articles_queryset.count()
    facebook_count = 0

    # Calculate the counts and graphs for each keyword
    keyword_data = []
    # Assuming KeywordSentiment is the name of your model
    keyword_sentiment_averages = KeywordSentiment.objects.filter(
        article__created_on__gte=six_hours_ago, keyword__is_enable=True
    ).values('keyword__name').annotate(
        overall_avg=Avg('sentiment_score', output_field=FloatField()),
        overall_avg_percent=ExpressionWrapper(
            (Avg('sentiment_score') + 1) * 50,  # Map [-1, 1] to [0, 100]
            output_field=FloatField()
        )
    )

    for keyword_sentiment_average in keyword_sentiment_averages:
        keyword_name = keyword_sentiment_average['keyword__name']
        total_count = articles_queryset.filter(keywords__name=keyword_name)
        if total_count.exists():
            total_count = total_count.count()
            overall_avg_percent = keyword_sentiment_average['overall_avg_percent']
            overall_avg = keyword_sentiment_average['overall_avg']

            # print(f"Keyword: {keyword_name}")
            keyword_sentiments = KeywordSentiment.objects.filter(keyword__name=keyword_name)
            avg_positive = keyword_sentiments.filter(sentiment_score__gt=0, sentiment_score__lte=1).aggregate(
                avg_positive=Avg('sentiment_score'))['avg_positive'] or 0
            avg_negative = keyword_sentiments.filter(sentiment_score__gte=-1, sentiment_score__lt=0).aggregate(
                avg_negative=Avg('sentiment_score'))['avg_negative'] or 0
            avg_neutral = keyword_sentiments.filter(sentiment_score=0).aggregate(avg_neutral=Avg('sentiment_score'))[
                              'avg_neutral'] or 0

            keyword_info = {
                "keyword": keyword_name,
                "overall_avg_percent":overall_avg_percent,
                "overall_avg":overall_avg,
                "avg_positive":avg_positive,
                "avg_negative":avg_negative,
                "avg_neutral":avg_neutral,
                "total_count": total_count
            }

            keyword_data.append(keyword_info)

    keyword_data_table = sorted(keyword_data, key=lambda x: x['avg_positive'], reverse=True)

    df = pd.DataFrame(keyword_data_table)
    df = df.round(2)
    # df.sort_values(by="total_count", ascending=False)
    keyword_data_table = df.to_dict(orient='records')

    keyword_counts = articles_queryset.prefetch_related('keywords') \
        .values('keywords__name') \
        .annotate(keyword_count=Count('id', filter=Q(keywords__isnull=False))) \
        .order_by('-keyword_count')

    # Similarly, count the occurrences for other fields, and add the filter condition
    # location_counts = articles_queryset.prefetch_related('location') \
    #     .values('location__name') \
    #     .annotate(location_count=Count('id', filter=Q(location__isnull=False))) \
    #     .order_by('-location__name')
    #
    state_counts = articles_queryset.prefetch_related('state') \
        .values('state__name') \
        .annotate(state_count=Count('id', filter=Q(state__isnull=False))) \
        .order_by('-state__name')

    # city_counts = articles_queryset.prefetch_related('city') \
    #     .values('city__name') \
    #     .annotate(city_count=Count('id', filter=Q(city__isnull=False))) \
    #     .order_by('-city__name')

    # country_counts = articles_queryset.prefetch_related('country') \
    #     .values('country__name') \
    #     .annotate(country_count=Count('id', filter=Q(country__isnull=False))) \
    #     .order_by('-country__name')

    tags_counts = articles_queryset.prefetch_related('tags') \
        .values('tags__name') \
        .annotate(tags_count=Count('id', filter=Q(tags__isnull=False))) \
        .order_by('-tags__name')

    people_counts = articles_queryset.prefetch_related('people') \
        .values('people__name') \
        .annotate(people_count=Count('id', filter=Q(people__isnull=False))) \
        .order_by('-people__name')

    keyword_data_count = [{"key": entry['keywords__name'].replace("'", ""), "value": entry['keyword_count']} for entry
                          in keyword_counts
                          if
                          entry['keywords__name'] is not None and entry['keyword_count'] is not None]

    # location_data = [{"key": entry['location__name'].replace("'", ""), "value": entry['location_count']} for entry in
    #                  location_counts if
    #                  entry['location__name'] is not None and entry['location_count'] is not None]

    state_data = [{"key": entry['state__name'].replace("'", ""), "value": entry['state_count']} for entry in
                  state_counts if
                  entry['state__name'] is not None and entry['state_count'] is not None]

    # city_data = [{"key": entry['city__name'].replace("'", ""), "value": entry['city_count']} for entry in city_counts if
    #              entry['city__name'] is not None and entry['city_count'] is not None]

    # country_data = [{"key": entry['country__name'].replace("'", ""), "value": entry['country_count']} for entry in
    #                 country_counts if
    #                 entry['country__name'] is not None and entry['country_count'] is not None]
    tags_data = [{"key": entry['tags__name'].replace("'", ""), "value": entry['tags_count']} for entry in tags_counts if
                 entry['tags__name'] is not None and entry['tags_count'] is not None]
    people_data = [{"key": entry['people__name'].replace("'", ""), "value": entry['people_count']} for entry in
                   people_counts if
                   entry['people__name'] is not None and entry['people_count'] is not None]
    # category_data = [{"key": entry['category__name'].replace("'", ""), "value": entry['category_count']} for entry in
    #                  category_counts if
    #                  entry['category__name'] is not None and entry['category_count'] is not None]
    # author_data = [{"key": entry['author__name'].replace("'", ""), "value": entry['author_count']} for entry in author_counts if
    #                entry['author__name'] is not None and entry['author_count'] is not None]

    # context = {}

    data_dict = {
        'keywords': keyword_data_count,
        # 'locations': location_data,
        'states': state_data,
        # 'cities': city_data,
        # 'countries': country_data,
        'tags': tags_data,
        'people': people_data,
        # 'categories': category_data,
        # 'authors': author_data
    }

    all_words = []
    for key, data in data_dict.items():
        if data:
            all_words += data
    all_words = sorted(all_words, key=lambda x: x['value'], reverse=True)
    context = {
        "cards": {
            "news_count": news_count,
            "tweet_count": tweet_count,
            "facebook_count": facebook_count,
            "total_count": total_volume
        },
        "word_cloud": json.dumps(all_words[:200]) if all_words else json.dumps(["No data found in last 6 hours"]),
        "table": keyword_data_table,
        "pie_chart": {
            "keyword": df['keyword'].tolist() if "keyword" in df.columns else [],
            "positive": df['positive'].tolist() if "positive" in df.columns else [],
            "negative": df['negative'].tolist() if "negative" in df.columns else [],
            "neutral": df['neutral'].tolist() if "neutral" in df.columns else []
        }
    }
    # print(all_words[:20])
    return JsonResponse(context)


class KeywordWiseSentimentViewSet(viewsets.ViewSet):

    def list(self, request):
        articles_queryset = KeywordSentiment.objects.all()

        # Calculate the counts and graphs for each keyword
        keyword_data = {
            "labels": [],
            "datasets": [
                {
                    "label": "Positive",
                    "data": [],
                    "backgroundColor": "rgba(75, 192, 192, 0.5)",
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 1,
                },
                {
                    "label": "Negative",
                    "data": [],
                    "backgroundColor": "rgba(255, 99, 132, 0.5)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1,
                },
                {
                    "label": "Neutral",
                    "data": [],
                    "backgroundColor": "rgba(255, 205, 86, 0.5)",
                    "borderColor": "rgba(255, 205, 86, 1)",
                    "borderWidth": 1,
                },
            ],
        }

        for keyword in Keyword.objects.filter(is_enable=True):
            articles = articles_queryset.filter(
                keywords=keyword,
            )

            positive_count = articles.filter(
                is_tweet=False,
                sentiment_score__gt=0,
            ).count()

            negative_count = articles.filter(
                is_tweet=False,
                sentiment_score__lt=-0,
            ).count()

            neutral_count = articles.filter(
                is_tweet=False,
                sentiment_score=0,
            ).count()

            keyword_data["labels"].append(keyword.name)
            keyword_data["datasets"][0]["data"].append(positive_count)
            keyword_data["datasets"][1]["data"].append(negative_count)
            keyword_data["datasets"][2]["data"].append(neutral_count)

        return Response(keyword_data)


class RealtimePageViewSet(viewsets.ViewSet):
    serializer_class = SentimentTrendSerializer

    def list(self, request):
        # Calculate the start time for the last 6 hours
        six_hours_ago = get_current_time() - timedelta(hours=6)
        articles_queryset = Article.objects.filter(
            created_on__gte=six_hours_ago,
        )
        # news, tweet, facebook count
        news_count = articles_queryset.filter(is_tweet=False).count()
        tweet_count = articles_queryset.filter(is_tweet=True).count()
        facebook_count = 0

        # Calculate the counts and graphs for each keyword
        keyword_data = []
        for keyword in Keyword.objects.filter(is_enable=True):
            articles = articles_queryset.filter(
                keywords=keyword,
            )

            positive_count = articles.filter(
                is_tweet=False,
                keywordsentiment__sentiment_score__gt=0,
            ).count()

            negative_count = articles.filter(
                is_tweet=False,
                keywordsentiment__sentiment_score__lt=-0,
            ).count()

            neutral_count = articles.filter(
                is_tweet=False,
                keywordsentiment__sentiment_score=0,
            ).count()

            # Get the current time
            current_time = get_current_time()

            # Create a list of the hours for the last 6 hours
            hour_list = [current_time - timedelta(hours=i) for i in range(6)]

            # Extract the hour component from each datetime object in the list
            hour_list = [hour.hour for hour in hour_list]

            hour_counts = []

            for hour in hour_list:
                # Calculate the count of articles for the current hour
                count = articles.filter(
                    is_tweet=False,
                    created_on__hour=hour
                ).count()

                hour_counts.append({"hour": hour, "count": count})

            keyword_info = {
                "keyword": keyword.name,
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
                "total_count_each_hour": hour_counts
            }

            keyword_data.append(keyword_info)

        # Now you have the data for each keyword in the desired format

        # for each keyword what are the positive / negative / neutral count for tweet false and tweet true
        # Use aggregation to count the occurrence of each keyword across all articles
        keyword_counts = Article.objects.filter(
            created_on__gte=six_hours_ago
        ).prefetch_related('keywords') \
            .values('keywords__name') \
            .annotate(keyword_count=Count('id', filter=Q(keywords__isnull=False))) \
            .order_by('-keyword_count')

        # Similarly, count the occurrences for other fields, and add the filter condition
        location_counts = Article.objects.filter(
            created_on__gte=six_hours_ago
        ).prefetch_related('location') \
            .values('location__name') \
            .annotate(location_count=Count('id', filter=Q(location__isnull=False))) \
            .order_by('-location__name')

        state_counts = Article.objects.filter(
            created_on__gte=six_hours_ago
        ).prefetch_related('state') \
            .values('state__name') \
            .annotate(state_count=Count('id', filter=Q(state__isnull=False))) \
            .order_by('-state__name')

        city_counts = Article.objects.filter(
            created_on__gte=six_hours_ago
        ).prefetch_related('city') \
            .values('city__name') \
            .annotate(city_count=Count('id', filter=Q(city__isnull=False))) \
            .order_by('-city__name')

        country_counts = Article.objects.filter(
            created_on__gte=six_hours_ago
        ).prefetch_related('country') \
            .values('country__name') \
            .annotate(country_count=Count('id', filter=Q(country__isnull=False))) \
            .order_by('-country__name')

        tags_counts = Article.objects.filter(
            created_on__gte=six_hours_ago
        ).prefetch_related('tags') \
            .values('tags__name') \
            .annotate(tags_count=Count('id', filter=Q(tags__isnull=False))) \
            .order_by('-tags__name')

        people_counts = Article.objects.filter(
            created_on__gte=six_hours_ago
        ).prefetch_related('people') \
            .values('people__name') \
            .annotate(people_count=Count('id', filter=Q(people__isnull=False))) \
            .order_by('-people__name')

        category_counts = Article.objects.filter(
            created_on__gte=six_hours_ago
        ).prefetch_related('category') \
            .values('category__name') \
            .annotate(category_count=Count('id', filter=Q(category__isnull=False))) \
            .order_by('-category__name')

        author_counts = Article.objects.filter(
            created_on__gte=six_hours_ago
        ).prefetch_related('author') \
            .values('author__name') \
            .annotate(author_count=Count('id', filter=Q(author__isnull=False))) \
            .order_by('-author_count')

        keyword_data_count = [{"text": entry['keywords__name'], "count": entry['keyword_count']} for entry in
                              keyword_counts if
                              entry['keywords__name'] is not None and entry['keyword_count'] is not None]

        location_data = [{"text": entry['location__name'], "count": entry['location_count']} for entry in
                         location_counts if
                         entry['location__name'] is not None and entry['location_count'] is not None]

        state_data = [{"text": entry['state__name'], "count": entry['state_count']} for entry in state_counts if
                      entry['state__name'] is not None and entry['state_count'] is not None]

        city_data = [{"text": entry['city__name'], "count": entry['city_count']} for entry in city_counts if
                     entry['city__name'] is not None and entry['city_count'] is not None]

        country_data = [{"text": entry['country__name'], "count": entry['country_count']} for entry in country_counts if
                        entry['country__name'] is not None and entry['country_count'] is not None]
        tags_data = [{"text": entry['tags__name'], "count": entry['tags_count']} for entry in tags_counts if
                     entry['tags__name'] is not None and entry['tags_count'] is not None]
        people_data = [{"text": entry['people__name'], "count": entry['people_count']} for entry in people_counts if
                       entry['people__name'] is not None and entry['people_count'] is not None]
        category_data = [{"text": entry['category__name'], "count": entry['category_count']} for entry in
                         category_counts if
                         entry['category__name'] is not None and entry['category_count'] is not None]
        author_data = [{"text": entry['author__name'], "count": entry['author_count']} for entry in author_counts if
                       entry['author__name'] is not None and entry['author_count'] is not None]

        # context = {}

        data_dict = {
            'keywords': keyword_data_count,
            'locations': location_data,
            'states': state_data,
            'cities': city_data,
            'countries': country_data,
            'tags': tags_data,
            'people': people_data,
            'categories': category_data,
            'authors': author_data
        }

        all_words = []
        for key, data in data_dict.items():
            if data:
                all_words += data

        context = {
            "cards": {
                "news_count": news_count,
                "tweet_count": tweet_count,
                "facebook_count": facebook_count
            },
            "word_cloud": all_words[:1000],
            "table": keyword_data
        }

        return Response(data=context)


class ArticleSentimentTrendViewSet(viewsets.ViewSet):
    serializer_class = SentimentTrendSerializer

    def list(self, request):
        context = {"trend": "use post method"}

        return Response(data=context)

    def post(self, request):
        serializer = SentimentTrendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        keywords = serializer.validated_data.get('keywords')
        hour = serializer.validated_data.get('hour', 36)
        timeframe = 'hour'

        enabled_keywords = Keyword.objects.filter(is_enable=True).values_list('id', flat=True)

        # Filter articles based on provided parameters
        articles = Article.objects.filter(keywords__in=enabled_keywords)

        # Default to the last 6 hours if from_date and to_date are not specified
        articles = articles.filter(date_publish__gte=timezone.now() - timedelta(hours=hour))

        if keywords:
            articles = articles.filter(keywords__name__in=keywords)

        articles = articles.annotate(
            time_interval=Trunc('date_publish', 'hour'),
        ).values('time_interval').annotate(
            positive=Count('id', filter=Q(sentiment_compound__gt=0.20)),
            negative=Count('id', filter=Q(sentiment_compound__lt=-0.20)),
            neutral=Count('id', filter=Q(sentiment_compound__gte=-0.20, sentiment_compound__lte=0.20)),
        ).order_by('time_interval')

        context = {
            "category": [each['time_interval'] for each in articles],
            "data": [
                {
                    "name": "Positive",
                    "data": [each['positive'] for each in articles]
                },
                {
                    "name": "Neutral",
                    "data": [each['neutral'] for each in articles]
                },
                {
                    "name": "Negative",
                    "data": [each['negative'] for each in articles]
                }
            ]
        }

        return Response(context)


class WorldCouldViewSet(viewsets.ViewSet):

    def list(self, request):
        # Use aggregation to count the occurrence of each keyword across all articles
        keyword_counts = Article.objects.prefetch_related('keywords') \
            .values('keywords__name') \
            .annotate(keyword_count=Count('id', filter=Q(keywords__isnull=False))) \
            .order_by('-keyword_count')

        # Similarly, count the occurrences for other fields, and add the filter condition
        location_counts = Article.objects.prefetch_related('location') \
            .values('location__name') \
            .annotate(location_count=Count('id', filter=Q(location__isnull=False))) \
            .order_by('-location__name')

        state_counts = Article.objects.prefetch_related('state') \
            .values('state__name') \
            .annotate(state_count=Count('id', filter=Q(state__isnull=False))) \
            .order_by('-state__name')

        city_counts = Article.objects.prefetch_related('city') \
            .values('city__name') \
            .annotate(city_count=Count('id', filter=Q(city__isnull=False))) \
            .order_by('-city__name')

        country_counts = Article.objects.prefetch_related('country') \
            .values('country__name') \
            .annotate(country_count=Count('id', filter=Q(country__isnull=False))) \
            .order_by('-country__name')

        tags_counts = Article.objects.prefetch_related('tags') \
            .values('tags__name') \
            .annotate(tags_count=Count('id', filter=Q(tags__isnull=False))) \
            .order_by('-tags__name')

        people_counts = Article.objects.prefetch_related('people') \
            .values('people__name') \
            .annotate(people_count=Count('id', filter=Q(people__isnull=False))) \
            .order_by('-people__name')

        category_counts = Article.objects.prefetch_related('category') \
            .values('category__name') \
            .annotate(category_count=Count('id', filter=Q(category__isnull=False))) \
            .order_by('-category__name')

        author_counts = Article.objects.prefetch_related('author') \
            .values('author__name') \
            .annotate(author_count=Count('id', filter=Q(author__isnull=False))) \
            .order_by('-author_count')

        keyword_data = [{"text": entry['keywords__name'], "count": entry['keyword_count']} for entry in keyword_counts
                        if
                        entry['keywords__name'] is not None and entry['keyword_count'] is not None]

        location_data = [{"text": entry['location__name'], "count": entry['location_count']} for entry in
                         location_counts if
                         entry['location__name'] is not None and entry['location_count'] is not None]

        state_data = [{"text": entry['state__name'], "count": entry['state_count']} for entry in state_counts if
                      entry['state__name'] is not None and entry['state_count'] is not None]

        city_data = [{"text": entry['city__name'], "count": entry['city_count']} for entry in city_counts if
                     entry['city__name'] is not None and entry['city_count'] is not None]

        country_data = [{"text": entry['country__name'], "count": entry['country_count']} for entry in country_counts if
                        entry['country__name'] is not None and entry['country_count'] is not None]
        tags_data = [{"text": entry['tags__name'], "count": entry['tags_count']} for entry in tags_counts if
                     entry['tags__name'] is not None and entry['tags_count'] is not None]
        people_data = [{"text": entry['people__name'], "count": entry['people_count']} for entry in people_counts if
                       entry['people__name'] is not None and entry['people_count'] is not None]
        category_data = [{"text": entry['category__name'], "count": entry['category_count']} for entry in
                         category_counts if
                         entry['category__name'] is not None and entry['category_count'] is not None]
        author_data = [{"text": entry['author__name'], "count": entry['author_count']} for entry in author_counts if
                       entry['author__name'] is not None and entry['author_count'] is not None]

        context = {}

        data_dict = {
            'keywords': keyword_data,
            'locations': location_data,
            'states': state_data,
            'cities': city_data,
            'countries': country_data,
            'tags': tags_data,
            'people': people_data,
            'categories': category_data,
            'authors': author_data
        }

        for key, data in data_dict.items():
            if data:
                context[key] = data

        return Response(context)


class KeywordViewSet(viewsets.ModelViewSet):
    serializer_class = KeywordSerializer
    queryset = Keyword.objects.all()
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['name', 'is_enable']
    ordering_fields = ['created_on', 'updated_on']
    ordering = ['-created_on']

    def get_queryset(self):
        queryset = super().get_queryset()
        is_enable = self.request.query_params.get('is_enable', None)
        if is_enable is not None:
            # Convert the value to lowercase for case-insensitive filtering
            is_enable = is_enable.lower()
            if is_enable == 'true':
                queryset = queryset.filter(is_enable=True)
            elif is_enable == 'false':
                queryset = queryset.filter(is_enable=False)
        return queryset


class TargetURLViewSet(viewsets.ModelViewSet):
    queryset = TargetURL.objects.all()
    serializer_class = TargetURLSerializer

    @action(detail=False, methods=['POST'])
    def upload_file(self, request):
        parser_classes = (FileUploadParser,)
        file_obj = request.data['file']

        if file_obj.name.endswith('.csv'):
            df = pd.read_csv(file_obj)
        elif file_obj.name.endswith('.xlsx'):
            df = pd.read_excel(file_obj)
        else:
            return Response({'error': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)

        new_urls = []
        existing_urls = set(TargetURL.objects.values_list('url', flat=True))

        for index, row in df.iterrows():
            url = row['url']
            if url not in existing_urls:
                selector = row['selector']
                is_active = row['is_active']
                new_urls.append(TargetURL(url=url, selector=selector, is_active=is_active))

        TargetURL.objects.bulk_create(new_urls)

        return Response({'message': f'{len(new_urls)} rows inserted'}, status=status.HTTP_201_CREATED)


class KeywordSentimentDataViewSet(viewsets.ViewSet):
    def list(self, request):
        # six_months_ago = timezone.now() - timezone.timedelta(days=180)
        keywords = Keyword.objects.filter(is_enable=True).values('id', 'name')

        keyword_sentiment_counts = []

        # articles = Article.objects.all()

        for keyword in keywords:
            articles = Article.objects.filter(keywords=keyword['id'])
            if articles.exists():
                positive_count = articles.filter(sentiment_compound__gte=0.20).count()
                neutral_count = articles.filter(sentiment_compound__gt=-0.20, sentiment_compound__lt=0.20).count()
                negative_count = articles.filter(sentiment_compound__lte=-0.20).count()

                total_count = positive_count + neutral_count + negative_count

                keyword_sentiment_counts.append({
                    "name": keyword['name'],
                    "positive": positive_count,
                    "neutral": neutral_count,
                    "negative": negative_count,
                    "total": total_count
                })

        # Sort the keyword_sentiment_counts by the total count in descending order
        keyword_sentiment_counts = sorted(keyword_sentiment_counts, key=lambda x: x['total'], reverse=True)[:10]

        context = {
            "category": [item["name"] for item in keyword_sentiment_counts],
            "data": [
                {
                    "name": "Positive",
                    "data": [item["positive"] for item in keyword_sentiment_counts]
                },
                {
                    "name": "Neutral",
                    "data": [item["neutral"] for item in keyword_sentiment_counts]
                },
                {
                    "name": "Negative",
                    "data": [item["negative"] for item in keyword_sentiment_counts]
                }
            ]
        }

        return Response(data=context)


class KeywordSentimentTableDataViewSet(viewsets.ViewSet):
    def list(self, request):
        # six_months_ago = timezone.now() - timezone.timedelta(days=180)
        keywords = Keyword.objects.filter(is_enable=True).values('id', 'name')

        keyword_sentiment_counts = []

        # articles = Article.objects.all()

        for keyword in keywords:
            articles = Article.objects.filter(keywords=keyword['id'])
            if articles.exists():
                positive_count = articles.filter(sentiment_compound__gte=0.20).count()
                neutral_count = articles.filter(sentiment_compound__gt=-0.20, sentiment_compound__lt=0.20).count()
                negative_count = articles.filter(sentiment_compound__lte=-0.20).count()

                total_count = positive_count + neutral_count + negative_count

                keyword_sentiment_counts.append({
                    "name": keyword['name'],
                    "positive": positive_count,
                    "neutral": neutral_count,
                    "negative": negative_count,
                    "total": total_count
                })

        # Sort the keyword_sentiment_counts by the total count in descending order
        context = sorted(keyword_sentiment_counts, key=lambda x: x['total'], reverse=True)

        return Response(data=context)


class PublicationAndStateSentimentDataViewSet(viewsets.ViewSet):
    def list(self, request):
        keywords = Keyword.objects.filter(is_enable=True)

        # six_months_ago = timezone.now() - timezone.timedelta(days=180)
        publications = Publication.objects.all().values('id', 'name')

        publication_sentiment_counts = []

        # articles = Article.objects.all()

        for publication in publications:
            articles = Article.objects.filter(publication=publication['id'], keywords__in=keywords, is_tweet=False)
            if articles.exists():
                positive_count = articles.filter(sentiment_compound__gte=0.20).count()
                neutral_count = articles.filter(sentiment_compound__gt=-0.20, sentiment_compound__lt=0.20).count()
                negative_count = articles.filter(sentiment_compound__lte=-0.20).count()

                total_count = positive_count + neutral_count + negative_count

                publication_sentiment_counts.append({
                    "name": publication['name'],
                    "positive": positive_count,
                    "neutral": neutral_count,
                    "negative": negative_count,
                    "total": total_count
                })

        # Sort the keyword_sentiment_counts by the total count in descending order
        publication_sentiment_counts = sorted(publication_sentiment_counts, key=lambda x: x['total'], reverse=True)

        publication_sentiment = {
            "category": [item["name"] for item in publication_sentiment_counts],
            "data": [
                {
                    "name": "Positive",
                    "data": [item["positive"] for item in publication_sentiment_counts]
                },
                {
                    "name": "Neutral",
                    "data": [item["neutral"] for item in publication_sentiment_counts]
                },
                {
                    "name": "Negative",
                    "data": [item["negative"] for item in publication_sentiment_counts]
                }
            ]
        }

        # six_months_ago = timezone.now() - timezone.timedelta(days=180)
        states = State.objects.all().values('id', 'name')

        state_sentiment_counts = []

        # articles = Article.objects.all()

        for state in states:
            articles = Article.objects.filter(state=state['id'], keywords__in=keywords, is_tweet=False)
            if articles.exists():
                positive_count = articles.filter(sentiment_compound__gte=0.20).count()
                neutral_count = articles.filter(sentiment_compound__gt=-0.20, sentiment_compound__lt=0.20).count()
                negative_count = articles.filter(sentiment_compound__lte=-0.20).count()

                total_count = positive_count + neutral_count + negative_count

                state_sentiment_counts.append({
                    "name": state['name'],
                    "positive": positive_count,
                    "neutral": neutral_count,
                    "negative": negative_count,
                    "total": total_count
                })

        # Sort the keyword_sentiment_counts by the total count in descending order
        state_sentiment_counts = sorted(state_sentiment_counts, key=lambda x: x['total'], reverse=True)

        state_sentiment = {
            "category": [item["name"] for item in state_sentiment_counts],
            "data": [
                {
                    "name": "Positive",
                    "data": [item["positive"] for item in state_sentiment_counts]
                },
                {
                    "name": "Neutral",
                    "data": [item["neutral"] for item in state_sentiment_counts]
                },
                {
                    "name": "Negative",
                    "data": [item["negative"] for item in state_sentiment_counts]
                }
            ]
        }

        context = {
            "publication": publication_sentiment,
            "state": state_sentiment
        }

        return Response(data=context)


class OverallSentimentViewSet(viewsets.ViewSet):
    def list(self, request):
        # Define the sentiment ranges
        # positive_range = (0.20, 1)
        # neutral_range = (-0.20, 0.20)
        # negative_range = (-1, -0.20)

        enabled_keywords = Keyword.objects.filter(is_enable=True).values_list('id', flat=True)

        articles = Article.objects.filter(keywords__in=enabled_keywords)

        positive_count = articles.filter(sentiment_compound__gt=0.20).count()
        negative_count = articles.filter(sentiment_compound__lt=-0.20).count()
        neutral_count = articles.filter(sentiment_compound__gte=-0.20, sentiment_compound__lte=0.20).count()
        total_count = positive_count + negative_count + neutral_count

        positive_percentage = round((positive_count / total_count) * 100, 2) if total_count > 0 else 0
        negative_percentage = round((negative_count / total_count) * 100, 2) if total_count > 0 else 0
        neutral_percentage = round((neutral_count / total_count) * 100, 2) if total_count > 0 else 0

        overall_sentiment = {
            'positive_count': positive_count,
            'positive_percentage': positive_percentage,
            'neutral_count': neutral_count,
            'neutral_percentage': neutral_percentage,
            'negative_count': negative_count,
            'negative_percentage': negative_percentage,
            'total': human_format(total_count)
        }

        positive_tweet_count = articles.filter(is_tweet=True, sentiment_compound__gt=0.20).count()
        negative_tweet_count = articles.filter(is_tweet=True, sentiment_compound__lt=-0.20).count()
        neutral_tweet_count = articles.filter(is_tweet=True, sentiment_compound__gte=-0.20,
                                              sentiment_compound__lte=0.20).count()
        total_tweet_count = positive_tweet_count + negative_tweet_count + neutral_tweet_count

        positive_tweet_percentage = round((positive_tweet_count / total_tweet_count) * 100,
                                          2) if total_tweet_count > 0 else 0
        negative_tweet_percentage = round((negative_tweet_count / total_tweet_count) * 100,
                                          2) if total_tweet_count > 0 else 0
        neutral_tweet_percentage = round((neutral_tweet_count / total_tweet_count) * 100,
                                         2) if total_tweet_count > 0 else 0

        total_tweet_sentiment = {
            'positive_tweet_count': positive_tweet_count,
            'positive_tweet_percentage': positive_tweet_percentage,
            'neutral_tweet_count': neutral_tweet_count,
            'neutral_tweet_percentage': neutral_tweet_percentage,
            'negative_tweet_count': negative_tweet_count,
            'negative_tweet_percentage': negative_tweet_percentage,
            'total': human_format(total_tweet_count)
        }

        positive_news_count = articles.filter(is_tweet=False, sentiment_compound__gt=0.20).count()
        negative_news_count = articles.filter(is_tweet=False, sentiment_compound__lt=-0.20).count()
        neutral_news_count = articles.filter(is_tweet=False, sentiment_compound__gte=-0.20,
                                             sentiment_compound__lte=0.20).count()
        total_news_count = positive_news_count + negative_news_count + neutral_news_count

        positive_news_percentage = round((positive_news_count / total_news_count) * 100,
                                         2) if total_news_count > 0 else 0
        negative_news_percentage = round((negative_news_count / total_news_count) * 100,
                                         2) if total_news_count > 0 else 0
        neutral_news_percentage = round((neutral_news_count / total_news_count) * 100, 2) if total_news_count > 0 else 0

        total_news_sentiment = {
            'positive_news_count': positive_news_count,
            'positive_news_percentage': positive_news_percentage,
            'neutral_news_count': neutral_news_count,
            'neutral_news_percentage': neutral_news_percentage,
            'negative_news_count': negative_news_count,
            'negative_news_percentage': negative_news_percentage,
            'total': human_format(total_news_count)
        }

        data = {
            "overall_sentiment": overall_sentiment,
            "overall_tweet_sentiment": total_tweet_sentiment,
            "total_news_sentiment": total_news_sentiment
        }

        pie_chart = {
            "overall_sentiment": {
                "labels": ["Positive", "Neutral", "Negative"],
                "series": [positive_percentage, neutral_percentage, negative_percentage]
            },
            "overall_tweet_sentiment": {
                "labels": ["Positive", "Neutral", "Negative"],
                "series": [positive_tweet_percentage, neutral_tweet_percentage, negative_tweet_percentage]
            },
            "total_news_sentiment": {
                "labels": ["Positive", "Neutral", "Negative"],
                "series": [positive_news_percentage, neutral_news_percentage, negative_news_percentage]
            }
        }

        context = {
            "data": data,
            "pie_chart": pie_chart
        }

        return Response(data=context)


class ArticleViewSet(viewsets.ViewSet):
    def list(self, request):
        # Calculate the datetime threshold for articles published within the last 6 hours
        six_hours_ago = get_current_time() - timezone.timedelta(hours=360)

        # Filter articles based on the publication date
        recent_articles = Article.objects.filter(date_publish__gte=six_hours_ago, category__name="politics")

        # Create a list to store the formatted data
        articles_data = []

        for article in recent_articles:
            # Calculate sentiment based on your criteria
            sentiment = 'neutral'
            if article.sentiment_compound > 0.20:
                sentiment = 'positive'
            elif article.sentiment_compound < -0.20:
                sentiment = 'negative'

            # Create a dictionary with the desired fields
            article_data = {
                'author': [str(author) for author in article.author.all()],
                'title': article.title,
                'source_url': article.source_url,
                'sentiment': sentiment,
                'people': [str(people) for people in article.people.all()],
                'keywords': [str(keyword) for keyword in article.keywords.all()],
                'state': [str(state) for state in article.state.all()],
                'city': [str(city) for city in article.city.all()],
                'category': [str(category) for category in article.category.all()],

            }

            articles_data.append(article_data)

        return Response(articles_data)