# 04 · FRP 内网穿透

没有公网 IP（校园网/家宽）时的标准解法：内网穿透把服务端映射到公网。
本文用樱花FRP（natfrp）示例，其他 frp 服务商同理。

## 1. 注册与建隧道

1. 注册 [sakurafrp.com](https://www.natfrp.com)，拿到**访问密钥**（只在板上配，勿外传）
2. 建隧道：
   - 游戏：TCP，本地端口 25565
   - 语音（可选）：UDP，本地端口 24454（Simple Voice Chat 用）
3. 记下分配的远程地址/端口

## 2. 安装 frpc 并做成服务

frpc 的 arm64 版本从服务商文档给的地址下载（注意老版本号路径会 404，以 API/文档为准）：

```bash
sudo mkdir -p /opt/natfrp && cd /opt/natfrp
# 下载并 chmod +x frpc
```

单元模板见 [`templates/systemd/natfrp.service`](../../templates/systemd/natfrp.service)，核心一行：

```ini
ExecStart=/opt/natfrp/frpc -f <访问密钥>:<游戏隧道ID>,<语音隧道ID>
```

```bash
sudo systemctl enable --now natfrp.service
```

## 3. 验证

PC 上装 `mcstatus` 验证（**不要**手写 MC ping 协议，新版本握手严格会被直接断连）：

```bash
pip install mcstatus
mcstatus <远程地址>:<远程端口> status
```

## 4. 语音聊天隧道的大坑（实测）

Simple Voice Chat 服务端默认让客户端连 `游戏服地址:24454`。走 FRP 后
**远程端口 ≠ 本地端口**，必须在服务端
`config/voicechat/voicechat-server.properties` 里显式设置：

```properties
voice_host=<远程地址>:<语音远程端口>
```

漏设的表现：语音进服后全员哑巴，没有报错。双端装 mod 并重启后生效。

端到端验证土法（板上无 tcpdump 时）：PC 向语音远程端口发个 UDP 包，
对比板上 `/proc/net/snmp` 的 `Udp InDatagrams` 增量。

## 5. 稳定性备注

- `Restart=on-failure` 已在单元里；网络波动会自动重连
- 重启 frpc 时服务商端可能误报"隧道已在线请勿重复开启"，停几秒再启即可
- 单元文件里只有访问密钥是敏感信息，**永远不要**把它写进任何文档/截图/仓库
