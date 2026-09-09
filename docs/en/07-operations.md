# 07 · Daily Ops & Pitfall Cheat-Sheet

## 1. Chunky pregeneration

Essential for big render distances on small devices: pregenerate chunks so exploration never stutters.

```bash
python3 scripts/mc-rcon.py "chunky world minecraft:overworld"
python3 scripts/mc-rcon.py "chunky radius 5000"
python3 scripts/mc-rcon.py "chunky start"
# progress reports every 20s in the log
python3 scripts/mc-rcon.py "chunky quiet 20"
```

**#1 pitfall**: stopping/restarting the server puts a running Chunky task into
**paused** state and it will NOT auto-resume (it once sat silently for 3 hours).
Recover with `chunky continue` (`chunky start` replies "already started").

Unattended overnight chaining: [`scripts/chunky-sequence.py`](../../scripts/chunky-sequence.py)
watches the log for the finish marker, then fires the next task via RCON.

Field reference (RK3576): overworld radius 5000 ≈ 390k chunks, ~3.8GB world;
the_end radius 3000 (142k chunks) in 36 min, peak ~62 cps.

## 2. Item-clearing datapack (ready to use)

[`datapacks/clear-items/`](../../datapacks/clear-items): every 10 minutes —
yellow warning → 60s later clear only items that have existed for 60+ seconds
(Age≥1200 ticks; freshly dropped items are safe) → gray confirmation.
Install: copy into `world/datapacks/` and restart the server.

- Manual run: `function clear_items:exec`
- Probe: `scoreboard players get #lastclear ci_age`
- ⚠️ `/reload` does not re-run load-tag functions on 26.2 — restart to apply changes
- ⚠️ `schedule` accepts only `t/s/d` (writing `9m` fails to load; use `540s`)

## 3. RCON notes

- Use `mcstatus` for status checks, never a hand-rolled ping
- Chinese text to console requires JSON text + unicode escaping (see backup-notify)
- Test entities summoned via RCON vanish instantly? The command source is near
  spawn with chunks unloaded. `forceload add 0 0` first, use NoGravity + absolute
  coords, then `forceload remove all`.

## 4. Pitfall cheat-sheet

| Symptom | Cause | Fix |
|---|---|---|
| World stops auto-saving after backup | save-on never sent | trap EXIT fallback; verify pairs via `Automatic saving` in log |
| Unreachable ~5 min after power loss | RTC-less clock jump + Persistent timer catch-up | ExecCondition uptime≥900s guard in backup unit |
| Old SSH port still open after change | Ubuntu ssh.socket activation | `systemctl restart ssh.socket` + daemon-reload |
| glances web page blank | apt build missing glances.js | pip `glances[web]`, ExecStart → /usr/local/bin/glances |
| Chunky not running after restart | persistent paused state | RCON `chunky continue` |
| Whitelisted player rejected | offline vs premium UUID (doc 06) | compute offline UUID, fix whitelist.json, reload |
| Voice chat dead silent | voice_host unset (doc 04) | set voice_host=remote:port in voicechat-server.properties |
| Datapack /reload no effect | 26.2 /reload skips load tag | restart server |
| schedule 9m fails to load | no `m` unit; pack_format cap | use 540s; check pack_format (81 on 26.2) |
| Scheduled functions idle when empty | `pause-when-empty-seconds=60` | expected; set 0 temporarily to test |
| Server refuses to start after mod install | missing dependency | check Modrinth Dependencies |
| SSH suddenly Permission denied | sshd rate limiting | wait 60-90s |

## 5. After a power cut

Verified self-healing: natfrp reconnects, minecraft auto-starts, backup guard
skips the boot window. Quick check afterwards:

```bash
mcstatus <PUBLIC_ADDR> status
systemctl --failed
ls -lt /opt/mcserver/backups | head -3
```
