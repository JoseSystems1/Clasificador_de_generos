# Proyecto-de-Final-IA:

## Nombre
José Eduardo Williams.

## Matrícula
23-EISN-2-048.

## Proyecto
Clasificador de géneros musicales.

## Descripción 
El Clasificador de Géneros Musicales es una aplicación desarrollada en Python que permite
identificar canciones y sus géneros musicales a partir de grabaciones o archivos de audio.
Utilizando la API de reconocimiento de ACRCloud, la aplicación puede detectar el título,
artista, álbum y géneros de una canción con alta precisión. Esta herramienta cuenta con,
una interfaz gráfica intuitiva construida con Gradio.

Este proyecto utiliza ACRCLOUD API que es una plataforma de reconocimiento de audio basada 
en Deep Learning que puede identificar canciones, programas de TV y otros contenidos de audio.


# Pasos para la instalación del proyecto y su uso: 

Requisitos: 

- Python 3.8 o superior
- Conexión a internet (para comunicarse con la API de ACRCloud)

Pasos de instalación: 

bash 

- git clone https://github.com/JoseSystems1/Clasificador_de_generos.git
- cd Clasificador_de_generos

Crea un entorno virtual: 

- Windows: python -m venv env
           env\Scripts\activate

- macOS/Linux: python -m venv env
               source env/bin/activate

Instala las dependencias:

pip install -r requirements.txt

## Después que hayas hecho los pasos anteriores, puedes ejecutar con éxito la aplicación de la siguiente forma:

bash:

python clasificador.py