def remove_index(name):
    return "_".join(name.split("_")[:-1])

def extract_protocol_name(path):
    return remove_index(path.split("/")[-2])

def extract_indexed_protocol_name(path):
    full = path.split("/")[-2]
    return remove_index(full),int(full.split("_")[-1])

def make_message_path(protocol_path,message,sender=None):
    if sender is not None:
        return f"{protocol_path}{message}_{sender}"
    return protocol_path+message

def make_protocol_path(parent_path,full_protocol_name):
    return parent_path+full_protocol_name+"/"

def extract_protocol_path(messagepath):
    return "/".join(messagepath.split("/")[:-1])+"/"

def extract_parent(path):
    return "/".join(path.split("/")[:-2])+"/"

def extract_indexed_message_name(messagepath):
    full = messagepath.split("/")[-1]
    return remove_index(full),int(full.split("_")[-1])
