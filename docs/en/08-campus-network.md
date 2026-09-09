# 08 · Campus Network Auto-Login

Campus networks (Ruijie eportal — the most common system in Chinese
universities) expire sessions and drop you offline, while your server needs
to be online 24/7. This recipe: a systemd timer that checks every 5 minutes
and re-authenticates automatically. Field-proven unattended for months.

> Applies to schools whose auth page URL contains `eportal/InterFace.do`
> (standard Ruijie). Other systems (Srun, etc.) use different APIs — the
> approach still applies, the script does not.

## 1. How it works

1. `GET http://edge.microsoft.com/captiveportal/generate_204`: 204 = online,
   exit; a redirect page = offline
2. Extract the `queryString` from the redirect page. The page wraps it in JS —
   the script truncates trailing junk (`'</script`) which otherwise corrupts
   every login attempt (field-tested pitfall)
3. POST `pageInfo` first to get a session cookie — **mandatory**. A bare login
   POST is rejected with "user not allowed to use this service" even with
   correct credentials (the browser always calls pageInfo first)
4. POST login (fields double-URL-encoded, mimicking the frontend's
   `encodeURIComponent` × 2)
5. `"result":"success"` in the response = done

## 2. Deploy

```bash
sudo mkdir -p /opt/campus-auth && cd /opt/campus-auth
sudo cp scripts/campus-auth.py .
sudo cp templates/campus-credentials.example credentials
sudo nano credentials     # fill in 4 values
sudo chmod 600 credentials   # credentials stay on the board only
sudo cp templates/systemd/campus-auth.service /etc/systemd/system/
sudo cp templates/systemd/campus-auth.timer /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now campus-auth.timer
```

## 3. The 4 credential values

- `USER_ID`: your campus account
- `PASSWORD_ENC`: **not your plaintext password**. Log in once from a browser,
  open devtools (F12) → network tab, find the `InterFace.do?method=login`
  POST, and copy its `password` field value verbatim (the script sends
  `passwordEncrypt=true`; the portal validates the encoded form)
- `SERVICE`: the service name shown on the auth page
- `PORTAL_HOST`: the intranet address your browser gets redirected to while offline

## 4. Verify & troubleshoot

```bash
sudo python3 /opt/campus-auth/campus-auth.py
journalctl -u campus-auth -f
```

Field-tested pitfalls:

| Symptom | Cause | Fix |
|---|---|---|
| frpc logs TLS cert errors every ~11s | network unauthenticated, HTTPS hijacked by the gateway | fix campus-auth first; frpc recovers on its own |
| "user not allowed to use this service" | three meanings: wrong service name / wrong encoded password (same error as wrong password) / MAC rejected by the portal | send the same request from a PC on the same network; if the PC succeeds, it's a MAC rejection |
| Rejected on any IP, PC works fine | Ruijie bans by MAC (repeated script failures can trigger it) | last-resort fix: log in manually once on the board's desktop; the MAC restriction lifts and the script resumes |
| Board landed in 172.23.x/17, SSH dead | pre-auth isolation segment (auth page only); auth follows MAC, not IP | use the adb USB channel; after auth you return to the normal segment with ~1 min DNS blip |
| queryString has trailing garbage | JS-wrapped redirect, `'</script` leaks in | built into the script's cleanup |
| First post-boot attempt fails | RTC-less clock jump | expected; next 5-min tick recovers |

## 5. Security note

Keep `credentials` at mode 600, on the board only. This repo's script, unit,
and example contain zero real account info — and your real `credentials` file
must **never** be committed anywhere.
