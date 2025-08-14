import leds
import pytest
import wpilib



# Create Mock DriverStation
class Mock_Alliance():
    kBlue = 1
    kRed = 0
class Mock_DS():
    def __init__(self):
        self.Alliance = Mock_Alliance()
        self.alliance_color = self.Alliance.kBlue
    def getAlliance(self):
        return self.alliance_color
@pytest.fixture()
def mock_ds_blue(monkeypatch):

    def mock_alliance():
        return Mock_DS().Alliance.kBlue
    
    monkeypatch.setattr(wpilib.DriverStation, "getAlliance",mock_alliance)
@pytest.fixture()
def mock_ds_red(monkeypatch):

    def mock_alliance():
        return Mock_DS().Alliance.kRed
    
    monkeypatch.setattr(wpilib.DriverStation, "getAlliance",mock_alliance)


# Create test object
led_strip = leds.Strip([], 'test')

# First test: valid values
def default_colors(mock_ds):
    
    assert led_strip.getDefaultHue() in [243, 360] # Blue or Red
    assert led_strip.getDefaultRgb() in [
        [0, 0, 255], 
        [255, 0, 0]
    ] # Full Blue or Full Red

def test_default_blue(mock_ds_blue):
    return default_colors(mock_ds_blue)
def test_default_red(mock_ds_red):
    return default_colors(mock_ds_red)
def test_blue_is_default(mock_ds_blue):
    assert led_strip.getDefaultHue() == 243
    assert led_strip.getDefaultRgb() == [0, 0, 255]
def test_red_is_default(mock_ds_red):
    assert led_strip.getDefaultHue() == 360
    assert led_strip.getDefaultRgb() == [255, 0, 0]