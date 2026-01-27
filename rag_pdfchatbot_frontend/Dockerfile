
# Stage 1: Builder stage - install dependencies and copy source code
FROM python:3.10-slim AS builder

WORKDIR /app

# Copy requirements and install Python packages in user mode
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy the full app code
COPY . .

# Stage 2: Runtime stage - create a clean image with just app and dependencies
FROM python:3.10-slim

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy app source code from builder stage
COPY --from=builder /app .

# Add local pip binaries to PATH
ENV PATH=/root/.local/bin:$PATH

# Expose Streamlit's default port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]