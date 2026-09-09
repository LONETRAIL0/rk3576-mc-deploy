# 08 · 校园网自动认证

校园网（锐捷 eportal，国内高校最常见）有个致命问题：**认证会过期/掉线**，
而你的服务器 24/7 跑在校园网里。本文的方案是一个 systemd timer 每 5 分钟
自动检查并重登录，实测几个月无人值守稳定运行。

> 适用范围：认证页 URL 里有 `eportal/InterFace.do` 的学校（锐捷标准接口）。
> 深澜 Srun 等其他系统的接口不同，本文脚本不适用，但思路相同。

## 1. 原理

1. `GET http://edge.microsoft.com/captiveportal/generate_204`：返回 204 = 在线，
   直接退出；返回重定向页 = 掉线了
2. 从重定向页里抠出 `queryString`（认证页会把它 JS 包一层，脚本里做了截断清洗——
   不清洗的话尾部会带 `'</script` 导致登录永远失败，这是实测坑）
3. 先 POST `pageInfo` 拿会话 cookie——**必须先走这步**，直接 POST login 会报
   "用户不允许使用本服务"，哪怕账号密码全对（浏览器页面就是先调 pageInfo 的）
4. POST login（字段要做双重 URL 编码，模拟前端 `encodeURIComponent` 两次的行为）
5. 返回 `"result":"success"` 即成功

## 2. 部署

```bash
sudo mkdir -p /opt/campus-auth && cd /opt/campus-auth
sudo cp scripts/campus-auth.py .
sudo cp templates/campus-credentials.example credentials
sudo nano credentials     # 填 4 个值
sudo chmod 600 credentials   # 凭据文件只留板上，root-only
sudo cp templates/systemd/campus-auth.service /etc/systemd/system/
sudo cp templates/systemd/campus-auth.timer /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now campus-auth.timer
```

## 3. 填 credentials（4 个值怎么来）

- `USER_ID`：学号/账号
- `PASSWORD_ENC`：**不是明文密码**。浏览器登录一次校园网，按 F12 打开网络面板，
  找到 `InterFace.do?method=login` 的 POST 请求，把 payload 里 `password` 字段的
  值原样抄过来（脚本带 `passwordEncrypt=true`，门户按编码值校验）
- `SERVICE`：认证页上的服务名下拉选项（如"校园网"）
- `PORTAL_HOST`：掉线状态下随便开个网页，被重定向到的那个内网地址

## 4. 验证与排障

```bash
sudo python3 /opt/campus-auth/campus-auth.py    # 手动跑一次
journalctl -u campus-auth -f
```

实测踩坑速查：

| 症状 | 原因 | 解法 |
|---|---|---|
| natfrp 每 ~11 秒报 TLS 证书错误 | 校园网未认证，HTTPS 被网关劫持 | 先查 campus-auth，修好认证 natfrp 自动恢复 |
| "用户不允许使用本服务" | 三义：服务名不匹配 / 密码编码值错（同密码错的报错）/ MAC 被门户拒绝 | 同一请求从 PC 发一遍，PC 能成就是 MAC 被拒 |
| 换 IP 仍被拒，PC 正常 | 锐捷按 MAC 拒绝（脚本反复失败会触发封禁） | 终极解法：接显示器在板子桌面上手动登录一次，成功后 MAC 限制解除，自动脚本恢复 |
| 板子进了 172.23.x/17 网段、SSH 全断 | 预认证隔离段（只通认证页），认证跟 MAC 走不跟 IP 走 | 用 adb USB 通道操作；认证后回到正常网段，DNS 约有 1 分钟瞬断 |
| queryString 尾部带乱码 | 重定向是 JS 包裹的，尾部混入 `'</script` | 脚本已内置截断清洗，无需处理 |
| 断电重启后第一个 tick 失败 | 无 RTC 时钟跳变 | 预期行为，5 分钟后下一轮恢复 already online |

## 5. 安全提示

凭据文件 `credentials` 权限务必 600 且只放板上——本仓库的脚本、单元、示例
里都不含任何真实账号信息，你自己的 `credentials` 也**永远不要**提交进任何仓库。
