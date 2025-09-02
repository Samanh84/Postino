# Use official Python image
FROM python:3.11-slim

# Set work directory to backend (جایی که manage.py هست)
WORKDIR /app/backend

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Copy project
COPY . /app/

# Expose port
EXPOSE 8000

# Start Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
