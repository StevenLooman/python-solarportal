# -*- coding: utf-8 -*-
"""Solarportal API for python."""

import hashlib
import logging
from datetime import datetime
from typing import Dict
from typing import List
from typing import Mapping
from urllib.parse import quote as urlquote
from xml.etree import ElementTree as ET

import aiohttp


_LOGGER = logging.getLogger(__name__)


class SolarPortalError(Exception):
    """SolarPortalException."""


class Token:
    """Token for portal."""

    def __init__(self, data: Mapping):
        """Initializer."""
        self._data = data
        self.created = datetime.now()

    @property
    def user_id(self):
        return self._data['userID']

    @property
    def username(self):
        return self._data['userName']

    @property
    def token(self):
        return self._data['token']

    def __repr__(self):
        return '<Token({}, {})>'.format(self.username, self.token)


class Inverter:
    """Inverter from the portal."""

    def __init__(self, data: Mapping):
        """Initializer."""
        self._data = data

    @property
    def sn(self):
        return self._data['sn']

    @property
    def status(self):
        return self._data['status']

    @property
    def power(self):
        return float(self._data['power'])

    @property
    def etoday(self):
        return float(self._data['etoday'])

    @property
    def energy_today(self):
        return self.etoday

    @property
    def etotal(self):
        return int(self._data['etotal'])

    @property
    def energy_total(self):
        return self.etotal

    @property
    def lastupdated(self):
        ts = int(self._data['lastupdated'])
        return datetime.fromtimestamp(ts)

    @property
    def mode(self):
        return self._data['mode']


class WiFi:
    """WiFi from the portal."""

    def __init__(self, data: Mapping):
        """Initializer."""
        self._data = data

    @property
    def id(self):
        return self._data['id']

    @property
    def inverter(self):
        if isinstance(self._data['inverter'], dict):
            return Inverter(self._data['inverter'])

        return self._data['inverter']


class Data:
    """Data from the portal."""

    def __init__(self, data: Mapping):
        """Initializer."""
        self._data = data

    @property
    def pic(self):
        return self._data['pic']

    @property
    def name(self):
        return self._data['name']

    @property
    def country(self):
        return self._data['country']

    @property
    def province(self):
        return self._data['province']

    @property
    def city(self):
        return self._data['city']

    @property
    def street(self):
        return self._data['street']

    @property
    def sunrise(self):
        return self._data['sunrise']

    @property
    def sunset(self):
        return self._data['sunset']

    @property
    def today_income(self):
        return float(self._data['income']['TodayIncome'])

    @property
    def actual_power(self):
        return float(self._data['income']['ActualPower'])

    @property
    def etoday(self):
        return float(self._data['income']['etoday'])

    @property
    def energy_today(self):
        return self.etoday

    @property
    def etotal(self):
        return int(self._data['income']['etotal'])

    @property
    def energy_total(self):
        return self.energy_total

    @property
    def total_income(self):
        return float(self._data['income']['TotalIncome'])

    @property
    def capacity(self):
        return float(self._data['detail']['Capacity'])

    @property
    def commissioning(self):
        ts = int(self._data['detail']['commissioning'])
        return datetime.fromtimestamp(ts)

    @property
    def last_updated(self):
        ts = int(self._data['detail']['lastupdated'])
        return datetime.fromtimestamp(ts)

    @property
    def wifi(self):
        if 'WiFi' not in self._data['detail']:
            return None

        return WiFi(self._data['detail']['WiFi'])

    @property
    def today_save_tree(self):
        return float(self._data['saving']['TodaySaveTree'])

    @property
    def total_save_tree(self):
        return float(self._data['saving']['TotalSaveTree'])

    @property
    def today_save_co2(self):
        return float(self._data['saving']['TodaySaveCo2'])

    @property
    def total_save_co2(self):
        return float(self._data['saving']['TotalSaveCo2'])


class Graph:
    """Graph from the portal."""

    def __init__(self, data: Mapping):
        """Initializer."""
        self._data = data

    @property
    def day_power(self):
        return float(self._data['daypower'])

    @property
    def income(self):
        return float(self._data['income'])

    @property
    def save_tree(self):
        return float(self._data['savetree'])

    @property
    def save_co2(self):
        return float(self._data['saveco2'])

    @property
    def graph_points(self):
        return [
            {
                'datetime': datetime.fromtimestamp(float(graph['datetime'])),
                'power': float(graph['power']),
            }
            for graph in self._data['graph']
        ]


class Powerstation:
    """Station from the portal."""

    def __init__(self, data: Mapping):
        """Initializer."""
        self._data = data

    @property
    def station_id(self):
        return self._data['stationID']

    @property
    def name(self):
        return self._data['name']

    @property
    def actual_power(self):
        return float(self._data['ActualPower'])

    @property
    def today_income(self):
        return float(self._data['TodayIncome'])

    @property
    def total_income(self):
        return float(self._data['TotalIncome'])

    @property
    def etoday(self):
        return float(self._data['etoday'])

    @property
    def etotal(self):
        return int(self._data['etotal'])

    @property
    def last_time(self):
        ts = int(self._data['LastTime'])
        return datetime.fromtimestamp(ts)

    @property
    def status(self):
        return int(self._data['status'])

    @property
    def longitude(self):
        return float(self._data['longitude'])

    @property
    def latitude(self):
        return float(self._data['latitude'])

    @property
    def country(self):
        return self._data['country']

    @property
    def province(self):
        return self._data['province']

    @property
    def city(self):
        return self._data['city']

    @property
    def commissioning(self):
        ts = int(self._data['commissioning'])
        return datetime.fromtimestamp(ts)

    @property
    def street(self):
        return self._data['street']

    @property
    def unit(self):
        return self._data['unit']

    @property
    def wifi(self):
        if 'WiFi' not in self._data:
            return None

        return WiFi(self._data['WiFi'])

    def __repr__(self):
        return '<Powerstation({})>'.format(self.station_id)


class Error:
    """Error from the portal."""

    def __init__(self, data: Mapping):
        """Initializer."""
        self._data = data

    @property
    def datetime(self):
        ts = int(self._data['DateTime'])
        return datetime.fromtimestamp(ts)

    @property
    def inverter(self):
        return self._data['inverter']

    @property
    def inv_err_code(self):
        return self._data['invErrCode']

    @property
    def state(self):
        return self._data['state']

    @property
    def text(self):
        return self._data['text']


def _xml_to_dict(el: ET.Element) -> Dict:
    """Convert XML to Dict."""
    result = {}
    for el_child in el:
        key = el_child.tag
        if len(el_child):
            value = _xml_to_dict(el_child)
        else:
            value = el_child.text or ''
        if key not in result:
            result[key] = value
        elif isinstance(key, list):
            result[key] = result[key] + [value]
        else:
            result[key] = [result[key]] + [value]
    return result


PORTALS = {
    'omnik': {
        'base_url': 'http://www.omnikportal.com:10000/serverapi/?'
    },
    'ginlong': {
        'base_url': 'http://www.ginlongmonitoring.com:10000/serverapi/?'
    },
    'trannergy': {
        'base_url': 'http://log.trannergy.com:10000/serverapi/?'
    },
    'solarmanpv': {
        'base_url': 'http://www.solarmanpv.com:10000/serverapi/?'
    },
}


class SolarPortal:

    def __init__(self, portal: str, base_url: str=None, client=None):
        self.portal = portal
        if portal == 'manual':
            self._base_url = base_url
        else:
            self._base_url = PORTALS[portal]['base_url']
        self._client = client

    async def _request(self, params: Mapping) -> Dict:
        args = [key + '=' + urlquote(value, safe='')
                for key, value in params.items()]
        url = self._base_url + '&'.join(args)
        _LOGGER.debug('Getting url: %s', url)

        if self._client:
            _LOGGER.debug('Getting with client')
            async with self._client.get(url) as response:
                status_code = response.status
                body = await response.text()
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    status_code = response.status
                    body = await response.text()

        _LOGGER.debug('Got response: %s', status_code)

        if status_code != 200:
            raise SolarPortalError('Status code not ok: %s' % (status_code, ))

        # check for errors
        xml = ET.fromstring(body)
        el_status = xml.find('.//status')
        if el_status is not None and el_status.text != 'true':
            el_error_code = xml.find('.//errorCode')
            error_code = el_error_code.text
            el_error_message = xml.find('.//errorMessage')
            error_message = el_error_message.text
            raise SolarPortalError('Error: %s, %s' % (error_code, error_message))

        return _xml_to_dict(xml)

    async def async_login(self, username: str, password: str, key='apitest', client='iPhone') -> Token:
        password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
        params = {
            'method': 'Login',
            'username': username,
            'password': password_md5,
            'key': key,
            'client': client,
        }
        data = await self._request(params)
        return Token(data)

    async def async_get_powerstations(self, token: Token, key='apitest') -> List[Powerstation]:
        params = {
            'method': 'Powerstationslist',
            'username': token.username,
            'token': token.token,
            'key': key,
        }
        data = await self._request(params)

        # ensure always a list
        if isinstance(data['power'], dict):
            data['power'] = [data['power']]

        return [Powerstation(s) for s in data['power']]

    async def async_get_powerstation_count(self, token: Token, key='apitest'):
        params = {
            'method': 'PowerstationslistCount',
            'username': token.username,
            'token': token.token,
            'key': key,
        }
        data = await self._request(params)

        return int(data['recordCount'])

    async def async_get_data(self, token: Token, powerstation: Powerstation, key='apitest') -> Data:
        params = {
            'method': 'Data',
            'username': token.username,
            'token': token.token,
            'key': key,
            'stationid': powerstation.station_id,
        }
        data = await self._request(params)
        return Data(data)

    async def async_get_graph(self, token: Token, powerstation_id: str, now: datetime, type: str, key='apitest') -> Data:
        params = {
            'method': 'Graph',
            'username': token.username,
            'token': token.token,
            'key': key,
            'stationid': powerstation_id,
            'now': now.isoformat(),
            'type': type,
        }
        data = await self._request(params)
        return Graph(data)

    async def async_get_errors(self, token: Token, powerstation_id: str, key='apitest') -> List[Error]:
        params = {
            'method': 'Error',
            'username': token.username,
            'token': token.token,
            'key': key,
            'stationid': powerstation_id,
            'page': '1',
            'perPage': '1000',
        }
        data = await self._request(params)

        # ensure always a list
        if isinstance(data['error'], dict):
            data['error'] = [data['error']]

        return [Error(e) for e in data['error']]

    async def async_logout(self, token: Token, key='apitest'):
        params = {
            'method': 'Logout',
            'username': token.username,
            'token': token.token,
            'key': key,
        }
        data = await self._request(params)
