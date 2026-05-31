FROM python:3.14-slim

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /code
COPY . /code/
WORKDIR /code
ENV FLASK_APP=entry_points.flask_app FLASK_DEBUG=1 PYTHONUNBUFFERED=1
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
