MODEL = """FilmGenres (
    FilmGenreID integer PRIMARY KEY,
    FilmID integer NOT NULL,
    GenreID integer NOT NULL,
    FOREIGN KEY (FilmID) REFERENCES Movies(FilmID),
    FOREIGN KEY (GenreID) REFERENCES Genres(GenreID))"""
