#!/usr/bin/env python3
"""Step 2 helper: poll mail.tm for the 6-digit login code from hello@netrun.io."""
import argparse, json, re, time, urllib.request

def req(url, token):
    r = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0"
    })
    with urllib.request.urlopen(r, timeout=20) as resp:
        return json.loads(resp.read().decode())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", default="/tmp/netrun-work/meta.json")
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    with open(args.meta) as f:
        meta = json.load(f)
    token = meta["token"]

    deadline = time.time() + args.timeout
    msg_id = None
    while time.time() < deadline:
        data = req("https://api.mail.tm/messages", token)
        members = data if isinstance(data, list) else data.get("hydra:member", [])
        for m in members:
            fr = (m.get("from") or {}).get("address", "")
            subj = m.get("subject", "")
            if "netrun" in fr.lower() or "netrun" in subj.lower() or "код" in subj.lower():
                msg_id = m["id"]
                break
        if msg_id:
            break
        time.sleep(3)

    if not msg_id:
        raise RuntimeError("Timed out waiting for Netrun verification email")

    detail = req(f"https://api.mail.tm/messages/{msg_id}", token)
    text = detail.get("text") or ""
    html = detail.get("html") or ""
    if isinstance(html, list):
        html = "\n".join(html)
    m = re.search(r"\b(\d{6})\b", text + "\n" + html + "\n" + detail.get("subject", ""))
    if not m:
        raise RuntimeError("Could not find 6-digit OTP in email body")
    print(m.group(1))

if __name__ == "__main__":
    main()
