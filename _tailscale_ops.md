# Tailscale 现状与操作纪律（2026-11-26 修复后）

## 一、两个实例，各管一件事

| 实例 | 节点名 | IP | 用途 | 启动方式 |
|---|---|---|---|---|
| 系统服务（推荐日常用） | desktop-n0hhqn3-sys | `100.84.28.40` | 电脑上网、出口节点、Google | Windows 服务 `Tailscale`（自动启动） |
| 用户态实例（画廊用） | desktop-n0hhqn3-2 | `100.74.238.39` | `tailscale serve 8861 → 127.0.0.1:8861`，公网 `http://199.68.217.229:8861/` 靠它 | `_start_tailscale_gallery.ps1`，state 在 `runs\_tsuser4` |

**两个都别删。** 用户态实例承载视频画廊的 nginx 反代，停掉画廊就 404/超时；系统实例承载本机上网。

## 二、系统实例当前配置（已登录并验证）

- 登录方式：auth key（不要用浏览器授权，Google OAuth 在无出口时是死循环）
- `accept-dns = true`（关键：否则 DNS 被污染，google.com 解析到 `2001::1` / `185.45.5.35`，必超时）
- 出口节点：rainyun 系列，`exit-node-allow-lan-access = true`
- 验证：`curl https://www.google.com` → 200；`youtube` → 200；`accounts.google.com` → 302

## 三、纪律（硬约束）

1. **不允许登出** tailscale；不允许 `tailscale down`；不允许结束 `tailscaled` / `tailscale` 进程。
2. 只允许在「直连」与「走本地代理 8899」之间切换：
   - 直连：清空 `HTTP_PROXY/HTTPS_PROXY`
   - 非直连：`HTTP_PROXY=http://127.0.0.1:8899`（`_local_connect_proxy.py`，ComfyUI 自带 python 启动）
3. 修网络只动 `tailscale set`（改 prefs），不动进程与登录态。

## 四、常见故障对照

| 现象 | 检查 | 处理 |
|---|---|---|
| Google 打不开但 `curl` 也失败 | `nslookup www.google.com` 是否返回 `2001::1` | `tailscale set --accept-dns=true` |
| 全部外网不通 | `tailscale status --json` 看 `ExitNodeStatus.Online` | `tailscale set --exit-node=<rainyun IP>` |
| 画廊 404 | 用户态实例 `serve status` | 重跑 `_start_tailscale_gallery.ps1`（只碰用户态实例） |
| 系统实例显示 Logged out | `tailscale status` | `tailscale up --authkey=tskey-auth-...`（勿用浏览器授权） |