# Cloudflare Free Tier Plan for ProblemGenerator

**Date**: 2026-03-13
**Status**: Research / Reference
**Relates to**: Layer 3 Task T218 (`docs/cloudflare-setup.md`)
**Cost**: $0 (free tier only)

---

## Table of Contents

1. [What Is Cloudflare](#1-what-is-cloudflare)
2. [Core Features (General)](#2-core-features-general)
3. [Our Specific Case: ProblemGenerator](#3-our-specific-case-problemgenerator)
4. [Implementation Plan (Step-by-Step)](#4-implementation-plan-step-by-step)
5. [Architecture Diagrams](#5-architecture-diagrams)
6. [Backend Code Changes](#6-backend-code-changes)
7. [Risks and Considerations](#7-risks-and-considerations)
8. [Sources](#8-sources)

---

## 1. What Is Cloudflare

### 1.1 The Company

Cloudflare is an internet infrastructure company founded in 2009. They operate one of the world's largest networks, spanning 300+ data centers in 100+ countries. Their network sits between your users and your servers, acting as a **reverse proxy** — every request to your site passes through Cloudflare first.

Think of it like a security checkpoint and express lane combined: Cloudflare inspects incoming traffic (blocking attacks), caches content (serving it faster from nearby locations), and then forwards legitimate requests to your actual server.

### 1.2 Why They Matter

Cloudflare democratized internet security. Before them, DDoS protection and CDNs were enterprise-only products costing thousands per month. They created a free tier that gives small projects the same fundamental protections that Fortune 500 companies use.

For a student project deployed on free tiers (Render.com, Vercel, Supabase), Cloudflare is the missing piece: **network-level security and performance that your hosting providers don't fully provide on their free plans.**

### 1.3 The Free Tier — What You Get for $0

| Feature | Free Tier Includes |
|---|---|
| **DDoS mitigation** | Unmetered — no cap on attack size |
| **CDN** | Global, 300+ PoPs, unlimited bandwidth |
| **DNS** | Fast authoritative DNS (1.1.1.1 resolver) |
| **SSL/TLS** | Free Universal SSL certificate, auto-renewed |
| **WAF custom rules** | 5 custom rules |
| **Rate limiting rules** | 1 rule |
| **Cache rules** | 10 rules |
| **Configuration rules** | 10 rules |
| **Redirect rules** | 10 rules |
| **Bot Fight Mode** | Basic — blocks known bad bots |
| **Analytics** | Traffic, threats, cache hit ratio, geographic distribution |
| **Always Use HTTPS** | Redirect all HTTP to HTTPS |
| **Minimum cache TTL** | 2 hours |

**What you do NOT get on free:**
- Advanced WAF managed rulesets (OWASP Core Rule Set requires Pro at $20/month)
- Detailed bot analytics / bot score breakdowns (Pro+)
- Image optimization (Polish, Mirage)
- Custom error pages
- SLA / uptime guarantees
- Priority support

---

## 2. Core Features (General)

### 2.1 DDoS Protection — Absorbing Attacks

**What it is:** A Distributed Denial of Service (DDoS) attack floods your server with so many requests that it can't serve real users. Imagine 10 million people trying to walk through a single door simultaneously.

**How Cloudflare helps:** Since all traffic passes through Cloudflare's 300+ data centers first, they absorb the flood at the edge of their network. Your origin server (Render.com) never sees the attack traffic. Cloudflare mitigates most attacks in under 3 seconds, automatically, with no configuration needed.

**Free tier:** Unmetered DDoS mitigation on all plans, including free. There is no bandwidth cap on attack mitigation.

### 2.2 CDN (Content Delivery Network) — Serving Content Faster

**What it is:** A CDN stores copies of your content in data centers around the world. When a user in Tokyo requests your site, they get it from a nearby Cloudflare server instead of your origin server in the US.

**How it helps:**
- **Latency reduction**: Content served from nearby edge nodes (e.g., 20ms vs 200ms)
- **Bandwidth savings**: Cached content doesn't hit your origin server
- **Origin offloading**: Your Render.com free tier handles fewer requests

**Free tier:** Full CDN access with unlimited bandwidth. Same edge network as enterprise customers.

### 2.3 DNS Management — Fast, Reliable Name Resolution

**What it is:** DNS translates domain names (e.g., `problemgenerator.com`) into IP addresses. When someone types your URL, DNS is the first thing that happens — before any page loads.

**Why Cloudflare DNS is popular:**
- One of the fastest authoritative DNS providers (typically <20ms globally)
- Easy dashboard for managing records
- Instant propagation for DNS changes (vs. minutes/hours with other providers)
- Built-in DNSSEC support (prevents DNS spoofing)

**Free tier:** Full DNS management, unlimited queries, DNSSEC.

### 2.4 SSL/TLS — Free HTTPS

**What it is:** SSL/TLS encrypts traffic between the user's browser and your server so nobody can read or tamper with data in transit (passwords, tokens, API responses).

**How Cloudflare helps:**
- **Universal SSL**: Free certificate for your domain, auto-renewed, zero configuration
- **Full (Strict) mode**: Encrypts both legs: browser-to-Cloudflare AND Cloudflare-to-origin
- **Automatic HTTPS rewrites**: Forces all traffic to HTTPS

**Free tier:** Universal SSL certificate included. Full encryption chain.

### 2.5 WAF (Web Application Firewall) — Blocking Bad Requests

**What it is:** A WAF inspects HTTP requests for malicious patterns (SQL injection, XSS, path traversal) and blocks them before they reach your server.

**Free tier limitations:**
- 5 custom WAF rules (you define matching criteria and actions)
- 1 rate limiting rule at the edge
- Basic managed rules for critical vulnerabilities only
- No OWASP Core Rule Set (requires Pro at $20/month)

The free tier WAF is a thin first line of defense — it catches obvious attacks. It does NOT replace application-level input validation.

### 2.6 Bot Protection — Filtering Automated Traffic

**What it is:** Bots are automated programs that scrape, spam, or attack websites. Bot Fight Mode uses behavioral analysis and machine learning to detect non-human traffic.

**Free tier:** Bot Fight Mode (basic) — blocks known malicious bots. Does not provide bot score analytics or fine-grained control (those require Pro+).

### 2.7 Caching — Reducing Server Load

**What it is:** Cloudflare stores copies of responses at the edge. Subsequent requests for the same content are served from cache without hitting your origin.

**Default behavior:**
- Static assets (JS, CSS, images, fonts) are cached automatically
- API responses (JSON) are NOT cached by default — you must opt in via cache rules
- Minimum TTL on free tier: 2 hours

**Free tier:** 10 cache rules to customize what gets cached and for how long.

### 2.8 Analytics — Understanding Your Traffic

**Free tier includes:**
- Total requests, bandwidth, unique visitors
- Threats blocked (by type and country)
- Cache hit ratio
- Geographic traffic distribution
- HTTP status code breakdown

**Not included on free:**
- Web Vitals / Core Web Vitals (Pro+)
- Bot score distribution (Pro+)
- Extended data retention

---

## 3. Our Specific Case: ProblemGenerator

### 3.1 Current Architecture

| Component | Service | Tier |
|---|---|---|
| Frontend (React SPA) | Vercel | Free |
| Backend API (FastAPI) | Render.com | Free |
| Database + Auth | Supabase | Free |
| Payments | Stripe | Pay-as-you-go |

### 3.2 Problems We Have Without Cloudflare

#### Problem 1: Rate Limiter IP Spoofing (HIGH — Security Finding)

**Current code** (`backend/app/rate_limiter.py`):
```python
def _get_rate_limit_key(request) -> str:
    """Uses the remote address (X-Forwarded-For or direct IP)."""
    return get_remote_address(request)
```

slowapi's `get_remote_address` reads the `X-Forwarded-For` header. An attacker can set this header to any value, sending unlimited requests while appearing as different IPs. Our rate limiter is trivially bypassable.

**Why this matters:** Rate limiting is our primary defense against brute-force attacks on auth endpoints (login, register, OTP verification). If bypassed, an attacker can:
- Brute-force passwords (even with HIBP check, weak but non-breached passwords exist)
- Enumerate email addresses via timing on login
- Exhaust Supabase free tier connection limits

#### Problem 2: No DDoS Protection

Render.com's free tier has no DDoS mitigation. A modest attack (even a few thousand req/sec) can make our backend unreachable. slowapi rate limiting is application-level — if the server is overwhelmed before FastAPI even processes the request, rate limiting never fires.

#### Problem 3: No WAF

Every request hits our FastAPI application directly. While we validate input in code, there is no network-level filtering for known attack patterns (SQL injection probes, path traversal, etc.).

#### Problem 4: No Trusted IP Source

Without Cloudflare, our backend sees Render.com's load balancer IP (or spoofed `X-Forwarded-For`). We have no reliable way to identify the actual client IP for:
- Rate limiting
- Security logging (`security_logging.py`)
- Abuse detection

#### Problem 5: No Custom Domain SSL Management

If we add a custom domain, we need to manage SSL certificates. Without Cloudflare, we rely on each provider's certificate management independently.

### 3.3 What Cloudflare Specifically Solves

| Problem | Cloudflare Solution | Impact |
|---|---|---|
| Rate limiter IP spoofing (HIGH) | `CF-Connecting-IP` header — set by Cloudflare, cannot be forged by client | Fixes our highest-severity security finding |
| No DDoS protection | Unmetered L3/L4/L7 DDoS mitigation at edge | Backend stays online during attacks |
| No WAF | 5 custom rules to block known bad patterns | First line of defense before FastAPI |
| No trusted IP | `CF-Connecting-IP` is verified by Cloudflare | Accurate security logging and rate limiting |
| SSL management | Universal SSL, auto-renewed | Zero-maintenance HTTPS |
| DNS management | Fast, reliable DNS with easy dashboard | Single place for all DNS records |
| Static caching | Cache `/api/tests/topics` (rarely changes) | Reduces Render.com free tier load |
| Analytics | Traffic, threats, geographic data | Visibility into who's hitting our API |

### 3.4 What Cloudflare Does NOT Solve

| Problem | Why Cloudflare Can't Help |
|---|---|
| **Render.com cold starts (10-30s)** | Cold start happens at the origin server level. Cloudflare forwards the request and waits. Only caching can avoid it (for cacheable endpoints). |
| **Application-level rate limiting** | Still need slowapi — Cloudflare free tier only allows 1 edge rate limiting rule. Our per-endpoint, per-user limits stay in app code. But now with trusted IP from `CF-Connecting-IP`. |
| **Supabase connection limits** | Database connections are origin-side. Cloudflare doesn't proxy database traffic. |
| **Code-level vulnerabilities** | Cloudflare can't fix bugs in our Python/TypeScript code. Input validation, auth logic, IDOR checks stay our responsibility. |
| **Stripe webhook security** | Webhooks come directly from Stripe, not through our domain. Stripe signature verification remains our responsibility. |

---

## 4. Implementation Plan (Step-by-Step)

### Prerequisites

- You own a domain name (e.g., from Namecheap, Google Domains, Porkbun, etc.)
- Your frontend is deployed on Vercel
- Your backend is deployed on Render.com

### Step 1: Create Cloudflare Account

1. Go to [cloudflare.com](https://www.cloudflare.com) and click "Sign Up"
2. Enter your email and password
3. Select the **Free** plan
4. No credit card required

### Step 2: Add Your Domain

1. In the Cloudflare dashboard, click **"Add a site"**
2. Enter your domain name (e.g., `problemgenerator.com`)
3. Select the **Free** plan when prompted
4. Cloudflare will scan your existing DNS records

### Step 3: Update Nameservers at Your Registrar

Cloudflare will give you two nameservers (e.g., `ada.ns.cloudflare.com` and `bob.ns.cloudflare.com`).

1. Log in to your domain registrar (Namecheap, Porkbun, etc.)
2. Find the nameserver settings for your domain
3. Replace the existing nameservers with Cloudflare's two nameservers
4. Save changes

**Important:** DNS propagation can take **up to 24-48 hours**, though it's often faster (minutes to a few hours). During propagation, some users may see the old DNS, others the new.

### Step 4: Configure DNS Records

In the Cloudflare DNS dashboard, create these records:

#### Frontend (Vercel):

| Type | Name | Target | Proxy Status |
|---|---|---|---|
| CNAME | `@` (root) | `cname.vercel-dns.com` | **DNS only** (initially) |
| CNAME | `www` | `cname.vercel-dns.com` | **DNS only** (initially) |

#### Backend API (Render.com):

| Type | Name | Target | Proxy Status |
|---|---|---|---|
| CNAME | `api` | `your-service.onrender.com` | **DNS only** (initially) |

**Why DNS only initially?** Both Vercel and Render need to verify domain ownership and issue their own SSL certificates. This fails if Cloudflare's proxy is active during setup.

**Important for Render.com:** Remove any AAAA records for your domain. Render does not support IPv6 and AAAA records can cause issues.

### Step 5: Verify Domains on Vercel and Render

1. **Vercel**: Go to your project settings > Domains > Add `problemgenerator.com` and `www.problemgenerator.com`. Wait for "Valid Configuration" status.
2. **Render**: Go to your web service > Settings > Custom Domains > Add `api.problemgenerator.com`. Wait for certificate issuance.

### Step 6: Enable Cloudflare Proxy

Once both providers have verified and issued certificates:

1. Go back to Cloudflare DNS
2. For each record, click the cloud icon to change from "DNS only" (gray cloud) to **"Proxied"** (orange cloud)
3. This routes traffic through Cloudflare's network

**Note on Vercel:** Some setups work fine proxied; others have issues with Vercel's edge functions. If you see errors after enabling the proxy for the frontend, switch it back to DNS only. The backend API is more important to proxy.

### Step 7: Configure SSL/TLS

1. Go to **SSL/TLS > Overview** in Cloudflare dashboard
2. Set encryption mode to **Full (Strict)**
   - "Full (Strict)" means Cloudflare encrypts traffic to the origin AND validates the origin's SSL certificate
   - This works because both Vercel and Render provide valid SSL certificates

3. Go to **SSL/TLS > Edge Certificates**:
   - Enable **"Always Use HTTPS"** — redirects all HTTP requests to HTTPS
   - Enable **"Automatic HTTPS Rewrites"** — fixes mixed-content issues

### Step 8: Configure Caching Rules

Go to **Rules > Cache Rules** and create:

**Rule 1: Cache the topics endpoint**
- When: URI Path equals `/api/tests/topics`
- Then: Cache eligible, Edge TTL = 2 hours (minimum on free)
- Why: Topics rarely change, this saves Render.com from serving the same static list repeatedly

**Rule 2: Bypass cache for all other API routes**
- When: URI Path starts with `/api/`
- Then: Bypass cache
- Why: Test generation, auth, billing — all dynamic, must hit origin every time
- **Place this rule BELOW Rule 1** (rules are evaluated in order; first match wins)

### Step 9: Configure WAF Custom Rules (Optional but Recommended)

Go to **Security > WAF > Custom rules**. You have 5 rules on free tier. Suggested rules:

**Rule 1: Block requests with suspicious User-Agents**
- When: `http.user_agent contains "sqlmap"` OR `http.user_agent contains "nikto"` OR `http.user_agent contains "nmap"`
- Action: Block
- Why: Blocks common automated scanning tools

**Rule 2: Block requests with SQL injection patterns in URL**
- When: `http.request.uri contains "UNION SELECT"` OR `http.request.uri contains "1=1"` OR `http.request.uri contains "../"`
- Action: Block
- Why: Catches obvious injection/traversal attempts in the URL

**Rule 3: Restrict API methods**
- When: `http.request.uri.path starts with "/api/"` AND NOT `http.request.method in {"GET" "POST" "DELETE" "OPTIONS"}`
- Action: Block
- Why: Our API only uses GET, POST, DELETE, OPTIONS. Block everything else (PUT, PATCH, TRACE, etc.)

Save the remaining 2 rules for future needs.

### Step 10: Enable Bot Fight Mode

1. Go to **Security > Bots**
2. Toggle **Bot Fight Mode** to ON
3. This automatically challenges or blocks known malicious bots

### Step 11: Update Backend to Use CF-Connecting-IP

This is a code change. See [Section 6](#6-backend-code-changes) for the exact implementation.

### Step 12: Test Everything

After all changes:

1. **DNS resolution**: `dig problemgenerator.com` should return Cloudflare IPs (104.x.x.x or 172.x.x.x range)
2. **Frontend**: Visit `https://problemgenerator.com` — should load the React app
3. **Backend**: `curl https://api.problemgenerator.com/api/health` — should return `{"status": "ok"}`
4. **SSL**: Check [ssllabs.com](https://www.ssllabs.com/ssltest/) — should show A or A+ rating
5. **Headers**: `curl -I https://api.problemgenerator.com/api/health` — should include `cf-ray` header (confirms traffic is going through Cloudflare)
6. **Rate limiting**: Confirm rate limiter works with CF-Connecting-IP (see test in Section 6)
7. **Cloudflare analytics**: Check the dashboard after a few hours — you should see traffic data

---

## 5. Architecture Diagrams

### 5.1 Before Cloudflare

```
                    ┌──────────────────────┐
User ──── HTTPS ───>│   Vercel (frontend)  │
                    │   React SPA + CDN    │
                    └──────────────────────┘

                    ┌──────────────────────┐
User ──── HTTPS ───>│  Render.com (backend)│
                    │  FastAPI API         │
                    └──────────────────────┘

Problems:
- No DDoS protection on backend
- Rate limiter IP easily spoofed via X-Forwarded-For
- No WAF filtering
- No visibility into attack traffic
```

### 5.2 After Cloudflare

```
                    ┌────────────┐    ┌──────────────────────┐
User ──── HTTPS ───>│ Cloudflare │───>│   Vercel (frontend)  │
                    │  (proxy)   │    │   React SPA + CDN    │
                    └────────────┘    └──────────────────────┘
                    │ DDoS filter│
                    │ WAF rules  │
                    │ Bot check  │
                    │ SSL term.  │
                    │ Cache      │
                    └────────────┘

                    ┌────────────┐    ┌──────────────────────┐
User ──── HTTPS ───>│ Cloudflare │───>│  Render.com (backend)│
                    │  (proxy)   │    │  FastAPI API         │
                    └────────────┘    └──────────────────────┘
                    │ DDoS filter│    │ Reads CF-Connecting- │
                    │ WAF rules  │    │ IP for rate limiting │
                    │ Bot check  │    │ + security logging   │
                    │ SSL term.  │    └──────────────────────┘
                    │ Cache /api │
                    │ /tests/    │
                    │ topics     │
                    └────────────┘
```

### 5.3 Request Flow Detail (API Call)

```
1. User's browser sends request to api.problemgenerator.com
            │
            v
2. Cloudflare DNS resolves to nearest Cloudflare edge node
            │
            v
3. Cloudflare edge node:
   a. DDoS check ─── attack traffic? → DROP
   b. Bot check ──── known bad bot?  → CHALLENGE/BLOCK
   c. WAF rules ──── matches rule?   → BLOCK
   d. Cache check ── cached?         → SERVE FROM CACHE (skip origin)
   e. If not cached/cacheable:
            │
            v
4. Cloudflare adds headers:
   - CF-Connecting-IP: <real user IP>
   - CF-IPCountry: <country code>
   - CF-Ray: <request ID>
   - X-Forwarded-For: <real user IP>  (sanitized by Cloudflare)
   - X-Forwarded-Proto: https
            │
            v
5. Cloudflare forwards request to Render.com (HTTPS)
            │
            v
6. FastAPI processes request:
   - Reads CF-Connecting-IP for rate limiting
   - Normal auth → subscription check → generate/serve
            │
            v
7. Response flows back: Render → Cloudflare → User
```

### 5.4 Stripe Webhook Flow (Unchanged)

```
Stripe ──── HTTPS ───> Render.com (directly, NOT through Cloudflare)
                       │
                       POST /api/billing/webhook
                       │
                       Stripe signature verification (webhook secret)
```

Stripe webhooks go directly to the Render.com URL, not through Cloudflare. This is fine — Stripe has its own security (signature verification). The webhook endpoint does not need Cloudflare protection and should NOT rely on CF-Connecting-IP.

---

## 6. Backend Code Changes

### 6.1 Update Rate Limiter to Use CF-Connecting-IP

The key code change: modify `_get_rate_limit_key` to prefer `CF-Connecting-IP` when present, but validate that the request actually came from Cloudflare.

**File: `backend/app/rate_limiter.py`**

Current:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

def _get_rate_limit_key(request) -> str:
    return get_remote_address(request)

limiter = Limiter(key_func=_get_rate_limit_key)
```

Proposed:
```python
import ipaddress
import logging

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

logger = logging.getLogger(__name__)

# Cloudflare IPv4 and IPv6 ranges (from https://www.cloudflare.com/ips/)
# These should be periodically verified against the official list.
CLOUDFLARE_IPV4_RANGES = [
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22",
    "103.31.4.0/22", "141.101.64.0/18", "108.162.192.0/18",
    "190.93.240.0/20", "188.114.96.0/20", "197.234.240.0/22",
    "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
    "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22",
]
CLOUDFLARE_IPV6_RANGES = [
    "2400:cb00::/32", "2606:4700::/32", "2803:f800::/32",
    "2405:b500::/32", "2405:8100::/32", "2a06:98c0::/29",
    "2c0f:f248::/32",
]

CLOUDFLARE_NETWORKS = [
    ipaddress.ip_network(r) for r in CLOUDFLARE_IPV4_RANGES + CLOUDFLARE_IPV6_RANGES
]


def _is_cloudflare_ip(ip_str: str) -> bool:
    """Check if an IP address belongs to Cloudflare's published ranges."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in network for network in CLOUDFLARE_NETWORKS)
    except ValueError:
        return False


def _get_rate_limit_key(request) -> str:
    """Extract client IP for rate limiting.

    Priority:
    1. CF-Connecting-IP (if request came from a Cloudflare IP)
    2. Fallback to get_remote_address (X-Forwarded-For / direct IP)

    CF-Connecting-IP is set by Cloudflare and cannot be forged by
    the client. However, we must verify the connecting IP is actually
    Cloudflare's — otherwise an attacker connecting directly to the
    origin could spoof the header.
    """
    cf_connecting_ip = request.headers.get("cf-connecting-ip")

    if cf_connecting_ip:
        # Verify the request actually came through Cloudflare
        # In production behind Render's proxy, request.client.host
        # is the last proxy hop. When proxied through Cloudflare,
        # this should be a Cloudflare IP.
        remote_ip = get_remote_address(request)
        if _is_cloudflare_ip(remote_ip):
            return cf_connecting_ip
        else:
            logger.warning(
                "CF-Connecting-IP header present but request is not from "
                "Cloudflare IP %s — possible spoofing attempt",
                remote_ip,
            )

    return get_remote_address(request)


limiter = Limiter(key_func=_get_rate_limit_key)
```

**Why validate the source IP?** If an attacker discovers your Render.com origin URL (e.g., `your-service.onrender.com`), they can bypass Cloudflare and connect directly. If we blindly trust `CF-Connecting-IP`, they can spoof it. By checking that the connecting IP belongs to Cloudflare's published ranges, we ensure the header is genuine.

### 6.2 Update Security Logging

The same `CF-Connecting-IP` logic should be used in `security_logging.py` for accurate event logging. Apply the same "trust only if from Cloudflare IP" pattern.

### 6.3 Environment Variable (Optional)

Add a `BEHIND_CLOUDFLARE` setting to `config.py` so the CF-Connecting-IP logic can be enabled/disabled per environment (off in local dev, on in production). This avoids the overhead of IP range checking in development.

---

## 7. Risks and Considerations

### 7.1 Single Point of Failure

**Risk:** If Cloudflare has an outage, your entire site goes down — even if Vercel and Render.com are fine. Cloudflare has had notable outages (e.g., June 2022 affected many major sites).

**Mitigation:** Cloudflare's uptime is >99.99% historically. For a student project, this is an acceptable tradeoff. Enterprise customers pay for multi-CDN failover; we don't need that.

### 7.2 DNS Propagation Delay

**Risk:** When you switch nameservers to Cloudflare, DNS propagation takes time. During this window (minutes to 48 hours, typically <4 hours), some users may not be able to reach your site.

**Mitigation:** Make the switch during low-traffic hours. Test with `dig` commands to check propagation status.

### 7.3 Cloudflare Can See All Traffic

**Risk:** As a reverse proxy, Cloudflare terminates TLS and can see all unencrypted request/response data (including auth tokens, API payloads). This is inherent to how any reverse proxy works.

**Mitigation:** This is the same trust model as using Vercel, Render.com, or any cloud provider. Cloudflare is SOC 2 Type II compliant and handles traffic for ~20% of the internet. For a student project, this is a non-issue. Just be aware of it architecturally.

### 7.4 Origin IP Exposure

**Risk:** If someone discovers your Render.com origin URL (`your-service.onrender.com`), they can bypass Cloudflare entirely and hit your server directly. Cloudflare's DDoS protection and WAF are ineffective against direct-to-origin attacks.

**Mitigation on Render.com free tier:**
- Render.com free tier does not support IP allowlisting at the infrastructure level
- The backend code validates `CF-Connecting-IP` only when the request comes from Cloudflare IPs (Section 6.1) — so rate limiting still works via `X-Forwarded-For` for direct connections
- The `.onrender.com` subdomain is not publicly advertised, but it's not secret either (DNS history, error messages, etc.)
- On a paid Render plan, you could restrict inbound traffic to Cloudflare IPs only. Not an option on free tier.

### 7.5 Free Tier WAF Limitations

**Risk:** The free WAF only has 5 custom rules and no OWASP managed ruleset. It's a thin layer, not comprehensive protection.

**Mitigation:** The 5 rules are enough to block the most common automated attacks (see Step 9). Our application already has input validation and parameterized queries. The WAF is defense-in-depth, not our sole protection.

### 7.6 Caching API Responses — Stale Data Risk

**Risk:** If we cache `/api/tests/topics` and add a new topic, users may see stale data for up to 2 hours (free tier minimum TTL).

**Mitigation:** Topics are extremely static (they change when we deploy new code, maybe once a month). 2-hour staleness is acceptable. If needed, you can manually purge the cache from the Cloudflare dashboard after deploying a topics change.

### 7.7 Vercel + Cloudflare Proxy Compatibility

**Risk:** Vercel has its own edge network. Putting Cloudflare's proxy in front of it can cause issues with Vercel's edge functions, automatic certificate renewal, and deployment previews.

**Mitigation:** If you experience issues, keep Cloudflare proxy OFF (DNS only) for the frontend CNAME records. The frontend is already on Vercel's CDN — Cloudflare's CDN benefit is marginal there. The primary value of Cloudflare is for the backend API (Render.com), which has no built-in CDN or DDoS protection.

### 7.8 Stripe Webhook Delivery

**Risk:** If Cloudflare blocks a Stripe webhook request (misidentified as a bot or blocked by WAF rules).

**Non-issue:** Stripe webhooks go directly to your Render.com URL, not through your custom domain's Cloudflare proxy. Stripe uses the webhook URL you configure in the Stripe dashboard. As long as you set the webhook URL to `https://your-service.onrender.com/api/billing/webhook` (the direct Render URL, not the custom domain), Cloudflare is not in the path.

---

## 8. Sources

- [Cloudflare Free Plan Overview](https://www.cloudflare.com/plans/free/)
- [Cloudflare Plans & Pricing](https://www.cloudflare.com/plans/)
- [Cloudflare DDoS Protection Docs](https://developers.cloudflare.com/ddos-protection/)
- [Cloudflare Free DDoS Protection](https://www.cloudflare.com/application-services/products/ddos-for-web/)
- [Cloudflare HTTP Headers (CF-Connecting-IP)](https://developers.cloudflare.com/fundamentals/reference/http-headers/)
- [Restoring Original Visitor IPs](https://developers.cloudflare.com/support/troubleshooting/restoring-visitor-ips/restoring-original-visitor-ips/)
- [Cloudflare IP Ranges](https://www.cloudflare.com/ips/)
- [Cloudflare IP Addresses Documentation](https://developers.cloudflare.com/fundamentals/concepts/cloudflare-ip-addresses/)
- [Configuring Cloudflare DNS for Render](https://render.com/docs/configure-cloudflare-dns)
- [Render Custom Domains with Cloudflare](https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/saas-customers/provider-guides/render/)
- [Cloudflare SSL Full (Strict) Mode](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/)
- [Cloudflare WAF Custom Rules](https://developers.cloudflare.com/waf/custom-rules/)
- [Cloudflare Cache Rules](https://developers.cloudflare.com/cache/how-to/cache-rules/)
- [Cloudflare Rules Upgraded Limits (Feb 2025)](https://developers.cloudflare.com/changelog/post/2025-02-12-rules-upgraded-limits/)
- [Cloudflare Bot Plans — Free](https://developers.cloudflare.com/bots/plans/free/)
- [Cloudflare WAF Rate Limiting Rules](https://developers.cloudflare.com/waf/rate-limiting-rules/)
- [Rate Limiting by IP with Cloudflare (Simon Willison)](https://til.simonwillison.net/cloudflare/rate-limiting)
- [Which Cloudflare Services Are Free? (DEV Community)](https://dev.to/ioniacob/which-cloudflare-services-are-free-2025-free-tier-guide-53jl)
- [Cloudflare Pricing 2026 (CheckThat.ai)](https://checkthat.ai/brands/cloudflare/pricing)
- [Vercel + Cloudflare Domain Setup](https://ahmadawais.com/vercel-cloudflare-domain-setup/)
