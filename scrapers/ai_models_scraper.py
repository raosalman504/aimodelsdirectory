import scrapy
from scrapy.crawler import CrawlerProcess
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import logging

class AIModelSpider(scrapy.Spider):
    name = 'ai_models'
    
    def start_requests(self):
        # List of URLs to scrape
        urls = [
            'https://huggingface.co/models',  # Hugging Face models
            'https://paperswithcode.com/methods',  # Papers with Code
            'https://www.reddit.com/r/artificial/hot.json',  # Reddit r/artificial
        ]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        if 'huggingface.co' in response.url:
            yield from self.parse_huggingface(response)
        elif 'paperswithcode.com' in response.url:
            yield from self.parse_paperswithcode(response)
        elif 'reddit.com' in response.url:
            yield from self.parse_reddit(response)

    def parse_huggingface(self, response):
        # Parse Hugging Face models page
        for model in response.css('.model-card'):
            yield {
                'name': model.css('.model-name::text').get(),
                'description': model.css('.model-description::text').get(),
                'website': f"https://huggingface.co{model.css('a::attr(href)').get()}",
                'company': 'Various',
                'category': ['Language Model'],
                'features': [tag.strip() for tag in model.css('.model-tags span::text').getall()],
                'pricing': 'Free',
                'source': 'HuggingFace',
                'last_updated': datetime.now().isoformat()
            }

    def parse_paperswithcode(self, response):
        # Parse Papers with Code methods
        for method in response.css('.row.infinite-item'):
            yield {
                'name': method.css('h1 a::text').get(),
                'description': method.css('.item-content-block::text').get(),
                'website': f"https://paperswithcode.com{method.css('h1 a::attr(href)').get()}",
                'company': 'Research',
                'category': ['Research', 'Academic'],
                'features': [tag.strip() for tag in method.css('.tags span::text').getall()],
                'pricing': 'Free',
                'source': 'PapersWithCode',
                'last_updated': datetime.now().isoformat()
            }

    def parse_reddit(self, response):
        # Parse Reddit posts about new AI models
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

def merge_models(new_models, existing_models):
    """Merge new models with existing ones, avoiding duplicates"""
    existing_names = {model['name'] for model in existing_models}
    merged = existing_models.copy()
    
    for model in new_models:
        if model['name'] not in existing_names:
            merged.append(model)
            existing_names.add(model['name'])
    
    return merged

def run_spider():
    """Run the spider and update models.json"""
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    # Create a temporary file for new results
    temp_file = 'temp_models.json'
    
    def crawler_results(signal, sender, item, response, spider):
        if os.path.exists(temp_file):
            with open(temp_file, 'r') as f:
                items = json.load(f)
        else:
            items = []
        items.append(item)
        with open(temp_file, 'w') as f:
            json.dump(items, f)
    
    from scrapy import signals
    process.signals.connect(crawler_results, signal=signals.item_scraped)
    
    # Run the spider
    process.crawl(AIModelSpider)
    process.start()
    
    # Merge results with existing models
    if os.path.exists(temp_file):
        with open(temp_file, 'r') as f:
            new_models = json.load(f)
        
        models_file = '../models.json'
        if os.path.exists(models_file):
            with open(models_file, 'r') as f:
                existing_models = json.load(f)
        else:
            existing_models = []
        
        # Merge and save
        merged_models = merge_models(new_models, existing_models)
        with open(models_file, 'w') as f:
            json.dump(merged_models, f, indent=4)
        
        # Clean up
        os.remove(temp_file)
        
        logging.info(f"Updated models.json with {len(new_models)} new models")
    else:
        logging.error("No new models found during scraping")
