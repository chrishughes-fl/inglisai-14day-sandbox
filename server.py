import asyncio, json, os, socket, struct, time
from collections import defaultdict, deque
from decimal import Decimal
import uvicorn
from fastapi import FastAPI, Request, Response

AUTH_IDS = {"HSM-9921-ALPHA", "TPM-8840-BETA"}
TRIAL_SEC = 14 * 86400
TRIAL_START = float(os.getenv("TRIAL_START_EPOCH", time.time()))
logs, lock = defaultdict(deque), asyncio.Lock()
app = FastAPI(title="InglisAI 14-Day Sandbox Gateway")

def validate_vault(raw: bytes, hw: str | None):
    if hw not in AUTH_IDS: return False, "Invalid Hardware Security ID"
    try:
        d = json.loads(raw.decode(), parse_float=str, parse_int=str)
        v = Decimal(str(d["amount"]))
        e = v.as_tuple().exponent
        if not v.is_finite() or v <= 0 or (isinstance(e, int) and abs(e) > 4): return False, "Decimal bounds error"
        b = json.dumps({"hw": hw, "amt": str(v), "tx": d.get("tx_id", "")}).encode()
        return True, struct.pack(">I", len(b)) + b
    except Exception: return False, "Malformed payload"

@app.middleware("http")
async def gate(req: Request, call_next):
    if (time.time() - TRIAL_START) > TRIAL_SEC: return Response("14-Day Trial Expired", status_code=402)
    if req.url.path == "/health": return await call_next(req)
    raw = await req.body()
    t0 = time.perf_counter()
    ip, hw, now = (req.client.host if req.client else "127.0.0.1"), req.headers.get("X-Hardware-Security-ID"), time.perf_counter()
    async with lock:
        w = logs[ip]
        while w and (now - w[0]) >= 1.0: w.popleft()
        if len(w) >= 30:
            us = round((time.perf_counter() - t0) * 1e6, 2)
            return Response(f"{us:.2f}", status_code=429, headers={"X-Gate-Latency-Us": f"{us:.2f}"})
        w.append(now)
    ok, res = validate_vault(raw, hw)
    if not ok:
        us = round((time.perf_counter() - t0) * 1e6, 2)
        return Response(f"{us:.2f}", status_code=422, headers={"X-Gate-Latency-Us": f"{us:.2f}"})
    req.state.frame = res
    resp = await call_next(req)
    resp.headers["X-Gate-Latency-Us"] = f"{round((time.perf_counter() - t0) * 1e6, 2):.2f}"
    return resp

@app.get("/health")
async def health(): return {"status": "active", "days_left": round((TRIAL_SEC - (time.time() - TRIAL_START)) / 86400, 2)}

@app.post("/transaction")
async def tx(req: Request): return {"status": "routed", "bytes": len(req.state.frame)}

if __name__ == "__main__":
    p = int(os.getenv("GATEWAY_PORT", 0))
    if not p:
        with socket.socket() as s: s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]
    open("port.txt", "w").write(str(p))
if __name__ == "__main__":
    p = int(os.getenv("GATEWAY_PORT", 0))
    if not p:
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            p = s.getsockname()[1]
    open("port.txt", "w").write(str(p))
    uvicorn.run(app, host="0.0.0.0", port=p, log_level="error")
