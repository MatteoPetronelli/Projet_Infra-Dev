import pandas as pd

print("Chargement du lourd fichier CSV en mémoire...")
df = pd.read_csv("data/processed/dvf_clean.csv")

print("Compression et conversion au format Apache Parquet...")
df.to_parquet("data/processed/dvf_clean.parquet", engine="pyarrow", compression="snappy")

print("Conversion terminée avec succès !")