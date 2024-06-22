FROM python:3.9-slim

# Set docker related environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /darwin-app

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

COPY requirements.txt /darwin-app/
RUN pip install -r requirements.txt

COPY . /darwin-app/

# Make entrypoint.sh executable
RUN chmod +x /darwin-app/entrypoint.sh

# # Expose the port the app runs on
# EXPOSE 8000

# ENTRYPOINT ["/darwin-app/entrypoint.sh"]