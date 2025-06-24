FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Make sure entrypoint is executable
RUN chmod +x entrypoint.sh

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run the startup script
ENTRYPOINT ["./entrypoint.sh"]