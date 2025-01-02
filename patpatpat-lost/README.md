ALTER TABLE lost_found ADD COLUMN status ENUM('lost', 'found') NOT NULL;
CREATE TABLE lost_found (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    photo VARCHAR(255) NOT NULL,
    status ENUM('lost', 'found') NOT NULL
);
