# syntax=docker/dockerfile:1

FROM python:3.8
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

EXPOSE 8050
CMD ["python", "./index.py", "--host=0.0.0.0"]


