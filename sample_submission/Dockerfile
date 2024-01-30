# This is a sample Dockerfile
# You may adapt this to meet your environment needs

FROM python:3.10

# Install necessary libraries; tesseract & dependencies for opencv
RUN apt-get update && \
    apt-get install -y tesseract-ocr libgtk-3-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev libjpeg-dev libpng-dev libtiff-dev \
    gfortran openexr libatlas-base-dev \
    libtbbmalloc2 libtbb-dev libopenexr-dev \
    libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libgl1-mesa-dev libglib2.0-0 

# Set the working directory in the container
WORKDIR /app

# Copy your Python script into the container at /app
COPY . /app/

# Install & download neccessary files required
RUN ./install.sh

# Install python requirements
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]