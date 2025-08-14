# SetMuteIn.py
import asyncio, websockets, json

NEW_INPUTS = {
    "System":    "Wave Link System",
    "Music":     "Wave Link Music",
    "Browser":   "Wave Link Browser",
    "VoiceChat": "Wave Link Voice Chat",
    "SFX":       "Wave Link SFX",
    "Game":      "Wave Link Game",
    "Aux1":      "Wave Link Aux 1",
    "Aux2":      "Wave Link Aux 2",
}
OLD_INPUTS = {
    "System": "PCM_OUT_01_V_00_SD2",
    "Music": "PCM_OUT_01_V_02_SD3",
    "Browser": "PCM_OUT_01_V_04_SD4",
    "VoiceChat": "PCM_OUT_01_V_06_SD5",
    "SFX": "PCM_OUT_01_V_08_SD6",
    "Game": "PCM_OUT_01_V_10_SD7",
    "Aux1": "PCM_OUT_01_V_12_SD8",
    "Aux2": "PCM_OUT_01_V_14_SD9"
}
MIXERS = {"local":"com.elgato.mix.local", "stream":"com.elgato.mix.stream"}

async def _call(ws, method, params, rid):
    await ws.send(json.dumps({"jsonrpc":"2.0","id":rid,"method":method,"params":params}))
    try:
        raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
        return json.loads(raw)
    except:
        return None

async def async_set_mute_input(value, input_key, mixer_key, host="127.0.0.1", port=1824):
    url = f"ws://{host}:{port}"
    mixer_id = MIXERS.get(mixer_key) or mixer_key
    ident = NEW_INPUTS.get(input_key) or OLD_INPUTS.get(input_key) or input_key
    async with websockets.connect(url) as ws:
        rid = 1
        await _call(ws, "getApplicationInfo", {}, rid); rid += 1
        resp = await _call(ws, "setInputConfig", {
            "property":"Mute",
            "identifier": ident,
            "mixerID": mixer_id,
            "forceLink": False,
            "value": bool(value)
        }, rid)

        if resp and "error" in resp and NEW_INPUTS.get(input_key) and OLD_INPUTS.get(input_key):
            ident2 = OLD_INPUTS[input_key]
            await _call(ws, "setInputConfig", {
                "property":"Mute",
                "identifier": ident2,
                "mixerID": mixer_id,
                "forceLink": False,
                "value": bool(value)
            }, rid+1)

def SetMuteInput(value: bool, input_id=None, mixer_id=None, websocket_url="ws://127.0.0.1", port="1824"):
    if input_id is None or mixer_id is None:
        raise ValueError("input Key or Mixer Key Invalid")
    host = websocket_url.replace("ws://","")
    asyncio.run(async_set_mute_input(value, input_id, mixer_id, host, int(port)))
