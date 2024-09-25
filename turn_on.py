from bleak import BleakScanner
import asyncio
import time
from mqtt_client import MQTT_Client

mqtt = MQTT_Client()

async def scan_for_rssi():
    adver = None
    def filter_function(dev, adv):
        nonlocal adver
        adver = adv
        return dev.name and "xiao" in dev.name.lower()

    while True:
        time.sleep(1)
        device = await BleakScanner.find_device_by_filter(filter_function)
        
        if device:
            print(f"Device found: {device}")
            # Print the RSSI
            print(f"RSSI: {adver.rssi} dBm")

            if adver.rssi > -85:
                mqtt.publish("ton/smart/wowza", "on")
                mqtt.publish("ton/smart/Mai", "on")
            elif adver.rssi <= -85:
                mqtt.publish("ton/smart/wowza", "off")
                mqtt.publish("ton/smart/Mai", "off")
        else:
            mqtt.publish("ton/smart/wowza", "off")
            mqtt.publish("ton/smart/Mai", "off")
            print("No device found matching the filter.")


# Run the scan function
asyncio.run(scan_for_rssi())


