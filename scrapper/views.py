from rest_framework.response import Response
from rest_framework import status
from scrapper.serializers import ScrapeSerializer
from rest_framework import viewsets, filters
from scrapper.modules.scrapper import parallel_news_scrape, linear_tweet_scrape, parallel_tweet_scrape, linear_news_scrape
from scrapper.modules.helpers import resync_keyword, resync_people
from django.conf import settings
from scrapper.models import Keyword, Article


class NewsScrapperViewSet(viewsets.ViewSet):
    serializer_class = ScrapeSerializer

    def list(self, request):
        return Response({"cronjob":settings.CRONJOBS})

    def post(self, request):
        parallel_news_scrape()
        return Response({"context":""})


class TweetScrapperViewSet(viewsets.ViewSet):
    serializer_class = ScrapeSerializer

    def list(self, request):
        return Response({"cronjob":settings.CRONJOBS})

    def post(self, request):
        parallel_tweet_scrape()
        return Response({"context":""})


class ReSyncKeywordsViewSet(viewsets.ViewSet):

    serializer_class = ScrapeSerializer

    def list(self, request):
        return Response({"message":"This function will iterate over all keyword and articles currently exists and update all newly updated keyword"})

    def post(self, request):
        updated_keyword = resync_keyword()
        updated_people = resync_people()

        return Response({"updated_keyword":updated_keyword, "updated_people":updated_people})

