from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import os
from pydantic import BaseModel

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Servir archivos estáticos desde "WEB/static"
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# Configurar Jinja2 para plantillas en la carpeta "WEB/resultados"
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "WEB", "resultados"))

# Modelo de datos que espera el formulario
class DatosFormulario(BaseModel):
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
    experiencia_conduccion: str  # Si no está en el HTML, elimínalo aquí

# ✅ Servir el formulario correctamente
@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index_2.html"))


# ✅ Recibir datos y redirigir a la página de resultados
@app.post("/recibir-datos")
async def recibir_datos(datos: DatosFormulario):
    try:
        # ✅ Guardar los datos en un archivo temporal
        temp_datos_path = os.path.join(BASE_DIR, "WEB", "temp_datos.json")
        with open(temp_datos_path, "w", encoding="utf-8") as f:
            json.dump(datos.dict(), f)

        # ✅ Redirigir a la página de resultados
        return RedirectResponse(url="/resultados", status_code=303)

    except Exception as e:
        return HTMLResponse(content=f"<h1>Error al procesar la solicitud: {str(e)}</h1>", status_code=500)


####  leer csv coches disponibles, 
# aplicarle usuario a todas la lineas,  
# leer pkl, 
# encoding, 
# predect_proba, 
# orderby, 
# top 10 results.



# ✅ Página de resultados
@app.get("/resultados", response_class=HTMLResponse)
async def mostrar_resultados(request: Request):
    try:
        json_path = os.path.join(BASE_DIR, "WEB", "top_5_results_with_info_and_urls.json")

        # ✅ Verificar si el archivo JSON existe antes de abrirlo
        if not os.path.exists(json_path):
            return HTMLResponse(content="<h1>Error: Archivo de resultados no encontrado.</h1>", status_code=404)

        with open(json_path, "r", encoding="utf-8") as f:
            coches = json.load(f)

        return templates.TemplateResponse(
            "resultados.html",
            {
                "request": request,
                "coches": coches  # Pasamos los coches al template
            }
        )
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=500)




