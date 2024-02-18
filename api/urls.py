from django.urls import path, include
from rest_framework import routers
from api.views import *


router = routers.DefaultRouter()
# router.register(r'target-url', TargetURLViewSet, basename='target-url')
router.register(r'keywords-v1', KeywordViewSet, basename='keywords')

# Home Page
# router.register(r'keywordwise-sentiment', KeywordWiseSentimentViewSet, basename='keywordwise-sentiment')

# router.register(r'keyword-sentiment', KeywordSentimentDataViewSet, basename='keyword-sentiment')
# router.register(r'keyword-sentiment-table', KeywordSentimentTableDataViewSet, basename='keyword-sentiment-table')
# router.register(r'publication-state-sentiment', PublicationAndStateSentimentDataViewSet, basename='publication-state-sentiment')
# router.register(r'overall-sentiment', OverallSentimentViewSet, basename='overall-sentiment')
# router.register(r'word-cloud', WorldCouldViewSet, basename='word-cloud')

# Realtime Page
# overall sentiment hourly sentiment
# router.register(r'realtime-page', RealtimePageViewSet, basename='realtime-page')
# router.register(r'sentiment-trend', ArticleSentimentTrendViewSet, basename='sentiment-trend')
# router.register(r'realtime-table', ArticleViewSet, basename='realtime-table')

urlpatterns = [
    path('', include(router.urls)),
]