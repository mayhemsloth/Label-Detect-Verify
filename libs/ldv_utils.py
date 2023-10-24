import os
import shutil
import random
import glob
import yaml
from xml.etree import ElementTree as ET

IMG_FILE_EXTENSIONS_ = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff'] # ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo'] in YOLOv7 loading

def clear_YOLO_dataset_folders(YOLO_dataset_folder):
    """
    Clears the temp YOLO dataset folder
    """
    # defining the folder paths
    all_folders = []
    for super_folder in ['images', 'labels']:
        one_path = os.path.join(YOLO_dataset_folder, super_folder)
        all_folders.append(one_path)

    for folder in all_folders:
        # clears the folders, so that new freshly random training source examples can populate it
        if os.path.exists(folder):
            shutil.rmtree(folder) # deletes entire directory tree and folder

def create_YOLO_dataset_folders(YOLO_dataset_folder):
    """
    Makes the temp YOLOv7 compatible dataset folder structure
    """
    # defining the folder paths images/train, images/valid, labels/train, labels/valid
    all_folders = []
    for super_folder in ['images', 'labels']:
        for sub_dir in ['train', 'valid']:
            one_path = os.path.join(YOLO_dataset_folder, super_folder, sub_dir)
            all_folders.append(one_path)
    
    for folder in all_folders:
        os.makedirs(folder, exist_ok=True) # makes the directory anew


def generate_class_mapping(input_dirs):
    """
    Generates the mapping of class names to class indices
    """
    class_names = set()
    for input_dir in input_dirs:
        for xml_file in glob.glob(os.path.join(input_dir, "*.xml")):
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for obj in root.findall("object"):
                class_name = obj.find("name").text
                class_names.add(class_name)

    class_mapping = {name: idx for idx, name in enumerate(sorted(class_names))} # note that Python dicts are now ordered dicts
    return class_mapping

def copy_files_to_YOLO_dataset_folder(training_source_folder, YOLO_dataset_folder, val_percentage=0.3):
    """
    Copies the image and XML files to the YOLO dataset folder structure. 
    Copies only those images that have corresponding XML files
    """
    # Get all image and XML file paths
    img_extensions = IMG_FILE_EXTENSIONS_
    img_files = [glob.glob(os.path.join(training_source_folder, f'*.{ext}')) for ext in img_extensions]
    img_files = [item for sublist in img_files for item in sublist]  # Flatten the list
    xml_files = glob.glob(os.path.join(training_source_folder, '*.xml'))

    # Create a list of file basenames that have both image and XML files
    img_basenames = set([os.path.basename(f).split('.')[0] for f in img_files])
    xml_basenames = set([os.path.basename(f).split('.')[0] for f in xml_files])
    common_basenames = list(img_basenames & xml_basenames)

    # Shuffle and split into training and validation sets
    random.shuffle(common_basenames)
    num_val = int(len(common_basenames) * val_percentage)
    val_set = set(common_basenames[:num_val])
    train_set = set(common_basenames[num_val:])

    # Copy image and XML files to respective training and validation folders
    for basename in common_basenames:
        img_file = next(f for f in img_files if (os.path.splitext(os.path.basename(f))[0] == basename)) # grabs the first file with same basename
        xml_file = os.path.join(training_source_folder, f"{basename}.xml")

        target_folder = 'valid' if basename in val_set else 'train'

        shutil.copy(img_file, os.path.join(YOLO_dataset_folder, 'images', target_folder))
        shutil.copy(xml_file, os.path.join(YOLO_dataset_folder, 'images', target_folder))

def copy_files_to_YOLO_test_folder(test_set_folder, temp_folder):
    """
    Copies the image and XML files to the YOLO test set folder structure. 
    Copies only those images that have corresponding XML files
    """
    # Get all image and XML file paths
    img_extensions = IMG_FILE_EXTENSIONS_
    img_files = [glob.glob(os.path.join(test_set_folder, f'*.{ext}')) for ext in img_extensions]
    img_files = [item for sublist in img_files for item in sublist]  # Flatten the list
    xml_files = glob.glob(os.path.join(test_set_folder, '*.xml'))

    # Create a list of file basenames that have both image and XML files
    img_basenames = set([os.path.basename(f).split('.')[0] for f in img_files])
    xml_basenames = set([os.path.basename(f).split('.')[0] for f in xml_files])
    common_basenames = list(img_basenames & xml_basenames)

    # Copy image and XML files to temporary test set folder
    for basename in common_basenames:
        img_file = next(f for f in img_files if (os.path.splitext(os.path.basename(f))[0] == basename)) # grabs the first file with same basename
        xml_file = os.path.join(test_set_folder, f"{basename}.xml")

        target_folder = 'test'

        shutil.copy(img_file, os.path.join(temp_folder, 'images', target_folder))
        shutil.copy(xml_file, os.path.join(temp_folder, 'images', target_folder))


def convert_voc_to_yolo(xml_path, class_mapping):
    """
    Converts the PASCAL VOC style bounding box annotations to to YOLO style bounding box annotations
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # get width and height of current image from VOC file
    img_width = int(root.find('size').find('width').text)
    img_height = int(root.find('size').find('height').text)
    img_channels = int(root.find('size').find('depth').text)

    yolo_annots = []

    for obj in root.findall("object"):
        class_name = obj.find("name").text
        class_idx = class_mapping[class_name]
        
        bbox = obj.find("bndbox")
        x_min = float(bbox.find("xmin").text)
        y_min = float(bbox.find("ymin").text)
        x_max = float(bbox.find("xmax").text)
        y_max = float(bbox.find("ymax").text)

        x_center = (x_min + x_max) / (2 * img_width)
        y_center = (y_min + y_max) / (2 * img_height)
        width = (x_max - x_min) / img_width
        height = (y_max - y_min) / img_height

        yolo_annots.append(f"{class_idx} {x_center} {y_center} {width} {height}")

    return "\n".join(yolo_annots)

def create_label_files(YOLO_dataset_folder, class_mapping):
    """
    Creates and saves the YOLO-compatible label files in the proper folders
    """

    for set_type in ['train', 'valid', 'test']:
        fldr_check = os.path.exists(os.path.join(YOLO_dataset_folder, 'images', set_type))  # can now use in both training set construction and test set construction
        xml_files = glob.glob(os.path.join(YOLO_dataset_folder, 'images', set_type, '*.xml')) if fldr_check else []
        for xml_file_path in xml_files:
            yolo_annotations = convert_voc_to_yolo(xml_file_path, class_mapping)  # does the converting from PASCAL VOC to YOLO style
            yolo_txt_path = os.path.join(YOLO_dataset_folder, 'labels', set_type, os.path.basename(xml_file_path).replace('.xml', '.txt'))
            
            with open(yolo_txt_path, 'w') as f:
                f.write(yolo_annotations)

def create_training_data_yaml_file(YOLO_dataset_folder, class_mapping):
    """
    Create a YAML file with given dataset paths and class mapping.
    
    Args:
    - dataset_path (str): The root folder for the dataset.
    - class_mapping (dict): Dictionary where keys are class names.
    """

    # construct paths
    train_path = os.path.join(YOLO_dataset_folder, 'images', 'train')
    val_path = os.path.join(YOLO_dataset_folder, 'images', 'valid')
    yaml_save_path = os.path.join(YOLO_dataset_folder, 'dataset_info.yaml')

    # Get class names and number of classes from the mapping
    class_names = sorted(list(class_mapping.keys())) # probably don't need the sorted, but whatever, just ensures previous sorted order
    num_classes = len(class_names)

    # Create the YAML data structure
    yaml_data = {
        "train": train_path,
        "val": val_path,
        "nc": num_classes,
        "names": class_names
    }

    # Write YAML file
    with open(yaml_save_path, 'w') as yaml_file:
        yaml.dump(yaml_data, yaml_file, sort_keys=False)

    return yaml_save_path

def update_nc_in_yaml(file_path, num_classes):
    """
    Update the 'nc' field in the YAML file with the new number of classes.
    
    Args:
    - file_path (str): Path to the existing YAML file.
    - num_classes (int): The new number of classes.
    """
    # Load existing YAML file
    with open(file_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    
    # Update 'nc' field
    yaml_data['nc'] = num_classes
    
    # Save updated YAML file back
    with open(file_path, 'w') as yaml_file:
        yaml.dump(yaml_data, yaml_file, sort_keys=False)

def train_model_file_helper(training_source_folder, temp_dataset_folder, model_config_yaml_path):
    """
    The helper function to be imported for primary functionality of Train Model action

    Args:
    - training_source_folder (str): The directory where training images and XML files are jointly are stored
    - temp_dataset_folder (str): The temp directory where the images/[train,valid] and labels/[train,valid] are created for YOLO compatibility
    - model_config_yaml_path (str): file path to where the 
    """

    # pre-emptive clear to reset the temporary folder
    clear_YOLO_dataset_folders(YOLO_dataset_folder=temp_dataset_folder)
    
    # create the YOLOv7 compatible dataset directories
    create_YOLO_dataset_folders(YOLO_dataset_folder=temp_dataset_folder)

    # generate class mapping dict of name to index, directly from the XML files. 
    # This is the ground truth for the class order
    class_mapping = generate_class_mapping(input_dirs=[training_source_folder])

    # locates all XML+image pairs in training source folder, splits into train and validation set, then copies over to images/{train,valid}
    copy_files_to_YOLO_dataset_folder(training_source_folder=training_source_folder,
                                      YOLO_dataset_folder=temp_dataset_folder,
                                      val_percentage=0.3)
    
    # create the YOLO style txt files and place in appropriate labels folders
    create_label_files(YOLO_dataset_folder=temp_dataset_folder, class_mapping=class_mapping)

    # create the YAML dataset file
    yaml_data_file_path = create_training_data_yaml_file(YOLO_dataset_folder=temp_dataset_folder, class_mapping=class_mapping)

    # update the model config YAML file (namely the number of classes value)
    update_nc_in_yaml(file_path=model_config_yaml_path, num_classes=len(class_mapping))

    return class_mapping, yaml_data_file_path


def move_verified_helper(last_open_dir, training_source_dir, optional_verified_dir=None):
    """
    The helper function to be imported for primary functionality of Move Verified Captures action
    Moves all VERIFIED images and associated files from the source directory to the training source directory.
    Optionally, copies the files to an additional directory.
    
    Args:
    - last_open_dir (str): The directory where currently opened/processed images are located.
    - training_source_dir (str): The directory where training images should be moved to.
    - optional_verified_dir (str, optional): An optional directory where copies of verified images can be stored.
    
    Returns:
    - report_str (str): The general report information relayed back
    """
    # Loop through all XML files in the source directory
    xml_file_list = [f for f in os.listdir(last_open_dir) if f.endswith('.xml')]
    num_xml_files_before = len(xml_file_list)
    num_verified_files_moved = 0

    for xml_file in xml_file_list:
        xml_path = os.path.join(last_open_dir, xml_file)

        # Parse the XML file to check for the 'verified' attribute
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Check if this image has been verified
        if root is not None and root.attrib.get('verified') == 'yes':
            # The corresponding image file should have the same name but different extension (e.g., .jpg, .png)
            img_file = xml_file.rsplit('.', 1)[0]  # Removing the .xml extension
            img_file_with_extension = None  # Initialize

            # Search for the image file with the corresponding name, and if found, set and break
            for ext in IMG_FILE_EXTENSIONS_:
                possible_img_file = f"{img_file}.{ext}"
                if os.path.exists(os.path.join(last_open_dir, possible_img_file)):
                    img_file_with_extension = possible_img_file
                    break

            # If corresponding image file is found, proceed to move
            if img_file_with_extension:
                # Move image and XML to the training source directory
                shutil.move(os.path.join(last_open_dir, img_file_with_extension), 
                            os.path.join(training_source_dir, img_file_with_extension))
                shutil.move(xml_path, os.path.join(training_source_dir, xml_file))
                num_verified_files_moved += 1

                # Optionally, move a copy to the optional verified directory as well
                if optional_verified_dir:
                    shutil.copy(os.path.join(training_source_dir, img_file_with_extension),
                                os.path.join(optional_verified_dir, img_file_with_extension))
                    shutil.copy(os.path.join(training_source_dir, xml_file),
                                os.path.join(optional_verified_dir, xml_file))
    
    new_xml_file_list = [f for f in os.listdir(last_open_dir) if f.endswith('.xml')]
    num_xml_files_after = len(new_xml_file_list)

    # construct final report str
    report_str = f"{num_verified_files_moved} Verified XML Files and associated images were moved to training source directory. \
        XML files before: {num_xml_files_before}. After: {num_xml_files_after} in {last_open_dir}."
    if optional_verified_dir:
        report_str += f" Additionally, {num_verified_files_moved} were copied to {optional_verified_dir}"

    return report_str

def construct_voc_from_yolo_annotations(img_full_path, yolo_annotations, class_mapping, imgsize, difficult_thresh=0.5):
    """
    Constructs the ElementTree object for the PASCAL VOC style annotations
    """

    index_to_class_mapping = {v:k for k,v in class_mapping.items()} # reverses the class mapping {'name': idx} to {idx : 'name'}

    # Create XML root element
    root = ET.Element('annotation')
    
    # Extract image size details
    height, width, channel = imgsize
    
    # Add image metadata
    ET.SubElement(root, 'folder').text = str(os.path.basename(os.path.dirname(img_full_path))) # gets the last folder name
    ET.SubElement(root, 'filename').text = str(os.path.basename(img_full_path))  # just the basename with the extension
    ET.SubElement(root, 'path').text = img_full_path   # the entire file path to the image (which will ultimately be wrong, but that's fine)
    
    source = ET.SubElement(root, 'source')
    ET.SubElement(source, 'database').text = 'Unknown'
    
    size = ET.SubElement(root, 'size')
    ET.SubElement(size, 'width').text = str(width)
    ET.SubElement(size, 'height').text = str(height)
    ET.SubElement(size, 'depth').text = str(channel)
    
    ET.SubElement(root, 'segmented').text = '0'
    
    if yolo_annotations:  # file has already been read. If there was no file, yolo_annotations should be None, so won't enter this part at all. 
        for line in yolo_annotations:
            parts = line.strip().split(" ")
            confidence = None
            if len(parts) == 6:  # the confidence score could be loaded in the .txt labels file. Let's handle it and integrate it into difficult label later
                class_idx, x_center, y_center, width_rel, height_rel, confidence = map(float, parts)
            else:
                class_idx, x_center, y_center, width_rel, height_rel = map(float, parts)
            class_idx=int(class_idx)
            
            # Convert YOLO to VOC
            x_center, y_center, width_rel, height_rel = x_center * width, y_center * height, width_rel * width, height_rel * height
            xmin, ymin, xmax, ymax = x_center - width_rel / 2, y_center - height_rel / 2, x_center + width_rel / 2, y_center + height_rel / 2
            
            # Create object element and append to root
            obj = ET.SubElement(root, 'object')
            ET.SubElement(obj, 'name').text = index_to_class_mapping.get(class_idx, "Unknown Class")
            ET.SubElement(obj, 'pose').text = 'Unspecified'
            ET.SubElement(obj, 'truncated').text = '0'
            ET.SubElement(obj, 'difficult').text = '1' if confidence and (confidence < difficult_thresh) else '0' # set difficult toggle when confidence under threshold 
            
            bbox = ET.SubElement(obj, 'bndbox')
            ET.SubElement(bbox, 'xmin').text = str(max(0, int(xmin)))
            ET.SubElement(bbox, 'ymin').text = str(max(0, int(ymin)))
            ET.SubElement(bbox, 'xmax').text = str(min(width, int(xmax)))
            ET.SubElement(bbox, 'ymax').text = str(min(height,int(ymax)))
    
    return ET.ElementTree(root)

def detect_raw_conversion_helper(raw_captures_dir, pred_labels_dir, class_mapping, imgname_to_imgsize):
    """
    The helper function to be imported and used within the Detect Raw Captures Action
    Helps AFTER the detections have been made by the importable detect.py function, to handle the
    proper massaging of the output of that function to what we want (PASCAL VOC files in the same folder) 

    Args:
    - raw_captures_dir (str): directory where the raw captures exist (and have just been detected)
    - pred_labels_dir (str): directory where the prediction labels are stored in .txt files of the same name as the image
    - class_mapping (dict): dictionary of {class_names: index}, originally taken from the model.names attribute
    - imgname_to_imgsize (dict): dictionary of { 'pic1.jpg' :  tuple of (H,W,Channels) } of all images that were predicted

    Returns:
    - None
    """

    # iterate through the image names that were known to have existed during the detection. 
    # Note, if no preds were made by model, no labels file would be created. We still want to handle this case and produce an "no labels" voc file
    for imgname, imgsize in imgname_to_imgsize.items():
        # path preparation
        img_full_path = os.path.join(raw_captures_dir, imgname)
        imgname_wo_ext, _ = os.path.splitext(imgname)
        labels_txt_full_path = os.path.join(pred_labels_dir, imgname_wo_ext+'.txt')   # expected in the prediction labels directory
        labels_xml_full_path = os.path.join(raw_captures_dir, imgname_wo_ext+'.xml')  # saving xml file to the raw captures directory, because it will be moved together with images to detected captures

        yolo_annotations = None
        if os.path.exists(labels_txt_full_path): # in the case where there EXISTS a labels text file with predictions
            try: # Read YOLO annotation lines from txt file
                with open(labels_txt_full_path, 'r') as f:
                    yolo_annotations = f.readlines()
            except Exception as e:
                print(f"An error {e} occured while attempting to load {labels_txt_full_path} which should exist.")
        xml_etree = construct_voc_from_yolo_annotations(img_full_path, yolo_annotations, class_mapping, imgsize)
        xml_etree.write(labels_xml_full_path)  # write the ElementTree object to XML file

def detect_raw_moving_helper(raw_captures_dir, detected_dir):
    """
    The helper function to be imported and used within the Detect Raw Captures Action
    Helps after the XML files have been created in the raw_captures_dir, and identifies and moves all the XML/image pairs
    into detected_dir. 

    Args:
    - raw_captures_dir (str):
    - detected_dir (str): 
    """

    xml_files = [f for f in os.listdir(raw_captures_dir) if f.endswith('.xml')]
    moving_counter = 0
    for xml_file in xml_files:
        xml_path = os.path.join(raw_captures_dir, xml_file)

        # parse the XML to get the associated image filename
        tree = ET.parse(xml_path)
        root = tree.getroot()
        image_filename = root.find('filename').text
        
        image_path = os.path.join(raw_captures_dir, image_filename)

        # move the XML and image files to detected_dir
        if os.path.exists(image_path):
            moving_counter += 1
            shutil.move(xml_path, os.path.join(detected_dir, xml_file))
            shutil.move(image_path, os.path.join(detected_dir, image_filename))
        else:
            print(f"Image file {image_filename} not found for {xml_file}")

    # construct final report str
    report_str = f"Of the {len(xml_files)} XML files found in the Raw Captures directory, {moving_counter} XML files and their associated images were moved to the Detected Captures"

    return report_str
    
def test_model_file_helper(test_set_folder, temp_test_folder, training_source_data_yaml_path):
    """
    The helper function to be importaed and used within the Test Model Action
    Helps with creating the test set YAML file and the folder structure (similar to the YOLO training dataset folder structure needed)
    Args:
    - test_set_folder (str): The directory where testing images and XML files are jointly are stored
    - temp_test_folder (str): The temp directory where the images/test and labels/test are created for YOLO compatibility
    """
    
    # pre-emptive clear to reset test's temporary folder
    # clears the folders, so that new freshly random training source examples can populate it
    if os.path.exists(temp_test_folder):
        #shutil.rmtree(temp_test_folder) # deletes entire directory tree and folder
        pass

    # create the YOLOv7 compatible test directory
    images_test_fldr = os.path.join(temp_test_folder, 'images', 'test')
    labels_test_fldr = os.path.join(temp_test_folder, 'labels', 'test')
    os.makedirs(images_test_fldr, exist_ok=True) # makes the directory anew
    os.makedirs(labels_test_fldr, exist_ok=True)

    # create the test YAML file
    yaml_save_path = os.path.join(temp_test_folder, 'test_set_info.yaml')
    # Get class names and number of classes from the file at training_source_data_yaml_path
    # Load existing YAML file
    with open(training_source_data_yaml_path, 'r') as f:
        training_source_data_yaml = yaml.safe_load(f)
    number_classes = training_source_data_yaml.get('nc', None)
    class_names = training_source_data_yaml.get('names', None)
    assert number_classes and class_names, f"Error loading the 'nc' and 'names' keys from the {training_source_data_yaml_path} YAML file"
    class_mapping = {name: idx for idx, name in enumerate(class_names)}
    # Create the YAML data structure
    yaml_data = {
        "test": images_test_fldr,
        "nc": number_classes,
        "names": class_names
    }
    # Write YAML file
    with open(yaml_save_path, 'w') as yaml_file:
        yaml.dump(yaml_data, yaml_file, sort_keys=False)

    # locates all XML+image pairs in test set folder then copies over to images/test
    copy_files_to_YOLO_test_folder(test_set_folder=test_set_folder,
                                   temp_folder=temp_test_folder)
    
    # create the YOLO style txt files and place in appropriate labels folders
    create_label_files(YOLO_dataset_folder=temp_test_folder, class_mapping=class_mapping)

    return yaml_save_path
