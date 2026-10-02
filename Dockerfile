FROM python:3.10-slim
WORKDIR /app
# install ffmpeg, git and build dependencies
# libgl1/libglib2.0-0/libsm6/libxext6 are required by opencv-python (cv2, used in
# VISHALMUSIC/plugins/tools/tiny.py). Debian slim does not ship them, so without
# these `import cv2` fails and the plugin logs a module-load error.
RUN apt-get update && apt-get install -y ffmpeg git build-essential \
    libgl1 libsm6 libxext6 \
    && (apt-get install -y libglib2.0-0 || apt-get install -y libglib2.0-0t64) \
    && rm -rf /var/lib/apt/lists/*
COPY . /app
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 3000
CMD ["python3", "-m", "VISHALMUSIC"] 
