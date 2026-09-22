CREATE TABLE IF NOT EXISTS universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT,                 -- National University / Private University
    region TEXT                -- Northern Taiwan, Central Taiwan, ...
);

CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL REFERENCES universities(id),
    program_name TEXT NOT NULL,
    field TEXT,                -- e.g. Information and communication technologies
    level TEXT NOT NULL DEFAULT '',   -- e.g. 'Master, Ph.D.'
    scholarship INTEGER NOT NULL,
    website_url TEXT,
    contact TEXT,
    last_checked TEXT,         -- date the data was collected
    UNIQUE (university_id, program_name, levels)
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    affiliation TEXT,
    major TEXT, 
    degree TEXT,
    about TEXT, 
    interests TEXT, 
    preferred_degree TEXT,
    preferred_field TEXT, 
    photo_path TEXT
);