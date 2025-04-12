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

class ReconocedorACRCloud:
    """
    Clase para interactuar con la API de ACRCloud para reconocimiento de audio.
    """
    def __init__(self, configuracion):
        self.configuracion = configuracion
        
        if not configuracion.get('access_key') or not configuracion.get('access_secret'):
            print('ERROR: No se ha proporcionado access_key o access_secret')
            sys.exit(1)
            
        if not configuracion.get('host'):
            self.host = 'identify-us-west-2.acrcloud.com'
        else:
            self.host = configuracion.get('host')
            
        self.tipo_consulta = configuracion.get('query_type', 'fingerprint')
        self.depurar = configuracion.get('debug', False)
            
    def reconocer_por_archivo(self, ruta_archivo, segundos_inicio=0):
        try:
            if not os.path.exists(ruta_archivo):
                return {'status': {'msg': 'El archivo no existe', 'code': 2005}}
                
            with open(ruta_archivo, 'rb') as f:
                contenido = f.read()
                
            return self.realizar_reconocimiento(contenido, segundos_inicio)
        except Exception as e:
            print('Error de reconocimiento:', str(e))
            return {'status': {'msg': 'Error de reconocimiento', 'code': 3000}}
            
    def realizar_reconocimiento(self, contenido, segundos_inicio=0):
        try:
            metodo_http = 'POST'
            uri_http = '/v1/identify'
            tipo_datos = 'audio'
            version_firma = '1'
            marca_tiempo = int(time.time())
            
            cadena_para_firmar = '\n'.join([
                metodo_http,
                uri_http,
                self.configuracion.get('access_key'),
                tipo_datos,
                version_firma,
                str(marca_tiempo)
            ])
            
            firma = base64.b64encode(
                hmac.new(
                    self.configuracion.get('access_secret').encode('utf-8'),
                    cadena_para_firmar.encode('utf-8'),
                    digestmod=hashlib.sha1
                ).digest()
            ).decode('utf-8')
            
            if self.depurar:
                print('Cadena para firmar:', cadena_para_firmar)
                
            archivos = {
                'sample': contenido
            }
            
            datos = {
                'access_key': self.configuracion.get('access_key'),
                'sample_bytes': str(len(contenido)),
                'timestamp': str(marca_tiempo),
                'signature': firma,
                'data_type': tipo_datos,
                'signature_version': version_firma
            }
            
            if segundos_inicio > 0:
                datos['start_seconds'] = str(segundos_inicio)
            
            tiempo_espera = self.configuracion.get('timeout', 10)
            url = 'https://' + self.host + uri_http
            
            if self.depurar:
                print('URL:', url)
                print('Datos:', datos)
                
            r = requests.post(url, files=archivos, data=datos, timeout=tiempo_espera)
            r.encoding = 'utf-8'
            
            if self.depurar:
                print('Estado HTTP:', r.status_code)
                
            if r.status_code == 200:
                return r.text
            else:
                return {'status': {'msg': 'Error HTTP', 'code': r.status_code}}
        except Exception as e:
            print('Error al realizar el reconocimiento:', str(e))
            return {'status': {'msg': 'Error al realizar el reconocimiento', 'code': 3000}}

def identificar_musica(ruta_audio):
    """
    Función principal para identificar música usando la API de ACRCloud
    """
    # Configuración de ACRCloud
    configuracion = {
        'host': 'identify-us-west-2.acrcloud.com',
        'access_key': '4867bdcd3b13539fcb6d51646e5b8fe8',
        'access_secret': 'riaQ5V5792fgnUqeB9CT9AoG3bm2O3YAniCEtTlO',
        'timeout': 10,
        'debug': True
    }
    
    reconocedor = ReconocedorACRCloud(configuracion)
    
    if not os.path.exists(ruta_audio):
        return "Error: No se pudo encontrar el archivo de audio."
    
    tiempo_inicio = time.time()
    resultado = reconocedor.reconocer_por_archivo(ruta_audio, 0)
    tiempo_transcurrido = time.time() - tiempo_inicio
    
    try:
        if isinstance(resultado, dict):
            diccionario_resultado = resultado
        else:
            diccionario_resultado = json.loads(resultado)
        
        print("Respuesta completa:", json.dumps(diccionario_resultado, indent=2))
        
        if 'status' in diccionario_resultado and diccionario_resultado['status']['code'] == 0:
            metadatos = diccionario_resultado.get('metadata', {})
            info_musica = metadatos.get('music', [])
            
            if info_musica:
                pista = info_musica[0]
                titulo = pista.get('title', 'Desconocido')
                artista = pista.get('artists', [{'name': 'Desconocido'}])[0]['name']
                album = pista.get('album', {}).get('name', 'Desconocido')
                
                # Recopilar géneros directamente de la API
                generos = []
                if 'genres' in pista and pista['genres']:
                    for genero in pista['genres']:
                        generos.append(genero.get('name', ''))
                
                texto_generos = ", ".join(generos) if generos else "No disponible"
                
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
            mensaje_error = diccionario_resultado.get('status', {}).get('msg', 'Error desconocido')
            codigo_error = diccionario_resultado.get('status', {}).get('code', 'Desconocido')
            return f"Error en el reconocimiento: {mensaje_error} (Código: {codigo_error})"
    except Exception as e:
        return f"Error al procesar la respuesta: {str(e)}\nRespuesta cruda: {str(resultado)}"

# Ejemplo de uso básico
if __name__ == "__main__":
    print("=" * 70)
    print("Clasificador de Géneros Musicales")
    print("Desarrollado por: José Eduardo Williams (23-EISN-2-048)")
    print("=" * 70)
    
    # Solicitar al usuario la ruta del archivo
    ruta_audio = input("Ingrese la ruta del archivo de audio a identificar: ")
    
    # Procesar e imprimir el resultado
    print("\nIdentificando música...")
    resultado = identificar_musica(ruta_audio)
    print("\nResultado:")
    print(resultado)
    
    print("=" * 70)