CREATE DATABASE IF NOT EXISTS synergai;
USE synergai;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    university VARCHAR(255),
    skills TEXT,
    interests TEXT,
    role VARCHAR(255),
    availability VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
