from configparser import RawConfigParser
import os
import sys

config = RawConfigParser()

def expand_path(path):
    # Expands environment variables like %LOCALAPPDATA% or ~
    return os.path.expandvars(os.path.expanduser(path))

def get_user_config_path():
    return os.path.join(os.getcwd(), 'config.ini')

def get_bundled_config_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'config.ini')
    return os.path.join(os.path.dirname(__file__), 'config.ini')

# Load config file
user_config = get_user_config_path()
if os.path.exists(user_config):
    config.read(user_config)
else:
    config.read(get_bundled_config_path())

# Extract settings with path expansion
PRINTER_NAME = config.get("Printer", "name")
PRINTER_DRIVER = config.get("Printer", "driver")
LABEL_DIRECTORY = expand_path(config.get("LabelLibrary", "path"))
SUMATRA_PATH = expand_path(config.get("SumatraPDF", "path"))
DEFAULT_COPIES = config.getint("PrintSettings", "default_copies")
PAPER_WIDTH_IN = config.getfloat("PrintSettings", "paper_width_in")
PAPER_HEIGHT_IN = config.getfloat("PrintSettings", "paper_height_in")