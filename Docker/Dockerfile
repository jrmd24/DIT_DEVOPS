FROM ubuntu:latest

RUN apt-get update -y

RUN apt-get install -y python3-pip
RUN apt-get install -y pip3
RUN apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git

RUN  rm -rf /var/lib/apt/lists/*

RUN mkdir /app

WORKDIR /app

#RUN git clone https://github.com/jrmd24/DIT_DEVOPS.git .

COPY ../. .

RUN pip3 install -r requirements.txt
#RUN apt-get install python3-pandas

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "g4_dc_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
