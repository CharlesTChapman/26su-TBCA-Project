-- Ensure this script is read as UTF-8 (the mysql client defaults to latin1
-- in this image, which would corrupt any non-ASCII data on import).
SET NAMES utf8mb4;

CREATE TABLE student (
    id          INTEGER PRIMARY KEY,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    email       VARCHAR(100) NOT NULL,
    address     VARCHAR(255),
    major       VARCHAR(100)
);

CREATE TABLE labor_statistician (
    id          INTEGER PRIMARY KEY,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    email       VARCHAR(100) NOT NULL
);

CREATE TABLE university (
    id             INTEGER PRIMARY KEY AUTO_INCREMENT,
    name           VARCHAR(100) NOT NULL UNIQUE,
    location       VARCHAR(255),
    student_fees   FLOAT,
    charges_fees     INTEGER,
    per_student_fees FLOAT,
    highest_degree FLOAT,
    staff_fte      FLOAT,
    web_pages      VARCHAR(50),
    total_students   FLOAT,
    latitude         FLOAT,
    longitude        FLOAT,
    country          VARCHAR(2)
);

CREATE TABLE budget_manager (
    id          INTEGER PRIMARY KEY,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    email       VARCHAR(100) NOT NULL
);

CREATE TABLE survey_form (
    student_id             INTEGER NOT NULL,
    created_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    student_budget         FLOAT,
    student_degree_level   INTEGER,
    student_size           INTEGER,
    student_major          VARCHAR(100),
    student_country        VARCHAR(100),
    student_proximity_min  INTEGER,
    student_proximity_max  INTEGER,
    student_campus_type    VARCHAR(20),
    student_financial_aid  BOOLEAN,
    PRIMARY KEY (student_id),
    FOREIGN KEY (student_id) REFERENCES student(id)
);

CREATE TABLE favorites (
    student_id    INTEGER NOT NULL,
    university_id INTEGER NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, university_id),
    FOREIGN KEY (student_id)    REFERENCES student(id),
    FOREIGN KEY (university_id) REFERENCES university(id)
);

CREATE TABLE recommendations (
    student_id    INTEGER NOT NULL,
    university_id INTEGER NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, university_id),
    FOREIGN KEY (student_id)    REFERENCES student(id),
    FOREIGN KEY (university_id) REFERENCES university(id)
);

CREATE TABLE country_coords (
    country    VARCHAR(100) NOT NULL PRIMARY KEY,
    latitude   FLOAT NOT NULL,
    longitude  FLOAT NOT NULL
);

CREATE TABLE pros_cons (
    student_id    INTEGER NOT NULL,
    university_id INTEGER NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pros          TEXT,
    cons          TEXT,
    PRIMARY KEY (student_id, university_id),
    FOREIGN KEY (student_id)    REFERENCES student(id),
    FOREIGN KEY (university_id) REFERENCES university(id)
);

CREATE TABLE academic_reports (
    university_id   INTEGER NOT NULL,
    year            YEAR NOT NULL,
    students        INTEGER,
    graduation_rate FLOAT,
    PRIMARY KEY (university_id, year),
    FOREIGN KEY (university_id) REFERENCES university(id)
);

CREATE TABLE budget_plan (
    id              INTEGER PRIMARY KEY,
    university_id   INTEGER NOT NULL,
    budget_manager_id INTEGER NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount    INTEGER,
    FOREIGN KEY (university_id) REFERENCES university(id),
    FOREIGN KEY (budget_manager_id) REFERENCES budget_manager(id)
);