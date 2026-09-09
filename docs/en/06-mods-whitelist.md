# 06 · Mods & Whitelist

## 1. Standard mod install flow

1. Download from [Modrinth](https://modrinth.com); **check three things**: MC
   version match, Fabric loader, **server-side** tag (server-only mods — clients stay vanilla)
2. Copy to `server/mods/` on the board
3. `sudo systemctl restart minecraft`
4. Verify: log shows `Done` with 0 ERRORs, mod count as expected,
   `mc-rcon.py list` works

## 2. The dependency pitfall (#1 crash cause)

Mods by Serilum/Fuzs almost always require library deps (collective /
ForgeConfigAPIPort / PuzzlesLib / ...). **A missing dep makes Fabric refuse to
start at all.** Check Dependencies on the Modrinth page and install them together.

Back up the mods dir before any change:
`cp -r server/mods server/mods.bak-$(date +%m%d)` — full-dir rollback if it breaks.

## 3. What this repo's author runs (reference)

Performance: Lithium, C2ME, Krypton, FerriteCore, ModernFix, ServerCore, VMP, ScalableLux
QoL: Essential Commands (/home /tpa /back /rtp), Viper Vein Miner, Sit!,
Leaves Be Gone, RightClickHarvest, Double Doors, Death Count
Gameplay: Better Combat + Player Animation Library, Traveler's Backpack,
Skin Restorer, Simple Voice Chat
Mob-griefing control: Convenient mobGriefing (per-mob overrides)
Monitoring: spark

## 4. Permissions & whitelist

- op for the owner only; `whitelist add` everyone else; no casual ops
- With `online-mode=false`, Essential Commands' default
  `use_permissions_api=false` is exactly right: non-ops get basics
  (/home /tpa /rtp /back), cheat commands are invisible. No LuckPerms needed.

## 5. Offline-mode UUID pitfall (must read)

**Symptom**: `whitelist add PlayerName` succeeds, but the player is rejected
with "not whitelisted".

**Cause**: offline-mode `whitelist add` **occasionally** stores the Mojang
premium UUID (name collides with a real account) instead of the offline UUID
computed from the name at join time.

**Fix** (rehearsed end-to-end on a live server):

1. Compute the offline UUID on your PC:
   ```bash
   python -c "import hashlib,uuid;h=bytearray(hashlib.md5(b'OfflinePlayer:PlayerName').digest());h[6]=(h[6]&0xf)|0x30;h[8]=(h[8]&0x3f)|0x80;print(uuid.UUID(bytes=bytes(h)))"
   ```
2. Compare with the uuid in `server/whitelist.json`; fix it if different
3. `whitelist reload` — effective immediately

**Detection trick**: if after `whitelist add` the stored/echoed name's case
changed (you typed ALL-CAPS, it stored Title-case) — you hit a real premium
account. This is the smoking gun.

**Also**: for such names, **don't** use name-based RCON commands (op/deop/ban) —
they resolve to the premium UUID too. Edit `ops.json` / `whitelist.json`
directly, then `whitelist reload`. Note ops.json external edits need a server
restart to load, but shutdown won't overwrite your edits with in-memory state.
