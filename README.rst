python-solarportal
==================

Python library to access the portals of:

- omnik
- ginlong
- trannergy
- solarmanpv


Usage
-----

Example usage::

    portal = solarportal.SolarPortal('omnik')
    token = await portal.async_login(username='your_username', password='your_password')
    powerstations = await portal.async_get_powerstations(token)
    powerstation = powerstations[0]
    data = await portal.async_get_data(token, powerstation)
    print('actual power: {} kWh'.format(data.actual_power))
    print('todays energy: {} kWh'.format(data.today_income))


A tool to log values to a CSV has been included: ``solarportal-to-csv``

Another tool to log values directly to PVOutput has been included: ``solarportal-to-pvoutput``
