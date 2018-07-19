from os import environ

# Database parameters
DB_USER = environ.get('DB_USER')
DB_PASS = environ.get('DB_PASS')
DB_URL = environ.get('DB_URL')
DB_NAME = environ.get('DB_NAME')
DB_PORT = environ.get('DB_PORT')

# Redis parameters
REDIS_URL = environ.get('REDIS_URL')

# Facebook API parameters
FB_ACCESS_TOKEN = environ.get('FB_ACCESS_TOKEN')

# Wit API parameters
WIT_ACCESS_TOKEN = environ.get('WIT_ACCESS_TOKEN')

# Zendesk API parameters
ZENDESK_ACCESS_TOKEN = environ.get('ZENDESK_ACCESS_TOKEN')
ZENDESK_EMAIL_ADDRESS = environ.get('ZENDESK_EMAIL_ADDRESS')
ZENDESK_SUBDOMAIN = environ.get('ZENDESK_SUBDOMAIN')

# Content manager API parameters
ADMIN_ACCESS_TOKEN = environ.get('ADMIN_ACCESS_TOKEN')


LOCATION = 'deis'
ENVIRONMENT = environ.get('ENVIRONMENT')
