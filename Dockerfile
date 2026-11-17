FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN useradd --create-home --uid 10001 app \
    && python manage.py migrate \
    && python manage.py seed \
    && chown -R app:app /app
USER app

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--threads", "8", "wallet_project.wsgi"]
