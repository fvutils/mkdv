import doit
from doit.action import CmdAction

def task_bar():
    return {
        "actions":[CmdAction("echo \"there\"")]
        }
    
def task_mkdv_list():
    return {
        "actions": [CmdAction("echo \"other\"")]
    }
    