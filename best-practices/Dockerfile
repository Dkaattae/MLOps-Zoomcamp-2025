FROM python:3.10.9-slim
WORKDIR /app

RUN pip install -U pip && pip install pipenv

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --dev
RUN pipenv install --system --deploy

COPY [ "batch.py", "batch.py" ]
COPY [ "model.bin", "model.bin" ]
COPY [ "tests", "./tests"]

CMD [ "python", "batch.py" ]