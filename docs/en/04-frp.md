# 04 · FRP Tunneling

The standard answer when you have no public IP (campus dorm, CGNAT): tunnel your server to the internet. SakuraFrp (natfrp) is the example; other frp providers work the same.

## 1. Create tunnels

1. Register, obtain your **access key** (stays on the board only, never share)
2. Create tunnels:
   - Game: TCP → local port 25565
   - Voice (optional): UDP → local port 24454 (Simple Voice Chat)
3. Note the assigned remote address/port

## 2. Install frpc as a service

Unit template: [`templates/systemd/natfrp.service`](../../templates/systemd/natfrp.service). The core line:

```ini
ExecStart=/opt/natfrp/frpc -f <ACCESS_KEY>:<GAME_TUNNEL_ID>,<VOICE_TUNNEL_ID>
```

```bash
sudo systemctl enable --now natfrp.service
```

## 3. Verify

Use `mcstatus` from your PC (**never** hand-roll the MC ping protocol — strict handshake in new versions drops the connection):

```bash
pip install mcstatus
mcstatus <REMOTE_ADDR>:<REMOTE_PORT> status
```

## 4. The voice-chat tunnel pitfall (field-tested)

Simple Voice Chat clients default to `game-server-address:24454`. Over FRP the
**remote port ≠ local port**, so the server must set it explicitly in
`config/voicechat/voicechat-server.properties`:

```properties
voice_host=<REMOTE_ADDR>:<VOICE_REMOTE_PORT>
```

Symptom if missed: everyone joins, nobody can hear anything, no errors.

E2E check without tcpdump: send a UDP packet at the remote voice port from your
PC and watch `Udp InDatagrams` in the board's `/proc/net/snmp` for the increment.

## 5. Stability notes

- The unit already has `Restart=on-failure`; network blips self-heal
- The provider may report "tunnel already online" right after a frpc restart — wait a few seconds
- The access key is the only secret here. **Never** commit it to any repo/doc/screenshot.
