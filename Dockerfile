FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY openenv.yaml .
COPY finops_env/ /app/finops_env/

# Expose required port
EXPOSE 7860

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1

# Start FastAPI server via Uvicorn
CMD ["uvicorn", "finops_env.main:app", "--host", "0.0.0.0", "--port", "7860"]