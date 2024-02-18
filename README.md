# NewsLix - Political News Sentiment Analysis

## Overview
NewsLix is a project that involves scraping political news articles from various websites and providing the scraped data through an API built with DjangoRest Framework.

## Project Structure
The project is organized into different modules, each responsible for scraping political news from a specific news website platform. These modules are designed to scrape political articles and news.

### Module Workflow
- Each module is configured to run on a specific schedule, typically daily at a specific time.
- The module will scrape all political news articles published on the specified day and repeat this process daily.
- The module accepts an argument called `url`. If `url` is not provided, it scrapes news from the website's landing page. If a `url` is given, it scrapes news from the specified URL page.

## Output Format
The output of the scraping process is provided in the following JSON format:

```json
{
  "status": "ok",
  "totalResults": 37,
  "articles": [
    {
        "author": 'list',
        "publication": 'str',
        "category": 'list',

        "location": 'list',
        "keywords": 'list',
        "tags":'list',

        "title": 'english str',
        "content": 'english str',

        "source_title": 'str',
        "source_content": 'str',
        "source_language": 'str',

        "source_url": 'str',
        "image_url": 'str',

        "sentiment_compound": 'float',
        "sentiment_neu":'float',
        "sentiment_neg":'float',
        "sentiment_pos":'float',

        "date_publish": 'DD-MM-YYYY HH:MM:SS',
        "is_tweet": 'Bool'
    }
  ]
}
```

## Sentiment Analysis
**sentiment_compound:** This score represents the overall compound sentiment of the text. It's a single value that provides an aggregate sentiment score for the entire text. It takes into account both positive and negative sentiments. The compound score can range from -1 (extremely negative) to 1 (extremely positive). A score around 0 indicates a neutral sentiment.

**sentiment_neu:** This score represents the level of neutrality in the text. It measures the extent to which the text is neither positive nor negative. The neu score ranges from 0 to 1, with higher values indicating a more neutral tone.

**sentiment_neg:** This score represents the level of negativity in the text. It measures the extent to which the text contains negative sentiments. The neg score ranges from 0 to 1, with higher values indicating more negative sentiment.

**sentiment_pos:** This score represents the level of positivity in the text. It measures the extent to which the text contains positive sentiments. The pos score ranges from 0 to 1, with higher values indicating more positive sentiment.


## API Documentations

#### Keyword API
You can use the following URLs for keywords CRUD operations:

    Create: POST to /keywords/
    Retrieve: GET to /keywords/{keyword_id}/
    Update: PUT or PATCH to /keywords/{keyword_id}/
    Delete: DELETE to /keywords/{keyword_id}/
    List: GET to /keywords/ (to retrieve a list of all keywords)

