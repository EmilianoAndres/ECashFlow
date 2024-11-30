# Use Python 3.12 to ensure compatibility with typed_ast
FROM python:3.12

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# Copy requirements and install dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Install additional packages
RUN apt-get update && apt-get install -y libzbar0 libgl1

# Expose the port
EXPOSE 8000

# Copy the application code
COPY . /code/