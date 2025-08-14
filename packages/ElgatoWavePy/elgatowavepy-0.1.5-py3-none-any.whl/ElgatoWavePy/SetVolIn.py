# SetVoliin.py — Elgato Wave Link ≥ 2.0.6 : set input volume via setInputConfig (0..100)
import asyncio, json, sys, websockets

ALIAS = {
    "System":"Wave Link System","Music":"Wave Link Music","Browser":"Wave Link Browser",
    "VoiceChat":"Wave Link Voice Chat","SFX":"Wave Link SFX","Game":"Wave Link Game",
    "Aux1":"Wave Link Aux 1","Aux2":"Wave Link Aux 2",
}
MIXERS = {"local":"com.elgato.mix.local","stream":"com.elgato.mix.stream"}

async def async_set_volume_input(volume, input_key, mixer_key, host="127.0.0.1", port=1824):
    # normalise 0..1 -> 0..100 ; clamp
    try:
        v = float(volume)
    except:
        raise ValueError("volume doit être un nombre")
    if v <= 1.0: v *= 100.0
    v = max(0, min(100, int(round(v))))

    identifier = ALIAS.get(input_key, input_key)
    mixerID    = MIXERS.get(mixer_key, mixer_key)

    url = f"ws://{host}:{port}"
    async with websockets.connect(url) as ws:
        # 1) petit poke pour réveiller l'API et purger la file
        await ws.send(json.dumps({"jsonrpc":"2.0","id":1,"method":"getApplicationInfo"}))
        try:
            await asyncio.wait_for(ws.recv(), timeout=0.25)
        except asyncio.TimeoutError:
            pass

        # 2) envoi du setter (comme dans ultra_probe, tel quel)
        payload = {
            "jsonrpc":"2.0",
            "id":2,
            "method":"setInputConfig",
            "params":{
                "property":"Volume",
                "identifier":identifier,
                "mixerID":mixerID,
                "value":v
            }
        }
        await ws.send(json.dumps(payload))

        # 3) Best-effort: on lit brièvement, mais on n’en dépend pas (l’effet est côté app)
        try:
            await asyncio.wait_for(ws.recv(), timeout=0.3)
        except asyncio.TimeoutError:
            pass

def SetVolumeInput(volume: int|float, input_id=None, mixer_id=None,
                   websocket_url="ws://127.0.0.1", port="1824"):
    if not input_id or not mixer_id:
        raise ValueError("input_id et mixer_id requis")
    host = websocket_url.replace("ws://", "")
    asyncio.run(async_set_volume_input(volume, input_id, mixer_id, host, int(port)))

if __name__ == "__main__":
    # Exemples:
    #   python SetVoliin.py "Music" local 25
    #   python SetVoliin.py "Game"  stream 70
    key = sys.argv[1] if len(sys.argv)>1 else "Game"
    mix = sys.argv[2] if len(sys.argv)>2 else "local"
    vol = sys.argv[3] if len(sys.argv)>3 else 25
    SetVolumeInput(vol, key, mix)
