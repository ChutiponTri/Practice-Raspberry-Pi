import asyncio
from bleak import BleakScanner, BleakClient


async def discover_devices():
    device = await BleakScanner.find_device_by_filter(
        lambda dev, adv: dev.name and "xiao" in dev.name.lower()
    )
    print(device.name, device.address)

if __name__ == '__main__':
    asyncio.run(discover_devices())


