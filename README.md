# MedQuery Local 🩺

### A local, private, GPU-accelerated application for querying your health data with natural language.

This project provides a web-based user interface, powered by Streamlit, to upload your own Electronic Health Record (EHR) data from a CSV file. It uses a locally-hosted Large Language Model (LLM) served by Ollama to create a powerful AI agent. This agent can understand questions asked in plain English, convert them into SQL queries, and give you back answers based on your data.

Your data never leaves your machine, ensuring 100% privacy.

## Features

  * **Private & Local:** Your data is processed entirely on your machine and is never sent to a third-party API.
  * **Natural Language Queries:** Ask complex questions like "How many patients have an average health expense over $5000?" instead of writing SQL code.
  * **GPU Accelerated:** Uses Ollama to run powerful open-source LLMs (like Llama 3, Gemma 2) on your local NVIDIA GPU for fast performance.
  * **Easy Setup:** The entire application stack is managed by Docker Compose and runs with a single command.
  * **Swappable Models:** Easily switch between different LLMs by changing just two lines of code.

## Architecture

The application runs as a multi-container setup managed by Docker Compose:

```
[User] <--> [Web Browser] <--> [Streamlit Container (medquery-app)] <--> [Ollama Container (ollama)] <--> [NVIDIA GPU]
```

1.  The **Ollama Container** downloads and serves the LLM, accessing the host's GPU for acceleration.
2.  The **Streamlit Container** runs the Python web application, waits for Ollama to be ready, and automatically pulls the required model before starting the UI.

## Prerequisites

Before you begin, ensure you have the following installed on your host machine:

  * [Docker](https://www.docker.com/products/docker-desktop/)
  * An **NVIDIA GPU** with sufficient VRAM for the chosen model (at least 8GB recommended).
  * The latest [NVIDIA Drivers](https://www.nvidia.com/download/index.aspx) for your operating system.
  * The [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html), which allows Docker to access the GPU.

## Installation & Running

1.  **Get the Project Files**
    Clone this repository or ensure you have the following files in a single directory:

      * `docker-compose.yml`
      * `Dockerfile`
      * `entrypoint.sh`
      * `app.py`
      * `requirements.txt`

2.  **Start the Application**
    Open a terminal in the project's root directory and run the following command:

    ```bash
    docker-compose up --build
    ```

    The first time you run this, it will:

      * Build the `medquery-app` Docker image.
      * Pull the official `ollama` image.
      * Start both containers.
      * The `medquery-app` will wait for the Ollama server and then automatically run `ollama pull` to download the language model (e.g., `llama3`). This may take several minutes.

3.  **Access the UI**
    Once you see the "Starting Streamlit application..." message in your terminal, open your web browser and navigate to:
    [**http://localhost:8501**](https://www.google.com/search?q=http://localhost:8501)

## How to Use

1.  In the web UI, use the sidebar to **upload a CSV file** containing your EHR data.
2.  Click the **"Load Data"** button. The application will load your data into a temporary, in-memory SQL database.
3.  Once the data is loaded, you can **ask questions** in the chat input box at the bottom of the page and press Enter. The agent will show its work in the terminal and display the final answer in the UI.

## Customization: How to Change the LLM

This project is configured to use `llama3` by default, but you can easily switch to another model like Google's `gemma2:9b`.

1.  **In `entrypoint.sh`**, change the `MODEL_NAME` variable to the new model you want to automatically pull.

    ```bash
    # In the ensure_model_exists() function:
    MODEL_NAME="gemma2:9b" # Or "phi3", "llama3:70b", etc.
    ```

2.  **In `app.py`**, update the `model` parameter in the `get_llm` function to match.

    ```python
    # In the get_llm function:
    def get_llm():
        return ChatOllama(model="gemma2:9b", ...)
    ```

3.  Rebuild and restart the application with `docker-compose up --build`.

## Project Files

  * `docker-compose.yml`: Defines and orchestrates the `ollama` and `medquery-app` services.
  * `Dockerfile`: Instructs Docker on how to build the Python/Streamlit application image.
  * `entrypoint.sh`: A startup script that waits for the Ollama server and automatically pulls the required model before launching the app.
  * `app.py`: The core Streamlit application code, containing the UI and LangChain agent logic.
  * `requirements.txt`: A list of the Python packages required for the application.