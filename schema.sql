-- =============================================================
-- MySQL table creation script for the Voltage Drop Project
-- Run this script once to set up the required database schema.
-- =============================================================

-- 1. Create (or switch to) the project database
CREATE DATABASE IF NOT EXISTS voltage_drop_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE voltage_drop_db;

-- 2. Create the user table
CREATE TABLE IF NOT EXISTS tbl_user (
    id         INT          NOT NULL AUTO_INCREMENT,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,          -- stores the Werkzeug password hash
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
