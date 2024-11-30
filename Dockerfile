FROM python:3.11.7
RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3-pip -y
RUN pip3 install -U pip
COPY . /app/
WORKDIR /app/
RUN pip3 install -r requirements.txt
CMD ["bash","start.sh"]
