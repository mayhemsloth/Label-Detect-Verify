# Label-Detect-Verify configurations
# In order to use Label-Detect-Verify properly, 
# this configuration file must be properly populated. 
# Do not change any of the attribute names, only the actual input

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Union
from pathlib import Path

@dataclass
class Training:

    # ---
    epochs: int = 20   # total number of epochs to train for
    batch_size: int = 4 # should be changed if you hit 
    img_input_size: List[int] =  field(init=False)  # see __post_init__ below for setting these
    workers: int = 2    # number of workers for data loaders

    # ---- Generally Don't Touch These ---- #
    yolov7_model_type: str = 'yolov7x'   # default will be yolov7x, other options are yolov7, yolov7-tiny, yolov7-e6e. But must download the weights files
    weights_filepath: str = str(Path(yolov7_model_type+'_training.pt')) # expects, from initial setup, to have the pre-trained weights in the home folder of yolov7 
    cfg_yaml_filepath: str= str(Path('cfg', 'training', yolov7_model_type+'.yaml'))
    hyperparameter_yaml_filepath: str = str(Path('data', 'hyp.scratch.custom.yaml'))
    use_adam = True

    def __post_init__(self):
        self.img_input_size = [1280, 1280] # images will be automatically resized to the square (X,X)
                                           # for training and test dataset purposes [X, Y] => ((X,X)_training, (Y,Y)_test)
    def to_dict(self):
        return asdict(self)

@dataclass
class LDVConfigs:
    ''' The final Configs compilation dataclass of all the other dataclasses '''

    training: Training = field(default_factory=Training)
    # stems_prep: StemsPrep =  field(default_factory=lambda: StemsPrep(stems_to_load=STEMS_TO_USE_, standard_sr=STANDARD_SR_))

    def to_dict(self):
        return asdict(self)

LDV_CONFIGS = LDVConfigs()

