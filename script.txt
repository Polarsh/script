import os
import sys
import json
from datetime import datetime
import time
import threading
from tkinter import Tk, ttk, StringVar, Label, Entry, Button, filedialog
from obs import ObsClient

root = None
accessKey = None
secretKey = None
bucketName = None
folderPath = None

loading = True

# ------- Loading 

def loading_animation(text, num_files=None):
    global loading
    
    # Limpia la consola
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while loading:
        for char in ['|', '/', '-', '\\']:
            display_text = text + " " + char
            if num_files is not None:
                display_text += f" - {num_files} rutas restantes"
            sys.stdout.write('\r' + display_text)
            sys.stdout.flush()
            time.sleep(0.2)

    loading = True

# ------- Upload File

def upload_files(obsClient, bucketName, folderPath, file_with_paths="paths.txt"):
    try:
        global loading

        with open(file_with_paths, "r") as file:
            lines = file.readlines()

        thread = threading.Thread(target=loading_animation, args=("Subiendo archivos al OBS...", len(lines)))
        thread.start()

        while True:
            if not is_time_in_range():
                log_to_file("La hora actual no se encuentra en el rango establecido.")
                break

            if not lines:
                log_to_file("No quedan archivos pendientes en 'paths.txt'.")
                break

            fullPath = lines[0].strip()
            relative_path = os.path.relpath(fullPath, folderPath).replace("\\", "/")
            folder_name = os.path.basename(folderPath)

            object_key = f"{folder_name}/{relative_path}"
            
            log_to_file(fullPath + " ha comenzado a subirse.")

            resp = obsClient.putFile(bucketName=bucketName, objectKey=object_key, file_path=fullPath)

            if resp.status < 300:
                log_to_file(fullPath + " ha finalizado satisfactoriamente.")
                remove_first_line_from_txt(file_with_paths)
            else:
                log_to_file(f"Error uploading {fullPath}. errorCode: {resp.errorCode}, errorMessage: {resp.errorMessage}")
                save_path_to_txt(fullPath)
                remove_first_line_from_txt(file_with_paths)

            with open(file_with_paths, "r") as file:
                lines = file.readlines()
            loading = False
            thread.join()
            if lines:
                thread = threading.Thread(target=loading_animation, args=("Subiendo archivos al OBS...", len(lines)))
                thread.start()
        
        # Detener la animación de carga
        loading = False
        thread.join()

    except:
        import traceback
        log_to_file("Error: " + traceback.format_exc())


# ------- Manage Files

def log_to_file(message, filename="logs.txt"):
    """Log a message to the specified file."""
    current_time = datetime.now().strftime('%d-%m %H:%M:%S') 
    with open(filename, 'a') as file:
        file.write(f"[{current_time}] {message}\n")

def save_path_to_txt(path, filename="paths.txt"):
    """Append a single path to a .txt file."""
    with open(filename, 'a') as file:
        file.write(path + "\n")

def remove_first_line_from_txt(filename="paths.txt"):
    """Remove the first line from a .txt file."""
    with open(filename, "r") as file:
        lines = file.readlines()

    # Re-write the file without the first line
    with open(filename, "w") as file:
        file.writelines(lines[1:])        

# ------- Get Paths

def get_full_paths_and_save(directory):
    """Get the full path of all files in the specified directory and save them to a .txt file."""
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file).replace("\\", "/")
            save_path_to_txt(full_path)

def get_paths(folderPath):
    global loading
    
    # Iniciar la animación de carga con un mensaje descriptivo
    thread = threading.Thread(target=loading_animation, args=("Generando rutas de archivos...",))
    thread.start()
    
    # Get the full paths of files in the selected directory and save them to a .txt file
    get_full_paths_and_save(folderPath)

    # Detener la animación de carga
    loading = False
    thread.join()

    log_to_file(f"Rutas de archivos guardadas en {os.path.abspath('paths.txt')}")


# ------- Load config

def load_config(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    return data

# ------- Save Config

def save_config():
    # Determinar la región según la selección en el Combobox
    selected_region = region.get()
    if selected_region == "Santiago":
        obs_region = "la-south-2"
    elif selected_region == "Lima":
        obs_region = "sa-peru-1"
    else:
        obs_region = ""  # Puede agregar un valor predeterminado o manejarlo como un error

    data = {
        'access_key': accessKey.get(),
        'secret_key': secretKey.get(),
        'bucket_name': bucketName.get(),
        'folder_path': folderPath.get(),
        'region': obs_region,  # Guardar la región en el archivo de configuración
        'start_time' : "00:00:00",
        'end_time' : "04:55:00",
    }

    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    log_to_file("Archivo de configuracion generado.")
    
    root.quit()


def browse_folder():
    folder = filedialog.askdirectory()
    folderPath.set(folder)

def create_config_gui():
    global root, accessKey, secretKey, bucketName, folderPath, region

    # Crear ventana principal
    root = Tk()
    root.title('Config')

    if hasattr(sys, '_MEIPASS'):
        icon_path = os.path.join(sys._MEIPASS, 'logo.ico')
    else:
        icon_path = 'logo.ico'

    root.iconbitmap(icon_path)

    # Establecer el tamaño de la ventana    
    window_width, window_height = 720, 150
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (window_width / 2)
    y = (screen_height / 2) - (window_height / 2)
    root.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")

    # Variables
    accessKey = StringVar()
    secretKey = StringVar()
    bucketName = StringVar()
    folderPath = StringVar()
    region = StringVar()

    # Labels y Entry para cada campo
    Label(root, text='Access Key').grid(row=0, column=0, padx=10, pady=10, sticky='w')
    Entry(root, textvariable=accessKey, width=30).grid(row=0, column=1, padx=10, pady=10, sticky='w')

    Label(root, text='Secret Key').grid(row=0, column=2, padx=10, pady=10, sticky='w')
    Entry(root, textvariable=secretKey, width=50).grid(row=0, column=3, columnspan=2,  padx=10, pady=10, sticky='w')

    Label(root, text='Folder Path').grid(row=1, column=0, padx=10, pady=10, sticky='w')
    Entry(root, textvariable=folderPath, width=80).grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky='w')
    Button(root, text="Search", command=browse_folder).grid(row=1, column=4, padx=10, pady=10)

    Label(root, text='Bucket Name').grid(row=2, column=0, padx=10, pady=10, sticky='w')
    Entry(root, textvariable=bucketName, width=30).grid(row=2, column=1, padx=10, pady=10, sticky='w')

    # Agregando el Combobox para seleccionar la región
    Label(root, text='Región').grid(row=2, column=2, padx=10, pady=10, sticky='w')
    regions_combobox = ttk.Combobox(root, textvariable=region, values=("Santiago", "Lima"), state="readonly")
    regions_combobox.grid(row=2, column=3, padx=10, pady=10, sticky='w')
    regions_combobox.set("Santiago")  # Establecer un valor predeterminado

    # Botón para guardar la configuración, ahora movido a la fila 4
    Button(root, text="Save", command=save_config).grid(row=2, column=4, padx=10, pady=10, columnspan=2)

    root.mainloop()


# ------- Get Time

def is_time_in_range():
    current_time = datetime.now().time()

    config_data = load_config('config.json')

    start_time = datetime.strptime(config_data["start_time"], "%H:%M:%S").time()
    end_time = datetime.strptime(config_data["end_time"], "%H:%M:%S").time()

    return start_time <= current_time <= end_time

def main():

    log_to_file("El programa ha iniciado.")

    if not os.path.exists('config.json'):
        create_config_gui()
        log_to_file("El programa ha finalizado.")
        sys.exit()
    else:
        config_data = load_config('config.json')
        accessKey = config_data['access_key']
        secretKey = config_data['secret_key']
        bucketName = config_data['bucket_name']
        folderPath = config_data['folder_path']
        region = config_data.get('region', 'la-south-2')
    
    if not os.path.exists("paths.txt"):
        get_paths(folderPath=folderPath)

    # Aquí determinamos la URL del servidor basándonos en la región
    serverUrl = f'https://obs.{region}.myhuaweicloud.com'

    obsClient = ObsClient(
        access_key_id=accessKey,
        secret_access_key=secretKey,    
        server=serverUrl
    )

    upload_files(obsClient=obsClient, bucketName=bucketName, folderPath=folderPath)

    log_to_file("El programa ha finalizado.")

    obsClient.close()


if __name__ == "__main__":
    main()