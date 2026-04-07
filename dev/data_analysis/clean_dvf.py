import polars as pl

chemin_fichier = "data/raw/valeursfoncieres-2025.csv"

df = pl.read_csv(
    chemin_fichier,
    separator=",",
    ignore_errors=True,
    infer_schema_length=10000
)

colonnes_cibles = [
    "id_mutation",
    "valeur_fonciere",
    "type_local",
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "longitude",
    "latitude"
]

df_ml = df.select(colonnes_cibles)

df_ml = df_ml.drop_nulls(subset=["valeur_fonciere", "surface_reelle_bati"])

df_ml = df_ml.filter(pl.col("type_local").is_in(["Appartement", "Maison"]))

df_propre = df_ml.group_by("id_mutation").agg([
    pl.col("valeur_fonciere").first(),
    pl.col("type_local").first(),
    pl.col("surface_reelle_bati").sum(),
    pl.col("nombre_pieces_principales").sum(),
    pl.col("longitude").first(),
    pl.col("latitude").first()
])

print(df_propre.head())
print(df_propre.shape)

df_propre.write_csv("data/processed/dvf_clean.csv")
print("Fichier nettoyé sauvegardé avec succès dans data/processed/dvf_clean.csv")