# 09 · Performance (RK3576 field data)

All numbers come from a real Rockchip RK3576 board (8 cores: 4×A72 + 4×A53,
4GB RAM, eMMC, no swap) that has been running this setup since Sept 2026. Use them to pick
hardware and set expectations; scale accordingly for other boards/PCs.

## 1. Resource usage (daily operation, 3-5 players online)

| Item | Measured | Notes |
|---|---|---|
| Total RAM | 3.8 GB | with desktop disabled (doc 01, frees ~300MB) |
| System + all services resident | ~2.2 GB, ~1.6 GB available | MC, frp, glances, etc. |
| MC server process RSS | ~1.9 GB | JVM heap cap 2G (doc 03) — runs right at the line |
| Load average | 0.8-1.3 | 8 cores mostly idle; CPU is not the bottleneck |
| Temperature | 45-62°C (passive cooling) | add heatsinks/a fan for hot summers |
| Disk | 23G / 56G used (system + world + backups) | world ~3.8G + backups 2.8G×4 |

**Takeaway**: 4GB RAM is the comfortable floor (don't try 2GB — JVM 2G + OS
won't fit); `view-distance=8 / simulation-distance=6` are the right values
for this memory class.

## 2. Gameplay

- 3-5 concurrent players on vanilla clients over the FRP tunnel: normal
  latency, no regular lag spikes
- With performance mods (Lithium/C2ME etc., see doc 06) ticks stay stable
- `pause-when-empty-seconds=60`: the whole server freezes when empty, resumes on join

## 3. Chunky pregeneration speed (the most CPU-hungry workload)

| Task | Size | Time | Rate |
|---|---|---|---|
| The End radius 3000 | 142,129 chunks | 36 min | peak ~62 chunks/s |
| Overworld radius 5000 | ~390k chunks | finished overnight | world size ~3.8 GB |

## 4. Backup duration

A hot backup compresses to 2.8 GB in about **4 minutes**, server never stops
(doc 05) — players at most notice slight lag with an in-game warning.

## 5. Power & power-cut recovery

- The board has no whole-system power meter (the 5V/0A in `sensors` is the
  OTG output port — don't trust it). Estimated from kernel energy-model tables
  plus utilization: **~3.5-4.5 W with 3 players** — pennies a month, which is
  exactly why an SBC makes a great home 24/7 server
- NPU pitfall: the BSP devfreq governor reports fake utilization (always
  100%), parking the idle NPU at high frequency. Pin the NPU governor to
  powersave at boot
- Power-cut self-healing (verified): auth recovers, frp reconnects, MC
  auto-starts, the backup timer's boot guard skips the clock-jump window —
  zero manual steps

## 6. When to upgrade

- Available RAM chronically < 500MB, or you want `view-distance≥10`: get an
  8GB board or add swap (SD-card swap wears out fast — be careful)
- Frequent 300k+ chunk pregeneration: move to an x86 mini-PC (N100 class), Chunky gets several× faster
- 10+ regular players: the RK3576 copes but the experience degrades — get a real server
