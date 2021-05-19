FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
COPY ./app /app
RUN apt-get update && apt-get install -y gnupg
COPY . /app
WORKDIR /app
RUN python -m pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
CMD ["python", "./run.py"]
