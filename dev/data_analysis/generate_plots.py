import polars as pl
import plotly.express as px

df = pl.read_csv("data/processed/dvf_clean.csv")

df_sample = df.sample(n=5000, seed=42)

fig = px.scatter_mapbox(
    df_sample.to_pandas(),
    lat="latitude",
    lon="longitude",
    color="valeur_fonciere",
    size="surface_reelle_bati",
    color_continuous_scale=px.colors.sequential.Plasma,
    size_max=15,
    zoom=4,
    mapbox_style="carto-positron",
    title="Carte des prix immobiliers"
)

fig.write_html("carte_prix_immobiliers.html")