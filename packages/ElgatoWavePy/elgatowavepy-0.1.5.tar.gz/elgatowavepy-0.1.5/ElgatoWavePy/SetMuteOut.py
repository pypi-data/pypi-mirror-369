# SetMuteOut.py
import asyncio, websockets, json

MIXERS = {"local":"com.elgato.mix.local", "stream":"com.elgato.mix.stream"}

async def async_set_mute_output(mixer, value, host="127.0.0.1", port=1824):
    url = f"ws://{host}:{port}"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({
            "jsonrpc":"2.0","id":1,"method":"setOutputConfig",
            "params":{
                "property":"Output Mute",
                "mixerID": mixer,
                "value": bool(value),
                "forceLink": False
            }
        }))
        try:
            await asyncio.wait_for(ws.recv(), timeout=1.0)
        except:
            pass

def SetMuteOutput(value: bool, mixer_id=None, websocket_url="ws://127.0.0.1", port="1824"):
    if mixer_id in MIXERS: mixer_id = MIXERS[mixer_id]
    if mixer_id is None: raise ValueError("Mixer Key Invalid")
    host = websocket_url.replace("ws://","")
    asyncio.run(async_set_mute_output(mixer_id, value, host, int(port)))
