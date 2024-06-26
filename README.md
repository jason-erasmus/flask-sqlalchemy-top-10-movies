# flask-sqlalchemy-top-10-movies

Website to rank and display movies. Data is sourced from an external database and stored in a local database with user added ranks. This was a fun exercise to learn flask and SQLlite with some Bootstrap.

## Demo

![demo3](https://github.com/jason-erasmus/flask-sqlalchemy-top-10-movies/assets/69726847/54b9e824-9138-4e73-9b38-1853f481f448)


## Installation

1. Clone the repository

```bash
 git clone <repository_url>
 cd <repository_dir>
```

2. Create a virtual environment (recommended)

```bash
  #windows
  python -m venv <env_name>

  #mac
  python3 -m venv <env_name>
```

3. Install framework and packages with pip using the requirements.txt file

```bash
  pip install -r requirements.txt
```

4. Run the main.py to initialize the local server and copy the link into your web browser

![initialize](https://github.com/jason-erasmus/flask-sqlalchemy-top-10-movies/assets/69726847/9121223a-dda8-49e5-b399-1a5020f16f0b)

## Documentation

### 1. Database

SQLAlchemy will make a local database on your machine to store user choice for movies. It will store required data for each movie to display on the web page.

### 2. Movie Data

Movie meta data is sourced from The Movie Database https://www.themoviedb.org/?language=en-GB you can simply register for an API key if you would like to experiment with the repo.

### 3. Build

Flask was used to build the website and styled using Bootstrap and WTForms.
