"""
Tax Tea
"""
import pkg_resources

__version__ = pkg_resources.require("django-taxtea")[0].version

default_app_config = "taxtea.apps.TaxTeaConfig"
