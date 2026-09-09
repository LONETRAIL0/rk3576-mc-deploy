# 07 · 日常运维与踩坑速查

## 1. Chunky 预生成

小设备跑大半径世界的必备：提前生成区块，玩家探索不卡。

```bash
# 经 RCON 操作（mc-rcon.py）
python3 scripts/mc-rcon.py "chunky world minecraft:overworld"
python3 scripts/mc-rcon.py "chunky radius 5000"
python3 scripts/mc-rcon.py "chunky start"
# 开进度报告（每 20 秒一条日志）
python3 scripts/mc-rcon.py "chunky quiet 20"
```

**头号坑**：停服/重启会把运行中的任务置为 paused 持久态，重启后**不会**
自动续跑（曾静默挂 3 小时）。恢复用 `chunky continue`
（`chunky start` 会提示 already started，语义不对）。

无人值守夜间接力：[`scripts/chunky-sequence.py`](../../scripts/chunky-sequence.py)
盯日志等上一任务完成标记，自动点火下一任务。

实测参考（RK3576，4 核 A72 + 4 核 A53）：主世界半径 5000 ≈ 39 万区块一夜跑完，
世界 ~3.8GB；末地半径 3000（14 万区块）36 分钟，峰值 ~62 cps。

## 2. 清掉落物数据包（开箱即用）

[`datapacks/clear-items/`](../../datapacks/clear-items)：每 10 分钟循环——
黄色预告 → 60 秒后只清**存在超过 60 秒**的掉落物（按 Age≥1200 tick 判定，
新掉的不误杀）→ 灰色确认。装法：拷进 `world/datapacks/` 后重启服务器。

- 手动触发：`function clear_items:exec`
- 探针：`scoreboard players get #lastclear ci_age` 读上次清理时的 gametime
- ⚠️ 改 load 函数后 `/reload` 不生效（26.2 的 /reload 不重执行 load 标签），
  必须重启服务器
- ⚠️ `schedule` 只认 `t/s/d`，没有 `m` 单位（写 9m 会加载失败，用 540s）

## 3. RCON 使用须知

- 验证服务器状态用 `mcstatus`，别手写 ping 协议（新版本握手严格，会被断连）
- 给控制台发**中文**必须走 JSON text + unicode 转义（backup-notify 即此法），
  RCON 直传中文会乱码
- RCON 召唤测试实体后立即消失？命令源在出生点附近且区块未加载。
  先 `forceload add 0 0`，实体加 NoGravity + 绝对坐标，测完 `forceload remove all`

## 4. 踩坑速查表

| 症状 | 原因 | 解法 |
|---|---|---|
| 备份后世界不再自动保存 | save-on 没发出（脚本中途死） | 单元 trap EXIT 兜底；日志 grep `Automatic saving` 验配对 |
| 断电重启后 ~5 分钟不可达 | 无 RTC 时钟跳变 + Persistent timer 补跑备份 | 备份单元加 ExecCondition uptime≥900s 守卫 |
| 改 SSH 端口后旧端口还在 | Ubuntu ssh.socket 激活模式 | `systemctl restart ssh.socket` + daemon-reload |
| glances 网页空白 | apt 版缺 glances.js | pip 装 `glances[web]`，ExecStart 指 /usr/local/bin/glances |
| 重启后 Chunky 不跑 | paused 持久态 | RCON `chunky continue` |
| whitelisted 玩家被拒进服 | 离线 UUID vs 正版 UUID（见 06 篇） | 算离线 UUID 改 whitelist.json + reload |
| 语音聊天全员哑巴 | voice_host 没设（见 04 篇） | voicechat-server.properties 设 voice_host=远程地址:远程端口 |
| 数据包 /reload 不生效 | 26.2 /reload 不重跑 load 标签 | 重启服务器 |
| schedule 9m 加载失败 | 无 m 单位；pack_format 上限 | 用 540s；核对 pack_format（26.2 上限 81） |
| 没人时调度函数不跑 | `pause-when-empty-seconds=60` 空载暂停 | 预期行为；测试时临时改 0 |
| mod 装完服务器拒启 | 缺前置依赖 | Modrinth 查 Dependencies，前置一起装 |
| 短时间多次 SSH 被拒 | sshd 限流 | 等 60-90 秒重试 |

## 5. 断电恢复清单

实测正常的断电自愈：SSH/服 → natfrp 自动重连 → minecraft 自启 → 备份守卫跳过
开机窗口。恢复后顺手验证：

```bash
mcstatus <公网地址> status
systemctl --failed
ls -lt /opt/mcserver/backups | head -3
```
