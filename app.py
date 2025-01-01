from flask import Flask, render_template, jsonify, request
from datetime import datetime
import json
import os
from scheduler import initialize_scheduler
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load AI models data
def load_models():
    if os.path.exists('models.json'):
        with open('models.json', 'r') as f:
            return json.load(f)
    return []

# Initialize with some example models
INITIAL_MODELS = [
    {
        "name": "ChatGPT",
        "description": "Large language model by OpenAI capable of natural conversations and various tasks",
        "website": "https://chat.openai.com",
        "company": "OpenAI",
        "category": ["Language Model", "Chatbot"],
        "features": ["Text Generation", "Conversation", "Code Generation"],
        "pricing": "Freemium",
        "source": "OpenAI"
    },
    {
        "name": "DALL-E 3",
        "description": "Advanced text-to-image generation model",
        "website": "https://openai.com/dall-e-3",
        "company": "OpenAI",
        "category": ["Image Generation"],
        "features": ["Text to Image", "Image Editing"],
        "pricing": "Paid",
        "source": "OpenAI"
    },
    {
        "name": "Claude",
        "description": "Advanced AI assistant capable of complex analysis and tasks",
        "website": "https://anthropic.com/claude",
        "company": "Anthropic",
        "category": ["Language Model", "Chatbot"],
        "features": ["Text Generation", "Analysis", "Research"],
        "pricing": "Freemium",
        "source": "Anthropic"
    }
]

# Save initial models if file doesn't exist
if not os.path.exists('models.json'):
    with open('models.json', 'w') as f:
        json.dump(INITIAL_MODELS, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/models')
def get_models():
    search = request.args.get('search', '').lower()
    category = request.args.get('category', '')
    source = request.args.get('source', '')
    
    models = load_models()
    
    if search:
        models = [
            model for model in models
            if search in model['name'].lower() or 
               search in model['description'].lower() or
               search in model['company'].lower()
        ]
    
    if category:
        models = [
            model for model in models
            if category in model['category']
        ]
        
    if source:
        models = [
            model for model in models
            if source == model.get('source', '')
        ]
    
    return jsonify(models)

@app.route('/api/categories')
def get_categories():
    models = load_models()
    categories = set()
    for model in models:
        categories.update(model['category'])
    return jsonify(list(categories))

@app.route('/api/sources')
def get_sources():
    models = load_models()
    sources = {model.get('source', 'Unknown') for model in models}
    return jsonify(list(sources))

if __name__ == '__main__':
    # Initialize the scheduler before running the app
    initialize_scheduler()
    app.run(debug=True)
