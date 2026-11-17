# InglisAI Edge Security Gateway — 14-Day Enterprise Sandbox Trial
**Inglis Advanced Infrastructure LLC** | [https://inglisai.com](https://inglisai.com)  
**Patent Reference:** U.S. Patent Application No. 19/853,850

## Overview
A zero-trust, high-concurrency edge API and Web Application Firewall (WAF) gateway engineered to deflect volumetric bursts and malformed financial payloads in microseconds before downstream ledger execution.

## Verified Sandbox Baselines
- **Concurrent Burst (`< 30 Req/Sec`):** 30 requests cleared (`200 OK`) & binary framed
- **Layer-1 WAF Block (`>= 30 Req/Sec`):** 20 excess requests deflected (`429`) at `1.44 us` isolated / `14.67 us` Linux container
- **Spoofed Hardware ID (`FAKE-HW-000`):** Rejected (`422`) at `4.53 us` isolated / `82.09 us` Linux container
- **Decimal Precision Overflow (`6` vs `4` places):** Rejected (`422`) at `42.20 us` isolated / `193.17 us` Linux container

## Quickstart (Local or Docker)
```bash
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
./venv/bin/python server.py
# In a second terminal:
./venv/bin/python benchmark.py
```
Docker:
```bash
docker build -t inglisai-gateway-trial .
docker run -d -p 8080:8080 -e GATEWAY_PORT=8080 inglisai-gateway-trial
```

## Commercial Licensing
Operates under a 14-day evaluation window (`/health` shows remaining trial days). For SaaS/IaaS licensing or a 30-day enterprise Proof of Concept, contact **Inglis Advanced Infrastructure LLC** at `flacmh@gmail.com` or [https://inglisai.com](https://inglisai.com).
