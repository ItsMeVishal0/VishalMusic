FROM python:3.10-slim
WORKDIR /app
# install ffmpeg and build dependencies
RUN apt-get update && apt-get install -y ffmpeg git build-essential && rm -rf /var/lib/apt/lists/*
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# Expose nothing; this is a background worker
CMD ["python3", "-m", "VISHALMUSIC"] 
