import os
import typer
from typing_extensions import Annotated
import cli_for_tools as ct

app = typer.Typer(
    help="Paco el chato es el asistente para las tareas de gabinete en el proyecto de erradicación de gato feral en Isla Guadalupe"
)


def clean_data_when_use_yolo():
    os.system("sudo chown --recursive $USER:$USER .")
    os.system("rm --force cat_detected/*.txt")
    os.system("rm --force --recursive camera_trap_photos/")


def setup_classifier():
    os.system("mkdir camera_trap_photos")
    os.system("cp *.* camera_trap_photos/")
    os.system("rm --recursive cat_detected/")


def clean_data_when_after_made_little_map():
    os.system("sudo chown --recursive $USER .")
    os.system("sudo chmod g+w --recursive .")
    os.system("echo ¿Qué borraremos?")


def analyze_photo():
    command = "docker run --volume $PWD:/workdir islasgeci/cetys_cat_recognition:latest make classification"
    os.system(command)


def update_ig_position_traps_map():
    command = "docker rmi --force islasgeci/ig_position_traps_map && docker pull islasgeci/ig_position_traps_map"
    os.system(command)


def update_cat_recognition():
    command = (
        "docker rmi --force islasgeci/cat_recognition && docker pull islasgeci/cat_recognition"
    )
    os.system(command)


@app.command()
def actualiza_comandos():
    """
    Actualiza los comandos: \n
    - `haz-mapa` \n
    - `clasifica-fotos`
    """
    update_cat_recognition()
    update_ig_position_traps_map()


@app.command()
def haz_mapa(
    positions_path: Annotated[str, typer.Argument()],
    mapsource_path: Annotated[str, typer.Argument()],
):
    """
    Hace un esbozo del mapa de Isla Guadalupe con las trampas activas e inactivas. \n
    Requerimiento: En la carpeta de trabajo debe estar: \n
    - IG_POSICION_{fecha}.txt         : Archivo que obtenemos de mapsource \n
    - IG_POSICION_TRAMPAS_{fecha}.xlsx: Archivos con los esfuerzos de la semana \n
    Al final generará el archivo `map_of_traps.jpg`.
    """
    command = f"docker run -v $PWD:/workdir/data islasgeci/ig_position_traps_map make data/map_of_traps.jpg positions_this_week={positions_path} mapsource_path={mapsource_path}"
    os.system(command)
    clean_data_when_after_made_little_map()


@app.command()
def clasifica_fotos():
    """
    Clasifica las fotos que vienen de las trampas cámara. \n
    Requerimiento: En la carpeta de trabajo debe estar una carpeta (varias carpetas) con las fotos. \n
    El nombre de la carpeta principal debe ser sin espacios. Por ejemplo: \n
    - `FOTOS GATOS`: es un nombre incorrecto, \n
    - `FOTOS_GATOS`: es un nombre correcto. \n
    Al final generará la carpeta `cat_detected` con las fotos en las que detectó gato.
    """
    setup_classifier()
    analyze_photo()
    clean_data_when_use_yolo()


@app.command()
def version():
    print(ct.__version__)


if __name__ == "__main__":
    app()
