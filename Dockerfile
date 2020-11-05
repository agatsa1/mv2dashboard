FROM tiangolo/uwsgi-nginx-flask:flask
#-python2.7

MAINTAINER Prashant Gupta <prashant.gupta@agatsa.com>

COPY /app/requirements.txt /tmp
#WORKDIR /flask_app

#RUN apt-get clean \
#    && apt-get -y update

#RUN apt-get install build-essential \
#    && apt-get install python-dev \
#    && apt-get install python-pip

RUN pip install --upgrade pip

RUN pip install -r /tmp/requirements.txt

COPY ./app /app

#RUN chmod +x ./start.sh

#CMD ["python", "pqrst.py"]