# 01 · 硬件与系统准备

目标：一块 ARM 开发板（示例：泰山派 RK3576，4GB 内存，arm64）跑成一台 24/7 无头 Linux 服务器。x86 旧电脑/NAS 同样适用，跳过板子特有步骤即可。

## 1. 硬件清单

- ARM 开发板（4GB 内存起步，eMMC 或高速 TF 卡装系统；eMMC 更稳）
- 5V 电源（建议 3A 以上，跑服 + 外设不要用边缘充电头）
- 网线（强烈建议有线，WiFi 掉线 = 全服掉线）

## 2. 系统与基础配置

烧录 Ubuntu 24.04（arm64 server 版优先）。几个实测有用的点：

- **关掉桌面省内存**（约 300MB）：
  ```bash
  sudo systemctl set-default multi-user.target
  sudo systemctl isolate multi-user.target
  ```
  不要删 lightdm 相关文件，保留"手动救生通道"：需要接显示器操作时
  `sudo systemctl isolate graphical.target` 一键拉起桌面。
- **SSH 固定端口**（默认 22 会被全网扫描器轰炸，改高位端口如 22222）：
  改 `/etc/ssh/sshd_config` 的 `Port` 后，Ubuntu 是 ssh.socket 激活模式，
  `systemctl reload ssh` **不生效**，必须：
  ```bash
  sudo systemctl daemon-reload && sudo systemctl restart ssh.socket
  ```
- **时间同步**：无 RTC 的板子断电重启后时钟会错，装 chrony 并确保 enabled；
  时钟跳变会影响后面备份 timer（见 05 篇的守卫设计）。
- **密钥登录**：PC 生成密钥对，`ssh-copy-id -p 22222 user@board`，
  在 `~/.ssh/config` 里配好别名（IP 变了只需改一处）。

## 3. 目录约定

全文统一：

```
/opt/mcserver/          # 一切 MC 相关的家
├── server/             # 服务端本体（jar、mods、world、配置）
├── backups/            # 热备份输出
├── mc-rcon.py          # RCON 小工具（scripts/ 里有）
├── backup-notify       # 备份广播（scripts/ 里有）
└── chunky-sequence.py  # 预生成接力器（可选）
```

## 4. 验证

```bash
ssh -p 22222 user@board uname -m      # 应输出 aarch64
ssh -p 22222 user@board free -h       # 看内存，确认桌面已关
```
