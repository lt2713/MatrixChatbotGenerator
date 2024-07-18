# Matrix Chatbot Generator

## Overview
The Matrix Chatbot Generator is a Python-based project that runs a Flask 
web application for the Quiz Database and the Quizbot itself. 
This repository contains all the necessary code and configuration to set up and run both 
applications in a Docker container.
It also contains a Client application, that accesses the flask application to write
to the Quiz database.

## Prerequisites
Before you begin, ensure you have the following installed on your local machine:
- Docker
- Docker Compose
- Python 3
- pyInstaller

## Installation of the Server application

- Clone the Repository

git clone https://github.com/yourusername/MatrixChatbotGenerator.git

- Copy the environment variables file:

cp .env.example .env

- Edit the .env file:

The Matrix User must exist on the selected Matrix Home Server. The DB-fields are
used for the Client Application as a default configuration. The DB_URL should be
the url the flask application is running at. 

- If you changed the port in the .env file, you need to change it in the Dockerfile
and in docker-compose.yml as well.

- Build and start the Docker container:

docker-compose up --build

## Accessing the Server Applications

The flaskapp should be available at http://localhost:8000 (or your chosen port).
The Quizbot should be available to chat on the Matrix Home Server.

## Installation of the Client Application

- Clone the Repository

git clone https://github.com/yourusername/MatrixChatbotGenerator.git

- Create the Client application:

python build_executable.py

## Accessing the Client Application

The Matrix Quizbot Generator.exe should now be in the dist directory of this repository. 



