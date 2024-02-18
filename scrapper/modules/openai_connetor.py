import django.conf
import openai
from django.conf import settings


def openai_extract_info(text_obj):
    openai.api_key = settings.OPENAI_API_KEY

    PROMPT = """Evaluate a given news article or tweet, identifying locations, countries, states, cities, people, 
    tags categories and overall_sentiment. sentiment threshold from -1 to 1 (-1: extremely negative, 1: extremely 
    positive).

    ### Instructions:
    1. Do not generate new keywords, pick only user provided keywords.
    2. You can extract people from given data.
    3. sentiment can not be null. analyse the accurate sentiment as mentioned threshold  -1 to 1
    4. calculate overall sentiment of the article/tweet.
    5. tags cant be null. add important tags from given data.
    6. category can't be null. add proper category of the news/tweet.
    
    Your expected output should be in the JSON format: ```json { "locations":["extract mentioned locations if there 
    are no locations mentioned then leave it as empty list"], "country":["extract mentioned country if there are no 
    country mentioned then leave it as empty list or you can guess the country if city of state mentioned"], 
    "state":["extract mentioned state if there are no state mentioned then leave it as empty list or you can guess 
    the state by city mentioned"], "city":["extract mentioned city if there are no city mentioned then leave it as 
    empty list"], "people_sentiment":["{'people':'extract mentioned people names in given data if there are no people 
    mentioned in data then leave it as empty list', 'sentiment':'Sentiment score between -1 and 1'}"], 
    "tags":["extract tags from given article or tweet"], "category":["analyse which category is data belong to like: 
    politics, crime etc. add those in list of strings"], "keywords_sentiment":[{"keyword":"From given list of 
    keywords by user analyse the sentiment of that keyword in entire article/wteet", "sentiment":"Sentiment score 
    between -1 and 1"}] "overall_sentiment": "analyse overall sentiment of the article/tweet value should be -1 to 1" 
    } ``` remember response should have all the keys mentioned above. overall sentiment of the given data should be 
    accurate ranging from -1 to 1 float value.
    """

    for _ in range(3):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": PROMPT
                    },
                    {
                        "role": "user",
                        "content": str(text_obj)
                    }
                ],
                temperature=0,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                timeout=30
            )

            for choice in response.choices:
                if "text" in choice:
                    return choice.text

            # If no response with text is found, return the first response's content (which may be empty)
            # print(response.usage)
            return response.choices[0].message.content

        except openai.error.Timeout as e:
            print(e)
            continue

        except Exception as e:
            print(e)
            break

    return "{}"
