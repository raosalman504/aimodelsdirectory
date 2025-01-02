from datetime import datetime
import json
from config import MODELS_FILE, SITE_URL
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_sitemap():
    """Generate a dynamic sitemap based on current models"""
    try:
        # Base URLs that are always present
        urls = [
            {
                'loc': SITE_URL,
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'changefreq': 'daily',
                'priority': '1.0'
            }
        ]
        
        # Add model-specific URLs if we have models
        if MODELS_FILE.exists():
            with open(MODELS_FILE, 'r', encoding='utf-8') as f:
                models = json.load(f)
                
            for model in models:
                model_url = f"{SITE_URL}/model/{model['name'].lower().replace(' ', '-')}"
                urls.append({
                    'loc': model_url,
                    'lastmod': model.get('last_updated', datetime.now().strftime('%Y-%m-%d')),
                    'changefreq': 'daily',
                    'priority': '0.8'
                })
        
        # Generate the XML
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        for url in urls:
            xml_content.append('  <url>')
            xml_content.append(f'    <loc>{url["loc"]}</loc>')
            xml_content.append(f'    <lastmod>{url["lastmod"]}</lastmod>')
            xml_content.append(f'    <changefreq>{url["changefreq"]}</changefreq>')
            xml_content.append(f'    <priority>{url["priority"]}</priority>')
            xml_content.append('  </url>')
        
        xml_content.append('</urlset>')
        
        # Save the sitemap
        sitemap_path = Path('static/sitemap.xml')
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(xml_content))
            
        logger.info(f"Generated sitemap with {len(urls)} URLs")
        return True
        
    except Exception as e:
        logger.error(f"Error generating sitemap: {str(e)}")
        return False
