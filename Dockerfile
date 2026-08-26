FROM python:3.11-slim

# Install system audio, compression, and imaging tools found in install.sh and server.py
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    zip \
    unzip \
    ffmpeg \
    sox \
    mediainfo \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the dependencies directly 
COPY webpy-v.0.76.zip /tmp/

# Install exact application requirements
RUN pip install --no-cache-dir /tmp/webpy-v.0.76.zip mutagen pillow markdown requests

# Copy source repository structure
COPY . /app

# Ensure required runfirst directories exist with proper access bounds
RUN mkdir -p p/posts p/zipped p/comborank p/heartrank p/deleted u/ r/visitors r/invites r/trusted r/users r/stopflood r/stopresetpass sessions

# Expose web.py's standard fallback port
EXPOSE 8080

# Run standalone server framework natively
CMD ["python3", "server.py"]
