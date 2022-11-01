FROM python:3.10.8-alpine3.16

WORKDIR  /usr/src/app

COPY requirements.txt ./requirements.txt
COPY main.py ./main.py
COPY ./dealership ./dealership
COPY ./test ./test

RUN pip install --no-cache-dir -r requirements.txt

CMD ["pytest"]
