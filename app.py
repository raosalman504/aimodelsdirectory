from flask import Flask, jsonify, render_template, send_from_directory, request
import json
import logging
from datetime import datetime
from config import MODELS_FILE, STATIC_DIR
from utils.sitemap import generate_sitemap
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def load_models():
    """Load models from JSON file with error handling"""
    try:
        if Path(MODELS_FILE).exists():
            with open(MODELS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        return []

def get_categories(models):
    """Extract unique categories from models"""
    categories = set()
    for model in models:
        categories.update(model.get('category', []))
    return sorted(list(categories))

def get_sources(models):
    """Extract unique sources from models"""
    sources = {model.get('source', 'Unknown') for model in models}
    return sorted(list(sources))

@app.context_processor
def inject_now():
    """Inject current year into all templates"""
    return {'now': datetime.now()}

@app.route('/')
def index():
    """Render the main page"""
    try:
        models = load_models()
        categories = get_categories(models)
        sources = get_sources(models)
        
        # Apply filters if any
        search = request.args.get('search', '').lower()
        category = request.args.get('category', '')
        source = request.args.get('source', '')
        
        if search:
            models = [
                model for model in models
                if search in model['name'].lower() or 
                   search in model.get('description', '').lower() or
                   search in model.get('company', '').lower()
            ]
        
        if category:
            models = [
                model for model in models
                if category in model.get('category', [])
            ]
            
        if source:
            models = [
                model for model in models
                if source == model.get('source', '')
            ]
        
        return render_template('index.html', 
                             models=models,
                             categories=categories,
                             sources=sources)
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return render_template('500.html'), 500

@app.route('/api/models')
def get_models_api():
    """API endpoint to get all models"""
    try:
        models = load_models()
        search = request.args.get('search', '').lower()
        category = request.args.get('category', '')
        source = request.args.get('source', '')
        
        if search:
            models = [
                model for model in models
                if search in model['name'].lower() or 
                   search in model.get('description', '').lower() or
                   search in model.get('company', '').lower()
            ]
        
        if category:
            models = [
                model for model in models
                if category in model.get('category', [])
            ]
            
        if source:
            models = [
                model for model in models
                if source == model.get('source', '')
            ]
        
        return jsonify(models)
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    """Serve robots.txt and sitemap.xml"""
    return send_from_directory(STATIC_DIR, Path(request.path).name)

@app.route('/model/<model_name>')
def model_detail(model_name):
    """Render individual model page"""
    try:
        models = load_models()
        model = next((m for m in models if m['name'].lower().replace(' ', '-') == model_name), None)
        if model:
            return render_template('model.html', model=model)
        return render_template('404.html'), 404
    except Exception as e:
        logger.error(f"Error rendering model detail: {str(e)}")
        return render_template('500.html'), 500

@app.before_request
def before_request():
    """Generate sitemap before each request if needed"""
    try:
        sitemap_path = Path(STATIC_DIR) / 'sitemap.xml'
        if not sitemap_path.exists() or (datetime.now() - datetime.fromtimestamp(sitemap_path.stat().st_mtime)).days >= 1:
            generate_sitemap()
    except Exception as e:
        logger.error(f"Error in before_request: {str(e)}")

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

@app.context_processor
def utility_processor():
    """Add utility functions to template context"""
    def format_date(date_string):
        try:
            date = datetime.fromisoformat(date_string)
            return date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return date_string
    return dict(format_date=format_date)

if __name__ == '__main__':
    app.run(debug=True)
