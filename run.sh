#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

IMAGE_NAME="finops-env"
CONTAINER_NAME="finops-env-container"
PORT=7860

echo "🚀 Building Docker image '$IMAGE_NAME'..."
docker build -t $IMAGE_NAME .

echo "🏃 Starting Docker container '$CONTAINER_NAME' on port $PORT..."
# Clean up any existing container with the same name
docker rm -f $CONTAINER_NAME 2>/dev/null || true
docker run -d --name $CONTAINER_NAME -p $PORT:$PORT $IMAGE_NAME

echo "⏳ Waiting for the FastAPI server to become healthy..."
MAX_RETRIES=15
RETRY_COUNT=0

# Loop until the healthcheck endpoint returns the expected JSON or we time out
until curl -s http://localhost:$PORT/health | grep -q '"status":"ok"'; do
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Healthcheck failed or timed out. Check container logs:"
        docker logs $CONTAINER_NAME
        docker rm -f $CONTAINER_NAME
        exit 1
    fi
    echo "   ...waiting (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT+1))
done

echo "✅ Environment is up and healthy!"

echo "🤖 Running baseline inference script..."
# Check if key is in the environment OR if a .env file exists
if [ -z "$OPENAI_API_KEY" ] && [ ! -f .env ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY environment variable is not set and no .env file found."
    echo "Please create a .env file with your key."
    echo "Cleaning up container..."
    docker rm -f $CONTAINER_NAME
    exit 1
else
    # Run the baseline script
    python3 finops_env/baseline.py
fi

echo "🧹 Cleaning up..."
docker rm -f $CONTAINER_NAME

echo "🎉 Run complete! Your OpenEnv submission is ready to ship."