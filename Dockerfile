FROM python:3.10

WORKDIR /code

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY .weather_concierge .weather_concierge

CMD ["uvicorn", "weather_concierge.main:app", "--host", "0.0.0.0", "--port", "8000"]