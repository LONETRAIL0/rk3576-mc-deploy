# 02 · Fabric Server Install

MC 26.2 + Fabric as the example (any version works the same). Goal: a **server-side-only** setup — friends join with vanilla clients.

## 1. Install Java

```bash
sudo apt install openjdk-21-jre-headless   # match your MC version
java -version
```

## 2. Get the server jar

Either use a modpack installer (e.g. [mrpack-install](https://github.com/sjaxel/mrpack-install)) for packs like Adrenaline, or grab the official Fabric server launcher:

```bash
cd /opt/mcserver/server
java -jar fabric-server-*.jar nogui
# First run fails and generates eula.txt
echo "eula=true" > eula.txt
```

## 3. server.properties Essentials

Copy-ready example: [`templates/server.properties.example`](../../templates/server.properties.example).

| Key | Value | Why |
|---|---|---|
| `online-mode` | `false` | Required for non-premium players; identity = name only, see the UUID pitfall in doc 06 |
| `white-list` / `enforce-whitelist` | `true` | Your only gate once exposed to the internet |
| `view-distance` / `simulation-distance` | `8` / `6` | Performance lifeline on small boards |
| `pause-when-empty-seconds` | `60` | Freezes ticks when empty (saves power). ⚠️ datapack `schedule` functions won't run while empty — expected |
| `enable-rcon` + `rcon.password` | on | Backups and ops depend on it |
| `sync-chunk-writes` | `false` | Less random write pressure on eMMC/SD |

⚠️ Voice chat over an FRP tunnel also needs `voice_host` — see doc 04.

## 4. Manual start check

```bash
java -Xms1024M -Xmx2048M ... -jar fabric-server-*.jar nogui
# Wait for "Done (xx.xxxs)! For help, type "help""
```

Then wrap it in systemd (doc 03).
