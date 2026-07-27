# Use the official Python runtime image
FROM python:3.12-slim  

# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Create the accounts directory
RUN mkdir /accounts

# Set the working directory inside the container
WORKDIR /accounts

# Upgrade pip
RUN pip install --upgrade pip 

# Copy the Django project  and install dependencies
COPY requirements.txt  /accounts/

# run this command to install all dependencies 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project to the container
COPY . /accounts/

# Create a non-root user and group for running the application
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
RUN mkdir -p /home/appuser && chown -R appuser:appgroup /home/appuser

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /accounts

# Switch to the non-root user
USER appuser

# Expose the Django port
EXPOSE 8000

# Run Django's development server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "users.wsgi:application"]