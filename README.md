# rk3576-mc-deploy

在 ARM 开发板（示例：泰山派 RK3576）上 24/7 运行 Minecraft Fabric 服务器的一整套部署方案：systemd 托管、零停机热备份、FRP 内网穿透、监控与踩坑速查。照着 `docs/` 走即可从零复刻。x86 小主机/NAS 同样适用。

[English](#english) | 中文

## 内容地图

| 文档 | 内容 |
|---|---|
| [docs/zh/01](docs/zh/01-hardware-os.md) | 硬件与系统准备（关桌面省内存、SSH 改端口、时间同步） |
| [docs/zh/02](docs/zh/02-mc-server.md) | Fabric 服务端安装与 server.properties 逐项说明 |
| [docs/zh/03](docs/zh/03-systemd.md) | systemd 托管（开机自启/崩溃拉起/JVM 调参） |
| [docs/zh/04](docs/zh/04-frp.md) | FRP 内网穿透 + 语音聊天独立 UDP 隧道的大坑 |
| [docs/zh/05](docs/zh/05-backup-monitor.md) | 每 2 小时零停机热备份（三道安全网）+ glances 监控 |
| [docs/zh/06](docs/zh/06-mods-whitelist.md) | Mod 管理流程 + 离线服 UUID 白名单大坑 |
| [docs/zh/07](docs/zh/07-operations.md) | Chunky 预生成、数据包、踩坑速查表 |

English versions: [docs/en/](docs/en/)（English mirror）

## 模板与脚本

- `templates/systemd/` — minecraft / 备份 service+timer / natfrp / glances 单元模板，注释里写明每道安全网
- `templates/server.properties.example` — 关键项带注释的示例配置
- `scripts/` — RCON 小工具、备份中文广播、Chunky 夜间接力器
- `datapacks/clear-items/` — 开箱即用的定时清掉落物数据包（只清 60 秒前的掉落物）

## 快速开始

1. 按 [01](docs/zh/01-hardware-os.md) 准备系统 → [02](docs/zh/02-mc-server.md) 装服务端 → [03](docs/zh/03-systemd.md) systemd 托管
2. [04](docs/zh/04-frp.md) 打通公网 → [05](docs/zh/05-backup-monitor.md) 上备份和监控
3. 加好友前读一遍 [06](docs/zh/06-mods-whitelist.md) 的 UUID 坑，能省你一晚上

## 安全须知

本仓库所有密钥均为占位符（`<YOUR_...>`）。frp 访问密钥、RCON 密码等只放你自己的板上，**永远不要**提交进仓库。

---

<a name="english"></a>
## English

A complete, field-tested recipe for running a Minecraft Fabric server 24/7 on an ARM single-board computer (example: Rockchip RK3576): systemd wrapping, zero-downtime hot backups, FRP tunneling, monitoring, and a pitfall cheat-sheet. Follow `docs/en/` from zero to a public server. Works on x86 mini-PCs / NAS too.

| Doc | Contents |
|---|---|
| [docs/en/01](docs/en/01-hardware-os.md) | Hardware & OS prep |
| [docs/en/02](docs/en/02-mc-server.md) | Fabric server install + server.properties explained |
| [docs/en/03](docs/en/03-systemd.md) | systemd wrapping & JVM tuning |
| [docs/en/04](docs/en/04-frp.md) | FRP tunneling + the voice-chat UDP pitfall |
| [docs/en/05](docs/en/05-backup-monitor.md) | 2h zero-downtime hot backups (3 safety nets) + glances |
| [docs/en/06](docs/en/06-mods-whitelist.md) | Mod management + the offline-mode UUID pitfall |
| [docs/en/07](docs/en/07-operations.md) | Chunky pregen, datapack, pitfall cheat-sheet |

Quick start: [01](docs/en/01-hardware-os.md) → [02](docs/en/02-mc-server.md) → [03](docs/en/03-systemd.md) → [04](docs/en/04-frp.md) → [05](docs/en/05-backup-monitor.md).

## Security note

Every secret in this repo is a placeholder (`<YOUR_...>`). Keep real frp access keys and RCON passwords on your own machine — never commit them.

## License

[MIT](LICENSE)
