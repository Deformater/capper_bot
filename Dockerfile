FROM python:3.11


WORKDIR /app


COPY requirements.txt requirements.txt


RUN pip install -U pip wheel setuptools && pip install --no-cache-dir --upgrade -r requirements.txt


COPY . .



CMD ["python", "main.py"]
