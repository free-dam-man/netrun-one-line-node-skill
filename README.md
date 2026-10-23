# netrun-one-line-node-skill

**零绑卡、零个人账号、一句话出码**：让任何带终端与浏览器的 AI Agent（Muse、Claude Code、ChatGPT Agent、Gemini、Cursor 等）在 [Netrun](https://netrun.io) 免费容器平台上全自动部署一个 **Xray（VLESS + WebSocket + TLS）** 节点，完成双层实测验收后直接交付**小火箭（Shadowrocket）/ v2rayN / Nekobox 订阅链接与扫码二维码**。

> **免责声明与合规说明**：本仓库仅用于个人网络容器化部署与 AI 自动化教学研究。请严格遵守所在地法律法规与目标平台服务条款，切勿用于任何违法或滥用用途。本仓库不包含任何真实账号、UUID、域名或密钥，所有示例均为占位符。

---

## 为什么选这套方案？

1. **真正零打扰**：AI 通过 `mail.tm` API 自动创建项目专用一次性邮箱，自动读取 `hello@netrun.io` 的 6 位登录验证码，**全程不向用户索要任何邮箱、密码、GitHub 授权或信用卡**。
2. **平铺 Zip 直传免 GitHub**：直接把 `Dockerfile` 与 `entrypoint.sh` 平铺打包成 `.zip` 上传，无需绑定 GitHub。
3. **免费 Website 模式长期可用**：Netrun 上 `Bot` 类型免费无邀请只能跑 3 小时；而暴露 `8080` 端口的 `Dockerfile` 会以 **Website（Веб-сервис）** 模式免费长期运行（**闲置 15 分钟休眠，有请求时数秒内自动唤醒**）。
4. **真实验收才交付**：先验 `GET https://<域名><WS路径>` 返回 `HTTP 400`，再由 AI 在本机跑真实 Xray 客户端连上节点访问外网、核实出口 IP 所在城市（实测为德国纽伦堡 `de2` 机房），最后生成二维码。

---

## 一句话启动口令（直接复制给你的 AI）

```text
按这个仓库的 SKILL.md 规格，在 Netrun 上帮我免费部署一个容器化 WebSocket 节点并交付连接信息，全程由你独立完成（用 mail.tm 自动建专用收信箱收 6 位验证码、用 files 控件上传平铺 zip 包、跑完 HTTP 400 与 Xray 实连验收），最后只交付订阅链接、二维码图片、实测出口城市和休眠说明，不要向我索要任何账号、密码或银行卡：
https://github.com/free-dam-man/netrun-one-line-node-skill
```

---

## 实战避坑指南（2026-10-23 实测验证）

| 坑点 | 现象 | 正确做法 |
|---|---|---|
| **项目名全局唯一** | 填 `xray-node` 点下一步报错 `Это имя уже занято. Придумайте другое`，源码步骤保持锁定 | 项目名对应全局子域名 `<name>.de2.netrun.io`，必须带随机后缀，如 `xray-node-556a86` |
| **Upload 拖放区两个控件** | 用 `choose a folder`（文件夹控件）挂载 `.zip` 时**不报错、文件不出现、Next 保持灰色** | 必须用拖放区的 **`files`（文件）控件**（`input[type="file"]:not([webkitdirectory])`）挂载平铺 `.zip` |
| **Zip 目录层级** | 把文件夹一起打包成 `pkg/Dockerfile` 导致识别不到 Dockerfile | `Dockerfile` 与 `entrypoint.sh` 必须**平铺在压缩包根目录**（`['Dockerfile', 'entrypoint.sh']`） |
| **项目类型选错** | 选成 `Bot` 免费版无邀请仅能运行 3 小时 | 选 `Website`（`Веб-сервис`），含 `EXPOSE 8080` 的 Dockerfile 上传后会自动识别为 `Веб-сервис` |

---

## 仓库目录结构

- `SKILL.md`：给 AI Agent 的完整分步执行规范与验收标准
- `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`：各家 AI Agent 自动识别入口
- `LAUNCH-PROMPT.md`：普通用户一键复制的启动口令
- `scripts/prepare_netrun_pkg.py`：自动调 `mail.tm` 建箱、生成随机 `UUID` 与 `WS_PATH`、打包平铺根目录 `xray-node.zip`
- `scripts/poll_netrun_otp.py`：自动轮询 `mail.tm` 提取 `hello@netrun.io` 的 6 位登录码
- `scripts/verify_and_qr.py`：自动执行 `HTTP 400` 探测 + 本机 Xray SOCKS5 实连测出口城市 + 生成二维码图片
- `templates/`：`Dockerfile.template` 与 `entrypoint.sh.template` 模板

---

## 订阅链接公式

```text
vless://<UUID>@<域名>:443?encryption=none&security=tls&sni=<域名>&type=ws&host=<域名>&path=%2F<WS路径去掉开头斜杠>#<节点名>
```

> **使用提示**：免费 Website 实例在**闲置 15 分钟后会休眠**，首次连接或长时间未用后重连需等待数秒唤醒。
