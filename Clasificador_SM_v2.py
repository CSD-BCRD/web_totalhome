import pandas as pd
import json
import ollama
import os
from pydantic import BaseModel, Field
from typing import Optional
from tqdm import tqdm

# Mantenemos la clase Pydantic igual
class ProductoClasificado(BaseModel):
    nombre_articulo: str = Field(description="Descripción principal sin marca ni cantidad")
    detalle: Optional[str] = Field(default="", description="Sabor, tipo de envase o característica extra")
    marca: str = Field(description="Nombre de la marca fabricante")
    cantidad: str = Field(description="Valor numérico + unidad de medida (ej: 1 LT, 500 G)")

def clasificar_producto(Articulo: str) -> ProductoClasificado:
    prompt = f"""
    Analiza la siguiente descripción de un producto de supermercado y extrae la información 
    en formato JSON siguiendo exactamente este esquema:
    {{
        "nombre_articulo": "nombre",
        "detalle": "características extras",
        "marca": "marca",
        "cantidad": "numero + unidad"
    }}

    Producto: "{Articulo}"
    """
    try:
        response = ollama.chat(
            model='qwen2.5:14b',
            messages=[{'role': 'user', 'content': prompt}],
            format='json',
            options={'temperature': 0}
        )
        datos_json = json.loads(response['message']['content'])
        return ProductoClasificado(**datos_json)
    except Exception as e:
        return ProductoClasificado(nombre_articulo="ERROR", detalle=str(e), marca="ERROR", cantidad="")

def main(archivo_entrada = "classificador/df/IBERIA.csv", archivo_salida = "productos_finales_IBERIA_completo.csv", batch_size = 200):
    
    # 1. Cargar datos originales
    df_original = pd.read_csv(archivo_entrada)
    
    if "id" not in df_original.columns:
        df_original["id"] = df_original.index + 1
    
    # 2. Intentar cargar progreso previo para no repetir
    if os.path.exists(archivo_salida):
        df_progreso = pd.read_csv(archivo_salida)
        indices_procesados = df_progreso['id'].tolist() # Asumiendo que tienes una columna 'ID'
        resultados = df_progreso.to_dict('records')
        print(f"🔄 Reanudando desde el registro {len(resultados)}...")
    else:
        indices_procesados = []
        resultados = []

    # 3. Filtrar registros que faltan por procesar
    df_pendiente = df_original[~df_original['id'].isin(indices_procesados)]

    print(f"🚀 Procesando {len(df_pendiente)} productos restantes...")

    for i, (index, row) in enumerate(tqdm(df_pendiente.iterrows(), total=len(df_pendiente)), 1):
        desc = row['Articulo']
        producto_validado = clasificar_producto(desc)
        
        resultado_row = {
            **row.to_dict(),
            "Nombre_Extraido": producto_validado.nombre_articulo,
            "Detalle_Extraido": producto_validado.detalle,
            "Marca_Extraida": producto_validado.marca,
            "Cantidad_Extraida": producto_validado.cantidad
        }
        resultados.append(resultado_row)

        # 4. Lógica de guardado cada 200 extracciones
        if i % batch_size == 0:
            pd.DataFrame(resultados).to_csv(archivo_salida, index=False, encoding='utf-8')
            print(f"\n💾 Checkpoint: {i + len(indices_procesados)} registros guardados...")

    # Guardado final
    pd.DataFrame(resultados).to_csv(archivo_salida, index=False, encoding='utf-8')
    print(f"✅ Proceso finalizado. Total: {len(resultados)} registros en {archivo_salida}")

if __name__ == "__main__":
    main(archivo_entrada = "classificador/df/IBERIA.csv", archivo_salida = "productos_finales_IBERIA_completo.csv", batch_size = 10)