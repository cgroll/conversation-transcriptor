FROM ubuntu:22.04

ADD src $HOME/src
COPY click_app.py $HOME/click_app.py
COPY requirements.txt $HOME/requirements.txt
COPY setup.py $HOME/setup.py
COPY .env $HOME/.env

RUN apt-get update
RUN apt-get install -y git python3.10 python3-pip ffmpeg portaudio19-dev python3-pyaudio

RUN pip install -r requirements.txt