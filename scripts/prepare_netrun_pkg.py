#!/usr/bin/env python3
"""Step 1 helper: create a dedicated mail.tm inbox, generate UUID & WS_PATH, and build flat xray-node.zip."""
import argparse, json, os, secrets, urllib.request, uuid, zipfile

def api_req(url, method="GET", data=None, headers=None):
    h = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    if headers:
        h.update(headers)
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/tmp/netrun-work", help="Working directory outside git repo")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    pkg_dir = os.path.join(args.out_dir, "pkg")
    os.makedirs(pkg_dir, exist_ok=True)

    domains = api_req("https://api.mail.tm/domains")
    domain_list = domains if isinstance(domains, list) else domains.get("hydra:member", [])
    active = [d["domain"] for d in domain_list if d.get("isActive", True)]
    if not active:
        raise RuntimeError("No active mail.tm domain returned")

    suffix = secrets.token_hex(5)
    address = f"nr{suffix}@{active[0]}"
    password = "Nr!" + secrets.token_urlsafe(12)

    acc = api_req("https://api.mail.tm/accounts", method="POST", data={"address": address, "password": password})
    tok = api_req("https://api.mail.tm/token", method="POST", data={"address": address, "password": password})

    node_uuid = str(uuid.uuid4())
    ws_path = "/ws-" + secrets.token_hex(4)
    project_name = f"xray-node-{suffix[:6]}"

    dockerfile = f"""FROM alpine:latest
RUN apk add --no-cache curl unzip ca-certificates
WORKDIR /app
RUN curl -L -o xray.zip https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip && unzip xray.zip && rm xray.zip && chmod +x xray
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENV UUID={node_uuid}
ENV WS_PATH={ws_path}
EXPOSE 8080
CMD ["/app/entrypoint.sh"]
"""

    entrypoint = f"""#!/bin/sh
PORT=${{PORT:-8080}}
UUID=${{UUID:-{node_uuid}}}
WS_PATH=${{WS_PATH:-{ws_path}}}
cat > /app/config.json <<EOF
{{
"log": {{ "loglevel": "warning"}},
"inbounds": [
{{
"listen": "0.0.0.0",
"port": ${{PORT}},
"protocol": "vless",
"settings": {{
"clients": [ {{ "id": "${{UUID}}", "flow": ""}}],
"decryption": "none"
}},
"streamSettings": {{
"network": "ws",
"wsSettings": {{ "path": "${{WS_PATH}}"}}
}},
"sniffing": {{ "enabled": true, "destOverride": ["http", "tls"]}}
}}
],
"outbounds": [ {{ "protocol": "freedom"}}]
}}
EOF
exec /app/xray run -c /app/config.json
"""

    df_path = os.path.join(pkg_dir, "Dockerfile")
    ep_path = os.path.join(pkg_dir, "entrypoint.sh")
    with open(df_path, "w", newline="\n") as f:
        f.write(dockerfile)
    with open(ep_path, "w", newline="\n") as f:
        f.write(entrypoint)
    os.chmod(ep_path, 0o755)

    zip_path = os.path.join(args.out_dir, "xray-node.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(df_path, arcname="Dockerfile")
        zf.write(ep_path, arcname="entrypoint.sh")

    meta = {
        "address": address,
        "password": password,
        "account_id": acc.get("id"),
        "token": tok.get("token"),
        "project_name": project_name,
        "uuid": node_uuid,
        "ws_path": ws_path,
        "zip_path": zip_path
    }
    meta_path = os.path.join(args.out_dir, "meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    os.chmod(meta_path, 0o600)

    print(json.dumps({
        "email": address,
        "project_name": project_name,
        "ws_path": ws_path,
        "zip_path": zip_path,
        "meta_path": meta_path
    }, indent=2))

if __name__ == "__main__":
    main()
