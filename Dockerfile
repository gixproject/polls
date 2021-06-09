FROM python:3.9.5

WORKDIR /code/

COPY pyproject.toml /code/

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

COPY . /code/
