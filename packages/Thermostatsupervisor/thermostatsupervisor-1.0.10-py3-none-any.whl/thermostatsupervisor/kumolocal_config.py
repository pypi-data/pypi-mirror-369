"""
kumolocal config file.
"""

ALIAS = "kumolocal"

# thermostat zones
MAIN_LEVEL = 0  # zone 0
BASEMENT = 1  # zone 1

# constants
MAX_HEAT_SETPOINT = 68
MIN_COOL_SETPOINT = 70

# all environment variables specific to this thermostat type
env_variables = {
    "KUMO_USERNAME": None,
    "KUMO_PASSWORD": None,
}

# supported thermostat configs
supported_configs = {
    "module": "kumolocal",
    "type": 5,
    "zones": [MAIN_LEVEL, BASEMENT],
    "modes": [
        "OFF_MODE",
        "HEAT_MODE",
        "COOL_MODE",
        "DRY_MODE",
        "AUTO_MODE",
        "UNKNOWN_MODE",
    ],
    "zip_code": "55760",  # Zip code for outdoor weather data
}

# metadata dict
# 'zone_name' is a placeholder, used at Thermostat class level.
# 'zone_name' is updated by device memory via Zone.get_zone_name()
# 'host_name' is used for DNS lookup to determine if device
# 'ip_address' is just for reference.
# 'local_net_available' is set by local network detection
metadata = {
    MAIN_LEVEL: {
        "ip_address": "192.168.86.229",  # local IP, for ref only.
        "zone_name": "Main Level",  # customize for your site.
        "host_name": "tbd",  # used for DNS lookup
        "local_net_available": None,  # updated by local network detection
    },
    BASEMENT: {
        "ip_address": "192.168.86.236",  # local IP, for ref only.
        "zone_name": "Basement",  # customize for your site.
        "host_name": "tbd",  # used for DNS lookup
        "local_net_available": None,  # updated by local network detection
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

# flag to check thermostat response time during basic checkout
check_response_time = False
