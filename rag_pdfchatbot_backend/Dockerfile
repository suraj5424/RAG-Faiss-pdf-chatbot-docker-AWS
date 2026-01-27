
# Stage 1: Builder stage - install build dependencies and Python packages
FROM python:3.10-slim AS builder

# Set working directory inside the container
WORKDIR /app

# Install build tools (if you have any native dependencies to compile)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies to a user directory to keep it isolated
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy the entire backend source code into the container
COPY . .

# Stage 2: Runtime stage - create minimal runtime image
FROM python:3.10-slim

WORKDIR /app

# Copy installed Python packages from the builder stage
COPY --from=builder /root/.local /root/.local

# Copy backend application code
COPY --from=builder /app .

# Copy the ONNX model directory into the container
COPY ./onnx_model /app/onnx_model

# Add local pip binaries to PATH
ENV PATH=/root/.local/bin:$PATH

# Expose the port your FastAPI app will run on
EXPOSE 8000

# Command to run the FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
