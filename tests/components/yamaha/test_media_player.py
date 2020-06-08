"""The tests for the Yamaha Media player platform."""
import pytest

import homeassistant.components.media_player as mp
from homeassistant.components.yamaha import media_player as yamaha
from homeassistant.components.yamaha.const import DOMAIN
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.setup import async_setup_component

from tests.async_mock import MagicMock, PropertyMock, call, patch

CONFIG = {"media_player": {"platform": "yamaha", "host": "127.0.0.1"}}


def _create_zone_mock(name, url):
    zone = MagicMock()
    zone.ctrl_url = url
    zone.zone = name
    return zone


class FakeYamahaDevice:
    """A fake Yamaha device."""

    def __init__(self, ctrl_url, name, zones=None):
        """Initialize the fake Yamaha device."""
        self.ctrl_url = ctrl_url
        self.name = name
        self._zones = zones or []

    def zone_controllers(self):
        """Return controllers for all available zones."""
        return self._zones


@pytest.fixture(name="main_zone")
def main_zone_fixture():
    """Mock the main zone."""
    return _create_zone_mock("Main zone", "http://main")


@pytest.fixture(name="device")
def device_fixture(main_zone):
    """Mock the yamaha device."""
    device = FakeYamahaDevice("http://receiver", "Receiver", zones=[main_zone])
    with patch("rxv.RXV", return_value=device):
        yield device


async def test_setup_host(hass, device, main_zone):
    """Test set up integration with host."""
    assert await async_setup_component(hass, mp.DOMAIN, CONFIG)
    await hass.async_block_till_done()

    state = hass.states.get("media_player.yamaha_receiver_main_zone")

    assert state is not None
    assert state.state == "off"


async def test_setup_no_host(hass, device, main_zone):
    """Test set up integration without host."""
    with patch("rxv.find", return_value=[device]):
        assert await async_setup_component(
            hass, mp.DOMAIN, {"media_player": {"platform": "yamaha"}}
        )
        self.addCleanup(self.hass.stop)

    assert scene_prop.call_count == 1
    assert scene_prop.call_args == call(scene)

    scene = "BD/DVD Movie Viewing"
    data["scene"] = scene

    await hass.services.async_call(DOMAIN, yamaha.SERVICE_SELECT_SCENE, data, True)

    assert scene_prop.call_count == 2
    assert scene_prop.call_args == call(scene)

    scene_prop.side_effect = AssertionError()

    missing_scene = "Missing scene"
    data["scene"] = missing_scene

    await hass.services.async_call(DOMAIN, yamaha.SERVICE_SELECT_SCENE, data, True)

    assert f"Scene '{missing_scene}' does not exist!" in caplog.text
