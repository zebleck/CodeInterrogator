import os

# Define the folder path where your files are located
folder_path = "results"

# Check if the folder exists
if os.path.exists(folder_path):
    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    # Iterate through the files
    for file in files:
        # Check if the file has a ".html" extension
        if ".html" in file:
            # Construct the new filename by removing the ".html" extension
            new_filename = file.replace(".html", "")
            
            # Rename the file by removing the ".html" extension
            os.rename(os.path.join(folder_path, file), os.path.join(folder_path, new_filename))
            
            # Print the updated filename
            print(f"Renamed '{file}' to '{new_filename}'")
else:
    print(f"The folder '{folder_path}' does not exist.")
