-- init-db.sql
-- This script runs automatically when PostgreSQL container starts for the first time

-- Create database for Django users service
CREATE DATABASE pms_users_db;

-- Create database for Flask tasks service
CREATE DATABASE pms_tasks_db;

-- Optional: Create separate users with limited permissions
CREATE USER users_service WITH PASSWORD 'users_password';
CREATE USER tasks_service WITH PASSWORD 'tasks_password';

GRANT ALL PRIVILEGES ON DATABASE pms_users_db TO users_service;
GRANT ALL PRIVILEGES ON DATABASE pms_tasks_db TO tasks_service;

SELECT 'CREATE DATABASE pms_notifications_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pms_notifications_db')\gexec