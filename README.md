# rk3576-mc-deploy

在 ARM 开发板（示例：泰山派 RK3576）上 24/7 运行 Minecraft Fabric 服务器的一整套部署方案：systemd 托管、零停机热备份、FRP 内网穿透、监控与踩坑速查。照着 `docs/` 走即可从零复刻。x86 小主机/NAS 同样适用。

[English](#english) | 中文

> **⚠️ 请先读我：作者是新手，本文仅供参考**
>
> 我不是专业运维，这套东西是我边查边踩坑攒出来的个人记录，能跑，但不代表是最佳实践。其中不少操作涉及 `systemctl`、SSH 配置、防火墙/内网穿透等系统级改动，**操作不当可能导致系统无法远程登录、数据丢失或安全暴露**。
>
> 请务必：① 动手前看懂每条命令再执行，不确定就先查；② 先在自己可折腾的环境试，别直接上主力设备；③ 改配置前备份原文件；④ 以官方文档为准，本文只能当参考路线，不要全信。
>
> 另外要坦白：**本文档的部署流程本身未经完整验证**——它只在我自己这一台板子上跑通过，没有在干净机器上由第三方照着走一遍。步骤之间可能有缺漏、依赖可能随版本变化。如果你照着做卡在某一步，那很可能是文档的问题而不是你的问题，欢迎提 issue 告诉我。

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
| [docs/zh/08](docs/zh/08-campus-network.md) | 校园网（锐捷 eportal）自动认证，5 分钟自愈 |
| [docs/zh/09](docs/zh/09-performance.md) | RK3576 实测性能：内存/温度/预生成速度/功耗 |

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

> **⚠️ Read this first: the author is a beginner — don't trust this blindly**
>
> I'm not a professional sysadmin. This is a personal field-notes project assembled through trial and error. It works for me, but it is not necessarily best practice. Many steps involve system-level changes (`systemctl`, SSH config, tunneling/firewall) where a mistake can lock you out of your machine, lose data, or expose you to the internet.
>
> Please: ① understand every command before running it; ② experiment on a disposable device first, not your main machine; ③ back up config files before editing; ④ treat official documentation as the authority — this guide is a reference route, not gospel.
>
> One more honest admission: **the guide itself is unverified as a whole** — it has only ever been walked through on my own single board, never followed end-to-end by someone else on a clean machine. Steps may have gaps, dependencies may have moved. If you get stuck, it may well be the docs' fault, not yours — please open an issue.

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
| [docs/en/08](docs/en/08-campus-network.md) | Campus network (Ruijie eportal) auto-login, 5-min self-healing |
| [docs/en/09](docs/en/09-performance.md) | RK3576 field performance: RAM, temps, pregen speed, power |

Quick start: [01](docs/en/01-hardware-os.md) → [02](docs/en/02-mc-server.md) → [03](docs/en/03-systemd.md) → [04](docs/en/04-frp.md) → [05](docs/en/05-backup-monitor.md).

## Security note

Every secret in this repo is a placeholder (`<YOUR_...>`). Keep real frp access keys and RCON passwords on your own machine — never commit them.

## License

[MIT](LICENSE)
