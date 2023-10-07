FROM python:3.10.12-slim


ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Required to install mysqlclient with Pip

# Install pipenv
COPY ./requirements.txt ./requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt update
RUN pip install -r requirements.txt
# Copy the application files into the image
COPY . /app/

# Expose port 8000 on the container
EXPOSE 8000