FROM python:3.10-slim
WORKDIR /app
# install ffmpeg, git and build dependencies
RUN apt-get update && apt-get install -y ffmpeg git build-essential && rm -rf /var/lib/apt/lists/*
COPY . /app
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 3000
CMD ["python3", "-m", "VISHALMUSIC"] 
