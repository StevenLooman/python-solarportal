# -*- coding: utf-8 -*-
"""Tests for Solarportal API for python."""

from datetime import datetime

import pytest
from aiohttp import web

from solarportal import SolarPortal
from solarportal import SolarPortalError
from solarportal import Token


def portal_with_response(response):
    def respond(request):
        return web.Response(body=response)

    def create_app(loop):
        app = web.Application(loop=loop)
        app.router.add_route('GET', '/serverapi/', respond)
        return app

    return create_app


class TestSolarPortal:

    async def test_login_ok(self, test_client):
        response = '''<?xml version="1.0" encoding="utf-8" ?>
<login>
    <status>true</status>
    <errorCode> </errorCode>
    <errorMessage> </errorMessage>
    <userID>1</userID>
    <userName>user_1</userName>
    <token>token_string</token>
</login>'''
        client = await test_client(portal_with_response(response))

        portal = SolarPortal('manual', base_url='/serverapi/?', client=client)
        token = await portal.async_login('user_1', 'password_1')
        assert token.user_id == '1'
        assert token.username == 'user_1'
        assert token.token == 'token_string'

    async def test_login_failed(self, test_client):
        response = '''<?xml version="1.0" encoding="utf-8" ?>
<error>
    <status>false</status>
    <errorCode>1</errorCode>
    <errorMessage>You've been logged out or you have no authorization to use the service</errorMessage>
</error>'''
        client = await test_client(portal_with_response(response))

        portal = SolarPortal('manual', base_url='/serverapi/?', client=client)
        with pytest.raises(SolarPortalError):
            await portal.async_login('user_1', 'password_1')

    async def test_get_powerstations(self, test_client):
        response = '''<?xml version="1.0" encoding="utf-8" ?>
<list>
    <status>true</status>
    <errorCode> </errorCode>
    <errorMessage> </errorMessage>
    <power>
        <stationID>1</stationID>
        <name>station_name</name>
        <timezone>0</timezone>
        <pic>http://example.org/image.jpg</pic>
        <ActualPower>100.1</ActualPower>
        <TodayIncome>1.00</TodayIncome>
        <TotalIncome>10.0</TotalIncome>
        <etoday>1.0</etoday>
        <etotal>300</etotal>
        <LastTime>1000000000</LastTime>
        <status>0</status>
        <longitude>1.0000000</longitude>
        <latitude>2.0000000</latitude>
        <country>Country</country>
        <province>Province</province>
        <city>City</city>
        <unit>â‚¬</unit>
        <street></street>
        <commissioning>1000000000</commissioning>
        <WiFi>
            <id>600000000</id>
            <inverter>1</inverter>
        </WiFi>
    </power>
</list>'''
        client = await test_client(portal_with_response(response))

        portal = SolarPortal('manual', base_url='/serverapi/?', client=client)
        token = Token({'token': 'test_token', 'userName': 'user_1'})
        powerstations = await portal.async_get_powerstations(token)
        assert len(powerstations) == 1

        powerstation = powerstations[0]
        assert powerstation.station_id == '1'
        assert powerstation.name == 'station_name'
        assert powerstation.actual_power == 100.1
        assert powerstation.today_income == 1.0
        assert powerstation.total_income == 10.0
        assert powerstation.etoday == 1.0
        assert powerstation.etotal == 300

    async def test_powerstation_count(self, test_client):
        response = '''<?xml version="1.0" encoding="utf-8" ?>
<list>
    <recordCount>1</recordCount>
    <perPageCount>10</perPageCount>
    <pageCount>1</pageCount>
</list>'''
        client = await test_client(portal_with_response(response))

        portal = SolarPortal('manual', base_url='/serverapi/?', client=client)
        token = Token({'token': 'test_token', 'userName': 'user_1'})
        count = await portal.async_get_powerstation_count(token)
        assert count == 1

    async def test_data(self, test_client):
        response = '''<?xml version="1.0" encoding="utf-8" ?>
<data>
    <status>true</status>
    <errorCode> </errorCode>
    <errorMessage> </errorMessage>
    <pic>http://www.example.org/image.jpg</pic>
    <name>station_name</name>
    <country>country</country>
    <province>province</province>
    <city>city</city>
    <street></street>
    <sunrise></sunrise>
    <sunset></sunset>
    <income>
        <TodayIncome>1.00</TodayIncome>
        <ActualPower>100.1</ActualPower>
        <etoday>1.0</etoday>
        <etotal>300</etotal>
        <TotalIncome>10.0</TotalIncome>
    </income>
    <detail>
        <Capacity>3.7</Capacity>
        <commissioning>1000000000</commissioning>
        <lastupdated>1000000000</lastupdated>
        <WiFi>
            <id>600000000</id>
            <inverter>
                <SN>000000000000001</SN>
                <status>0</status>
                <power>1.00</power>
                <etoday>2.0</etoday>
                <etotal>2000</etotal>
                <lastupdated>1000000000</lastupdated>
                <mode>98</mode>
            </inverter>
        </WiFi>
    </detail>
    <saving>
        <TodaySaveTree>0.1</TodaySaveTree>
        <TotalSaveTree>1.0</TotalSaveTree>
        <TodaySaveCo2>0.1</TodaySaveCo2>
        <TotalSaveCo2>1.0</TotalSaveCo2>
    </saving>
</data>'''
        client = await test_client(portal_with_response(response))

        portal = SolarPortal('manual', base_url='/serverapi/?', client=client)
        token = Token({'token': 'test_token', 'userName': 'user_1'})
        data = await portal.async_get_data(token, powerstation_id='1')
        assert data.name == 'station_name'
        assert data.today_income == 1.00
        assert data.actual_power == 100.1
        assert data.etoday == 1.0
        assert data.etotal == 300
        assert data.total_income == 10.0
        assert data.today_save_tree == 0.1
        assert data.total_save_tree == 1.0

    async def test_get_graph(self, test_client):
        response = '''<?xml version="1.0" encoding="UTF-8"?>
<graphs>
   <status>true</status>
   <errorCode />
   <errorMessage />
   <daypower>1.0</daypower>
   <income>0.5</income>
   <savetree>0.1</savetree>
   <saveco2>0.1</saveco2>
   <graph>
      <datetime>1000000000</datetime>
      <power>0.0</power>
   </graph>
   <graph>
      <datetime>1000000001</datetime>
      <power>1.0</power>
   </graph>
</graphs>'''
        client = await test_client(portal_with_response(response))

        portal = SolarPortal('manual', base_url='/serverapi/?', client=client)
        token = Token({'token': 'test_token', 'userName': 'user_1'})
        now = datetime.now()
        graph = await portal.async_get_graph(token, powerstation_id='1', now=now, type='1')
        assert graph.day_power == 1.0
        assert graph.income == 0.5
        assert len(graph.graph_points) == 2

    async def test_get_error(self, test_client):
        response = '''<?xml version="1.0" encoding="UTF-8"?>
<errors>
   <status>true</status>
   <errorCode />
   <errorMessage />
   <errTotal>1</errTotal>
   <page>1</page>
   <perPage>100</perPage>
   <error>
      <DateTime>1000000000</DateTime>
      <inverter>000000000000001</inverter>
      <invErrCode>1015</invErrCode>
      <state>waiting</state>
      <text>NO-G</text>
   </error>
</errors>'''
        client = await test_client(portal_with_response(response))

        portal = SolarPortal('manual', base_url='/serverapi/?', client=client)
        token = Token({'token': 'test_token', 'userName': 'user_1'})
        errors = await portal.async_get_errors(token, powerstation_id='1')
        assert len(errors) == 1

        error = errors[0]
        assert error.inv_err_code == '1015'
        assert error.state == 'waiting'
        assert error.text == 'NO-G'

    async def test_logout(self, test_client):
        response = '''<?xml version="1.0" encoding="UTF-8"?>
<login>
   <status>true</status>
   <errorCode />
   <errorMessage />
   <userID>1</userID>
   <userName>user_1</userName>
   <token>test_token</token>
</login>'''
        client = await test_client(portal_with_response(response))

        portal = SolarPortal('manual', base_url='/serverapi/?', client=client)
        token = Token({'token': 'test_token', 'userName': 'user_1'})
        await portal.async_logout(token)
