# Label-Detect-Verify configurations
# In order to use Label-Detect-Verify properly, 
# this configuration file must be properly populated. 
# Do not change any of the attribute names, only the actual input

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Union
from pathlib import Path  # used for 

@dataclass
class FolderLocations:


    def to_dict(self):
        return asdict(self)


@dataclass
class LDVConfigs:
    ''' The final Configs compilation dataclass of all the other dataclasses '''

    def to_dict(self):
        return asdict(self)

LDV_CONFIGS = LDVConfigs()