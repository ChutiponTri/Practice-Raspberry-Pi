# Import necessary libraries
import platform               # Used to determine platform (e.g., Windows, Linux)
import logging                # For logging purposes
import asyncio                # To manage asynchronous operations
from bleak import BleakClient # A class from the bleak library for BLE communication
from bleak import _logger as logger  # Logger for bleak library
from bleak.uuids import uuid16_dict  # A dictionary containing commonly used UUIDs for BLE services
import json

# Define Nordic Uart Service (NUS) characteristic UUIDs
UART_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for RX
UART_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for TX

UART_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e".format(
    0xFFE1
)  # The format here does not do anything

# Global flag to check for new data
queue1 = asyncio.Queue()
queue2 = asyncio.Queue()

async def conn(address):
    async with BleakClient(address[1],) as client1, \
               BleakClient(address[0],) as client2:
        x = await client1.is_connected()
        print("Connected: {0}".format(x))
        x = await client2.is_connected()
        print("Connected: {0}".format(x))

        # Notification handler function, prints received data and sets dataFlag to True
        def notification_handler1(sender, data):
            print(f"Dev1 : {data}") 
            data = json.loads(data)
            queue1.put_nowait(data)

        def notification_handler2(sender, data):
            print(f"Dev2 : {data}") 
            # print("Queue2", queue2.qsize())
            data = json.loads(data)
            queue2.put_nowait(data)

        await client1.start_notify(UART_TX_UUID, notification_handler1)
        await client2.start_notify(UART_TX_UUID, notification_handler2)
        while True : 
            await asyncio.sleep(0)

async def async_main(address):
    try:
        await asyncio.wait_for(
            asyncio.gather(conn(address)), 20
        )
    except asyncio.TimeoutError:
        print(queue1.qsize())
        print(queue2.qsize())

if __name__ == "__main__":
    #this is MAC of our BLE device
    address = (
        "E3:CD:91:AC:53:CD",                               # สำหรับตัวมีจอ
        "FF:09:AA:27:E2:E8",                               # สำหรับตัวเล็ก

    )

    data = asyncio.run(async_main(address))