import os
import sys

# Read the folder_path and size_limit from command-line arguments
if len(sys.argv) < 3:
    print("Usage: python script.py <folder_path> <size_limit_in_bytes>")
    sys.exit(1)

folder_path = sys.argv[1]
size_limit = int(sys.argv[2])  # Convert the argument to an integer

# Check if the folder exists
if not os.path.exists(folder_path):
    print(f"Folder {folder_path} does not exist.")
    sys.exit(1)

# Loop through all files in the directory
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    # Ensure that it's actually a file and not a directory
    if os.path.isfile(file_path):
        # Get the size of the file in bytes
        file_size = os.path.getsize(file_path)
        
        # Check if the file size exceeds the limit
        if file_size > size_limit or filename.startswith("v"):
            print(f"Deleting {filename}, size: {file_size} bytes")
            os.remove(file_path)