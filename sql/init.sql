CREATE DATABASE IF NOT EXISTS corpwatch
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE corpwatch;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS monitoring_targets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL,
    expected_status INT NOT NULL DEFAULT 200,
    timeout_seconds INT NOT NULL DEFAULT 5,
    max_response_time_ms INT NOT NULL DEFAULT 1000,
    check_interval_seconds INT NOT NULL DEFAULT 60,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_targets_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS check_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    target_id INT NOT NULL,
    status_code INT NULL,
    response_time_ms INT NULL,
    result_type ENUM(
        'SUCCESS',
        'SLOW_RESPONSE',
        'WRONG_STATUS',
        'TIMEOUT',
        'CONNECTION_ERROR'
    ) NOT NULL,
    error_message TEXT NULL,
    checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_results_target
        FOREIGN KEY (target_id)
        REFERENCES monitoring_targets(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    target_id INT NOT NULL,
    check_result_id INT NOT NULL,
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL,
    message TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,

    CONSTRAINT fk_alerts_target
        FOREIGN KEY (target_id)
        REFERENCES monitoring_targets(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_alerts_result
        FOREIGN KEY (check_result_id)
        REFERENCES check_results(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_id INT NULL,
    notification_type ENUM('FAILURE', 'SLOW_RESPONSE', 'REPORT') NOT NULL,
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT NULL,
    status ENUM('SENT', 'FAILED') NOT NULL,
    error_message TEXT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notifications_alert
        FOREIGN KEY (alert_id)
        REFERENCES alerts(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_targets_active
    ON monitoring_targets(is_active);

CREATE INDEX idx_check_results_target_time
    ON check_results(target_id, checked_at);

CREATE INDEX idx_alerts_target_resolved
    ON alerts(target_id, is_resolved);

CREATE INDEX idx_notifications_alert
    ON notifications(alert_id);

INSERT INTO users (name, email)
VALUES ('Default Admin', 'admin@corpwatch.local')
ON DUPLICATE KEY UPDATE email = email;