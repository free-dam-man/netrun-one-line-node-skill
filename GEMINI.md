# AGENTS.md（给所有 AI Agent 的入口）

你是被用户派来在 Netrun 上零绑卡、零个人账号部署免费容器化 WebSocket（VLESS+WS+TLS）节点的 Agent。请直接阅读 `SKILL.md` 并全程独立执行：

1. 运行 `python3 scripts/prepare_netrun_pkg.py --out-dir /tmp/netrun-work` 自动创建 `mail.tm` 专用邮箱、生成随机 `UUID` 与 `/ws-xxxxxxxx` 路径、打包平铺根目录的 `xray-node.zip`（含 `Dockerfile` 与 `entrypoint.sh`）。
2. 在浏览器打开 `https://auth.netrun.io/login` 填入专用邮箱，运行 `python3 scripts/poll_netrun_otp.py --meta /tmp/netrun-work/meta.json` 自动读取 `hello@netrun.io` 发来的 6 位验证码并完成登录。
3. 在 `https://netrun.io/new` 新建项目（名称带随机后缀如 `xray-node-<6位hex>`，避免重名），选择上传源码（Upload / Загрузить），**必须使用拖放区的 `files` 文件控件**（`input[type="file"]:not([webkitdirectory])`）挂载 `/tmp/netrun-work/xray-node.zip`（切勿使用 `choose a folder` 文件夹控件，否则会静默忽略 `.zip`），启动免费版（Веб-сервис / Website，闲置 15 分钟休眠、有请求数秒内唤醒）。
4. 部署变为 `Работает` 后，拿到分配的 `<项目名>.de2.netrun.io` 域名，运行 `python3 scripts/verify_and_qr.py --meta /tmp/netrun-work/meta.json --domain <分配的域名>` 完成两步实测（`GET https://<域名><WS路径>` 返回 `HTTP 400` + 本机 Xray 客户端实连测出出口 IP 与城市）并生成订阅链接与二维码 PNG。

硬规则：全程不向用户索要任何邮箱、密码、GitHub 或银行卡；任何一步卡住如实报告卡点与已尝试办法，严禁编造结果。
