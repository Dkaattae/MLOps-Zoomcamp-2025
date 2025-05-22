FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

COPY ["Pipfile", "Pipfile.lock",  "./"]

RUN pip install -U pip
RUN pip install pipenv

RUN pipenv install --system --deploy

COPY ["starter.py", "./"]

ENTRYPOINT ["python", "-u", "starter.py"]
CMD ["--year=2023", "--month=5"]