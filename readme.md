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

All terminal commands given below are for Windows machines.

## Installation of the Server application

Clone the Repository:

>git clone https://github.com/lt2713/MatrixChatbotGenerator

Create the file ".env" in the base directory using the file ".env.example" as a model:

>copy .env.example .env

Edit the .env file:
Some parameteres can be adjusted using the .env file. The Matrix Server, User and password 
must exist and be correct. The other parameters can be left as they are.
The DB-variables are used for the Client Application as a default configuration. 
The DB_URL must be the url the flask application is running at. 

If you want to enable HTTPS, you have to copy your cert.pem and key.pem files into 
the store directory and edit the file store/flask_app.py and set ssl_enabled to True.

If you changed the port in the .env file, you need to change it in the Dockerfile
and in docker-compose.yml as well.

Build and start the Docker container:

>docker-compose up --build

### Installation of the Server application without Docker

You can run the application without using docker. To do so, follow the guide above until you have
setup your .env file. Then follow these steps:

Install the dependencies using a virtual environment:

>python install.py

Activate the virtual environment:

>venv\Scripts\activate

Run the flask app used for the HTTP Requests of the client application:

>python MatrixChatbotGenerator\run_flask_app.py

In a different terminal run the script to start the Chatbot after activating the virtual environment:

>python MatrixChatbotGenerator\run_quizbot.py

## Accessing the Server Applications

The flaskapp should be available at http://localhost:8000 (or your chosen port).
The Quizbot should be available to chat on the Matrix Home Server.

## Installation of the Client Application

Clone the Repository

>git clone https://github.com/lt2713/MatrixChatbotGenerator

Install the dependencies using a virtual environment:

>python install.py

Activate the virtual environment:

>venv\Scripts\activate

Create the Client application:

> python build_executable.py

## Accessing the Client Application

The Matrix Quizbot Generator.exe should now be in the dist directory of the repository. 



