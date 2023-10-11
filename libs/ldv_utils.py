import os
import shutil
from xml.etree import ElementTree as ET

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
            for ext in ['jpg', 'png', 'jpeg']:
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
    
