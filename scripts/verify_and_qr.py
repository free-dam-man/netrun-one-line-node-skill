#!/usr/bin/env python3
"""Step 4 & 5 helper: verify HTTP 400 on WS path, run real Xray proxy check, and generate VLESS link + QR PNG."""
import argparse, json, os, subprocess, time

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", default="/tmp/netrun-work/meta.json")
    ap.add_argument("--domain", required=True, help="Assigned *.netrun.io domain, e.g. xray-node-xxxxxx.de2.netrun.io")
    ap.add_argument("--node-name", default="Netrun-DE")
    args = ap.parse_args()

    with open(args.meta) as f:
        meta = json.load(f)

    out_dir = os.path.dirname(os.path.abspath(args.meta))
    domain = args.domain.strip().replace("https://", "").replace("http://", "").strip("/")
    uuid_val = meta["uuid"]
    ws_path = meta["ws_path"]
    ws_no_slash = ws_path.lstrip("/")

    vless_uri = (
        f"vless://{uuid_val}@{domain}:443"
        f"?encryption=none&security=tls&sni={domain}&type=ws&host={domain}"
        f"&path=%2F{ws_no_slash}#{args.node_name}"
    )

    # 1. HTTP 400 check
    probe = subprocess.check_output(
        ["curl", "-sS", "-i", "--max-time", "15", f"https://{domain}{ws_path}"],
        text=True
    )
    first_line = probe.splitlines()[0] if probe.splitlines() else ""
    print("HTTP probe:", first_line)
    if "400" not in first_line:
        raise RuntimeError(f"Expected HTTP 400 on {ws_path}, got: {first_line}")

    # 2. Local Xray real connection test
    xray_bin = None
    for p in ["/usr/local/bin/xray", "/usr/bin/xray", "/tmp/xray-bin/xray"]:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            xray_bin = p
            break
    if not xray_bin:
        os.makedirs("/tmp/xray-bin", exist_ok=True)
        subprocess.check_call([
            "bash", "-c",
            "curl -sL -o /tmp/xray-bin/xray.zip https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip "
            "&& unzip -qo /tmp/xray-bin/xray.zip -d /tmp/xray-bin && chmod +x /tmp/xray-bin/xray"
        ])
        xray_bin = "/tmp/xray-bin/xray"

    cfg_path = os.path.join(out_dir, "client-config.json")
    client_cfg = {
        "log": {"loglevel": "warning"},
        "inbounds": [{"listen": "127.0.0.1", "port": 10809, "protocol": "socks", "settings": {"udp": True}}],
        "outbounds": [{
            "protocol": "vless",
            "settings": {"vnext": [{"address": domain, "port": 443, "users": [{"id": uuid_val, "encryption": "none"}]}]},
            "streamSettings": {
                "network": "ws",
                "security": "tls",
                "tlsSettings": {"serverName": domain},
                "wsSettings": {"path": ws_path, "headers": {"Host": domain}}
            }
        }]
    }
    with open(cfg_path, "w") as f:
        json.dump(client_cfg, f, indent=2)

    proc = subprocess.Popen([xray_bin, "run", "-c", cfg_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        time.sleep(1.5)
        ipinfo = subprocess.check_output(
            ["curl", "-sS", "--max-time", "20", "--socks5-hostname", "127.0.0.1:10809", "https://ipinfo.io/json"],
            text=True
        )
        print("Exit IP info:", ipinfo.strip())
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    vless_file = os.path.join(out_dir, "vless.txt")
    with open(vless_file, "w") as f:
        f.write(vless_uri + "\n")
    os.chmod(vless_file, 0o600)

    qr_path = os.path.join(out_dir, "netrun-vless-qr.png")
    import qrcode
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=3)
    qr.add_data(vless_uri)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(qr_path)
    print("Saved VLESS link to:", vless_file)
    print("Saved QR image to:", qr_path)

if __name__ == "__main__":
    main()
