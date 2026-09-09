# 03 · systemd 托管

让服务端开机自启、崩溃自动拉起、停服走正规保存流程。模板：[`templates/systemd/minecraft.service`](../../templates/systemd/minecraft.service)。

## 安装

```bash
sudo cp templates/systemd/minecraft.service /etc/systemd/system/
# 核对 ExecStart 里的 jar 文件名和内存参数后：
sudo systemctl daemon-reload
sudo systemctl enable --now minecraft.service
```

## JVM 参数说明（4GB 板实测）

- `-Xms1024M -Xmx2048M`：堆 2G 上限，给系统和系统缓存留空间
- G1 全套低停顿参数：整合包（Lithium/C2ME 等）配合下 3-5 人在线 tick 稳定
- `Restart=on-failure` + `RestartSec=15`：崩溃 15 秒后自动拉起
- `TimeoutStopSec=120`：给世界保存留够时间，避免被 SIGKILL 截断

## 常用操作

```bash
systemctl status minecraft          # 状态
journalctl -u minecraft -f          # 实时日志
sudo systemctl restart minecraft    # 重启（会打断 Chunky 任务，见 07 篇）
```

## 通用改单元姿势

1. `sudo cp /etc/systemd/system/xxx.service{,.bak-$(date +%m%d)}` 先备份
2. 改完 `daemon-reload` → `restart`
3. **实际验证**（`systemctl status` / `journalctl` / 游戏内实测），不许口头宣称成功

## 无 RTC 板子的提醒

断电重启后时钟错误会导致 Persistent 型 timer 误触发（备份在开机 5 分钟内
突然跑起来把服务停了又打的怪现象）。解法见 05 篇备份单元里的
`ExecCondition` uptime 守卫。
