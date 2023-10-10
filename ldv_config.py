# Label-Detect-Verify configurations
# In order to use Label-Detect-Verify properly, 
# this configuration file must be properly populated. 
# Do not change any of the attribute names, only the actual input

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Union
from pathlib import Path  # used for 

@dataclass
class FolderLocations:
    """ The folder locations for various files. 
    Because everything is done locally, these ideally should be full, absolute paths (but can be relative paths as well)
    """
    # where the new raw captures are expected to be populated into from the image source
    raw_captures_folder: Path = Path("") 

    # after a model runs inference (object detects on the raw captures folder), all captures with corresponding files will be moved to this folder
    # this is the folder that should be opened in Label-Detect-Verify during the verify part of the sequence (primary usage)
    detected_captures_folder: Path = Path("") 
    
    
    verified_captures_folder: Path = Path("")


    def to_dict(self):
        return asdict(self)


@dataclass
class LDVConfigs:
    ''' The final Configs compilation dataclass of all the other dataclasses '''
    folder_locations: FolderLocations = field(default_factory=FolderLocations)

    def to_dict(self):
        return asdict(self)

LDV_CONFIGS = LDVConfigs()