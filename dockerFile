# Base image
FROM python:3.12.2-slim-bullseye as production

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential default-libmysqlclient-dev pkg-config \
  && pip install --no-cache-dir --upgrade pip


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
WORKDIR /code
COPY ./requirements.txt /code
RUN pip install -r requirements.txt

# Copy project
COPY . /code

# Expose the port
EXPOSE 8000

# Dockerfile

# Set environment variables during the build process
ARG ALPHA_VANTAGE_API_KEY
ARG DATABASE_URL
ARG SECRET_KEY

# Set them as environment variables inside the container
ENV ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY}
ENV DATABASE_URL=${DATABASE_URL}
ENV SECRET_KEY=${SECRET_KEY}


# Example of using the environment variable in your app
# Install dependencies, etc.
RUN echo $ALPHA_VANTAGE_API_KEY  # just for demonstration


# Run the application
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "financialapp.wsgi:application"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

