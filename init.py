import database_access
import json
from pathlib import Path
import os 

def init_check():
    # check file {init} exist or not
    # if not exist mean database not initialized, return "not_init"
    # if exist, check if the file is empty or not
    # if empty, mean database not initialized, return "not_init"
    # if not empty, mean database initialized, return "init_finished"

    try:
        init_file = Path("init")
        if init_file.is_file():
            with open("init", "r") as f:
                init = f.read()
            if init == "init_finished":
                return "already_initalized"
            else:
                return "not_init"
        else:
            return "not_init"
    except Exception as e:
        print(e)
        return "failure"
        
def initialization():
    try:
        os.makedirs("./data")
    except FileExistsError:
        pass

    database_access.init_database()
    with open("config.json", "r") as f:
        config = json.load(f)
        admin_uid = config["admin_uid"]
    database_access.add_admin(admin_uid,"system_initalization")
    with open("init", "w") as f:
        f.write("init_finished")