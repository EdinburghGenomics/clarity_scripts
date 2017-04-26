import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("clarity_scripts").version
except pkg_resources.DistributionNotFound:
    __version__ = ""
