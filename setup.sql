-- File: setup.sql
-- ...
CREATE ROLE mechanic_user WITH LOGIN PASSWORD 'your_password';

CREATE DATABASE mechanicgpt_db
    OWNER = mechanic_user;
-- ...