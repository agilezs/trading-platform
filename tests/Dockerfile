FROM python:3.11-slim

WORKDIR /

#ENV PYTHONPATH=/app
COPY . ./tests

RUN pip install -r /tests/requirements.txt

CMD pytest /tests --html=/tests/reports/report.html --self-contained-html -s -v