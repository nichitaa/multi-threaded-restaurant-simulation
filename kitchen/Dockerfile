FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 5000

CMD [ "python3", "-u" , "main.py"]

# 3'rd
# docker build --tag kitchen .
# docker run -d --net nt --name kitchen kitchen
# docker build --tag kitchen . && docker run --net nt --name kitchen kitchen