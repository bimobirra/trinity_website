# form_ml_django

A Django-based web application for car price prediction using a machine learning model.

## Project Structure
- `api/` - Django app for prediction API
- `model/` - Contains the trained ML model (`best_model_pipeline.pkl`)
- `static/` - CSS, JS, images
- `templates/` - HTML templates

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Run the server:
   ```bash
   python manage.py runserver
   ```

## API
- `POST /api/predict/` - Predict car price

## Author
- Migrated from Flask (Form_ML) to Django
