from django.urls import path, include
from rest_framework import routers
from scrapper.views import *


router = routers.DefaultRouter()
router.register(r'scrape_news', NewsScrapperViewSet, basename='scrape_news')
router.register(r'scrape_tweet', TweetScrapperViewSet, basename='scrape_tweet')

router.register(r'resync-keywords', ReSyncKeywordsViewSet, basename='resync-keywords')

urlpatterns = [
    path('', include(router.urls)),
]