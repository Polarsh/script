import json
import os
from obs import ObsClient

def upload_file(obsClient, bucketName, folderPath, file_with_paths="paths.txt" ):
    try:
        with open(file_with_paths, "r") as file:
            for line in file:
                fullPath = line.strip()

                relative_path = os.path.relpath(fullPath, folderPath).replace("\\", "/")

                resp = obsClient.putFile(bucketName=bucketName, objectKey=relative_path, file_path=fullPath)

                if resp.status < 300: 
                    print("Elimina path")
                else:
                    print('errorCode:', resp.errorCode) 
                    print('errorMessage:', resp.errorMessage)
                    

    except:
        import traceback
        print(traceback.format_exc())


# --------------------

def get_full_paths(directory):
    """Get the full path of all files in the specified directory."""
    paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file).replace("\\", "/")
            paths.append(full_path)
    return paths

def save_to_txt(paths, filename="paths.txt"):
    """Save the provided paths to a .txt file."""
    with open(filename, 'w') as file:
        for path in paths:
            file.write(path + "\n")

def get_paths(folderPath):
    # Get the full paths of files in the selected directory
    paths = get_full_paths(folderPath)

    # Save the paths to a .txt file
    save_to_txt(paths)

    print(f"Paths saved to {os.path.abspath('paths.txt')}")

def load_json_data(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


if __name__ == "__main__":
    data = load_json_data('config.json')
    
    access_key = data['access_key']
    secret_key = data['secret_key']
    bucket_name = data['bucket_name']
    folder_path = data['folder_path']

    # Create an instance of ObsClient.
    obsClient = ObsClient(
        access_key_id=access_key,    
        secret_access_key=secret_key,    
        server='https://obs.sa-peru-1.myhuaweicloud.com'
    )

    if not os.path.exists("paths.txt"):
        get_paths(folderPath= folder_path)

    upload_file(obsClient=obsClient, bucketName= bucket_name, folderPath= folder_path)

    obsClient.close()