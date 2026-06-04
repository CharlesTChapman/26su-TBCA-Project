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
    id          INTEGER PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    location    VARCHAR(255)
);

CREATE TABLE budget_manager (
    id          INTEGER PRIMARY KEY,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    email       VARCHAR(100) NOT NULL
);

CREATE TABLE survey_form (
    student_id  INTEGER NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
    avg_gpa         FLOAT,
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

CREATE TABLE budget_plan_university (
    plan_id       INTEGER NOT NULL,
    university_id INTEGER NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount        INTEGER,
    PRIMARY KEY (plan_id, university_id),
    FOREIGN KEY (plan_id)       REFERENCES budget_plan(id),
    FOREIGN KEY (university_id) REFERENCES university(id)
);