# Label-Detect-Verify configurations
# In order to use Label-Detect-Verify properly, 
# this configuration file must be properly populated. 
# Do not change any of the attribute names, only the actual input

from dataclasses import dataclass, field, asdict
from typing import List
from pathlib import Path

@dataclass
class Training:
    ''' Configurations used for Training '''

    # ---- Generally these can and should be changed ---- #
    epochs: int = 400       # total number of epochs to train for. If you don't like performance, try to train longer, or label more high quality data for low performance classes
    batch_size: int = 4      # should be lowered if you hit out of memory errors. Generally works best with a factor of 2 (1,2,4,8,16,32,64 are all good if you have the memory)
    img_input_size: List[int] =  field(init=False)  # PLEASE SEE __post_init__ BELOW for setting this configuration
    yolov7_model_type: str = 'yolov7x'   # default will be yolov7x, other options are yolov7, yolov7-tiny, yolov7-e6e. But MUST download the corresponding weights files

    # ---- Generally Don't Touch These ---- #
    weights_filepath: str = str(Path(yolov7_model_type+'_training.pt'))  # expects, from initial setup, to have the pre-trained weights in the home folder of yolov7 
    cfg_yaml_filepath: str = str(Path('cfg', 'training', yolov7_model_type+'.yaml'))  # note that these file paths are with respect to the yolov7 folder, because we change dir in the code
    hyperparameter_yaml_filepath: str = str(Path('data', 'hyp.scratch.custom.yaml')) # further hyperparameters (like data augmentation) are stored in this YAML file
    use_adam = True              # use the Adam optimizer, because duh
    device: str = '0'            # defaults to trying to use a single GPU, but will fall back to CPU via the YOLOv7 code if not available
    workers: int = batch_size    # number of workers for data loaders. Lower this to 1 or 0 if any weird dataloader/workers error shows up. 

    def __post_init__(self):
        self.img_input_size = [1280, 1280] # during training, images will be automatically resized to the square (X,X) with padding
                                           # for training and validation dataset purposes [First, Second] => ((First, First)_training, (Second, Second)_validation)
                                           # Note: each value must be an integer multiple of 32. (640, 960, 1280, 1600, 1920 are all good candidates)
    def to_dict(self):
        return asdict(self)

@dataclass 
class Inference:
    ''' Configurations used for Inference (Detection)'''

    img_input_size: int = 1280            # should be the same as the training input image size for best performance
    confidence_threshold: float = 0.3     # any bounding boxes whose confidence score is below this will NOT be considered a detected object. [0-1]. Lower values produces more "guesses". Higher values produces fewer, more confident boxes.
    iou_threshold: float = 0.45           # any additional bounding boxes predicting the same class with an IOU OVER this threshold will be thrown out (except 1) due to assumption they are the same instance of that class
    device: str = '0'                     # defaults to trying to use a single GPU, but will fall back to CPU via the YOLOv7 code if not available
    batch_size: int = 1                   # during inference batch size does not really matter, so we set at 1
    overwrite_test_set_res: bool = True   # if True, during the Test Model action, will overwrite the test results folder created inside the selected model folder. IE, only keep the last run test set for each model

    def to_dict(self):
        return asdict(self)

@dataclass
class LDVConfigs:
    ''' The final Configs compilation dataclass of all the other dataclasses '''

    training: Training = field(default_factory=Training)
    inference: Inference = field(default_factory=Inference)

    def to_dict(self):
        return asdict(self)

LDV_CONFIGS = LDVConfigs()

