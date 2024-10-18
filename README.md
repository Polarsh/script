# Script de Subida de Archivos a OBS en Huawei Cloud

Este script permite subir archivos desde una carpeta local a un bucket en el Object Storage Service (OBS) de Huawei Cloud. La configuración se realiza mediante un archivo `config.json`, que contiene las credenciales y parámetros necesarios. El script también valida un horario determinado para ejecutar la subida y se puede programar con el Programador de Tareas de Windows.

## Configuración

Antes de ejecutar el script, debes configurar el archivo `config.json` con los siguientes parámetros:

```json
{
  "access_key": "",
  "secret_key": "",
  "bucket_name": "rpaimages",
  "folder_path": "C:/Users/dybsm/Escritorio/RPP",
  "region": "sa-peru-1",
  "start_time": "00:00:00",
  "end_time": "23:55:00"
}
```

### Descripción de los Parámetros:
- `access_key`: Clave de acceso para Huawei Cloud OBS.
- `secret_key`: Clave secreta para Huawei Cloud OBS.
- `bucket_name`: Nombre del bucket donde se subirán los archivos.
- `folder_path`: Ruta de la carpeta local que contiene los archivos.
- `region`: Región de tu servicio en Huawei Cloud (por ejemplo, `sa-peru-1`).
- `start_time`: Hora de inicio en formato `HH:MM:SS` para permitir la subida.
- `end_time`: Hora de fin en formato `HH:MM:SS` para detener la subida.

## Ejecución

### Desde Python:
Puedes ejecutar el script manualmente desde la línea de comandos:

```bash
python script.py
```

### Desde el ejecutable:
Si ya tienes un ejecutable, solo debes ejecutarlo directamente. Este ejecutable crea automáticamente el archivo `config.json` y permite configurarlo.

### Programador de Tareas de Windows:
Puedes usar el **Programador de Tareas** de Windows para automatizar la ejecución del script en horarios específicos.

## Archivos de Soporte

- **logs.txt**: Registra las actividades y posibles errores durante la ejecución.
- **paths.txt**: Almacena el progreso de las subidas para que el proceso se pueda reanudar desde donde se quedó.

## Dependencias

El script utiliza las siguientes librerías y módulos de Python:

- **os** y **sys**: Para manipulación de archivos y gestión del entorno.
- **json**: Para leer y escribir archivos `config.json`.
- **datetime** y **time**: Para gestionar las validaciones de tiempo.
- **threading**: Para gestionar la ejecución en paralelo.
- **Tkinter**: Para la interfaz gráfica de configuración.
- **ObsClient**: Cliente para interactuar con el servicio OBS de Huawei Cloud (debe instalarse).
  
### Instalación de dependencias:
Para ejecutar el script desde Python, debes instalar las siguientes dependencias:

```bash
pip install obs
pip install tkinter
```

## Notas
- El script solo subirá archivos durante el rango horario especificado en `config.json`.
- Asegúrate de revisar los archivos `logs.txt` y `paths.txt` para monitorear el estado del proceso y verificar cualquier error.
