import polars as pl

chemin_fichier = "data/raw/valeursfoncieres-2025.csv"

try:
    df = pl.read_csv(
        chemin_fichier, 
        separator=",", 
        ignore_errors=True,
        infer_schema_length=10000
    )
    
    print(df.head())
    print(df.shape)
    
except Exception as e:
    print(e)