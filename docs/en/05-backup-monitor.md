# 05 · Hot Backup & Monitoring

Design goal: **zero-downtime** backups, players never notice; belt-and-suspenders so the world never silently corrupts.

## 1. How hot backup works

`save-off` (freeze world writes) → `save-all flush` → `tar` (server keeps running; changes made during those minutes aren't in the snapshot) → `save-on`.

Templates: [`templates/systemd/minecraft-backup.service`](../../templates/systemd/minecraft-backup.service) + [`.timer`](../../templates/systemd/minecraft-backup.timer).

## 2. Three safety nets (born from real incidents — keep them)

1. **Boot guard `ExecCondition`**: skip when uptime < 900s. On RTC-less boards a
   clock jump after power loss makes the Persistent timer think it "missed" a
   slot and fire immediately — it once stopped the freshly booted server,
   packed it for ~4.5 min, and started it again ("unreachable ~5 min after boot").
2. **Disk guard**: skip when free space < 6G. A full disk = world write failures.
3. **`trap EXIT` fallback `save-on`**: guarantee auto-save is re-enabled on any
   exit path. **A missed save-on = the world silently stops auto-saving** —
   the #1 risk of this whole mechanism.

Verify the pair: `grep 'Automatic saving'` in the server log.

## 3. Other details

- Every 2 hours (`OnCalendar=*-*-* 00/2:00:00`), keep 4 copies ≈ 8h history,
  max data-loss window 2h. Tune to your disk budget.
- **In-game Chinese broadcasts must go through the `backup-notify` script**
  (in scripts/): the tellraw payload is unicode-escaped inside Python. Inline
  tellraw in the unit gets mangled by systemd/shell quoting — don't regress.
- Shell variables in units must be written `$$` (systemd eats single `$VAR`).
- After changing `OnCalendar`, restarting the timer immediately runs the "missed"
  slot (Persistent behavior). Harmless, but wait ~4 min for it to finish before
  concluding anything is stuck.

## 4. Monitoring: glances

Loopback-only, never exposed. Template: [`templates/systemd/glances-web.service`](../../templates/systemd/glances-web.service).

```bash
# Ubuntu's apt glances serves a blank page (missing glances.js). Use pip:
sudo pip3 install --break-system-packages --ignore-installed "glances[web]"
# ExecStart must point at /usr/local/bin/glances (the pip one)
sudo systemctl enable --now glances-web.service
```

View via SSH tunnel:

```bash
ssh -L 61208:127.0.0.1:61208 -p 22222 user@board
# open http://localhost:61208/
```

Deeper performance work: install the [spark](https://modrinth.com/mod/spark) mod,
use `/spark tps` and `/spark profiler` in game.
