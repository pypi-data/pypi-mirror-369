# PyWaveLink/__init__.py

from .SetOutputDevice import SetOutput
from .SetVolIn import SetVolumeInput
from .SetMuteOut import SetMuteOutput
from .SetMuteIn import SetMuteInput
from .Mainvolume import SetMainVolume
from .Mainvolume import SetVolumeLocal
from .Mainvolume import SetVolumeStream


from .getOutput import dumpOutputs
from .getConfig import dumpOutputStatus