-- Table structure for table `country`
CREATE TABLE country (
    country_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Table structure for table `university`
CREATE TABLE university (
    university_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    alpha_two_code VARCHAR(10),
    state_province VARCHAR(255),
    domains JSON,
    web_pages JSON,
    country_id INT REFERENCES country(country_id),
    UNIQUE (name, country_id)
);

-- Table structure for table `location`
CREATE TABLE location (
    location_id SERIAL PRIMARY KEY,
    street VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postcode VARCHAR(50),
    latitude VARCHAR(50),
    longitude VARCHAR(50),
    timezone_offset VARCHAR(10),
    timezone_description VARCHAR(255),
    UNIQUE (street, city, state, country, postcode)
);

-- Table structure for table `users`
CREATE TABLE users (
    users_id SERIAL PRIMARY KEY,
    gender VARCHAR(10),
    title VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255),
    date_of_birth TIMESTAMP,
    registered_date TIMESTAMP,
    phone VARCHAR(20),
    cell VARCHAR(20),
    nationality VARCHAR(50),
    picture_large VARCHAR(255),
    picture_medium VARCHAR(255),
    picture_thumbnail VARCHAR(255),
    location_id INT REFERENCES location(location_id)
);
select * from users
