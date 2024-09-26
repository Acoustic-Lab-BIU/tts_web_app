#!/bin/bash

# Start the Docker container
cd /home/lab/Desktop/tts_web_app || exit 

docker compose up -d

# Give it a moment to ensure the container is running
sleep 1

# Open the web app in a new browser window (you can use any browser)
# Here, we're using Google Chrome as an example; adjust as needed
firefox --new-window http://localhost:5000 &

# Store the PID of the browser
BROWSER_PID=$!
echo $BROWSER_PID
# Wait for the browser to close
wait $BROWSER_PID

# Stop the Docker container
docker compose down
