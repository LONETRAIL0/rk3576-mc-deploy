# 02 · Fabric 服务端安装

以 MC 26.2 + Fabric 为例（年式版本号，其他版本流程相同）。目标是**纯服务端**：朋友用原版客户端就能进。

## 1. 装 Java

```bash
sudo apt install openjdk-21-jre-headless   # 按你的 MC 版本选 JRE 大版本
java -version
```

## 2. 获取服务端 jar

推荐用 mrpack 整合包安装器（如 [mrpack-install](https://github.com/sjaxel/mrpack-install)）直接装 Adrenaline 这类服务端整合包，或手动从 Fabric 官网拿 server launcher jar：

```bash
cd /opt/mcserver/server
# 把下载好的 fabric-server-...jar 放进来
java -jar fabric-server-mc.<版本>-loader.<版本>-launcher.<版本>.jar nogui
# 首次启动会失败并生成 eula.txt
echo "eula=true" > eula.txt
```

## 3. server.properties 关键项

完整可抄示例见 [`templates/server.properties.example`](../../templates/server.properties.example)。逐条说明：

| 项 | 建议值 | 原因 |
|---|---|---|
| `online-mode` | `false` | 朋友没用正版账号时必须关；代价是身份只看名字，见 06 篇白名单坑 |
| `white-list` / `enforce-whitelist` | `true` | 公网暴露后唯一的门 |
| `view-distance` / `simulation-distance` | `8` / `6` | 小内存板子的性能生命线 |
| `pause-when-empty-seconds` | `60` | 空载冻结 tick 省电。⚠️ 会导致"没人时 schedule/数据包不跑"，属预期行为 |
| `enable-rcon` + `rcon.password` | 开 | 备份/运维全靠它 |
| `sync-chunk-writes` | `false` | TF 卡/eMMC 减少小写入 |

⚠️ 语音聊天走 FRP 隧道时还要设 `voice_host`，见 04 篇。

## 4. 手动启动验证

```bash
java -Xms1024M -Xmx2048M ... -jar fabric-server-*.jar nogui
# 看日志出现 "Done (xx.xxxs)! For help, type "help"" 即成功
```

启动成功再进入 03 篇做成 systemd 服务。
