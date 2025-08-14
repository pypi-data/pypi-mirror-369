# main_output_volume.py
import asyncio, json, websockets

_MIXERS = {"local": "com.elgato.mix.local", "stream": "com.elgato.mix.stream"}

def _norm_value(v):
    # accepte 0..100 ou 0..1
    v = float(v)
    if 0.0 <= v <= 1.0:
        v *= 100.0
    return max(0, min(100, int(round(v))))

async def _async_set_output_volume(value, which, websocket_url="ws://127.0.0.1", port="1824"):
    if which not in _MIXERS:
        raise ValueError("which doit être 'local' ou 'stream'")
    v = _norm_value(value)
    url = f"{websocket_url}:{int(port)}"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "setOutputConfig",
        "params": {
            "property": "Output Level",
            "mixerID": _MIXERS[which],
            "value": v,
            "forceLink": False
        }
    }
    async with websockets.connect(url) as ws:
        # poke optionnel
        try:
            await ws.send(json.dumps({"jsonrpc":"2.0","id":0,"method":"getApplicationInfo"}))
            await asyncio.wait_for(ws.recv(), timeout=0.3)
        except Exception:
            pass

        # envoi
        await ws.send(json.dumps(payload))

        # best-effort: on lit 2-3 messages (beaucoup de versions ne répondent pas avec un "result")
        for _ in range(3):
            try:
                _ = await asyncio.wait_for(ws.recv(), timeout=0.25)
            except asyncio.TimeoutError:
                break

def SetMainVolume(value, which, websocket_url="ws://127.0.0.1", port="1824"):
    asyncio.run(_async_set_output_volume(value, which, websocket_url, port))

def SetVolumeLocal(value, websocket_url="ws://127.0.0.1", port="1824"):
    SetMainVolume(value, "local", websocket_url, port)

def SetVolumeStream(value, websocket_url="ws://127.0.0.1", port="1824"):
    SetMainVolume(value, "stream", websocket_url, port)
