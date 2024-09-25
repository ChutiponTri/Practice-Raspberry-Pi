import platform               # Used to determine platform (e.g., Windows, Linux)
import logging                # For logging purposes
import asyncio                # To manage asynchronous operations
from bleak import BleakClient # A class from the bleak library for BLE communication
from bleak import _logger as logger  # Logger for bleak library
from bleak.uuids import uuid16_dict  # A dictionary containing commonly used UUIDs for BLE services
import json
from threading import Thread
from mqtt_client import MQTT_Client

# Define Nordic Uart Service (NUS) characteristic UUIDs
UART_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for RX
UART_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for TX

# Global flag to check for new data
dataFlag = False
listA = asyncio.Queue()
listB = asyncio.Queue()

# List of MQTT Data
ax1_mqtt, ay1_mqtt, az1_mqtt = [], [], []
gx1_mqtt, gy1_mqtt, gz1_mqtt = [], [], []

broker = MQTT_Client()

async def run_func(address):
    try:
        async with BleakClient(address) as client:
            x = client.is_connected
            print("Connected: {0}".format(x))

            async def notification_handler(sender, data):
                data = json.loads(data)
                # print(data, type(data))
                # listA.put_nowait(data)

                ax1_mqtt.append(data["ax"])
                ay1_mqtt.append(data["ay"])
                az1_mqtt.append(data["az"])
                gx1_mqtt.append(data["gx"])
                gy1_mqtt.append(data["gy"])
                gz1_mqtt.append(data["gz"])
                task_1 = Thread(target=check_list_1)
                task_1.start()

            await client.start_notify(UART_TX_UUID, notification_handler)

            # Continuously check for connection status and received data
            while True:
                await asyncio.sleep(0)
                if not client.is_connected:
                    print("Sensor disconnected")
                    break

    except asyncio.CancelledError:
        print("Task cancelled")

def check_list_1():
    if len(gz1_mqtt) >= 10:
        msg = {"ax1":ax1_mqtt, "ay1":ay1_mqtt, "az1":az1_mqtt, "gx1":gx1_mqtt, "gy1":gy1_mqtt, "gz1":gz1_mqtt}
        json_payload = json.dumps(msg)
        try:
            broker.publish("ton/server/one", json_payload)
        except Exception as e:
            print(e)
        ax1_mqtt.clear()
        ay1_mqtt.clear()
        az1_mqtt.clear()
        gx1_mqtt.clear()
        gy1_mqtt.clear()
        gz1_mqtt.clear()  

async def getget(address):
    task = [
        asyncio.create_task(run_func(address)),
    ]
    await asyncio.gather(*task)

if __name__ == "__main__":

    # Define the BLE device address
    address = "ff:09:aa:27:e2:e8" 
    address = "E3:CD:91:AC:53:CD"
    try:
        asyncio.run(getget(address))
    except KeyboardInterrupt:
        print("Program terminated by user")

