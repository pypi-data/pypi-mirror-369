"""
nest config file.
"""

ALIAS = "nest"

# thermostat zones
MAIN_LEVEL = 0  # zone 0
BASEMENT = 1  # zone 1

# constants
MAX_HEAT_SETPOINT = 69.0
MIN_COOL_SETPOINT = 70.0

# Safety temperature settings
# These are used when thermostat is OFF and normal setpoints are unavailable
# Users can adjust these values based on their comfort and safety requirements
SAFETY_HEAT_TEMPERATURE = 45.0  # Minimum safe temperature (°F)
SAFETY_COOL_TEMPERATURE = 75.0  # Maximum safe temperature (°F)

# all environment variables specific to this thermostat type
env_variables = {
    "GCLOUD_CLIENT_ID": None,
    "GCLOUD_CLIENT_SECRET": None,
    "DAC_PROJECT_ID": None,
    "NEST_ACCESS_TOKEN": None,
    "NEST_REFRESH_TOKEN": None,
    "NEST_TOKEN_EXPIRES_IN": None,
}

# min required env variables on all runs
required_env_variables = {}

# supported thermostat configs
supported_configs = {
    "module": "nest",
    "type": 7,
    "zones": [MAIN_LEVEL, BASEMENT],
    "modes": [
        "OFF_MODE",
        "HEAT_MODE",
        "COOL_MODE",
        "DRY_MODE",
        "AUTO_MODE",
        "UNKNOWN_MODE",
        "MANUAL_ECO",
    ],
    "zip_code": "55760",  # Zip code for outdoor weather data
}

# metadata dict
# 'zone_name' is a placeholder, used at Thermostat class level.
# 'zone_name' is updated by device memory via Zone.get_zone_name()
# 'host_name' is used for DNS lookup to determine if device
# 'ip_address' is just for reference.
metadata = {
    MAIN_LEVEL: {
        "ip_address": "192.168.86.229",  # local IP, for ref only.
        "zone_name": "Main Level Thermostat",  # customize your site.
        "host_name": "tbd",  # used for DNS lookup
    },
    BASEMENT: {
        "ip_address": "192.168.86.236",  # local IP, for ref only.
        "zone_name": "Basement Thermostat",  # customize for your site.
        "host_name": "tbd",  # used for DNS lookup
    },
}


def get_available_zones():
    """
    Return list of available zones.

    for this thermostat type, available zones is all zones.

    inputs:
        None.
    returns:
        (list) available zones.
    """
    return supported_configs["zones"]


default_zone = supported_configs["zones"][0]
default_zone_name = metadata[default_zone]["zone_name"]

argv = [
    "supervise.py",  # module
    ALIAS,  # thermostat
    str(default_zone),  # zone
    "16",  # poll time in sec
    "356",  # reconnect time in sec
    "4",  # tolerance
    "OFF_MODE",  # thermostat mode
    "2",  # number of measurements
]

# force use of credentials.json file for credentials
use_credentials_file = False
credentials_file_location = ".//credentials.json"

# data caching parameters
# 20 sec. cache period needed to avoid spamming nest server.
cache_period_sec = 20.0  # cache period for data, min 5 sec.
cache_file_location = ".//token_cache.json"  # oauth credentials

# flag to check thermostat response time during basic checkout
check_response_time = False
