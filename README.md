# Label-Detect-Verify (LDV)

Label-Detect-Verify (LDV) is an open source project by Thomas Hymel to combine the functionalities of two other open source project: [LabelImg](https://github.com/HumanSignal/labelImg) (simple PyQt-based GUI for labeling objects in images and saving bounding box labels) and [YOLOv7](https://github.com/WongKinYiu/yolov7) (training code and pre-trained weights for object detection model) into one simple-to-use GUI for creating labels, training a model locally on those labels, detecting new images, and verifying the new detections for an all-in-one, human-in-the-loop, object detection solution for extracting domain-specific information from RGB images. Far below is the original README (with some small picture-focused edits and changed to Markdown) of the forked LabelImg repo. This repo was forked from LabelImg, and then the YOLOv7 code was copied into the `yolov7` folder inside the LDV repo.

## Use Cases
LDV may be useful for you if you have the following object detection design requests:

- To automate most of a knowledge extraction task from a consistent source of domain-specific RGB imagery (may support single channel images? but not tested)
- To have human verification be the final judgment for the predicted labels
- To utilize the structured bounding box data in some further processing pipeline (by transferring verified images and XML files to an optional extra folder)
- To use local computation and storage to complete the model training and detection for ensuring privacy/proprietary data purposes
- To not need to know that much Python or machine learning to utilize the recent incredible advances in computer vision

## Limitations
Notable Out of Scope Features (what LDV is not):

- LDV is NOT a scalable solution for generic object detection. It is specifically for fine-tuning on a small dataset. It needs to learn from a high-quality, well-labeled dataset to perform well.
- LDV does NOT support cloud-based computation for training or inference, and is not designed with "Dockerization" in mind.

## To-Do List:

- **Complete a robust README, with clear Installation, Initial Setup, and Normal Usage guides.**
- **Make the output of Test Model Action more user friendly.** Right now the Test Model is basically the same as the original `test.py` script from YOLOv7, which isn't the most user-friendly output. The Test Model action is focused on testing a model on your test set, so I want an quick, at-a-glance summary with real examples comparing the predicted bounding boxes overlaid on the images alongside an image with the the actual ground truth bounding boxes overlaid on the images. 
- **Fundamentally change the dataloader code to eliminate the temporary copying of dataset.** The YOLOv7 dataloader code requires a very folder-specific structure for loading in the data. This structure is not human-friendly for LDV purposes, as I made the decision to have a single training source folder, and a test set folder, and the validation set is randomly chosen each training run with a 70:30 split across the training source folder. For these reasons, my hacky solution was to simply copy the files into a temporary folder structure, and then delete the copies after they are needed. This feels bad and should be changed.
- **Ensure single channel images are supported by LDV** (that is, histogram-like imaging works well with LabelImg GUI and YOLOv7 automatically handles the casting/copying into 3 channel dimensions)


# Label-Detect-Verify Installation Instructions

1. **Install Dependencies**

   - [**Python**](https://www.python.org/downloads/windows/)  
      - Make sure you choose the correct installer for your operating system (Windows, Mac, or Linux).  
      - During the installation on Windows, you may want to check the option to “Add Python to PATH” to simplify running Python from the command prompt.

2. **Clone the Label-Detect-Verify repository**  
   - Use a version control tool like [Git](https://git-scm.com/downloads) to clone the repository:
     ```shell
     git clone https://github.com/YourUsername/Label-Detect-Verify.git
     ```
   - You can clone it to any folder you like. The actual location doesn’t have to be near your data or project folders. You will specify other paths later when running the program.
   - If you’re not comfortable with Git, you can also download the repository as a ZIP file from GitHub and extract it anywhere you want.

3. **Set up a Python virtual environment**  
   - Virtual environments help isolate project-specific dependencies and avoid potential conflicts with other Python projects on your machine.  
   - You can set up a virtual environment using [venv](https://docs.python.org/3/library/venv.html) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).  
   - Example using **venv** in your project folder:
     ```shell
     python -m venv venv
     ```
     Then activate it:  
     - **Windows**:
       ```shell
       venv\Scripts\activate
       ```
     - **Mac/Linux**:
       ```shell
       source venv/bin/activate
       ```

4. **Install Required Python Packages**
    1. After ensuring that your virtual environment is activated, open your command prompt or terminal and navigate (using `cd`) to the folder where you cloned **Label-Detect-Verify**. 
    2. Run the following command to install the required packages in this environment.
        ```shell
        pip install -r requirements.txt
        ```


5. **Compile LDV resources**  
   1. Open your command prompt or terminal and navigate (using `cd`) to the folder where you cloned **Label-Detect-Verify**.  
   2. Run the following command to compile the necessary resource files:
      ```shell
      pyrcc5 -o libs/resources.py resources.qrc
      ```
   - This is a one-time compilation step to convert `.qrc` files (Qt resource files) into a Python file so PyQt can use them properly.

6. **Download YOLOv7 pre-trained weights**  
   - Go to the [YOLOv7 repository](https://github.com/WongKinYiu/yolov7) or its releases page where pre-trained `.pt` files are provided. Common files are:
     - `yolov7x.pt`
     - `yolov7.pt`
     - `yolov7-tiny.pt`
     - `yolov7-e6e.pt`
   - These files are slightly different model architectures with varying accuracy and performance.  
   - **Important:** Place these `.pt` files inside the `yolov7` folder in your cloned **Label-Detect-Verify** repository. This location is where the program will look for them.
   - These weights are the things that will ultimately be changed during your training runs, but these will always be kept constant as a fantastic starting point to make it very easy to get to the custom class output.

7. **Using Label-Detect-Verify**  
   1. Activate your virtual environment (if not already activated).  
   2. Navigate to the Label-Detect-Verify directory (where `LDV.py` is located).  
   3. Run:
      ```shell
      python LDV.py
      ```
   - This should launch the LDV application in a new, stand alone window. You can now configure where to store images, set up new project folders, and start using the tool. Note that the terminal from which you launched LDV will print out useful information during some actions and needs to be kept open for LDV window to persist.


### Installation Troubleshooting Tips

- If you run into permission issues while installing Python packages, try adding `--user` to the pip install command (e.g., `pip install --user lxml`), or make sure you’re in an activated virtual environment.  
- If you have issues installing lxml on Windows, consider installing [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) or using [conda](https://docs.conda.io/en/latest/).  
- Ensure the YOLOv7 `.pt` files are placed in the correct folder; otherwise, the program will not find them.

---

# Usage Guide

The overview usage flow of Label-Detect-Verify is the following:

1. Install properly following the instructions above (done only once).
2. First Time Setup following the instructions below (done only once per project).
3. Manually label your training dataset (this is the LabelImg functionality)
4. Train a model (this is the YOLOv7 functionality)
5. Populate the Raw Captures folder with new images that need to be predicted with object detections from a distribution similar to the images that you have labeled
6. Detect the Raw Captures folder using a trained model
7. Verify the detections as already correct, or correct them and then verify them
8. Repeat steps 4 through 7 as needed to get a better and better model, or add more classes to detect.

The additional Label-Detect-Verify components built into the LabelImg framework consists of 4 primary actions, seen in the `LDV Actions` drop down menu of the toolbar. Because these are meaningfully important, non-destructive but also generally non-undoable actions, there is a Confirm Action Pop-up message to confirm any of these actions. That pop-up message itself is toggleable on and off.

1. **Detect Raw Captures** - This action first checks if there are any valid images present in the set Raw Captures folder. If there are, then it automatically looks for and selects a trained model directory to use for detection purposes. The model is selected based on the best results of the validation set metrics *during its own training run*. Optionally, you may select which model to use with the Optional Settings under the `LDV Settings` drop down menu of the toolbar. After detection, the images in the Raw Captures folder are automatically moved into the `detected_captures` project subfolder (which should be the primary, usual working directory opened in LabelImg) to faciliate validation!

2. **Move Verified Captures** - This action moves all *verified* images (images with the yellow/green background: verified status is toggled with the `spacebar` hotkey) and associated label files from the currently opened directory to the `training_source` project subfolder. Optionally, if the Verified Output folder is set than ALSO move a copy of all verified images to that location as well. This optional Verified Output folder is provided if you care to process the data further externally, for example, to run some other script that automatically integrates the newly verified outputs into a database which can then apply further logic to make decisions.
3. **Train Model** - This action, after ensuring the `training_source` subfolder is not empty, trains a new model on the entirety of images in the `training_source` subfolder. The training configuration is set by the `ldv_config.py` file (more on that below). All the necessary model information, including the weights, are stored in the `trained_models` project subfolder. The terminal will update with some information about the the training of the model.
4. **Test Model** - This action, after ensuring the `test_set` subfolder is not empty, tests the selected model on the test set of images. These images should not ever be a part of the `training_source`, and should be manually labeled and kept entirely separate in the `test_set` folder. This set of images could function as some of the "hardest" images in your distribution to detect properly, or it could simply function as a solid representation to test the models against.


---

## First Time Setup Explanation and Instructions

After installation and first start up, there are a few things to do. 

- Set the Project Folder
- Move your starting training image set into the `training_source` subfolder of your project.
- Open up, look at, and configure the file `ldv_config.py`.
- Set the Raw Captures Folder


--- 

#### Below this point is the original LabelImg README file convert to Markdown, kept for historical purposes.

---

# About LabelImg

![PyPI version](https://img.shields.io/pypi/v/labelimg.svg)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/tzutalin/labelImg/Package?style=for-the-badge)
![Language: English](https://img.shields.io/badge/lang-en-blue.svg)
![Language: Chinese](https://img.shields.io/badge/lang-zh-green.svg)
![Language: Japanese](https://img.shields.io/badge/lang-jp-green.svg)

LabelImg, the popular image annotation tool created by Tzutalin with the help of dozens contributors, is no longer actively being developed and has become part of the Label Studio community. Check out [Label Studio](https://github.com/heartexlabs/label-studio), the most flexible open source data labeling tool for images, text, hypertext, audio, video and time-series data. [Install Label Studio](https://labelstud.io/guide/install.html) and join the [slack community](https://label-studio.slack.com/) to get started.

LabelImg is a graphical image annotation tool.

It is written in Python and uses Qt for its graphical interface.

Annotations are saved as XML files in PASCAL VOC format, the format used by [ImageNet](http://www.image-net.org/). Besides, it also supports YOLO and CreateML formats.

![Demo Image](https://raw.githubusercontent.com/tzutalin/labelImg/master/demo/demo3.jpg)
![Demo Image](https://raw.githubusercontent.com/tzutalin/labelImg/master/demo/demo.jpg)

[Watch a demo video](https://youtu.be/p0nR2YsCY_U)

## Installation

### Get from PyPI but only python3.0 or above
This is the simplest (one-command) install method on modern Linux distributions such as Ubuntu and Fedora.

```shell
pip3 install labelImg
labelImg
labelImg [IMAGE_PATH] [PRE-DEFINED CLASS FILE]
```

# Build from source

Linux/Ubuntu/Mac requires at least [Python 2.6](https://www.python.org/getit/) and has been tested with [PyQt 4.8](https://www.riverbankcomputing.com/software/pyqt/intro). However, [Python 3 or above](https://www.python.org/getit/) and [PyQt5](https://pypi.org/project/PyQt5/) are strongly recommended.

## Ubuntu Linux

### Python 3 + Qt5

```shell
sudo apt-get install pyqt5-dev-tools
sudo pip3 install -r requirements/requirements-linux-python3.txt
make qt5py3
python3 labelImg.py
python3 labelImg.py [IMAGE_PATH] [PRE-DEFINED CLASS FILE]
```

## macOS

### Python 3 + Qt5

```shell
brew install qt  # Install qt-5.x.x by Homebrew
brew install libxml2

# or using pip

pip3 install pyqt5 lxml # Install qt and lxml by pip

make qt5py3
python3 labelImg.py
python3 labelImg.py [IMAGE_PATH] [PRE-DEFINED CLASS FILE]
```

### Python 3 Virtualenv (Recommended)

Virtualenv can avoid a lot of the QT / Python version issues.

```shell
brew install python3
pip3 install pipenv
pipenv run pip install pyqt5==5.15.2 lxml
pipenv run make qt5py3
pipenv run python3 labelImg.py
# [Optional] rm -rf build dist; pipenv run python setup.py py2app -A;mv "dist/labelImg.app" /Applications
```

> Note: The Last command gives you a nice .app file with a new SVG Icon in your /Applications folder. You can consider using the script: build-tools/build-for-macos.sh

## Windows

Install [Python](https://www.python.org/downloads/windows/), [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5) and [install lxml](http://lxml.de/installation.html).

Open cmd and go to the [labelImg](#labelimg) directory

```shell
pyrcc4 -o libs/resources.py resources.qrc
# For pyqt5, pyrcc5 -o libs/resources.py resources.qrc

python labelImg.py
python labelImg.py [IMAGE_PATH] [PRE-DEFINED CLASS FILE]
```

If you want to package it into a separate EXE file

```shell
# Install pyinstaller and execute:

pip install pyinstaller
pyinstaller --hidden-import=pyqt5 --hidden-import=lxml -F -n "labelImg" -c labelImg.py -p ./libs -p ./
```

### Windows + Anaconda

Download and install [Anaconda](https://www.anaconda.com/download/#download) (Python 3+)

Open the Anaconda Prompt and go to the [labelImg](#labelimg) directory

```shell
conda install pyqt=5
conda install -c anaconda lxml
pyrcc5 -o libs/resources.py resources.qrc
python labelImg.py
python labelImg.py [IMAGE_PATH] [PRE-DEFINED CLASS FILE]
```

## Use Docker

```shell
docker run -it \
--user $(id -u) \
-e DISPLAY=unix$DISPLAY \
--workdir=$(pwd) \
--volume="/home/$USER:/home/$USER" \
--volume="/etc/group:/etc/group:ro" \
--volume="/etc/passwd:/etc/passwd:ro" \
--volume="/etc/shadow:/etc/shadow:ro" \
--volume="/etc/sudoers.d:/etc/sudoers.d:ro" \
-v /tmp/.X11-unix:/tmp/.X11-unix \
tzutalin/py2qt4

make qt4py2;./labelImg.py
```

You can pull the image which has all of the installed and required dependencies. [Watch a demo video](https://youtu.be/nw1GexJzbCI)

## Usage

### Steps (PascalVOC)

1. Build and launch using the instructions above.
2. Click 'Change default saved annotation folder' in Menu/File
3. Click 'Open Dir'
4. Click 'Create RectBox'
5. Click and release left mouse to select a region to annotate the rect box
6. You can use right mouse to drag the rect box to copy or move it

The annotation will be saved to the folder you specify.

You can refer to the below hotkeys to speed up your workflow.

### Steps (YOLO)

1. In `data/predefined_classes.txt` define the list of classes that will be used for your training.
2. Build and launch using the instructions above.
3. Right below "Save" button in the toolbar, click "PascalVOC" button to switch to YOLO format.
4. You may use Open/OpenDIR to process single or multiple images. When finished with a single image, click save.

A txt file of YOLO format will be saved in the same folder as your image with same name. A file named "classes.txt" is saved to that folder too. "classes.txt" defines the list of class names that your YOLO label refers to.

**Note:**

- Your label list shall not change in the middle of processing a list of images. When you save an image, classes.txt will also get updated, while previous annotations will not be updated.
- You shouldn't use "default class" function when saving to YOLO format, it will not be referred.
- When saving as YOLO format, "difficult" flag is discarded.

### Create pre-defined classes

You can edit the [`data/predefined_classes.txt`](https://github.com/tzutalin/labelImg/blob/master/data/predefined_classes.txt) to load pre-defined classes.

### Annotation visualization

1. Copy the existing labels file to same folder with the images. The labels file name must be same with image file name.
2. Click File and choose 'Open Dir' then Open the image folder.
3. Select image in File List, it will appear the bounding box and label for all objects in that image.

(Choose Display Labels mode in View to show/hide labels)

### Hotkeys

| Key              | Function                                  |
|------------------|-------------------------------------------|
| Ctrl + u         | Load all of the images from a directory   |
| Ctrl + r         | Change the default annotation target dir  |
| Ctrl + s         | Save                                      |
| Ctrl + d         | Copy the current label and rect box       |
| Ctrl + Shift + d | Delete the current image                  |
| Space            | Flag the current image as verified        |
| w                | Create a rect box                         |
| d                | Next image                                |
| a                | Previous image                            |
| del              | Delete the selected rect box              |
| Ctrl++           | Zoom in                                   |
| Ctrl--           | Zoom out                                  |
| ↑→↓←             | Keyboard arrows to move selected rect box |

#### Verify Image:

When pressing space, the user can flag the image as verified, a green background will appear.
This is used when creating a dataset automatically, the user can then go through all the pictures and flag them instead of annotating them.

#### Difficult:

The "difficult" field is set to 1 and indicates that the object has been annotated as "difficult," for example, an object which is clearly visible but difficult to recognize without substantial use of context.
According to your deep neural network implementation, you can include or exclude difficult objects during training.

### How to Reset the Settings

In case there are issues with loading the classes, you can either:

1. From the top menu of labelImg, click on `Menu/File/Reset All`
2. Remove the `.labelImgSettings.pkl` from your home directory. In Linux and Mac, you can execute: `rm ~/.labelImgSettings.pkl`

### How to Contribute

Send a pull request.

### License

[Free software: MIT license](https://github.com/tzutalin/labelImg/blob/master/LICENSE)

Citation: Tzutalin. LabelImg. Git code (2015). [https://github.com/tzutalin/labelImg](https://github.com/tzutalin/labelImg)

### Related and Additional Tools

1. [Label Studio](https://github.com/heartexlabs/label-studio) to label images, text, audio, video and time-series data for machine learning and AI.
2. [ImageNet Utils](https://github.com/tzutalin/ImageNet_Utils) to download images, create a label text for machine learning, etc.
3. [Use Docker to run labelImg](https://hub.docker.com/r/tzutalin/py2qt4)
4. [Generating the PASCAL VOC TFRecord files](https://github.com/tensorflow/models/blob/4f32535fe7040bb1e429ad0e3c948a492a89482d/research/object_detection/g3doc/preparing_inputs.md#generating-the-pascal-voc-tfrecord-files)
5. App Icon based on Icon by Nick Roach (GPL) from [Elegant Themes](https://www.elegantthemes.com/)
6. [Setup Python development in VSCode](https://tzutalin.blogspot.com/2019/04/set-up-visual-studio-code-for-python-in.html)
7. [The link of this project on iHub platform](https://code.ihub.org.cn/projects/260/repository/labelImg)
8. [Convert annotation files to CSV format or format for Google Cloud AutoML](https://github.com/tzutalin/labelImg/tree/master/tools)

### Stargazers Over Time

![Stargazers Over Time](https://starchart.cc/tzutalin/labelImg.svg)

