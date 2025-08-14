# dump_outputs.py
import asyncio, json, websockets

async def _async_dump_outputs(websocket_url="ws://127.0.0.1", port="1824", json_out: str | None = None):
    url = f"{websocket_url}:{port}"
    out = {"available": {"localMixer": [], "streamMixer": []}, "selected": {"localMixer": "", "streamMixer": ""}}

    async with websockets.connect(url) as ws:
        # Requête
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getOutputs"}))
        raw = await ws.recv()
        resp = json.loads(raw)

        if "result" not in resp:
            print("[!] Pas de 'result' dans la réponse :", resp)
            return out

        r = resp["result"]
        outs = r.get("outputs", {})
        sel  = r.get("selectedOutput", {})

        # Normalise / remplit
        out["available"]["localMixer"]  = outs.get("localMixer",  [])
        out["available"]["streamMixer"] = outs.get("streamMixer", [])
        out["selected"]["localMixer"]   = sel.get("localMixer", "")
        out["selected"]["streamMixer"]  = sel.get("streamMixer", "")

        # Affichage lisible
        print("=== Available outputs ===")
        for mixer_key in ("localMixer", "streamMixer"):
            print(f"- {mixer_key}:")
            for dev in out["available"][mixer_key]:
                name = dev.get("name", "?")
                ident = dev.get("identifier", "?")
                mark = "  (selected)" if out["selected"].get("localMixer" if mixer_key=="localMixer" else "streamMixer") == ident else ""
                print(f"    • {name}  [{ident}]{mark}")

        print("\n=== Selected output ===")
        print(json.dumps(out["selected"], indent=2))

    if json_out:
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] Écrit → {json_out}")

    return out

def dumpOutputs(websocket_url="ws://127.0.0.1", port="1824", json_out: str | None = None):
    """Affiche et retourne les sorties dispo + la sortie sélectionnée. Option: export JSON."""
    return asyncio.run(_async_dump_outputs(websocket_url, port, json_out))
