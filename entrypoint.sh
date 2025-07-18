#!/bin/sh

# Set the Ollama host and model name
OLLAMA_HOST="ollama:11434"
MODEL_NAME="llama3"

# --- Wait for Ollama Server to be Ready ---
echo "Waiting for Ollama server at $OLLAMA_HOST..."
while ! curl -s "http://$OLLAMA_HOST/api/tags" > /dev/null; do
    echo "Ollama not ready, waiting 5 seconds..."
    sleep 5
done
echo "Ollama server is ready."

# --- Check if the Model is Already Pulled ---
echo "Checking if model '$MODEL_NAME' is available..."
if curl -s "http://$OLLAMA_HOST/api/tags" | jq -e ".models[] | select(.name == \"$MODEL_NAME:latest\")" > /dev/null; then
    echo "Model '$MODEL_NAME' is already available."
else
    # --- Pull the Model if it's Not Available ---
    echo "Model '$MODEL_NAME' not found. Pulling model..."
    curl "http://$OLLAMA_HOST/api/pull" -d "{\"name\": \"$MODEL_NAME\"}"
    echo "Model pull complete."
fi

# Execute the command passed to this script (e.g., streamlit run app.py)
exec "$@"