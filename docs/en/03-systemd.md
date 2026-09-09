# 03 · systemd Wrapping

Auto-start on boot, auto-restart on crash, clean shutdown with world saves. Template: [`templates/systemd/minecraft.service`](../../templates/systemd/minecraft.service).

## Install

```bash
sudo cp templates/systemd/minecraft.service /etc/systemd/system/
# Fix the jar filename and memory flags in ExecStart, then:
sudo systemctl daemon-reload
sudo systemctl enable --now minecraft.service
```

## JVM flags (field-tested on a 4GB board)

- `-Xms1024M -Xmx2048M`: 2G heap cap, leave room for OS + page cache
- G1 low-pause set: stable ticks with 3-5 players on a modded server
- `Restart=on-failure` + `RestartSec=15`: auto-restart 15s after a crash
- `TimeoutStopSec=120`: enough time for a clean world save

## Common ops

```bash
systemctl status minecraft
journalctl -u minecraft -f
sudo systemctl restart minecraft    # interrupts Chunky tasks, see doc 07
```

## How to edit units safely

1. Backup first: `sudo cp /etc/systemd/system/xxx.service{,.bak-$(date +%m%d)}`
2. Edit → `daemon-reload` → `restart`
3. **Actually verify** (status / journalctl / in-game). Never claim success untested.

## RTC-less boards

A wrong clock after power loss makes Persistent timers misfire (a backup
suddenly runs 5 minutes after boot and bounces the server). Fix: the
`ExecCondition` uptime guard in the backup unit — see doc 05.
