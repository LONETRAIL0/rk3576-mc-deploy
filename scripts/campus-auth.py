#!/usr/bin/env python3
"""Campus network (Ruijie eportal) auto-login.

Generic version for any school whose portal is `eportal/InterFace.do`
(the standard Ruijie eportal interface). Adapted from a real deployment
that has run unattended for months.

Credentials AND the portal address are read at runtime from
credentials next to this script (root-only, mode 600) — no secrets,
no school-specific literals in this source file.

    USER_ID       校园网账号（学号）
    PASSWORD_ENC  编码后的密码（见 docs/08 的抓取方法，不是明文）
    SERVICE       认证服务名（如"校园网"，以学校为准）
    PORTAL_HOST   校园认证门户的 IP 或域名（各校不同）

Security note: both request targets are validated before connect —
the probe host must resolve to public IPs, the portal must resolve to
exactly the address pinned in the credentials file (the campus portal
is an intranet host by design — that single pinned IP is not an SSRF
surface).
"""
import http.client
import ipaddress
import os
import re
import socket
import sys
import urllib.parse

CREDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials")

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "campus-auth/1.0",
}


def _check_ips(host, port, expect=None):
    """Resolve host and verify addresses: exact match, or public for probe."""
    for info in socket.getaddrinfo(host, port):
        ip = ipaddress.ip_address(info[4][0])
        if expect is None:
            if not ip.is_global:
                raise ValueError("%s resolved to non-public IP %s" % (host, ip))
        elif str(ip) != expect:
            raise ValueError("%s resolved outside pinned address: %s" % (host, ip))


def probe():
    """Returns (status, body). Body empty means network failure."""
    try:
        _check_ips("edge.microsoft.com", 80, expect=None)
        conn = http.client.HTTPConnection("edge.microsoft.com", 80, timeout=10)
        conn.request("GET", "/captiveportal/generate_204", headers=HEADERS)
        r = conn.getresponse()
        return r.status, r.read().decode(errors="replace")
    except Exception:
        return 0, ""


def portal(portal_host, data, cookie=None):
    """POST login to the pinned campus portal."""
    try:
        _check_ips(portal_host, 80, expect=portal_host)
        headers = dict(HEADERS)
        if cookie:
            headers["Cookie"] = cookie
        conn = http.client.HTTPConnection(portal_host, 80, timeout=10)
        conn.request("POST", "/eportal/InterFace.do?method=login",
                     body=data.encode(), headers=headers)
        r = conn.getresponse()
        return r.status, r.read().decode(errors="replace")
    except Exception:
        return 0, ""


def page_info(portal_host, data):
    """Register the login intent via pageInfo (single-encoded queryString).

    The portal rejects a bare login POST with "用户不允许使用本服务"
    even when every credential is correct — the browser page always calls
    pageInfo first, and the login must carry the session cookie pageInfo
    returns. Returns (status, body, set-cookie).
    """
    try:
        _check_ips(portal_host, 80, expect=portal_host)
        conn = http.client.HTTPConnection(portal_host, 80, timeout=10)
        conn.request("POST", "/eportal/InterFace.do?method=pageInfo",
                     body=data.encode(), headers=HEADERS)
        r = conn.getresponse()
        return r.status, r.read().decode(errors="replace"), r.getheader("Set-Cookie")
    except Exception:
        return 0, "", None


def load_creds():
    creds = {}
    for line in open(CREDS_PATH, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            creds[k.strip()] = v.strip()
    for key in ("USER_ID", "PASSWORD_ENC", "SERVICE", "PORTAL_HOST"):
        if not creds.get(key):
            raise SystemExit("missing %s in %s" % (key, CREDS_PATH))
    return creds


def main():
    creds = load_creds()
    portal_host = creds["PORTAL_HOST"]

    status, probe_body = probe()
    if status == 204:
        print("already online")
        return 0
    if not probe_body:
        print("no response from probe (link down?)")
        return 1

    m = re.search(r'index\.jsp\?([^"> ]+)', probe_body)
    if not m:
        print("no captive portal link found (status %s): %s" % (status, probe_body[:120]))
        return 1
    qs = m.group(1)
    # The redirect is JS-wrapped: ...index.jsp?<qs>'</script> — the regex
    # excludes " > and space but lets a trailing '</script' and/or quote in,
    # which corrupts the login. Cut at '<' and strip trailing quote junk.
    lt = qs.find("<")
    if lt != -1:
        qs = qs[:lt]
    qs = qs.rstrip("'\" ")
    if not qs:
        print("empty queryString after cleanup")
        return 1

    # eportal frontend double-encodes both fields (encodeURIComponent twice)
    enc_qs = urllib.parse.quote(urllib.parse.quote(qs, safe=""), safe="")
    enc_svc = urllib.parse.quote(urllib.parse.quote(creds["SERVICE"], safe=""), safe="")

    # pageInfo takes the queryString single-encoded (browser: pageInfo(
    # encodeURIComponent(getQueryString()))).
    _, _, cookie = page_info(portal_host, "queryString=" + urllib.parse.quote(qs, safe=""))

    body = urllib.parse.urlencode({
        "userId": creds["USER_ID"],
        "password": creds["PASSWORD_ENC"],
        "service": enc_svc,
        "queryString": enc_qs,
        "operatorPwd": "",
        "operatorUserId": "",
        "validcode": "",
        "passwordEncrypt": "true",
    })
    _, resp = portal(portal_host, body, cookie)
    print(resp[:200])
    if '"result":"success"' in resp:
        print("LOGIN OK")
        return 0
    print("LOGIN FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
