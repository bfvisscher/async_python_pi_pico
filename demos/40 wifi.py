import json

from async_network import connect_wifi
from async_runner import add_task, start_tasks
from async_tasks import cpu_load

# To connect to a wifi, a simple tasks is available, connect_wifi.
# It requires one parameter, a dictionary
#  network_logins = {
#    "<ssid_network1>": "password_network1",
#    "<ssid_network2>": "password_network2",
#    "<ssid_network3>": "password_network3",
#  }


# load in json file  (dictionary with secret information)
with open('secrets.json', 'rt') as f:
    secrets = json.load(f)

network_logins = {
    secrets['wifi.ssid']: secrets['wifi.password'],
}

add_task(connect_wifi, network_logins)  # provides continues monitoring of the wifi and reconnects when needed
add_task(cpu_load)  # show how little cpu is being used

start_tasks()
