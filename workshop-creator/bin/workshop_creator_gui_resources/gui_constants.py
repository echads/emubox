import os
#TODO: make this file editable through the GUI somehow
# Constants
BOX_SPACING = 5
PADDING = 5
WORKSHOP_CONFIG_DIRECTORY = os.path.join(os.getcwd(),"workshop_creator_gui_resources","workshop_configs")
WORKSHOP_MATERIAL_DIRECTORY = os.path.join(os.getcwd(),"workshop_creator_gui_resources","workshop_materials")
WORKSHOP_RDP_DIRECTORY = os.path.join(os.getcwd(), "workshop_creator_gui_resources","workshop_rdp")
GUI_MENU_DESCRIPTION_DIRECTORY = os.path.join(os.getcwd(),"workshop_creator_gui_resources","menuDescription.xml")
VBOXMANAGE_DIRECTORY = "C:/Program Files/Oracle/VirtualBox/VBoxManage.exe"
#TODO: make this just the directory
WORKSHOP_CREATOR_FILE_PATH = os.path.join(os.getcwd(),"workshop-creator.py")
WORKSHOP_RDP_CREATOR_FILE_PATH = os.path.join(os.getcwd(),"workshop-rdp.py")
WORKSHOP_RESTORE_FILE_PATH = os.path.join(os.getcwd(),"workshop-restore.py")
MANAGER_SAVE_DIRECTORY = os.path.join(os.getcwd(),"..","workshop-manager","bin","WorkshopData")
