CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    start_time TIME,
    end_date DATE,
    end_time TIME,
    completed TINYINT(1) DEFAULT 0
);
