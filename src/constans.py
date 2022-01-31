from pathlib import Path

# names
DB_NAME = 'db.sqlite'
RESOURCES_DIR_NAME = 'Resources'

# directories
BASE_DIR = Path(__file__).resolve().absolute().parent
PROJECT_DIR = BASE_DIR.parent.parent.parent
RESOURCES_DIR = Path.joinpath(PROJECT_DIR, RESOURCES_DIR_NAME)

# DB
DB_URI = Path.joinpath(RESOURCES_DIR, DB_NAME)

# SCHEMAS
DATETIME_FORMAT = '%d-%m-%Y %H:%M%:%S'
