import asyncio, json, websockets

async def dump_elgato_all(ws_url="ws://127.0.0.1", port=1824):
    url = f"{ws_url}:{port}"
    async with websockets.connect(url) as ws:
        print("[*] Connected to Elgato Wave Link")

        # poke: getApplicationInfo
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getApplicationInfo"}))
        try:
            print("<APPINFO>", json.loads(await asyncio.wait_for(ws.recv(), timeout=0.5)))
        except:
            pass

        # dump config global sortie
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "getOutputConfig"}))
        print("\n[OUTPUT CONFIG]")
        try:
            print(json.dumps(json.loads(await asyncio.wait_for(ws.recv(), timeout=1)), indent=2))
        except:
            pass

        # dump config global entrée
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 3, "method": "getInputConfig"}))
        print("\n[INPUT CONFIG]")
        try:
            print(json.dumps(json.loads(await asyncio.wait_for(ws.recv(), timeout=1)), indent=2))
        except:
            pass

        # dump routing table (utile pour lier les devices)
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 4, "method": "getRoutingTable"}))
        print("\n[ROUTING TABLE]")
        try:
            print(json.dumps(json.loads(await asyncio.wait_for(ws.recv(), timeout=1)), indent=2))
        except:
            pass

if __name__ == "__main__":
    asyncio.run(dump_elgato_all())
