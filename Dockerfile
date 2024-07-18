# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory
WORKDIR /MatrixChatbotGenerator

# Copy the current directory contents into the container at /app
COPY . /MatrixChatbotGenerator

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy example env file to actual env file
# COPY .env.example .env

# Make port available to the world outside this container
EXPOSE 8000

# Run flask and the server
CMD ["sh", "-c", "python MatrixChatbotGenerator/run_quizbot.py & python MatrixChatbotGenerator/run_flask_app.py"]
