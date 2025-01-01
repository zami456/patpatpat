need to add some columns:
ALTER TABLE users
ADD COLUMN contact_no VARCHAR(11);


ALTER TABLE pets
ADD COLUMN img2 VARCHAR(255),
ADD COLUMN img3 VARCHAR(255);





CREATE TABLE users(  id INT AUTO_INCREMENT PRIMARY KEY,  email VARCHAR(255) NOT NULL UNIQUE,  first_name VARCHAR(255) NOT NULL,  password VARCHAR(255) NOT NULL  );




--
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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);



CREATE TABLE adoption_request (
    user_id INT NOT NULL,
    pet_id INT NOT NULL,
    PRIMARY KEY (user_id, pet_id),
    message TEXT,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
);
