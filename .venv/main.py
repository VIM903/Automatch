from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pandas as pd
import joblib
import os
from typing import Dict
import pickle
import json

app = FastAPI()

# Configurar CORS (opcional, pero recomendado)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite acceso desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite cualquier método HTTP
    allow_headers=["*"],  # Permite cualquier cabecera
)

# Configuración de directorios
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "resultados"))

# Modelo de datos que recibimos del formulario
class DatosEntrada(BaseModel):
    renta: str
    condiciones_conduccion: str
    vacaciones: str
    sector: str
    comunidad_autonoma: str
    familia: str
    tipo_combustible: str
    frecuencia_uso: str
    cambio: str
    plaza_parking: str
    experiencia_conduccion: str

# Endpoint para servir el formulario
@app.get("/", response_class=JSONResponse)
def serve_index():
    return JSONResponse(open("C:/Users/swatc/Desktop/UNI/Proyecto grupal/Automatch/.venv/index_2.html").read(), headers={"Content-Type": "text/html; charset=utf-8"})

# Endpoint para recibir los datos del formulario y mostrar los resultados
@app.post("/recibir-datos", response_class=JSONResponse)
def recibir_datos(datos: DatosEntrada, request: Request):
    print(datos)


    try:

        #leer coches disponibles
        df_coches = pd.read_csv(
            "C:/Users/swatc/Desktop/UNI/Proyecto grupal/Automatch/artifacts/data/coches_disponibles.csv"
        )

        #renombrar columna tipo_combustible a tipo_combustible.1 para que no se confunda con la del usuario
        df_coches = df_coches.rename(columns={'tipo_combustible': 'tipo_combustible.1'})
        
        # Convertir los datos del usuario en un diccionario
        usuario_dict = datos.dict()

        # Replicar los datos del usuario en cada fila del CSV de coches
        for key, value in usuario_dict.items():
            df_coches[key] = value  # Esto añade una nueva columna por cada dato del usuario

        df_coches = df_coches.drop(columns=['presupuesto'])


        #Columnas para pasar a boolean:
        columns_to_convert = ['plaza_parking']

        # Convertir una columna con valores 'sí'/'no' a booleanos (True/False)
        df_coches[columns_to_convert] = df_coches[columns_to_convert].replace({'sí': True, 'no': False})

        # Asegurar de que la columna sea de tipo booleano
        df_coches[columns_to_convert] = df_coches[columns_to_convert].astype(bool)

        # Quitamos el "km" para que el campo sea numérico
        df_coches['Kms'] = df_coches['Kms'].str.replace('km', '', regex=False)

        # Convertir la columna a tipo numérico
        df_coches['Kms'] = pd.to_numeric(df_coches['Kms'], errors='coerce')

        # Quitamos el "CV" para que el campo sea numérico
        df_coches['Potencia'] = df_coches['Potencia'].str.replace('CV', '', regex=False)

        # Convertir la columna a tipo numérico
        df_coches['Potencia'] = pd.to_numeric(df_coches['Potencia'], errors='coerce')

        # Label Encoding

        #Renta
        renta_mapping = {
            '-12000': 0,
            '12000 - 20000': 1,
            '20000 - 35000': 2,
            '35000-60000': 3,
            '60000 - 100000': 4,
            '100000': 5
        }


        df_coches['renta_encoded'] = df_coches['renta'].map(renta_mapping)

        #Familia
        familia_mapping = {
            'No': 0,
            'Si, pequeña': 1,
            'Si, grande': 2,
        }


        df_coches['familia_encoded'] = df_coches['familia'].map(familia_mapping)

        #freq.uso:
        frecuencia_uso_mapping = {
            'ocasional': 0,
            'semanal': 1,
            'diario': 2,
        }


        df_coches['frecuencia_uso_encoded'] = df_coches['frecuencia_uso'].map(frecuencia_uso_mapping)

        #Exp. conduccion
        experiencia_conduccion_mapping = {
            'novato': 0,
            'intermedio': 1,
            'experto': 2,
        }


        df_coches['experiencia_conduccion_encoded'] = df_coches['experiencia_conduccion'].map(experiencia_conduccion_mapping)


        # Aplicar Mapeo de frequency encoding:

        # Lista de las columnas codificadas
        columnas_a_codificar = [
            'vacaciones', 
            'sector', 
            'comunidad_autonoma', 
            'condiciones_conduccion', 
            'Caja_velocidades', 
            'tipo_combustible',
            'tipo_combustible.1',
            'Marca'
        ]

        # Aplicar el mapeo de frecuencias a df_coches
        for col in columnas_a_codificar:
            # Cargar el mapeo guardado para cada columna
            freq_encoding = pd.read_pickle(f'C:/Users/swatc/Desktop/UNI/Proyecto grupal/Automatch/artifacts/data/{col}_freq_map.pkl')
            
            # Aplicar el Frequency Encoding al nuevo DataFrame (df_coches)
            df_coches[f'{col}_freq'] = df_coches[col].map(freq_encoding)
            
            # Si hay valores desconocidos, asignar un valor por defecto (0 o NaN)
            df_coches[f'{col}_freq'].fillna(0, inplace=True)


        # Quitar cpolumnas innecesarias:
        df_coches = df_coches.drop(columns=[
            'renta', 'condiciones_conduccion','vacaciones', 'sector', 'comunidad_autonoma', 'familia',
            'tipo_combustible.1', 'cambio','frecuencia_uso','experiencia_conduccion', 'Caja_velocidades','tipo_combustible', 'Marca'])

        columnas_para_prediccion = [
            'Price',
            'Year',
            'Kms',
            'Potencia',
            'renta_encoded',
            'familia_encoded',
            'frecuencia_uso_encoded',
            'experiencia_conduccion_encoded',
            'vacaciones_freq',
            'sector_freq',
            'comunidad_autonoma_freq',
            'condiciones_conduccion_freq',
            'tipo_combustible.1_freq',
            'Marca_freq'
        ]

        # cargar picke
        modelo = joblib.load(
            "C:/Users/swatc/Desktop/UNI/Proyecto grupal/Automatch/artifacts/data/modelo_users_cars1.pkl"
            )

        df_input = df_coches[columnas_para_prediccion]

        # Hacer las predicciones
        y_pred = modelo.predict_proba(df_input)
        y_pred_class = y_pred[:, 1]  # Probabilidad de la clase 1 (positiva)

        #guardar predicciones
        df_coches['prediccion'] = y_pred_class  # Agregar las predicciones a un nuevo dataframe
        df_coches.to_csv("C:/Users/swatc/Desktop/UNI/Proyecto grupal/Automatch/artifacts/data/resultados.csv", index=False)
        
        # Ordenar por la columna 'prediccion' en orden descendente para obtener los coches con mayor probabilidad
        df_top_5 = df_coches.sort_values(by='prediccion', ascending=False).head(5)

        # Convertir el DataFrame a un formato JSON
        df_top_5 = df_top_5.drop(columns=['plaza_parking', 'renta_encoded', 'familia_encoded', 'frecuencia_uso_encoded', 'experiencia_conduccion_encoded', 
                                          'vacaciones_freq', 'sector_freq', 'comunidad_autonoma_freq', 'condiciones_conduccion_freq', 'Caja_velocidades_freq',
                                          'tipo_combustible_freq','tipo_combustible.1_freq', 'Marca_freq', 'prediccion'])
        top_5 = df_top_5.to_dict(orient="records")

        
        # top_5_json = json.dumps(top_5, ensure_ascii=False, indent=4)

        # Renderizar la plantilla de resultados y pasar los coches recomendados
        print(len(top_5))

        templates = Jinja2Templates(directory="C:/Users/swatc/Desktop/UNI/Proyecto grupal/Automatch/.venv/")
        
        return templates.TemplateResponse(
            "resultados.html",
            {
                "request": request,
                "coches": top_5  # Pasamos los coches al template
            }
        )

    except Exception as e:
         return JSONResponse(
            status_code=500,  # Código de error, puedes cambiarlo según sea necesario
            content={"detail": f"Error al procesar la solicitud: {str(e)}"}
        )