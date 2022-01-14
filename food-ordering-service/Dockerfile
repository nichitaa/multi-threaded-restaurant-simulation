FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 5000

CMD [ "python3", "-u" , "main.py"]

# 1'st
# docker build --tag food_ordering .
# docker network create nt
# docker run -d --net nt --name food_ordering food_ordering
# docker build --tag food_ordering . && docker run --net nt --name food_ordering food_ordering