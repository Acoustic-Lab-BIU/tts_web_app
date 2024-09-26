# # Use an official Python runtime as a parent image
# FROM python:3.9-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the current directory contents into the container at /app
# COPY . .

# # Copy the SSH key to the container
# COPY id_rsa /root/.ssh/id_rsa

# # Set the appropriate permissions for the SSH key
# RUN chmod 600 /root/.ssh/id_rsa

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Make port 5000 available to the world outside this container
# EXPOSE 5000

# # Define environment variable
# ENV FLASK_APP=app.py

# # Run the application
# CMD ["flask", "run", "--host=0.0.0.0"]

# Use an appropriate base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Copy the SSH key into the container
COPY id_rsa /root/.ssh/id_rsa

# Set permissions for the SSH key
RUN chmod 600 /root/.ssh/id_rsa

# Expose the port your app runs on
EXPOSE 5000

# Command to run your application
CMD ["python3", "app.py"]
