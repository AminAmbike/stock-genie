import finnhub
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import requests
import time
import asyncio
import aiohttp

API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
headers = {"Authorization": "Bearer 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"}
finnhub_client = finnhub.Client(api_key="")


# def scrape_article_text(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # The exact tag/attribute you need depends on the site's structure
#         # This is an example where the main content is within <article> tags
#         article_text = soup.find('article')
        
#         if article_text:
#             return article_text.get_text(separator=' ', strip=True)
#         else:
#             # Fallback to a more generic approach if the structure is unknown
#             return soup.get_text(separator=' ', strip=True)
#     else:
#         return None

async def scrape_article_text(session, url):
    async with session.get(url) as response:
        try:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract article content based on the site's structure
            article_text = soup.find('article')
            if article_text:
                return article_text.get_text(separator=' ', strip=True)
            else:
                # Fallback to more generic content scraping
                return soup.get_text(separator=' ', strip=True)
        
        except Exception as e:
            return None
      
# def query(payload):
#     response = requests.post(API_URL, headers=headers, json=payload)
#     return response.json()

async def async_query(session, payload):
    async with session.post(API_URL, headers=headers, json=payload) as response:
        try:
            return await response.json(content_type=None)
        except Exception as e:
            text = await response.text()
            print(f"Failed to parse JSON. Status: {response.status}, Response: {text}")
            return {
                "error": f"Failed to parse JSON. Status: {response.status}",
                "response_text": text,
                "status_code": response.status,
            }
def get_dates():
    today = datetime.today()
    three_days_prior = today - timedelta(days=3)
    today = today.strftime('%Y-%m-%d')
    three_days_prior = three_days_prior.strftime('%Y-%m-%d')
    return three_days_prior, today


# def get_news(ticker):
#     stories = {}
#     stories_unretrieved = {}
#     three_days_prior, today = get_dates()
#     news = finnhub_client.company_news(ticker, _from=three_days_prior, to=today)
#     print("news: ", len(news))
#     for story in news:
#         article_text = scrape_article_text(story['url'])
#         if article_text:
#             stories[story['headline']] = article_text
#         else:
#             stories_unretrieved[story['headline']] = ""
    
#     print("no error: ", len(stories))
#     return stories, stories_unretrieved

async def get_news_async(ticker, session):
    stories = {}
    stories_unretrieved = {}
    three_days_prior, today = get_dates()
    news = finnhub_client.company_news(ticker, _from=three_days_prior, to=today)
    news = news[:100]
    print("news: ", len(news))
    # Create a list of tasks for each article URL
    tasks = []
    for story in news:
        task = asyncio.create_task(scrape_article_text(session, story['url']))
        tasks.append((story['headline'], task))
    
    # Run all scraping tasks concurrently and wait for the results
    results = await asyncio.gather(*[task for _, task in tasks])
    print("parsed: ", len(results))
    # Collect the results into stories and unretrieved
    for (headline, task), article_text in zip(tasks, results):
        if article_text:
            stories[headline] = article_text
        else:
            stories_unretrieved[headline] = ""
    
    print("no error: ", len(stories))
    return stories, stories_unretrieved

async def run_get_news(ticker):
    async with aiohttp.ClientSession() as session:
        return await get_news_async(ticker, session)

# async def summarize_story(session, headline, text):
#     summary = await async_query(session, {"inputs": text, "parameters": {"max_length": 130, "min_length": 30}})
#     if isinstance(summary, list):
#         return headline, summary[0]['summary_text']
#     return headline, ""

async def summarize_stories_async(session, ticker):
    stories, stories_unretrieved = await run_get_news(ticker)
    tasks = []
    for headline, text in stories.items():
        if text:  # Only summarize if the text is not empty
            task = asyncio.create_task(async_query(session, {"inputs": text, "parameters": {"max_length": 130, "min_length": 30}}))
            tasks.append((headline,task))

    # Run all tasks concurrently and wait for their results
    results = await asyncio.gather(*[task for _, task in tasks],return_exceptions=True)
    summarized_stories = {}

    for (headline, task), result in zip(tasks, results):
        if isinstance(result, Exception) or "error" in result:
            summarized_stories[headline] = "Error or no summary generated"
        elif isinstance(result, list) and 'summary_text' in result[0]:
            summarized_stories[headline] = result[0]['summary_text']
        else:
            # Handle unexpected response formats
            summarized_stories[headline] = "Error or unexpected response format"

    summarized_stories.update(stories_unretrieved)

    return summarized_stories

# Wrapper to run the async function in a synchronous context
async def run_summarize_stories(ticker):
    async with aiohttp.ClientSession() as session:
        output = await summarize_stories_async(session, ticker)
        return output
    #return asyncio.run(summarize_stories_async(ticker))
    

# def summarize_stories(ticker):
#     stories, stories_unretrieved = get_news(ticker)
#     summarized_stories = {}
#     for headline, text in stories.items():
#         if text:
#             # summary = None
#             # while not isinstance(summary, list):
#             #     summary = query({"inputs":text,"parameters":{"max_length": 130,"min_length":30}})
#             summary = query({"inputs":text,"parameters":{"max_length": 130,"min_length":30}})
#             if isinstance(summary, list):
#                 summarized_stories[headline] = summary[0]['summary_text']
#     summarized_stories.update(stories_unretrieved)

#     return summarized_stories
