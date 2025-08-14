"""
connection to 3m50 thermoststat on local net.
"""

# built-in imports
import datetime
import pprint
import socket
import time
import traceback
import urllib
from typing import Union

# third-party imports
from dns.exception import DNSException

# local imports
from thermostatsupervisor import environment as env
from thermostatsupervisor import mmm_config
from thermostatsupervisor import thermostat_api as api
from thermostatsupervisor import thermostat_common as tc
from thermostatsupervisor import utilities as util

# radiotherm import
MMM_DEBUG = False  # debug uses local radiotherm repo instead of pkg
if MMM_DEBUG and not env.is_azure_environment():
    mod_path = "..//radiotherm"
    if env.is_interactive_environment():
        mod_path = "..\\" + mod_path
    radiotherm = env.dynamic_module_import("radiotherm", mod_path)
else:
    import radiotherm  # noqa E402, from path / site packages

SOCKET_TIMEOUT = 45  # http socket timeout override


class ThermostatClass(tc.ThermostatCommon):
    """3m50 thermostat zone functions."""

    def __init__(self, zone, verbose=True):
        """
        Constructor, connect to thermostat.

        inputs:
            zone(str):  zone of thermostat on local net.
                        mmm_config.metadata dict must have correct local IP
                        address for each zone.
            verbose(bool): debug flag.
        """
        # construct the superclass
        # tc.ThermostatCommonZone.__init__(self)
        # tc.ThermostatCommon.__init__(self)
        super().__init__()

        # set tstat type and debug flag
        self.thermostat_type = mmm_config.ALIAS
        self.verbose = verbose

        # configure zone info
        self.zone_name = int(zone)
        # use hard-coded IP address if provided, otherwise
        # use host dns lookup
        self.host_name = mmm_config.metadata[self.zone_name]["host_name"]
        # populate IP address from metadata dict.
        if "ip_address" in mmm_config.metadata[self.zone_name]:
            self.ip_address = mmm_config.metadata[self.zone_name]["ip_address"]
        else:
            # get IP address from DNS lookup on local net.
            ip_status, self.ip_address = util.is_host_on_local_net(
                self.host_name, verbose=True
            )
            if not ip_status:
                raise DNSException(
                    f"failed to resolve ip address for 3m thermostat "
                    f"'{self.host_name}'"
                )
        self.device_id = self.get_target_zone_id()

    def get_target_zone_id(self) -> object:
        """
        Return the target zone ID from the
        zone number provided.

        inputs:
            None
        returns:
            (obj):  device object.
        """
        # verify thermostat exists on network
        try:
            self.device_id = radiotherm.get_thermostat(self.ip_address)
        except urllib.error.URLError as ex:
            raise RuntimeError(
                f"FATAL ERROR: 3m thermostat not found at ip address: "
                f"{self.ip_address}"
            ) from ex
        return self.device_id

    def print_all_thermostat_metadata(self, zone):
        """
        Return initial meta data queried from thermostat.

        inputs:
            zone(int) zone number
        returns:
            None
        """
        # dump all meta data
        self.get_all_metadata(zone)

        # dump uiData in a readable format
        self.exec_print_all_thermostat_metadata(self.get_latestdata, [zone])

    def get_meta_data_dict(self, zone) -> dict:
        """Build meta data dictionary from list of object attributes.

        inputs:
            zone(int): zone number
        returns:
            (dict) of meta data
        """
        util.log_msg(
            f"querying thermostat zone {zone} for meta data...",
            mode=util.BOTH_LOG,
            func_name=1,
        )
        attr_dict = {}
        ignore_fields = ["get", "post", "reboot", "set_day_program"]
        for attr in dir(self.device_id):
            if attr[0] != "_" and attr not in ignore_fields:
                key = attr
                try:
                    val = self.device_id.__getattribute__(key)
                except TypeError:
                    val = "<attribute is not readable>"
                except AttributeError as ex:
                    val = ex
                except socket.timeout:
                    val = "<socket timeout>"
                attr_dict[key] = val
        return attr_dict

    def get_all_metadata(self, zone, retry=False) -> list:
        """
        Get all the current thermostat metadata.

        inputs:
            zone(int): zone number
            retry(bool): if True will retry with extended retry mechanism.
        returns:
            (list) of thermostat attributes.
        """
        return self.get_metadata(zone, retry=retry)

    def get_metadata(
        self, zone, trait=None, parameter=None, retry=False
    ) -> Union[dict, str]:
        """
        Get the current thermostat metadata settings.

        inputs:
          zone(str or int): zone name
          trait(str): trait or parent key, if None will assume a non-nested dict
          parameter(str): target parameter, None = all settings
          retry(bool): if True will retry with extended retry mechanism
        returns:
          (dict) if parameter=None
          (str) if parameter != None
        """
        del trait  # not used on mmm

        def _get_metadata_internal():
            if parameter is None:
                return self.get_meta_data_dict(zone)
            else:
                return self.get_meta_data_dict(zone)[parameter]["raw"]

        if retry:
            # Use standardized extended retry mechanism
            return util.execute_with_extended_retries(
                func=_get_metadata_internal,
                thermostat_type=self.thermostat_type,
                zone_name=str(zone),
                number_of_retries=5,
                initial_retry_delay_sec=30,
                exception_types=(
                    urllib.error.URLError,
                    socket.timeout,
                    socket.error,
                    ConnectionError,
                    TimeoutError,
                    DNSException,
                    AttributeError,
                    KeyError,
                    TypeError,
                ),
                email_notification=None,  # MMM doesn't import email_notification
            )
        else:
            # Single attempt without retry
            return _get_metadata_internal()

    def get_latestdata(self, zone, debug=False) -> Union[dict, str]:
        """
        Get the current thermostat latest data.

        inputs:
          zone(int): target zone
          debug(bool): debug flag
        returns:
          (dict) if parameter=None
          (str) if parameter != None
        """
        latest_data_dict = self.get_meta_data_dict(zone)
        if debug:
            util.log_msg(
                f"zone{zone} latestData: {latest_data_dict}",
                mode=util.BOTH_LOG,
                func_name=1,
            )
        return latest_data_dict

    def get_ui_data(self, zone) -> dict:
        """
        Get the latest thermostat ui data

        inputs:
          zone(int): target zone.
        returns:
          (dict)
        """
        return self.get_meta_data_dict(zone)

    def get_ui_data_param(self, zone, parameter) -> dict:
        """
        Get the latest thermostat ui data for one specific parameter.

        inputs:
          zone(int): target zone
          parameter(str): UI parameter
        returns:
          (various) value or data structure of interest
        """
        return self.get_meta_data_dict(zone)[parameter]["raw"]


class ThermostatZone(tc.ThermostatCommonZone):
    """3m50 thermostat zone functions."""

    def __init__(self, Thermostat_obj, verbose=True):
        """
        Constructor, connect to thermostat.

        mmm_metadata dict above must have correct local IP address for each
            zone.

        inputs:
            Thermostat_obj(obj):  Thermostat class instance.
            verbose(bool): debug flag.
        """
        # construct the superclass
        super().__init__()

        # switch config for this thermostat
        self.system_switch_position[tc.ThermostatCommonZone.COOL_MODE] = 2
        self.system_switch_position[tc.ThermostatCommonZone.HEAT_MODE] = 1
        self.system_switch_position[tc.ThermostatCommonZone.OFF_MODE] = 0
        self.system_switch_position[tc.ThermostatCommonZone.AUTO_MODE] = 3

        # need verification
        self.system_switch_position[tc.ThermostatCommonZone.DRY_MODE] = util.BOGUS_INT
        self.system_switch_position[tc.ThermostatCommonZone.FAN_MODE] = util.BOGUS_INT

        # zone info
        self.verbose = verbose
        self.thermostat_type = mmm_config.ALIAS
        self.device_id = Thermostat_obj.device_id
        self.zone_name = Thermostat_obj.zone_name
        self.zone_name = self.get_zone_name()

        # runtime parameter defaults
        self.poll_time_sec = 10 * 60  # default to 10 minutes
        self.connection_time_sec = 8 * 60 * 60  # default to 8 hours

    def get_zone_name(self, zone=None):
        """
        Return the name associated with the zone number.

        inputs:
            zone(int): Zone number
        returns:
            (str) zone name
        """
        if zone is None:
            # pull from thermostat
            return self.device_id.name["raw"]
        else:
            # override from config file
            return mmm_config.metadata[zone]["zone_name"]

    def get_display_temp(self) -> float:
        """
        Return DispTemperature.

        inputs:
            None
        returns:
            (float): display temp in °F.
        """
        return float(self.device_id.temp["raw"])

    def get_display_humidity(self) -> Union[float, None]:
        """
        Return Humidity.

        inputs:
            None
        returns:
            (float, None): humidity in %RH, return None if not supported.
        """
        return None  # not available

    def get_is_humidity_supported(self) -> bool:
        """
        Return humidity sensor status.

        inputs:
            None
        returns:
            (bool): True if humidity is supported.
        """
        return self.get_display_humidity() is not None

    def is_heat_mode(self) -> int:
        """
        Return the heat mode.

        inputs:
            None
        returns:
            (int): heat mode.
        """
        return int(self._get_tmode() == self.system_switch_position[self.HEAT_MODE])

    def is_cool_mode(self) -> int:
        """
        Return the cool mode.

        inputs:
            None
        returns:
            (int): 1=cool mode enabled, 0=disabled.
        """
        return int(self._get_tmode() == self.system_switch_position[self.COOL_MODE])

    def is_dry_mode(self) -> int:
        """
        Return the dry mode.

        inputs:
            None
        returns:
            (int): 1=dry mode enabled, 0=disabled.
        """
        return int(self._get_tmode() == self.system_switch_position[self.DRY_MODE])

    def is_auto_mode(self) -> int:
        """
        Return the auto mode.

        inputs:
            None
        returns:
            (int): 1=auto mode enabled, 0=disabled.
        """
        return int(self._get_tmode() == self.system_switch_position[self.AUTO_MODE])

    def is_eco_mode(self) -> int:
        """
        Return the eco mode.

        inputs:
            None
        returns:
            (int): 1=eco mode enabled, 0=disabled.
        """
        return int(self._get_tmode() == self.system_switch_position[self.ECO_MODE])

    def _get_tmode(self, retries=1):
        """
        Get tmode from device, retry on Attribute error.
        """

        def _get_tmode_internal():
            return self.device_id.tmode["raw"]

        # Use standardized extended retry for more robust error handling
        try:
            return util.execute_with_extended_retries(
                func=_get_tmode_internal,
                thermostat_type=self.thermostat_type,
                zone_name=str(self.zone_name),
                number_of_retries=5,
                initial_retry_delay_sec=60,
                exception_types=(AttributeError, ConnectionError, TimeoutError),
                email_notification=None,  # MMM doesn't import email_notification
            )
        except Exception:
            # Fallback to original simple retry for backward compatibility
            try:
                tmode = self.device_id.tmode["raw"]
            except AttributeError as ex:
                if retries > 0:
                    print(traceback.format_exc())
                    print(
                        "WARNING: AttributeError while querying tstat.tmode, "
                        "retrying after brief delay..."
                    )
                    time.sleep(10)
                    tmode = self._get_tmode(retries - 1)
                else:
                    raise ex
            return tmode

    def is_fan_mode(self) -> int:
        """
        Return the fan mode.

        Fan mode is fan on for circulation but not applying heat or cooling.
        inputs:
            None
        returns:
            (int): 1=fan mode enabled, 0=disabled.
        """
        return int(self.device_id.fmode["raw"] == 2 and self.is_off_mode())

    def is_off_mode(self) -> int:
        """
        Return the off mode.

        inputs:
            None
        returns:
            (int): off mode, 1=enabled, 0=disabled.
        """
        return int(
            self._get_tmode() == self.system_switch_position[self.OFF_MODE]
            and self.device_id.fmode["raw"] != 2
        )

    def is_heating(self):
        """Return 1 if heating relay is active, else 0."""
        return int(
            self.is_heat_mode()
            and self.is_power_on()
            and self.get_heat_setpoint_raw() > self.get_display_temp()
        )

    def is_cooling(self):
        """Return 1 if cooling relay is active, else 0."""
        return int(
            self.is_cool_mode()
            and self.is_power_on()
            and self.get_cool_setpoint_raw() < self.get_display_temp()
        )

    def is_drying(self):
        """Return 1 if drying relay is active, else 0."""
        return 0  # not applicable

    def is_auto(self):
        """Return 1 if auto relay is active, else 0."""
        return 0  # not applicable

    def is_eco(self):
        """Return 1 if eco relay is active, else 0."""
        return 0  # not applicable

    def is_fanning(self) -> int:
        """Return 1 if fan relay is active, else 0."""
        return int(self.is_fan_on() and self.is_power_on())

    def is_power_on(self) -> int:
        """Return 1 if power relay is active, else 0."""
        return int(self.device_id.power["raw"] > 0)

    def is_fan_on(self) -> int:
        """Return 1 if fan relay is active, else 0."""
        return int(self.device_id.fstate["raw"])

    def is_defrosting(self) -> int:
        """Return 1 if defrosting is active, else 0."""
        return 0  # not applicable

    def is_standby(self) -> int:
        """Return 1 if standby is active, else 0."""
        return 0  # not applicable

    def get_setpoint_list(self, sp_dict, day) -> list:
        """
        Return list of 4 setpoints for the day.

        inputs:
            sp_dict(dict): setpoint dictionary
            day(int): day of the week, 0=Monday
        returns:
            list of 8 elements, representing 4 pairs of elapsed minutes
            and setpoint
        """
        sp_lst = sp_dict["raw"][str(day)]
        if len(sp_lst) != 8:
            raise ValueError(f"setpoint list is not 8 elements long: {sp_lst}")
        return sp_dict["raw"][str(day)]

    def get_previous_days_setpoint(self, sp_dict) -> int:
        """
        Return last setpoint from day before today.

        inputs:
            sp_dict(dict): setpoint dictionary
        returns:
            (int)last temperature set the day before.
        """
        today = datetime.datetime.today().weekday()
        if today == 0:
            yesterday = 6
        else:
            yesterday = today - 1
        return self.get_setpoint_list(sp_dict, yesterday)[-1]

    def get_schedule_setpoint(self, sp_dict) -> float:
        """
        Return current setpoint.

        inputs:
            sp_dict(dict): setpoint dictionary
        returns:
            (float) last temperature set the day before.
        """
        current_sp = self.get_previous_days_setpoint(sp_dict)
        now = datetime.datetime.now()
        minutes_since_midnight = (
            now - now.replace(hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds() / 60
        todays_setpoint_lst = self.get_setpoint_list(
            sp_dict, datetime.datetime.today().weekday()
        )
        for idx in [0, 2, 4, 6]:
            if todays_setpoint_lst[idx] > minutes_since_midnight:
                return current_sp
            else:
                # store setpoint corresponding to this time
                current_sp = todays_setpoint_lst[idx + 1]
        return float(current_sp)

    def get_heat_setpoint(self) -> str:
        """
        Return the current heat setpoint.

        t_heat field is only present if in heat mode.
        """
        return util.temp_value_with_units(self.get_heat_setpoint_raw())

    def get_heat_setpoint_raw(self) -> float:
        """
        Return the current raw heat setpoint.

        t_heat field is only present if in heat mode.
        inputs:
            None
        returns:
            (float): current raw heat set point in °F.
        """
        result = self.get_heat_setpoint()
        if not isinstance(result, float):
            raise TypeError(
                f"heat set point raw is type {type(result)}, should be float"
            )
        return result

    def get_cool_setpoint(self) -> str:
        """
        Return the current cool setpoint.
        """
        return util.temp_value_with_units(self.get_cool_setpoint_raw())

    def get_cool_setpoint_raw(self) -> float:
        """
        Return the current raw cool setpoint.

        t_cool field is only present if in cool mode.
        inputs:
            None
        returns:
            (float): current raw cool set point in °F.
        """
        result = float(self.get_cool_setpoint())
        return result

    def get_schedule_program_heat(self) -> dict:
        """
        Return the scheduled heat program, times and settings.

        inputs:
            None
        returns:
            (dict): scheduled heat set points and times in °F.
        """
        result = self.device_id.program_heat["raw"]
        if not isinstance(result, dict):
            raise TypeError(
                f"heat program schedule set point is type {type(result)},"
                f" should be dict"
            )
        return result

    def get_schedule_heat_sp(self) -> float:
        """
        Return the scheduled heat setpoint.

        inputs:
            None
        returns:
            (float): current scheduled heat set point in °F.
        """
        result = float(self.get_schedule_setpoint(self.device_id.program_heat))
        return result

    def get_schedule_program_cool(self) -> dict:
        """
        Return the sechduled cool setpoint.

        inputs:
            None
        returns:
            (dict): current scheduled cool set point in °F.
        """
        result = self.device_id.program_cool["raw"]
        if not isinstance(result, dict):
            raise TypeError(
                f"schedule program cool set point is type {type(result)},"
                f" should be dict"
            )
        return result

    def get_schedule_cool_sp(self) -> float:
        """
        Return the sechduled cool setpoint.

        inputs:
            None
        returns:
            (float): current schedule cool set point in °F.
        """
        result = float(self.get_schedule_setpoint(self.device_id.program_cool))
        return result

    def get_is_invacation_hold_mode(self) -> bool:
        """
        Return the in vacation hold status.

        inputs:
            None
        returns:
            (int): 0=Disabled, 1=Enabled
        """
        result = bool(self.device_id.hold["raw"])
        return result

    def get_vacation_hold(self) -> bool:
        """
        Return the Hold setting.

        inputs:
            None
        returns:
            (int): 0=Disabled, 1=Enabled
        """
        result = bool(self.device_id.override["raw"])
        return result

    def get_vacation_hold_until_time(self) -> int:
        """
        Return the 'VacationHoldUntilTime'.

        inputs:
            None
        returns:
            (int): vacation hold time in minutes.
        """
        return -1  # not implemented

    def get_temporary_hold_until_time(self) -> int:
        """
        Return the 'TemporaryHoldUntilTime'.

        inputs:
            None
        returns:
            (int): temporary hold time in minutes.
        """
        if self.is_heat_mode() == 1:
            sp_dict = self.device_id.program_heat
        elif self.is_cool_mode() == 1:
            sp_dict = self.device_id.program_cool
        else:
            # off mode, use dummy dict.
            sp_dict = {
                "raw": {
                    "0": [0] * 8,
                    "1": [0] * 8,
                    "2": [0] * 8,
                    "3": [0] * 8,
                    "4": [0] * 8,
                    "5": [0] * 8,
                    "6": [0] * 8,
                }
            }
            # raise ValueError("unknown heat/cool mode")
        now = datetime.datetime.now()
        minutes_since_midnight = (
            now - now.replace(hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds() / 60
        todays_setpoint_lst = self.get_setpoint_list(
            sp_dict, datetime.datetime.today().weekday()
        )
        for idx in [0, 2, 4, 6]:
            if todays_setpoint_lst[idx] > minutes_since_midnight:
                time_delta = todays_setpoint_lst[idx] - minutes_since_midnight
                break  # found next timer
            else:
                time_delta = 24 * 60 - minutes_since_midnight

        return int(time_delta)

    def get_setpoint_change_allowed(self) -> bool:
        """
        Return the 'SetpointChangeAllowed' setting.

        inputs:
            None
        returns:
            (bool): 'SetpointChangeAllowed' will be True in heating mode,
            False in OFF mode (assume True in cooling mode too)
        """
        return False  # not implemented

    def get_system_switch_position(self) -> int:
        """Return the thermostat mode.

        inputs:
            None
        returns:
            (int): thermostat mode, refer to tc.system_swtich position
            for details.
        """
        result = self._get_tmode()
        if not isinstance(result, int):
            raise TypeError(
                f"get_system_switch_position is type {type(result)}, should be int"
            )
        return result

    def set_heat_setpoint(self, temp: int) -> None:
        """
        Set a new heat setpoint.

        This will also attempt to turn the thermostat to 'Heat'
        inputs:
            temp(int): desired temperature in °F.
        returns:
            None
        """
        self.device_id.t_heat = temp

    def set_cool_setpoint(self, temp: int) -> None:
        """
        Set a new cool setpoint.

        This will also attempt to turn the thermostat to 'Cool'
        inputs:
            temp(int): desired temperature in °F.
        returns:
            None
        """
        self.device_id.t_cool = temp


# monkeypatch radiotherm.thermostat.Thermostat __init__ method with longer
# socket.timeout delay, based on radiotherm version 2.1
def __init__(self, host, timeout=SOCKET_TIMEOUT):  # changed from 4 (default)
    self.host = host
    self.timeout = timeout


radiotherm.thermostat.Thermostat.__init__ = __init__
# end of monkeypatch radiotherm.thermostat.Thermostst __init__

if __name__ == "__main__":
    # verify environment
    env.get_python_version()
    env.show_package_version(radiotherm)

    # get zone override
    api.uip = api.UserInputs(argv_list=None, thermostat_type=mmm_config.ALIAS)
    zone_number = api.uip.get_user_inputs(api.uip.zone_name, api.input_flds.zone)

    _, Zone = tc.thermostat_basic_checkout(
        mmm_config.ALIAS, zone_number, ThermostatClass, ThermostatZone
    )

    tc.print_select_data_from_all_zones(
        mmm_config.ALIAS,
        mmm_config.get_available_zones(),
        ThermostatClass,
        ThermostatZone,
        display_wifi=False,
        display_battery=False,
    )

    # measure thermostat response time
    if mmm_config.check_response_time:
        MEASUREMENTS = 60  # running higher than normal count here because
        # intermittent failures have been observed.
        meas_data = Zone.measure_thermostat_repeatability(
            MEASUREMENTS,
            measure_response_time=True,
        )
        ppp = pprint.PrettyPrinter(indent=4)
        ppp.pprint(meas_data)
