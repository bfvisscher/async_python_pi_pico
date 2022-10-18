# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


import network


def connect_wifi(network_logins, idle_when_connected_ms=1000, rescan=False):
    """
    asynchonous task that connects and maintains connection to wifi network(s)

    :param network_logins: dictionary with ssid : password combinations
    :param idle_when_connected_ms: time to sleep between checking network connection
    :param rescan: when available networks is likely to events (ie moving between zone), enable rescan
    :return:
    """
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)

    found_ssid = None
    any_matches = False
    while True:
        if wlan.isconnected():
            yield idle_when_connected_ms  # don't check for another (5) second
        else:
            if found_ssid is None or rescan or not any_matches:
                print('Scanning for available wifi networks.')
                found_ssid = wlan.scan()  # no async way known so may take up lots of time suddenly
            any_matches = False
            for ssid_code in found_ssid:
                ssid = ssid_code[0].decode('utf-8')
                if ssid in network_logins:
                    print("Attempting to connect to '%s'" % ssid)
                    wlan.connect(ssid, network_logins[ssid])
                    any_matches = True

                    while wlan.status() == network.STAT_CONNECTING:
                        yield 100
                    status = wlan.status()
                    if status == network.STAT_GOT_IP:
                        print("Connected to wifi '%s'" % ssid)
                        break
                    elif status == network.STAT_WRONG_PASSWORD:
                        print("Unable to connect to wifi '%s' : Incorrect password" % ssid)
                    elif status == network.STAT_NO_AP_FOUND:
                        print("Unable to connect to wifi '%s' : Access Point not accessible" % ssid)
                    else:
                        print("Could not connect to wifi '%s'" % ssid)
