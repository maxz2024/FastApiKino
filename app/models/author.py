MODEL = """ Author (
    id INTEGER PRIMARY KEY,
    user_id Integer NOT NULL,
    author_name TEXT NOT NULL,
    birth_date DATE NOT NULL,
    FOREIGN KEY(user_id) REFERENCES User(id))"""