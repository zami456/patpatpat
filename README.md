changed pet table is here
create the pet table in xampp using this, drop previous one

CREATE TABLE pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    area VARCHAR(100) NOT NULL,
    pet_type VARCHAR(100),
    breed VARCHAR(100),
    age INT NOT NULL,
    sex VARCHAR(10),
    vaccinated BOOLEAN,
    neutered BOOLEAN,
    description TEXT,
    image_filename VARCHAR(255),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
