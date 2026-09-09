# 06 · Mod 管理与白名单

## 1. 装 mod 的标准流程

1. PC 上从 [Modrinth](https://modrinth.com) 下载，**核对三件事**：MC 版本匹配、
   loader 是 Fabric、标签是 **Server 端可用**（纯服务端装，客户端不用装才能进）
2. 传到板上 `server/mods/`
3. `sudo systemctl restart minecraft`
4. 验证：启动日志出现 `Done` 且 0 ERROR、mod 数符合预期、`mc-rcon.py list` 正常

```bash
python3 /opt/mcserver/mc-rcon.py list
```

## 2. 前置依赖坑（头号翻车点）

Serilum/Fuzs 系 mod 普遍有前置依赖库（collective / ForgeConfigAPIPort /
PuzzlesLib 等），**缺前置 Fabric loader 会直接拒启**。装之前在 Modrinth 页面
查 Dependencies，把前置一起装。

装新 mod（尤其批量装）前先备份整个 mods 目录：
`cp -r server/mods server/mods.bak-$(date +%m%d)`，翻车可整目录回滚。

## 3. 本仓库作者在用的服务端 mod（参考）

性能：Lithium、C2ME、Krypton、FerriteCore、ModernFix、ServerCore、VMP、ScalableLux
QoL：Essential Commands（/home /tpa /back /rtp）、Viper Vein Miner（连锁挖矿）、
Sit!、Leaves Be Gone、RightClickHarvest、Double Doors、Death Count
玩法：Better Combat + Player Animation Library、Traveler's Backpack、
Skin Restorer（离线服拉正版皮肤）、Simple Voice Chat
防破坏：Convenient mobGriefing（逐条关闭苦力怕/凋灵等破坏，保留村民种田）
监控：spark

## 4. 权限与白名单

- op 只给服主本人；新玩家先 `whitelist add`，非必要不给 op
- 离线服（online-mode=false）下 Essential Commands 保持
  `use_permissions_api=false` 默认即可：非 op 玩家基础命令可用、作弊命令不可见，
  无需 LuckPerms

## 5. 离线服 UUID 大坑（必读）

**症状**：明明 `whitelist add 玩家名` 成功了，玩家进服却被拒 not whitelisted。

**原因**：离线服的 `whitelist add` **偶发**存入 Mojang 正版档案 UUID（名字恰好
是正版账号，或查询串了），而玩家进服时按名字算的是离线 UUID，两者不符。

**修复流程**（已实机演练验证）：

1. PC 上算玩家离线 UUID：
   ```bash
   python -c "import hashlib,uuid;h=bytearray(hashlib.md5(b'OfflinePlayer:玩家名').digest());h[6]=(h[6]&0xf)|0x30;h[8]=(h[8]&0x3f)|0x80;print(uuid.UUID(bytes=bytes(h)))"
   ```
2. 对比板上 `server/whitelist.json` 里该条的 uuid；不符则手工改成离线 UUID
3. `whitelist reload` 即时生效

**判别技巧**：`whitelist add` 后服务器反馈/存储的名字大小写变了（比如你输
全大写、它存成首字母大写）＝ 撞上正版账号了，此坑实锤。

**注意**：对这类名字**不要**用 RCON 的 op/deop/ban 等名字类命令（同样会解析
到正版 UUID），改权限直接编辑 `ops.json` / `whitelist.json` 后
`whitelist reload`。另外 ops.json 运行中外改不即时生效，须重启服务器加载；
但关服不会用内存态覆盖你的外部修改，文件改动可安全保留。
