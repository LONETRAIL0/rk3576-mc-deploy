# 05 · 热备份与监控

设计目标：**服务器不停机**备份，玩家无感；宁可机制繁琐也要保证世界不静默损坏。

## 1. 热备份原理

`save-off` 冻结世界落盘 → `save-all flush` 刷到磁盘 → `tar` 打包（此时服务器照常跑，只是这几分钟的世界改动不在备份里）→ `save-on` 恢复。

模板：[`templates/systemd/minecraft-backup.service`](../../templates/systemd/minecraft-backup.service) + [`.timer`](../../templates/systemd/minecraft-backup.timer)。

## 2. 三道安全网（实测踩出来的，别删）

1. **开机守卫 `ExecCondition`**：uptime < 900s 直接跳过。无 RTC 板子断电重启后
   时钟跳变，Persistent timer 会误判"错过排程"立刻补跑——曾把刚启动好的
   服务器停了打包 4 分半再拉起，表现即"断电后 ~5 分钟不可达"。
2. **磁盘守卫**：剩余 < 6G 跳过。备份包 ~3G×4 份，塞满盘 = 世界写入失败。
3. **`trap EXIT` 兜底 `save-on`**：任何路径退出都保证恢复自动保存。
   **漏发 save-on = 世界静默停止自动保存**，是这套机制的头号风险。

验证 save-on/off 配对：服务端日志 grep `Automatic saving`。

## 3. 其他细节

- 每 2 小时一次（`OnCalendar=*-*-* 00/2:00:00`），保留 4 份 ≈ 8 小时历史，
  数据丢失窗口最长 2h。按磁盘预算调整。
- **中文进服广播只准走 `backup-notify` 脚本**（scripts/ 里有）：tellraw 参数在
  Python 内拼 unicode 转义。单元里内联 tellraw 中文会被 systemd/shell 多层
  引号转义搞翻车，勿回退。
- 单元里写 shell 变量必须 `$$`（systemd 会空展开 `$VAR`）。
- 改 `OnCalendar` 后 restart timer 会立刻补跑一次"错过的"档位（Persistent 行为），
  无害，但验证时要等备份跑完（~4 分钟）再下结论。
- ⚠️ `save-off` 期间服务器**不会**停止运行，玩家照常玩，只是这几分钟改动不进备份。

## 4. 监控：glances

只监听本机，不暴露公网。模板：[`templates/systemd/glances-web.service`](../../templates/systemd/glances-web.service)。

```bash
# Ubuntu apt 版 glances 网页是空白页（缺编译产物 glances.js），必须 pip 装：
sudo pip3 install --break-system-packages --ignore-installed "glances[web]"
# ExecStart 指向 /usr/local/bin/glances（pip 版），不是 /usr/bin/glances
sudo systemctl enable --now glances-web.service
```

查看（SSH 隧道转发）：

```bash
ssh -L 61208:127.0.0.1:61208 -p 22222 user@board
# 浏览器打开 http://localhost:61208/
```

性能监控进阶：装 [spark](https://modrinth.com/mod/spark) mod，游戏内 `/spark tps`、`/spark profiler` 看卡顿归因。
