CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20) UNIQUE
);

ALTER TABLE contacts
ADD COLUMN email VARCHAR(100),
ADD COLUMN birthday DATE,
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN group_id INTEGER;

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE phones (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10)
    CHECK (type IN ('home', 'work', 'mobile'))
);

ALTER TABLE contacts
ADD CONSTRAINT fk_group
FOREIGN KEY (group_id)
REFERENCES groups(id);