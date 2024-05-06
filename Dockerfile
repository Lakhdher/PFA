# Use the official Python image as the base image
FROM python:3.10-slim 

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY ./requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose the Flask application port
EXPOSE 8000

# Set the command to run the Flask app
CMD [ "python3", "-m" , "run", "--host=0.0.0.0"]
