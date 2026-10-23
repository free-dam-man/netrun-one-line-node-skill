---
name: netrun-one-line-node
description: >-
  Use when the user wants a one-sentence zero-card, zero-account free proxy node
  deployed on Netrun (netrun.io) using a disposable mail.tm inbox, flat
  Dockerfile+entrypoint.sh zip upload, end-to-end Xray verification, and
  VLESS+WS+TLS QR code delivery.
---
# Netrun One-Line Node Skill (Zero-Card / Zero-Account Containerized VLESS+WS+TLS)

Deploy a free containerized Xray (`VLESS + WebSocket + TLS`) service on [Netrun](https://netrun.io) from a single sentence, without asking the user for any email, password, GitHub login, or credit card, and deliver a verified `vless://` subscription link and scannable QR code.

## Core Advantages & Field-Verified Facts (2026-10-23)

- **Zero user input**: Dedicated inbox created automatically via `mail.tm` API (`POST https://api.mail.tm/accounts` + `POST https://api.mail.tm/token`), receives the 6-digit OTP from `hello@netrun.io` at `https://auth.netrun.io/login`.
- **No card, no GitHub OAuth**: Uses Netrun Free plan (`Веб-сервис` / Website mode) with direct `.zip` upload.
- **Global unique subdomain**: Project name becomes `https://<project-name>.de2.netrun.io`. Never hardcode `xray-node` (already taken globally — returns «Это имя уже занято. Придумайте другое»). Always append random hex, e.g. `xray-node-<6hex>`.
- **Zip upload trap**: Package `Dockerfile` and `entrypoint.sh` flat at the root of the `.zip` archive (no parent directory). In the Upload dropzone, **must** attach via the **files** input (`input[type="file"]:not([webkitdirectory])`, «выбрать файлы»), **never** the folder input (`webkitdirectory`, «выбрать папку»), which silently ignores `.zip` files and keeps «Дальше» disabled.
- **Website vs Bot**: A `Dockerfile` zip upload that exposes port `8080` is automatically detected as **Веб-сервис** (Website), which runs long-term on the Free tier and sleeps after 15 minutes of inactivity (waking in a few seconds on first request), unlike Bot projects which stop after 3 hours without referrals.

---

## Step-by-Step Autonomous Workflow

### Step 1: Prepare Dedicated Email (`mail.tm`), Credentials & Flat Zip Package

Run a script in an isolated workspace directory (e.g. `/tmp/netrun-work`, never inside a git repo) to:
1. Query `GET https://api.mail.tm/domains`, pick an active domain, create an account (`POST https://api.mail.tm/accounts`), and fetch a Bearer token (`POST https://api.mail.tm/token`).
2. Generate a random UUIDv4 (`<UUID>`) and a random WebSocket path `/ws-<8hex>` (`<WS_PATH>`), plus a unique project name `xray-node-<6hex>`.
3. Generate `Dockerfile` and `entrypoint.sh` with the exact same `<UUID>` and `<WS_PATH>`, and zip them **flat at the archive root** (`['Dockerfile', 'entrypoint.sh']`).

#### `Dockerfile` template
```dockerfile
FROM alpine:latest
RUN apk add --no-cache curl unzip ca-certificates
WORKDIR /app
RUN curl -L -o xray.zip https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip && unzip xray.zip && rm xray.zip && chmod +x xray
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENV UUID=<UUID>
ENV WS_PATH=<WS_PATH>
EXPOSE 8080
CMD ["/app/entrypoint.sh"]
```

#### `entrypoint.sh` template
```sh
#!/bin/sh
PORT=${PORT:-8080}
UUID=${UUID:-<UUID>}
WS_PATH=${WS_PATH:-<WS_PATH>}
cat > /app/config.json <<EOF
{
"log": { "loglevel": "warning"},
"inbounds": [
{
"listen": "0.0.0.0",
"port": ${PORT},
"protocol": "vless",
"settings": {
"clients": [ { "id": "${UUID}", "flow": ""}],
"decryption": "none"
},
"streamSettings": {
"network": "ws",
"wsSettings": { "path": "${WS_PATH}"}
},
"sniffing": { "enabled": true, "destOverride": ["http", "tls"]}
}
],
"outbounds": [ { "protocol": "freedom"}]
}
EOF
exec /app/xray run -c /app/config.json
```

### Step 2: Register & Sign In on Netrun

1. Open `https://auth.netrun.io/login` in the browser.
2. Fill the `mail.tm` address and click Continue («Продолжить»).
3. Poll `GET https://api.mail.tm/messages` with `Authorization: Bearer <TOKEN>` until the email from `hello@netrun.io` («Код для входа · Netrun») arrives, then fetch `GET https://api.mail.tm/messages/<id>` and extract the 6-digit code (`\b\d{6}\b`).
4. Enter the 6-digit code on `https://auth.netrun.io/login` to complete login.

### Step 3: Create Project & Upload Flat Zip

1. Open `https://netrun.io/new`.
2. Enter the unique project name `xray-node-<6hex>` and click «Дальше» (Next). If a toast says «Это имя уже занято. Придумайте другое», generate a new suffix and retry.
3. Choose Source: **Upload** («Загрузить»).
4. Attach `xray-node.zip` using the **files** input control (`input[type="file"]:not([webkitdirectory])`), **not** the folder control.
5. Verify the UI shows `xray-node.zip` («архив · 1 файл») and «Дальше» becomes enabled, then click «Дальше».
6. If asked for project type, select **Website** («Сайт» / «Веб-сервис»). On the current Netrun wizard, uploading a `Dockerfile` archive automatically launches as **Веб-сервис** on the Free plan («без оплаты»).
7. Wait ~10–30 seconds until status reaches **Работает** and record the assigned domain `<project-name>.de2.netrun.io` (or `*.netrun.io`).

### Step 4: Two-Stage Liveness & Real Client Verification

1. **HTTP Probe**:
   `curl -sS -i https://<DOMAIN><WS_PATH>`
   Must return `HTTP/2 400` (`Bad Request` with `sec-websocket-version: 13`), proving Xray is listening behind Netrun's TLS reverse proxy.
2. **End-to-End Xray Client Test**:
   Run local `xray` client with a SOCKS5 inbound connected to `<DOMAIN>:443` (`protocol: vless`, `security: tls`, `sni: <DOMAIN>`, `network: ws`, `path: <WS_PATH>`, `host: <DOMAIN>`), and request `https://ipinfo.io/json` through the proxy to verify real internet access and record the exit IP, ASN, and city/country (typically Nuremberg, Germany `DE`).

### Step 5: Build Subscription Link & QR Code

Build the URI using the exact formula:

```text
vless://<UUID>@<DOMAIN>:443?encryption=none&security=tls&sni=<DOMAIN>&type=ws&host=<DOMAIN>&path=%2F<WS_PATH_WITHOUT_LEADING_SLASH>#<NODE_NAME>
```

Generate a scannable QR code PNG (`qrcode[pil]` or `qrencode`) encoding the `vless://` URI, and deliver:
- Scannable QR code image + subscription URI
- Verified exit IP location (country/city)
- Mandatory sleep notice: **「闲置 15 分钟休眠、首次连接需数秒唤醒」**

## Security & Boundaries
- Free plan only: never bind a card or upgrade to paid tiers.
- Never ask for or touch any of the user's personal accounts (email, GitHub, Google).
- Never commit real UUIDs, domains, emails, or tokens into any repository or skill file.
