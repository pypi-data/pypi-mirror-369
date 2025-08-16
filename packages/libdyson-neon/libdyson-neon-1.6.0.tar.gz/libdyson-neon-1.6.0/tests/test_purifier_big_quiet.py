"""Tests for Big+Quiet."""

import pytest

from libdyson import DEVICE_TYPE_PURE_COOL
from libdyson.const import ENVIRONMENTAL_FAIL, ENVIRONMENTAL_INIT, ENVIRONMENTAL_OFF
from libdyson.dyson_purifier_big_quiet import DysonBigQuiet

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT
from .test_fan_device import assert_command

DEVICE_TYPE = DEVICE_TYPE_PURE_COOL

STATUS = {
    "mode-reason": "RAPP",
    "state-reason": "MODE",
    "dial": "OFF",
    "rssi": "-46",
    "channel": "1",
    "product-state": {
        "fpwr": "OFF",
        "fdir": "OFF",
        "auto": "OFF",
        "oscs": "OFF",
        "nmod": "OFF",
        "rhtm": "OFF",
        "fnst": "OFF",
        "ercd": "NONE",
        "wacd": "NONE",
        "nmdv": "0004",
        "fnsp": "AUTO",
        "bril": "0002",
        "corf": "ON",
        "cflr": "0100",
        "hflr": "0100",
        "sltm": "OFF",
        "otal": "0025",
        "otau": "0025",
        "anct": "CUST",
        "ancp": "CUST",
    },
    "scheduler": {"srsc": "000000005b1792f0", "dstv": "0001", "tzid": "0001"},
}

ENVIRONMENTAL_DATA = {
    "data": {
        "tact": "OFF",
        "hact": "OFF",
        "pm25": "OFF",
        "pm10": "OFF",
        "va10": "INIT",
        "noxl": "FAIL",
        "p25r": "OFF",
        "p10r": "OFF",
        "sltm": "OFF",
    }
}


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of Pure Cool Link."""
    device = DysonBigQuiet(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)

    # Status
    assert device.is_on is False
    assert device.auto_mode is False
    assert device.front_airflow is False
    assert device.night_mode_speed == 4
    assert device.carbon_filter_life == 100
    assert device.hepa_filter_life == 100

    # Environmental
    assert device.particulate_matter_2_5 == ENVIRONMENTAL_OFF
    assert device.particulate_matter_10 == ENVIRONMENTAL_OFF
    assert device.volatile_organic_compounds == ENVIRONMENTAL_INIT
    assert device.nitrogen_dioxide == ENVIRONMENTAL_FAIL

    new_status = {
        "mode-reason": "LAPP",
        "state-reason": "MODE",
        "product-state": {
            "fpwr": ["OFF", "ON"],
            "fdir": ["OFF", "ON"],
            "auto": ["OFF", "ON"],
            "oscs": ["OFF", "ON"],
            "nmod": ["OFF", "ON"],
            "rhtm": ["OFF", "ON"],
            "fnst": ["OFF", "ON"],
            "ercd": ["NONE", "NONE"],
            "wacd": ["NONE", "NONE"],
            "nmdv": ["0004", "0010"],
            "fnsp": ["AUTO", "AUTO"],
            "bril": ["0002", "0002"],
            "corf": ["ON", "ON"],
            "cflr": ["0100", "INV"],
            "hflr": ["0100", "80"],
            "sltm": ["OFF", "OFF"],
            "otal": ["0025", "0050"],
            "otau": ["0025", "0050"],
            "anct": ["CUST", "CUST"],
            "ancp": ["CUST", "CUST"],
        },
        "scheduler": {"srsc": "000000005b1792f0", "dstv": "0001", "tzid": "0001"},
    }
    mqtt_client.state_change(new_status)
    assert device.is_on is True
    assert device.auto_mode is True
    assert device.front_airflow is True
    assert device.night_mode_speed == 10
    assert device.carbon_filter_life is None
    assert device.hepa_filter_life == 80
    assert device.tilt == 50

    mqtt_client._environmental_data = {
        "data": {
            "tact": "2977",
            "hact": "0058",
            "pm25": "0009",
            "pm10": "0005",
            "va10": "0004",
            "noxl": "0011",
            "p25r": "0009",
            "p10r": "0005",
            "co2r": "0400",
            "otal": "0050",
            "otau": "0050",
            "sltm": "OFF",
        }
    }
    device.request_environmental_data()
    assert device.particulate_matter_2_5 == 9
    assert device.particulate_matter_10 == 5
    assert device.volatile_organic_compounds == 0.4
    assert device.nitrogen_dioxide == 1.1
    assert device.carbon_dioxide == 400


@pytest.mark.parametrize(
    "command,command_args,msg_data",
    [
        ("turn_on", [], {"fpwr": "ON"}),
        ("turn_off", [], {"fpwr": "OFF"}),
        ("set_speed", [3], {"fpwr": "ON", "fnsp": "0003"}),
        ("enable_auto_mode", [], {"auto": "ON"}),
        ("disable_auto_mode", [], {"auto": "OFF"}),
        ("enable_continuous_monitoring", [], {"fpwr": "OFF", "rhtm": "ON"}),
        ("disable_continuous_monitoring", [], {"fpwr": "OFF", "rhtm": "OFF"}),
        ("enable_front_airflow", [], {"fdir": "ON"}),
        ("disable_front_airflow", [], {"fdir": "OFF"}),
        ("set_tilt", [25], {"otal": "0025", "otau": "0025", "anct": "CUST"}),
        ("set_tilt", [359], {"otal": "0359", "otau": "0359", "anct": "BRZE"}),
    ],
)
def test_command(
    mqtt_client: MockedMQTT,
    command: str,
    command_args: list,
    msg_data: dict,
):
    """Test commands of Pure Cool Link."""
    assert_command(
        DysonBigQuiet(SERIAL, CREDENTIAL, DEVICE_TYPE),
        mqtt_client,
        command,
        command_args,
        msg_data,
    )
