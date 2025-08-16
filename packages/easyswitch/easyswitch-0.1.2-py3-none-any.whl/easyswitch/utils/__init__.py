from datetime import datetime, timezone
import platform
from types import ModuleType
import urllib.parse
from importlib import metadata
from typing import Union
from pathlib import Path
from importlib import import_module
from phonenumbers.phonenumberutil import country_code_for_region, region_code_for_country_code

try:
    __version__ = metadata.version('easyswitch')
except metadata.PackageNotFoundError:
    __version__ = '0.0.0'
    


USER_AGENT = (
    f'EasySwitch-python/{__version__} ({platform.machine()}'
    f'{platform.system().lower()}) Python/{platform.python_version()}'
    )


####    PARSE PHONE NUMBER
def parse_phone(number:str, raise_exception = False):
    ''' Return A dict of country code, national number and country alpha2 '''
    
    import phonenumbers

    try:
        parsed_number = phonenumbers.parse(number,None)
        return {
            'country_code': parsed_number.country_code,
            'national_number': parsed_number.national_number,
            'country_alpha2': region_code_for_country_code(parsed_number.country_code)
        }
    except phonenumbers.NumberParseException:
        # Raise an exception if needed
        if raise_exception:
            raise phonenumbers.NumberParseException(
                msg='Invalid phone number'
            )
        return {
            'country_code': None,
            'national_number': None,
            'country_alpha2': None
        }


# DICT TO QUERY STRING
def dict_to_encoded_query_string(data: dict) -> str:
    """Converts a dictt object into a url safe encoded string"""
    query_string = urllib.parse.urlencode(data)
    return urllib.parse.quote(query_string)

# QUERY STRING TO DICT
def encoded_query_string_to_dict(encoded: str) -> dict:
    """Converts a url safe query str into a dict."""
    decoded = urllib.parse.unquote(encoded)
    return dict(urllib.parse.parse_qsl(decoded))

# IMPORT MODULE
def import_module_from(path: Union[str,Path]) ->'ModuleType':
    """Import module using importlib"""
    return import_module(path)