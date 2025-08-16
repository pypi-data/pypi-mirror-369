import sys, requests
API_BASE = "https://api.crowe-ai.com"  # Your API endpoint

def main():
    if len(sys.argv) < 2:
        print("Usage: crowe /hi  |  crowe <message>")
        return
    text = " ".join(sys.argv[1:]).strip()

    # Slash commands
    if text.lower() in ("/hi","/hello"):
        text = "Hi"
    elif text.lower() in ("/help","/?"):
        print("Commands: /hi, /help"); return
    elif text.startswith("/"):
        text = text[1:]

    try:
        r = requests.post(API_BASE.rstrip("/") + "/api/chat",
                          json={"query": text}, timeout=60)
    except Exception as e:
        print(f"[Crowe] Network error: {e}")
        return

    if not r.ok:
        try: detail = r.json()
        except Exception: detail = r.text
        print(f"[Crowe] Error {r.status_code}: {detail}")
        return

    print(r.json().get("message",""))
