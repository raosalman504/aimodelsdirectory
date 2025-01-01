# AI Models Directory

A comprehensive directory of AI models with a clean, modern interface for searching and filtering AI models based on user requirements. Features automatic scraping and continuous updates.

## Features

- Extensive list of AI models with direct links
- Real-time search functionality
- Filter by categories, capabilities, and pricing
- Responsive modern UI
- Automatic scraping and updates every 5 minutes
- Source tracking and last update timestamps

## Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Deployment on GitHub Pages

1. Fork this repository
2. Go to repository Settings > Pages
3. Set up GitHub Pages with your preferred settings
4. The site will be available at `https://<your-username>.github.io/ai-models-list`

## Continuous Updates

The application uses GitHub Actions to automatically scrape and update the AI models data:
- Scraping runs every 5 minutes
- New models are automatically added to `models.json`
- Changes are automatically committed and pushed
- The website updates automatically with new data

## Data Sources

Currently scraping from:
- HuggingFace Models
- Papers with Code
- Reddit r/artificial
- And more...

## Contributing

Feel free to contribute by:
1. Adding new AI models
2. Improving the interface
3. Adding new data sources
4. Fixing bugs

## Setup GitHub Actions (Important!)

To enable automatic updates:
1. Go to repository Settings > Actions > General
2. Under "Workflow permissions", select "Read and write permissions"
3. Save the changes

The scraper will now run automatically every 5 minutes and update the models list!
