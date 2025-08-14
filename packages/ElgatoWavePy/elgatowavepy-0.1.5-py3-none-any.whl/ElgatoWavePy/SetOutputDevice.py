# set_output_selected.py
import asyncio, json, websockets

_MIXERS = {"local":"com.elgato.mix.local", "stream":"com.elgato.mix.stream"}
_KEY_FOR = {"local":"localMixer", "stream":"streamMixer"}

async def _rpc(ws, method, params=None, rid=1, timeout=0.7):
    await ws.send(json.dumps({"jsonrpc":"2.0","id":rid,"method":method, **({"params":params} if params else {})}))
    try:
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
        return json.loads(raw)
    except asyncio.TimeoutError:
        return None

async def _get_outputs(ws):
    r = await _rpc(ws, "getApplicationInfo", {}, rid=1, timeout=0.4)
    _ = await _rpc(ws, "getOutputs", {}, rid=2, timeout=1.0)
    return _ or {}

def _resolve_target_identifier(outs_resp, which, target):
    """
    target = ident complet (avec #\WAVE..) OU nom lisible ("Headphones (Elgato XLR Dock)")
    Renvoie (identifier, name) si trouvé, sinon (None, None).
    """
    outs = outs_resp.get("result", {}).get("outputs", {})
    lst = outs.get(_KEY_FOR[which], []) or []
    # si target ressemble à un ident, on matche direct
    if any(ch in str(target) for ch in ("#","\\","PCM_", "{")):
        for dev in lst:
            if dev.get("identifier") == target:
                return dev.get("identifier"), dev.get("name")
    # sinon on matche par nom (case-insensitive)
    tnorm = str(target).strip().lower()
    for dev in lst:
        if str(dev.get("name","")).strip().lower() == tnorm:
            return dev.get("identifier"), dev.get("name")
    return None, None

def _is_already_selected(outs_resp, which, identifier):
    sel = outs_resp.get("result", {}).get("selectedOutput", {})
    return sel.get(_KEY_FOR[which]) == identifier

async def _async_set_output(target, which="local", websocket_url="ws://127.0.0.1", port="1824"):
    which = which.lower()
    if which not in _MIXERS:
        raise ValueError("which doit être 'local' ou 'stream'")
    url = f"{websocket_url}:{int(port)}"

    async with websockets.connect(url) as ws:
        # 1) snapshot initial
        outs = await _get_outputs(ws)
        ident, name = _resolve_target_identifier(outs, which, target)
        if not ident:
            raise ValueError(f"Sortie '{target}' introuvable dans {which}.")
        if _is_already_selected(outs, which, ident):
            return {"changed": False, "identifier": ident, "name": name, "which": which}

        mixer_id = _MIXERS[which]
        tried = []

        async def _confirm():
            latest = await _rpc(ws, "getOutputs", {}, rid=999, timeout=0.8)
            return bool(latest and _is_already_selected(latest, which, ident))

        # 2) variantes à tenter (ordre du + probable au moins probable)
        attempts = [
            ("setSelectedOutput", {"identifier": ident, "mixerID": mixer_id}),
            ("setSelectedOutput", {"name": name, "mixerID": mixer_id}),
            ("setOutputDevice",   {"identifier": ident, "mixerID": mixer_id}),
            ("setOutputDevice",   {"name": name, "mixerID": mixer_id}),
            # quelques variantes de clés
            ("setSelectedOutput", {"outputIdentifier": ident, "mixerID": mixer_id}),
            # fallback via config (parfois supporté)
            ("setOutputConfig",   {"property": "Selected Output", "mixerID": mixer_id, "identifier": ident}),
            ("setOutputConfig",   {"property": "SelectedOutput",  "mixerID": mixer_id, "identifier": ident}),
        ]

        rid = 10
        for method, params in attempts:
            tried.append((method, params))
            _ = await _rpc(ws, method, params, rid=rid, timeout=0.6); rid += 1
            # certaines versions ne renvoient pas de "result", on vérifie via getOutputs
            if await _confirm():
                return {"changed": True, "identifier": ident, "name": name, "which": which, "used": (method, params)}

        # Rien n'a confirmé le switch → on remonte les essais effectués pour debug
        raise RuntimeError(f"Impossible de sélectionner la sortie '{name or target}' ({which}). Tentatives: {tried}")

def SetOutput(target: str, which: str = "local", websocket_url="ws://127.0.0.1", port="1824"):
    """
    target: identifiant COMPLET OU nom lisible affiché par getOutputs()
    which : 'local' ou 'stream'
    """
    return asyncio.run(_async_set_output(target, which, websocket_url, port))
