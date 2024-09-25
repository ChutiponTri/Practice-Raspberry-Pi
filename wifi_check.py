import subprocess

def check_wifi_connected():
    try:
        result = subprocess.check_output("netsh wlan show interfaces", shell=True, stderr=subprocess.STDOUT)
        return "State" in result.decode("utf-8") and "connected" in result.decode("utf-8")
    except subprocess.CalledProcessError:
        return False