from django.db import transaction
from scrapper.models import *


def save_article(context):
    with transaction.atomic():
        exists = Article.objects.filter(source_url=context['source_url'], is_tweet=context['is_tweet']).exists()
        if exists:
            print("Tweet already exist :", context['source_url'], context['is_tweet'])
            return exists
        # Get or create related objects
        authors = [Author.objects.get_or_create(name=author.lower())[0] for author in context['author'] if author and "www" not in author.lower()]
        publication = Publication.objects.get_or_create(name=context['publication'].lower())[0]
        categories = [Category.objects.get_or_create(name=category.lower())[0] for category in context['category']]
        locations = [Location.objects.get_or_create(name=location.lower())[0] for location in context['location']]
        state = [State.objects.get_or_create(name=state.lower())[0] for state in context['state']]
        city = [City.objects.get_or_create(name=city.lower())[0] for city in context['city']]
        country = [Country.objects.get_or_create(name=country.lower())[0] for country in context['country']]
        people = [People.objects.get_or_create(name=people.lower())[0] for people in context['people']]
        keywords = [Keyword.objects.get_or_create(name=keyword.lower())[0] for keyword in context['keywords']]
        tags = [Tag.objects.get_or_create(name=tag.lower())[0] for tag in context['tags']]

        # Create the article
        article = Article.objects.create(
            publication=publication,
            title=context['title'],
            content=context['content'],
            source_title=context['source_title'],
            source_content=context['source_content'],
            source_language=context['source_language'],
            source_url=context['source_url'],
            image_url=context['image_url'],
            sentiment_compound=context['sentiment_compound'],
            date_publish=context['date_publish'],
            is_tweet=context['is_tweet']
        )

        # Add many-to-many relationships
        article.author.set(authors)
        article.category.set(categories)
        article.location.set(locations)
        article.state.set(state)
        article.city.set(city)
        article.country.set(country)
        article.people.set(people)
        article.keywords.set(keywords)
        article.tags.set(tags)

        # Save Keyword Sentiment
        for i in context['keywords_sentiment']:
            try:
                if i['sentiment'] and i['keyword']:
                    kw_ins = Keyword.objects.get(name=i['keyword'].lower())
                    KeywordSentiment.objects.create(
                        article=article,
                        keyword=kw_ins,
                        sentiment_score=i['sentiment']
                    )
            except Exception as e:
                print(f"keyword not exist in keyword table form openai {i}")
                print(e)

        # Save People Sentiment
        for i in context['people_sentiment']:
            try:
                if i['sentiment'] and i['people']:
                    ppl_ins = People.objects.get(name=i['people'].lower())
                    PeopleSentiment.objects.create(
                        article=article,
                        people=ppl_ins,
                        sentiment_score=i['sentiment']
                    )
            except Exception as e:
                print(f"people not exist in people table form openai {i}")
                print(e)

        print("saved")
        return article