import pandas as pd

def extrae_nodup(archivo_entrada: str = "classificador/df/IBERIA.csv", archivo_salida:str = "classificador/df/categoria_IBERIA.csv"):

    df = pd.read_csv(archivo_entrada)
    print(df.shape)
    

    df_nodp = df.drop_duplicates(subset=['Articulo'])

    print(df_nodp.shape)

    df_nodp.to_csv(archivo_salida, index=False)


def extractor_muestra(archivo_entrada: str = "classificador/df/IBERIA.csv", archivo_salida:str = "classificador/df/muestra_IBERIA.csv", n: int=100):
     
    df = pd.read_csv(archivo_entrada)
    
    muestra = df.sample(n=n)
    
    print(muestra.head())
    
    muestra.to_csv(archivo_salida, index=False)
    
    print(f"Archivo de muestra generado en la ruta: {archivo_salida}")

    
def fusionador(bd_full: str = "df/IBERIA.csv", 
               clasificador: str = "df/categoria_IBERIA_clasificada.csv" ,
               archivo_salida:str = "df/bd_iberia_full_clasificada.parquet"):
    
    df_left = pd.read_csv(bd_full)
    df_right = pd.read_csv(clasificador)
    
    print(df_left.head())
    print(f"El archivo a fusionar tiene: {df_left.shape[0]} Columnas y {df_left.shape[1]} Filas")
    
    print(df_right.columns)
    
    print(f"El archivo diccionario tiene: {df_right.shape[0]} Columnas y {df_right.shape[1]} Filas")
    
    df_right = df_right[['Articulo', 'Nombre_Extraido', 'Detalle_Extraido', 'Marca_Extraida',
       'Cantidad_Extraida']]
    
    print(df_right.head())
    
    df_fusionada = df_left.merge(df_right, how="left", on="Articulo", indicator=False)
    
    df_fusionada.to_parquet(archivo_salida, index=False)
    
    print(df_fusionada.head(n=50))
    
    print(f"El archivo clasificado fue guardado exitosamente en la ruta: {archivo_salida}")
    

if __name__ == "__main__":
    
    fusionador(bd_full = "medallion_SM/garrido/raw/Supermercado_Garrido.csv", 
               clasificador = "medallion_SM/garrido/silver/categoria_garrido_clasificada.csv", 
               archivo_salida = "medallion_SM/garrido/gold/bd_garrido_full_clasificada.parquet")