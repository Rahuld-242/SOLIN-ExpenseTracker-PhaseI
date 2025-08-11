import os
import json

# ----------------------------------------
# Core Memory Operations
# ----------------------------------------

def remember(key, value):
    # Define a path to the memory file
    memory_file="memory/memory.json"
 
    # Load current memory (if file exists)
    if os.path.exists(memory_file):
        with open(memory_file, "r") as file:
            data=json.load(file)
    else:
        data={}

    # Update memory
    data[key] = value 

    # Save back to Json
    with open(memory_file, "w") as file:
        json.dump(data, file, indent=4)
        
def recall(key):
    # Define the memory file path
    memory_file="memory/memory.json"
    
    # Check if the file exists
    if not os.path.exists(memory_file):
        return None
    
    # Load the file
    with open(memory_file,"r") as file:
        data=json.load(file)
    
    # Return the requested file
    return data.get(key)
        
def forget(key):
    memory_file="memory/memory.json"
    
    if not os.path.exists(memory_file):
        return False
    
    with open(memory_file,"r") as file:
        data=json.load(file)
        
    if key in data:
        del data[key]
        with open(memory_file, "w") as file:
            json.dump(data, file, indent=4)
        return True
    
    else:
        return False

        
            
        
        
    