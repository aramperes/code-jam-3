FROM python:3.6.5-stretch

ADD . .

RUN pip install pipenv
RUN pipenv lock --pre
RUN pipenv sync

CMD pipenv run python3 .
