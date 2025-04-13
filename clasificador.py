#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Proyecto: Clasificador de Géneros Musicales.
Autor: José Eduardo Williams.
Matrícula: 23-EISN-2-048.

"""

import os
import sys
import time
import json
import base64
import hmac
import hashlib
import requests
import gradio as gr

# Clase para interactuar con la API de ACRCloud para reconocimiento de audio.
class ReconocedorACRCloud:

    # Inicializa el reconocedor con la configuración proporcionada.
    def __init__(self, configuracion):
        self.configuracion = configuracion
        
        # Verificar que las credenciales estén presentes
        if not configuracion.get('access_key') or not configuracion.get('access_secret'):
            print('ERROR: No se ha proporcionado access_key o access_secret')
            sys.exit(1)

        # Establecer el host predeterminado si no se proporciona    
        if not configuracion.get('host'):
            self.host = 'identify-us-west-2.acrcloud.com'
        else:
            self.host = configuracion.get('host')

        # Establecer el tipo de consulta   
        self.tipo_consulta = configuracion.get('query_type', 'fingerprint')
        self.depurar = configuracion.get('debug', False)


    # Realiza el reconocimiento de audio mediante un archivo.       
    def reconocer_por_archivo(self, ruta_archivo, segundos_inicio=0):
        try:
            # Verificar que el archivo existe
            if not os.path.exists(ruta_archivo):
                return {'status': {'msg': 'El archivo no existe', 'code': 2005}}

            # Leer el contenido del archivo    
            with open(ruta_archivo, 'rb') as f:
                contenido = f.read()

            # Realizar el reconocimiento    
            return self.realizar_reconocimiento(contenido, segundos_inicio)
        except Exception as e:
            print('Error de reconocimiento:', str(e))
            return {'status': {'msg': 'Error de reconocimiento', 'code': 3000}}

    # Ejecuta el proceso de reconocimiento enviando los datos a ACRCloud.       
    def realizar_reconocimiento(self, contenido, segundos_inicio=0):

        try:
            # Definir parámetros para la firma
            metodo_http = 'POST'
            uri_http = '/v1/identify'
            tipo_datos = 'audio'
            version_firma = '1'
            marca_tiempo = int(time.time())

            # Crear la cadena para firmar
            cadena_para_firmar = '\n'.join([
                metodo_http,
                uri_http,
                self.configuracion.get('access_key'),
                tipo_datos,
                version_firma,
                str(marca_tiempo)
            ])
            
            # Generar la firma HMAC
            firma = base64.b64encode(
                hmac.new(
                    self.configuracion.get('access_secret').encode('utf-8'),
                    cadena_para_firmar.encode('utf-8'),
                    digestmod=hashlib.sha1
                ).digest()
            ).decode('utf-8')
            
            # Mostrar información de depuración si está habilitado
            if self.depurar:
                print('Cadena para firmar:', cadena_para_firmar)

            # Preparar los archivos para la petición   
            archivos = {
                'sample': contenido
            }
            
            # Preparar los datos para la petición
            datos = {
                'access_key': self.configuracion.get('access_key'),
                'sample_bytes': str(len(contenido)),
                'timestamp': str(marca_tiempo),
                'signature': firma,
                'data_type': tipo_datos,
                'signature_version': version_firma
            }

            # Añadir el tiempo de inicio si es mayor que cer
            if segundos_inicio > 0:
                datos['start_seconds'] = str(segundos_inicio)
            
            # Obtener el tiempo de espera y construir la URL
            tiempo_espera = self.configuracion.get('timeout', 10)
            url = 'https://' + self.host + uri_http
            
            # Mostrar más información de depuración si está habilitado
            if self.depurar:
                print('URL:', url)
                print('Datos:', datos)

            # Realizar la petición POST    
            r = requests.post(url, files=archivos, data=datos, timeout=tiempo_espera)
            r.encoding = 'utf-8'
            
            # Mostrar el estado HTTP si está en modo depuración
            if self.depurar:
                print('Estado HTTP:', r.status_code)

            # Devolver la respuesta según el estado HTTP    
            if r.status_code == 200:
                return r.text
            else:
                return {'status': {'msg': 'Error HTTP', 'code': r.status_code}}
        except Exception as e:
            print('Error al realizar el reconocimiento:', str(e))
            return {'status': {'msg': 'Error al realizar el reconocimiento', 'code': 3000}}

#   Función principal identificar la música usando la API de ACRCloud
def identificar_musica(ruta_audio):

    # Configuración de ACRCloud
    configuracion = {
        'host': 'identify-us-west-2.acrcloud.com',
        'access_key': '4867bdcd3b13539fcb6d51646e5b8fe8',
        'access_secret': 'riaQ5V5792fgnUqeB9CT9AoG3bm2O3YAniCEtTlO',
        'timeout': 10,
        'debug': True
    }
    
    # Inicializar el reconocedor con la configuración
    reconocedor = ReconocedorACRCloud(configuracion)
    
    # Verificar que el archivo existe
    if not os.path.exists(ruta_audio):
        return "Error: No se pudo encontrar el archivo de audio."
    
    # Realizar el reconocimiento y medir el tiempo que toma
    tiempo_inicio = time.time()
    resultado = reconocedor.reconocer_por_archivo(ruta_audio, 0)
    tiempo_transcurrido = time.time() - tiempo_inicio
    
    # Analizar los resultados del reconocimiento
    try:
        # Convertir el resultado a diccionario si no lo es ya
        if isinstance(resultado, dict):
            diccionario_resultado = resultado
        else:
            diccionario_resultado = json.loads(resultado)
        
        print("Respuesta completa:", json.dumps(diccionario_resultado, indent=2))

        # Verificar si el reconocimiento fue exitoso
        if 'status' in diccionario_resultado and diccionario_resultado['status']['code'] == 0:
            # Extraer los metadatos de la respuesta
            metadatos = diccionario_resultado.get('metadata', {})
            info_musica = metadatos.get('music', [])
            
            if info_musica:
                # Obtener información de la primera pista encontrada
                pista = info_musica[0]
                titulo = pista.get('title', 'Desconocido')
                artista = pista.get('artists', [{'name': 'Desconocido'}])[0]['name']
                album = pista.get('album', {}).get('name', 'Desconocido')
                
                # Extraer géneros directamente de la API sin procesamiento adicional
                generos = []
                if 'genres' in pista and pista['genres']:
                    for genero in pista['genres']:
                        generos.append(genero.get('name', ''))

                # Formar el string de géneros o usar un valor predeterminado
                texto_generos = ", ".join(generos) if generos else "No disponible"
                
                # Formar el texto de resultado
                texto_resultado = f"""
                Título: {titulo}
                Artista: {artista}
                Álbum: {album}
                Géneros: {texto_generos}
                Tiempo de reconocimiento: {tiempo_transcurrido:.2f} segundos
                """
                return texto_resultado
            else:
                return "No se pudo identificar la música en el audio."
        else:
            # Extraer información de error
            mensaje_error = diccionario_resultado.get('status', {}).get('msg', 'Error desconocido')
            codigo_error = diccionario_resultado.get('status', {}).get('code', 'Desconocido')
            return f"Error en el reconocimiento: {mensaje_error} (Código: {codigo_error})"
    except Exception as e:
        return f"Error al procesar la respuesta: {str(e)}\nRespuesta cruda: {str(resultado)}"

# Procesa el audio ya grabado y lo identifica    
def procesar_audio(audio):
    if audio is None:
        return "Por favor, graba o sube un archivo de audio."
    
    # El audio puede ser un archivo temporal o un path
    ruta_audio = audio

    # Identificar la música
    print("Identificando música en:", ruta_audio)
    resultado = identificar_musica(ruta_audio)
    return resultado

# Iniciar la aplicación con Gradio
if __name__ == "__main__":
    print("=" * 70)
    print("Clasificador de Géneros Musicales")
    print("Desarrollado por: José Eduardo Williams (23-EISN-2-048)")
    print("=" * 70)
    print("Iniciando aplicación...")

    # Interfaz de la aplicación con Gradio
    with gr.Blocks(title="Clasificador de Géneros Musicales") as app:
        with gr.Tabs() as pestanas:

            # Primera pestaña: Información del Proyecto
            with gr.Tab("Información del Proyecto"):
                gr.Markdown("# Clasificador de Géneros Musicales")
                gr.Markdown("""
                            
                **Nombre del Proyecto:** Clasificador de Géneros Musicales ED.
                            
                **Desarrollador:** José Eduardo Williams.
                            
                ### Tecnología Utilizada:
                Este proyecto utiliza la API de ACRCloud para identificar canciones y sus géneros musicales.
                            
                ACRCloud es una plataforma de reconocimiento de audio basada en Deep Learning que puede identificar
                canciones, programas de TV y otros contenidos de audio. La tecnología utiliza redes neuronales convolucionales
                y algoritmos de huella digital acústica para comparar patrones de audio con una extensa base de datos.
                            
                """)

                gr.Markdown("### ¡ESPERO QUE TE PUEDAS DIVERTIR, RECUERDA PONER TÚ CANCIÓN FAVORITA Y PASARLA BIEN!❤️🎵")

            # Segunda pestaña: Géneros Musicales
            with gr.Tab("Géneros Musicales"):
                gr.Markdown("# Géneros musicales disponibles para ser clasificados:")

                with gr.Accordion("Géneros Principales", open=True):
                    gr.Markdown("""
                    - Pop
                    - Rock
                    - Hip Hop/Rap
                    - R&B/Soul
                    - Electrónica/Dance
                    - Country
                    - Jazz
                    - Blues
                    - Reggae
                    - Música Clásica
                    - Folk
                    - Metal
                    - Punk
                    - Alternativo/Indie
                    - Gospel/Cristiana
                    """)
                    
                with gr.Accordion("Géneros Latinos", open=True):
                    gr.Markdown("""
                    - Reggaeton
                    - Trap Latino
                    - Bachata
                    - Salsa
                    - Merengue
                    - Cumbia
                    - Vallenato
                    - Mariachi
                    - Ranchera
                    - Pop Latino
                    - Rock Latino
                    - Urbano Latino
                    - Música Tropical
                    """)
                    
                with gr.Accordion("Otros Géneros", open=False):
                    gr.Markdown("""
                    ### Géneros Asiáticos:
                    - K-Pop
                    - J-Pop
                    - C-Pop
                    - Bollywood
                                    
                    ### Géneros Africanos:
                    - Afrobeat
                    - Amapiano
                    - Highlife
                        
                    ### Géneros Electrónicos:
                    - House
                    - Techno
                    - Trance
                    - Dubstep
                    - EDM
                        
                    ### Otros:
                    - Música Instrumental
                    - Bandas Sonoras
                    - Música Ambiente/New Age
                    """)
                    
             # Tercera pestaña: Clasificador
            with gr.Tab("Clasifica tu Canción"):
                gr.Markdown("# Clasificador de Canciones y Géneros Musicales")

                # 1. Las instrucciones de uso
                gr.Markdown("""
                ### Instrucciones de Uso:
                1. Graba un fragmento de audio (mínimo 10 segundos) o sube un archivo de música.
                2. Cuando quieras detener la grabación del audio, presiona "STOP".  
                3. Si deseas pausar la grabación del audio, presiona el icono pequeño al lado de STOP, después presiona "RESUME" para reanudar.      
                4. Haz clic en "Identificar Canción".
                5. Espera mientras se procesa la identificación.
                6. Revisa los resultados que incluyen título, artista, álbum y género musical.
                """)

                # 2. Sección para grabar o subir audio
                gr.Markdown("Graba un clip de audio o sube un archivo de música para identificar su título, artista y géneros.")

                with gr.Row():
                    entrada_audio = gr.Audio(type="filepath", label="Audio")

                with gr.Row():
                    boton_enviar = gr.Button("Identificar Canción", variant="primary")

                # 3. Finalmente el resultado
                with gr.Row():
                    salida = gr.Textbox (label="Resultado del Reconocimiento", lines=10)

                boton_enviar.click(fn=procesar_audio, inputs=entrada_audio, outputs=salida)

    # Lanzar la aplicación
    app.launch()

    print("¡Gracias por usar el Clasificador de Géneros Musicales!")
    print("=" * 70)