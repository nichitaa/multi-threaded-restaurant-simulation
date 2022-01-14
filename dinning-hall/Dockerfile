FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 5000

CMD [ "python3", "-u" , "main.py"]

# 2'nd
# docker build --tag dinning_hall .
# docker run -d --net nt --name dinning_hall dinning_hall
# docker build --tag dinning_hall . && docker run --net nt --name dinning_hall dinning_hall