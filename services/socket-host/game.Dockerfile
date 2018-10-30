FROM python:3.6.5-stretch

ADD . .

RUN pip install pipenv
RUN pipenv lock
RUN pipenv sync

CMD pipenv run python3 . --game
