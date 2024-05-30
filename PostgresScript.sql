CREATE TABLE country (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) UNIQUE
);

CREATE TABLE university (
    university_id SERIAL PRIMARY KEY,
    university_name VARCHAR(255),
    country_id INT,
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

CREATE TABLE person (
    person_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(100),
    gender VARCHAR(10),
    country_id INT,
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);
select * from university