from flask_frozen import Freezer
from app import app

freezer = Freezer(app)

@freezer.register_generator
def api_models():
    yield {}  # Generate the base API endpoint
    
@freezer.register_generator
def api_categories():
    yield {}

@freezer.register_generator
def api_sources():
    yield {}

if __name__ == '__main__':
    freezer.freeze()
