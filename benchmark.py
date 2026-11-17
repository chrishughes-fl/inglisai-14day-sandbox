import asyncio, statistics, httpx

async def run():
    port = open("port.txt").read().strip()
    url = f"http://127.0.0.1:{port}/transaction"
    ok = {"X-Hardware-Security-ID": "HSM-9921-ALPHA"}
    async with httpx.AsyncClient() as c:
        res = await asyncio.gather(*[c.post(url, json={"amount": "149.9900", "tx_id": f"TX-{i}"}, headers=ok) for i in range(50)])
        u200 = [float(r.headers["X-Gate-Latency-Us"]) for r in res if r.status_code == 200]
        u429 = [float(r.headers["X-Gate-Latency-Us"]) for r in res if r.status_code == 429]
        await asyncio.sleep(1.1)
        r_hw = await c.post(url, json={"amount": "149.9900", "tx_id": "SPOOF"}, headers={"X-Hardware-Security-ID": "FAKE-HW-000"})
        r_dc = await c.post(url, json={"amount": "149.992599", "tx_id": "OVER"}, headers=ok)
    print(f"200 OK: {len(u200)} | 429 Block: {len(u429)} ({statistics.mean(u429):.2f} us) | HW ({r_hw.status_code}): {float(r_hw.headers['X-Gate-Latency-Us']):.2f} us | Dec ({r_dc.status_code}): {float(r_dc.headers['X-Gate-Latency-Us']):.2f} us")

asyncio.run(run())
