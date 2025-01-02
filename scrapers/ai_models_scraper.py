import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModelSpider(scrapy.Spider):
    name = 'ai_models'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 1,
        'COOKIES_ENABLED': False,
    }
    
    def __init__(self, *args, **kwargs):
        super(AIModelSpider, self).__init__(*args, **kwargs)
        self.items = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AIModelSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.item_scraped, signal=signals.item_scraped)
        return spider

    def item_scraped(self, item, response, spider):
        self.items.append(dict(item))
    
    def start_requests(self):
        urls = [
            'https://huggingface.co/models',
            'https://paperswithcode.com/methods',
            'https://www.reddit.com/r/artificial/hot.json',
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.handle_error,
                dont_filter=True
            )
    
    def handle_error(self, failure):
        logger.error(f"Request failed: {failure.request.url}, {str(failure.value)}")

    def parse(self, response):
        try:
            if 'huggingface.co' in response.url:
                yield from self.parse_huggingface(response)
            elif 'paperswithcode.com' in response.url:
                yield from self.parse_paperswithcode(response)
            elif 'reddit.com' in response.url:
                yield from self.parse_reddit(response)
        except Exception as e:
            logger.error(f"Error parsing {response.url}: {str(e)}")

    def parse_huggingface(self, response):
        try:
            for model in response.css('.model-card'):
                yield {
                    'name': model.css('.model-name::text').get('').strip(),
                    'description': model.css('.model-description::text').get('').strip(),
                    'website': f"https://huggingface.co{model.css('a::attr(href)').get('')}",
                    'company': 'Various',
                    'category': ['Language Model'],
                    'features': [tag.strip() for tag in model.css('.model-tags span::text').getall()],
                    'pricing': 'Free',
                    'source': 'HuggingFace',
                    'last_updated': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error parsing HuggingFace model: {str(e)}")

    def parse_paperswithcode(self, response):
        try:
            for method in response.css('.row.infinite-item'):
                yield {
                    'name': method.css('h1 a::text').get('').strip(),
                    'description': method.css('.item-content-block::text').get('').strip(),
                    'website': f"https://paperswithcode.com{method.css('h1 a::attr(href)').get('')}",
                    'company': 'Research',
                    'category': ['Research', 'Academic'],
                    'features': [tag.strip() for tag in method.css('.tags span::text').getall()],
                    'pricing': 'Free',
                    'source': 'PapersWithCode',
                    'last_updated': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error parsing PapersWithCode method: {str(e)}")

    def parse_reddit(self, response):
        try:
            data = json.loads(response.text)
            for post in data['data']['children']:
                post_data = post['data']
                if any(keyword in post_data['title'].lower() 
                      for keyword in ['model', 'ai', 'neural', 'transformer']):
                    yield {
                        'name': post_data['title'],
                        'description': post_data.get('selftext', '')[:200],
                        'website': f"https://reddit.com{post_data['permalink']}",
                        'company': 'Community',
                        'category': ['Discussion'],
                        'features': [],
                        'pricing': 'Unknown',
                        'source': 'Reddit',
                        'last_updated': datetime.now().isoformat()
                    }
        except Exception as e:
            logger.error(f"Error parsing Reddit data: {str(e)}")

def merge_models(new_models, existing_models):
    """Merge new models with existing ones, avoiding duplicates"""
    try:
        existing_names = {model['name'] for model in existing_models}
        merged = existing_models.copy()
        
        for model in new_models:
            if model['name'] and model['name'] not in existing_names:
                merged.append(model)
                existing_names.add(model['name'])
        
        return merged
    except Exception as e:
        logger.error(f"Error merging models: {str(e)}")
        return existing_models

def run_spider():
    """Run the spider and update models.json"""
    try:
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'LOG_LEVEL': 'ERROR'
        })

        # Create a temporary file for new results
        temp_file = 'temp_models.json'
        models_file = Path('models.json')

        spider = AIModelSpider()
        process.crawl(spider)
        process.start()

        # Save spider results
        if spider.items:
            try:
                # Merge with existing models
                if models_file.exists():
                    with open(models_file, 'r', encoding='utf-8') as f:
                        existing_models = json.load(f)
                else:
                    existing_models = []

                # Merge and save
                merged_models = merge_models(spider.items, existing_models)
                with open(models_file, 'w', encoding='utf-8') as f:
                    json.dump(merged_models, f, ensure_ascii=False, indent=4)

                logger.info(f"Updated models.json with {len(spider.items)} new models")
            except Exception as e:
                logger.error(f"Error processing results: {str(e)}")
        else:
            logger.warning("No new models found during scraping")

    except Exception as e:
        logger.error(f"Error running spider: {str(e)}")
        raise
