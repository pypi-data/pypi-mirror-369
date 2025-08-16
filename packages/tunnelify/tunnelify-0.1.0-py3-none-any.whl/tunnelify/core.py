import subprocess
import re
import threading

def tunnel(port):
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    url = None
    def reader():
        nonlocal url
        for line in proc.stdout:
            m = re.search(r"https://[0-9a-zA-Z\-]+\.trycloudflare\.com", line)
            if m:
                url = m.group(0)
                break
    t = threading.Thread(target=reader, daemon=True)
    t.start()
    while url is None:
        pass
    return url, proc