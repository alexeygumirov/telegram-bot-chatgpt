# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY app/. /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
# EXPOSE 80

# Define environment variable
# ENV TELEGRAM_API_TOKEN your_telegram_api_token
# ENV CHATGPT_API_KEY your_chatgpt_api_key

# Run telegram_bot.py when the container launches
CMD ["python", "telegram_bot.py"]

