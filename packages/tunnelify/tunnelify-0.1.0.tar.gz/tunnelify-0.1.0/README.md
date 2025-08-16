# Tunnelify

Tunnelify is a Python library to easily create and manage Cloudflare tunnels, powered by Cloudflared.

# Example

```python
from tunnelify import tunnel

url, proc = tunnel(8000) # Create a tunnel on port 8000
print(url) # trycloudflare.com URL

while True:
    val = input("'exit' to exit: ")

    if val == "e":
        proc.terminate()
        break
    else: pass
```

# Installation

Just:
`pip install tunnelify`

Tunnelify requires Cloudflared package to work. If it doesn't exist on your system, Tunnelify will automatically install it.