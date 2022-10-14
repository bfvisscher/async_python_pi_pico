import network


def connect_wifi(network_dict, blackboard):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    while True:
        blackboard['WIFI connected'] = wlan.isconnected()
        if blackboard['WIFI connected']:
            yield 60000  # don't check for another minute
        else:
            print('Connecting to network...scanning')
            found_ssid = wlan.scan()
            for ssid_code in found_ssid:
                ssid = ssid_code[0].decode('utf-8')
                if ssid in network_dict:
                    print("Connecting to '%s'" % ssid)
                    wlan.connect(ssid, network_dict[ssid])

                    retry = 0
                    while not wlan.isconnected() and wlan.status() >= 0 and retry < 300:
                        retry += 1
                        yield 100
                    if retry < 300:
                        print("Connected to '%s'" % ssid)
                        break
                    print("Could not connect to '%s'" % ssid)
