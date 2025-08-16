# import os

# # Get version from VERSION file in the root directory
# _version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "VERSION")
# with open(_version_file, 'r') as f:
#     __version__ = f.read().strip()

from .bota_driver_ext import __doc__, DriverState, BotaDriver

