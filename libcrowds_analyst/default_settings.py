# LibCrowds API key for an admin user
API_KEY = ''

# URL of the LibCrowds server
ENDPOINT = 'http://www.libcrowds.com'

# Basic auth username for libcrowds-analyst
USERNAME = 'admin'

# Basic auth password for libcrowds-analyst
PASSWORD = 'secret'

# Key for cryptographically signing form data
SECRET_KEY = 'its-a-secret'

# Server host and port
HOST = '0.0.0.0'
PORT = 5001

# Debugging
DEBUG = False

# Z3950 setup
Z3950_DATABASES = {}
Z3950_URL = ""

# Folder to store task input zip files
ZIP_FOLDER = "/tmp/"

# Required match percentage
MATCH_PERCENTAGE = 60

# Task run info keys to be excluded from results processing
# ip_address is excluded by default as it is used by libcrowds-data
EXCLUDED_KEYS = ['ip_address']