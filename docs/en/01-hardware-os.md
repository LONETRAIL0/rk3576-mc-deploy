# 01 · Hardware & OS Prep

Goal: turn an ARM single-board computer (example: Rockchip RK3576 board, 4GB RAM, arm64) into a 24/7 headless Linux server. Old x86 PCs / NAS work too — skip board-specific steps.

## 1. Hardware

- ARM SBC (4GB RAM minimum; eMMC preferred over SD card)
- 5V/3A+ PSU
- Wired Ethernet strongly recommended (WiFi drops = whole server drops)

## 2. System & Base Config

Flash Ubuntu 24.04 (arm64 server preferred). Field-tested tips:

- **Disable the desktop** to free ~300MB RAM:
  ```bash
  sudo systemctl set-default multi-user.target
  sudo systemctl isolate multi-user.target
  ```
  Keep lightdm files intact as a rescue channel: `sudo systemctl isolate graphical.target` brings the desktop back when you need a monitor.
- **Change the SSH port** (port 22 gets hammered by internet scanners):
  after editing `Port` in `/etc/ssh/sshd_config`, Ubuntu runs ssh in socket-activation mode — `systemctl reload ssh` does NOT work, you need:
  ```bash
  sudo systemctl daemon-reload && sudo systemctl restart ssh.socket
  ```
- **Time sync**: RTC-less boards boot with a wrong clock. Install chrony and enable it; clock jumps affect the backup timer (see the guard in doc 05).
- **Key-based login**: `ssh-copy-id -p 22222 user@board`, plus a `~/.ssh/config` alias.

## 3. Directory Convention

```
/opt/mcserver/          # everything MC-related
├── server/             # the server itself (jar, mods, world, configs)
├── backups/            # hot backup output
├── mc-rcon.py          # RCON helper (in scripts/)
├── backup-notify       # backup broadcast (in scripts/)
└── chunky-sequence.py  # pregen sequencer (optional)
```

## 4. Verify

```bash
ssh -p 22222 user@board uname -m      # expect aarch64
ssh -p 22222 user@board free -h       # confirm desktop is off
```
