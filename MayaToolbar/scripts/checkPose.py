import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import json
import sys
import os

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class SimpleUI(QtWidgets.QDialog):
    """
    PySide UI
    """

    def __init__(self, parent=maya_main_window()):
        
        input_path = os.path.normpath("C:\\tmp\\bone_data.json")
        
        # Read data from file and check if file exists and is not empty
        file_name = "empty"
        frame_number = "empty"       
        if not os.path.exists(input_path):
            os.makedirs(os.path.dirname(input_path))
        else:
            try:
                with open(input_path, "r") as infile:
                    json_string = infile.read()
                    if not json_string:
                        pass
                    else:
                        stored_bone_data = json.loads(json_string)   
                        file_name = stored_bone_data.get("stored_file", "empty")
                        frame_number = stored_bone_data.get("frame_number", "empty")
            except:
                pass
        
        # Create layout settings
        super(SimpleUI, self).__init__(parent)
        self.setWindowTitle("Pose Compare Tool")
        #self.setFixedSize(300, 200)

        # Create widgets
        self.label = QtWidgets.QLabel("Current Saved File: " + file_name)
        self.file_path_label = QtWidgets.QLabel("Saved Frame Number: " + str(frame_number))
        self.record_data_button = QtWidgets.QPushButton("Record Data")
        self.read_data_button = QtWidgets.QPushButton("Read Data")

        # Create layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.file_path_label)
        layout.addWidget(self.record_data_button)
        layout.addWidget(self.read_data_button)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Connect signals
        self.record_data_button.clicked.connect(self.record_data)
        self.read_data_button.clicked.connect(self.read_data)

    def record_data(self):
        """
        Record current bone data to txt file
        """
        # Get all bones in the scene
        bones = cmds.ls(type='joint')
        
        #create dictionary to store skeleton information
        stored_bone_data = {}
        
        # Iterate through each bone
        for bone in bones:
            
            # Get the translation and rotation values for the bone at the current frame
            translation = cmds.xform(bone, query=True, translation=True)
            rotation = cmds.xform(bone, query=True, rotation=True)
            # If translation and rotation values are less than 0.001, make them 0.0
            translation = [0.0 if abs(val) < 0.001 else round(val, 3) for val in translation]
            rotation = [0.0 if abs(val) < 0.001 else round(val, 3) for val in rotation]
            
            # Add the translation and rotation values to the dictionary for the current bone
            stored_bone_data[bone] = {'translation': translation, 'rotation': rotation}
            
        # Add current file path and frame number to the dictionary
        stored_file_path = cmds.file(query=True, sceneName=True)
        stored_file = os.path.basename(stored_file_path)
        frame_number = cmds.currentTime(query=True)
        stored_bone_data['stored_file'] = stored_file
        stored_bone_data['frame_number'] = frame_number

        output_path = os.path.normpath("C:\\tmp\\bone_data.json")
        
        # Convert the dictionary to a JSON string
        json_string = json.dumps(stored_bone_data)
        
        # Open a file for writing
        try:
            with open(output_path, "w") as outfile:
                # Write the JSON string to the file
                outfile.write(json_string)
        except FileNotFoundError:
            cmds.warning("File Not Found!")
            return
   
        # Confirm Process Complete        
        cmds.warning("Data Saved!")
        
    def read_data(self):
        """
        Read bone data from txt file and compare to current frame
        """
        
        # Get all bones in the scene
        bones = cmds.ls(type='joint')
        
        #create dictionary to store skeleton information
        current_bone_data = {}
        
        # Iterate through each bone
        for bone in bones:
            
            # Get the translation and rotation values for the bone at the current frame
            translation = cmds.xform(bone, query=True, translation=True)
            rotation = cmds.xform(bone, query=True, rotation=True)
            # If translation and rotation values are less than 0.001, make them 0.0
            translation = [0.0 if abs(val) < 0.001 else round(val, 3) for val in translation]
            rotation = [0.0 if abs(val) < 0.001 else round(val, 3) for val in rotation]
            
            # Add the translation and rotation values to the dictionary for the current bone
            current_bone_data[bone] = {'translation': translation, 'rotation': rotation}

        input_path = os.path.normpath("C:\\tmp\\bone_data.json")
        # Open the file for reading
        with open(input_path, "r") as infile:
            # Read the JSON string from the file
            json_string = infile.read()
    
        # Convert the JSON string to a dictionary
        stored_bone_data = json.loads(json_string)
    
        # Compare the current values to the values in the dictionary
        badBones = []
        match = True
        for bone in stored_bone_data:
            if bone != 'stored_file':
                if bone != 'frame_number':
                    if stored_bone_data[bone] != current_bone_data[bone]:
                        match = False
                        badBones.append(bone)
        if match == True:
            QtWidgets.QMessageBox.information(None, 'MATCH', 'All bones rotations and translations match!')
        else:
            QtWidgets.QMessageBox.information(None, 'DO NOT MATCH', 'The values for these bones do not match:\n' + '\n'.join(badBones))        
        
ui = SimpleUI()
ui.show()