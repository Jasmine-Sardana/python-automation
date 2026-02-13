FROM python:3.13-slim

# Update and upgrade OS packages
RUN apt-get update && apt-get upgrade -y 

# Upgrade pip
RUN pip3 install --no-cache-dir --upgrade pip

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy and install application
COPY . /app
RUN pip3 install -e .

CMD ["python3", "-m", "src"]
