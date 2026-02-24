import pandas as pd
import json
import asyncio
import os
from ollama import AsyncClient
from pydantic import BaseModel, Field
from typing import Optional
from tqdm.asyncio import tqdm # Versión asíncrona de la barra de progreso

class ProductoClasificado(BaseModel):
    nombre_articulo: str = Field(description="Descripción principal sin marca ni cantidad")
    detalle: Optional[str] = Field(default="", description="Sabor, tipo de envase o característica extra")
    marca: str = Field(description="Nombre de la marca fabricante")
    cantidad: str = Field(description="Valor numérico + unidad de medida (ej: 1 LT, 500 G)")

# Configuración
MODEL_NAME = 'qwen2.5:14b'
BATCH_SIZE_SAVE = 10 # Guardar cada 200 registros
MAX_CONCURRENT_TASKS = 4 # Cuántos productos procesar a la vez (Ajusta según tu GPU)

# Semáforo para controlar la carga en Ollama
sem = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

async def clasificar_producto_async(client: AsyncClient, Articulo: str) -> dict:
    prompt = f"Analiza la siguiente descripción de un producto de supermercado y extrae la información en formato JSON siguiendo exactamente este esquema: {{'nombre_articulo': 'nombre', 'detalle': 'características', 'marca': 'marca', 'cantidad': 'valor+unidad'}} Producto: '{Articulo}'"
    
    async with sem: # Controla que no se lancen más de MAX_CONCURRENT_TASKS a la vez
        try:
            response = await client.chat(
                model=MODEL_NAME,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                options={'temperature': 0}
            )
            datos = json.loads(response['message']['content'])
            return {**datos, "status": "OK"}
        except Exception as e:
            return {"nombre_articulo": "ERROR", "detalle": str(e), "marca": "ERROR", "cantidad": "", "status": "FAIL"}

async def main_async(archivo_entrada = "df/categoria_IBERIA.csv", archivo_salida = "df/categoria_IBERIA_clasificada.csv"):       
    
    df_original = pd.read_csv(archivo_entrada)
    
    if "id" not in df_original.columns:
        df_original["id"] = df_original.index + 1
    
    # Lógica de reanudación
    if os.path.exists(archivo_salida):
        df_progreso = pd.read_csv(archivo_salida)
        indices_procesados = df_progreso['id'].tolist()
        resultados = df_progreso.to_dict('records')
    else:
        indices_procesados = []
        resultados = []

    df_pendiente = df_original[~df_original['id'].isin(indices_procesados)]
    client = AsyncClient()
    
    print(f"🚀 Procesando {len(df_pendiente)} productos de forma asíncrona (Concurrencia: {MAX_CONCURRENT_TASKS})...")

    # Creamos las tareas
    tasks = []
    for _, row in df_pendiente.iterrows():
        tasks.append(procesar_y_formatear(client, row))

    # Ejecutamos con barra de progreso
    for i, task in enumerate(tqdm(asyncio.as_completed(tasks), total=len(tasks)), 1):
        resultado_final = await task
        resultados.append(resultado_final)

        # Checkpoint cada BATCH_SIZE_SAVE
        if i % BATCH_SIZE_SAVE == 0:
            pd.DataFrame(resultados).to_csv(archivo_salida, index=False)
    
    # Guardado final
    pd.DataFrame(resultados).to_csv(archivo_salida, index=False)
    print(f"✅ ¡Listo! Resultados guardados en {archivo_salida}")

async def procesar_y_formatear(client, row):
    """Función auxiliar para mantener el formato del CSV original"""
    res = await clasificar_producto_async(client, row['Articulo'])
    return {
        **row.to_dict(),
        "Nombre_Extraido": res.get('nombre_articulo', 'ERROR'),
        "Detalle_Extraido": res.get('detalle', ''),
        "Marca_Extraida": res.get('marca', 'ERROR'),
        "Cantidad_Extraida": res.get('cantidad', '')
    }

if __name__ == "__main__":
    asyncio.run(main_async(archivo_entrada = "medallion_SM/pricesmart/bronze/categoria_pricesmart.csv", archivo_salida = "medallion_SM/pricesmart/silver/categoria_pricesmart_clasificada.csv"))