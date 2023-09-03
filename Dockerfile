# Use an official Python runtime as a parent image
FROM python:3.8-slim
#RUN apt-get update -y
#RUN apt-get install curl -y
# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
#RUN chmod -R 777 /app
#ENV FLASK_APP=backend.py

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
#ENV FLASK_ENV=development

# Run the Flask application
#CMD ["flask", "run", "--host", "0.0.0.0"]
CMD ["python", "backend.py"]