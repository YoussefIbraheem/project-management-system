# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim

# Env Vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create a non-root user and group for running the application
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
RUN mkdir -p /home/appuser && chown -R appuser:appgroup /home/appuser

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install pip requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Run Alembic migrations on container start
COPY alembic_migration_entrypoint.sh /alembic_migration_entrypoint.sh
RUN chmod +x /alembic_migration_entrypoint.sh

ENTRYPOINT ["/alembic_migration_entrypoint.sh"]

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()"]
