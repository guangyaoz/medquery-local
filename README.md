# 🩺 MedQuery Local: LLM-Powered EHR Query Tool

MedQuery Local is a powerful, privacy-focused AI agent that allows you to ask complex questions about your medical data using natural language. It runs entirely on your local machine using Docker and Ollama, ensuring your data never leaves your computer.

The setup is fully automated. On the first run, the application will automatically download the required LLM model and then start the interactive query session.

## Key Features

* **100% Local**: All components, including the Large Language Model, run locally.
* **Privacy First**: Your data is never uploaded to a third-party service.
* **Natural Language Queries**: Ask questions in plain English instead of writing complex SQL or code.
* **Automated Setup**: The required LLM model is automatically downloaded on the first launch.
* **Dockerized**: The entire application is containerized for a clean, one-command setup.

---
## Tech Stack

* **Orchestration**: Docker, Docker Compose
* **LLM Serving**: Ollama
* **AI Framework**: LangChain
* **Backend**: Python
* **Model**: Llama3

---
## Setup and Installation

### Prerequisites

You only need **Docker**  installed on your system.

### Step 1: Clone the Repository

Open your terminal and clone the project repository from GitHub.

### Step 2: Add Your Data

Place all of your clinical data CSV files (e.g., patients.csv, encounters.csv) inside the ./data folder.

### Step 3: Build

Run a single command from your project's root directory to build and start everything:

<code>docker-compose up --build</code>

### Step 4: Run

Run this command to start an interactive section to chat with the agent. 

<code>docker-compose run --rm app</code>

To stop the application, enter "exit" into the chatbox.