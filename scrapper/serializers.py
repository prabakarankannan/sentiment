# serializers.py
from rest_framework import serializers


class ScrapeSerializer(serializers.Serializer):
    scrape = serializers.CharField()

