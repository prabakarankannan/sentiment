from rest_framework import serializers
from scrapper.models import Keyword, TargetURL, Article
from rest_framework import serializers


class SentimentTrendSerializer(serializers.Serializer):
    keywords = serializers.ListField(child=serializers.CharField(), required=False)
    hour = serializers.IntegerField(default=6, initial=6, required=False)


class KeywordSerializer(serializers.ModelSerializer):
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Keyword
        fields = ['id', 'name', 'is_enable', 'created_on', 'updated_on']


class TargetURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetURL
        fields = ['id', 'url', 'selector', 'is_active']


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
