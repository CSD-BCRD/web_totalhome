import pandas as pd
from tools import extrae_nodup

extrae_nodup(archivo_entrada= "medallion_SM/pricesmart/raw/PriceSmart.csv", archivo_salida= "medallion_SM/pricesmart/bronze/categoria_pricesmart.csv")