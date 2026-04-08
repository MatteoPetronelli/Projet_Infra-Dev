import polars as pl
import plotly.express as px

df = pl.read_csv("data/processed/dvf_clean.csv")

df = df.with_columns(
    (pl.col("type_local") == "Maison").cast(pl.Int32).alias("est_maison")
)

df = df.filter(
    (pl.col("surface_reelle_bati") >= 9) &
    (pl.col("surface_reelle_bati") <= 500) &
    (pl.col("nombre_pieces_principales") <= 20)
)

df_sample = df.sample(n=5000, seed=42)
df_pandas = df_sample.to_pandas()

fig = px.scatter_map(
    df_pandas,
    lat="latitude",
    lon="longitude",
    color="valeur_fonciere",
    size="surface_reelle_bati",
    custom_data=["surface_reelle_bati", "nombre_pieces_principales", "est_maison"],
    hover_data={
        "latitude": False, 
        "longitude": False, 
        "valeur_fonciere": ":,.0f",
        "surface_reelle_bati": True,
        "nombre_pieces_principales": True,
        "est_maison": True
    },
    color_continuous_scale=px.colors.sequential.Plasma,
    size_max=15,
    zoom=4,
    map_style="carto-positron",
    title="Carte interactive des transactions"
)

html_content = fig.to_html(include_plotlyjs="cdn", full_html=True)

if not html_content.startswith('<!DOCTYPE html>'):
    html_content = '<!DOCTYPE html>\n' + html_content

css_fix = """
<style>
    canvas, img, video {
        overflow: clip !important;
    }
</style>
"""

custom_js = """
<script>
    window.addEventListener('load', function() {
        var plotElements = document.getElementsByClassName('plotly-graph-div');
        if (plotElements.length > 0) {
            var myPlot = plotElements[0];
            myPlot.on('plotly_click', function(data) {
                var pt = data.points[0];
                var payload = {
                    lat: pt.lat,
                    lon: pt.lon,
                    surface: pt.customdata[0],
                    pieces: pt.customdata[1],
                    est_maison: pt.customdata[2]
                };
                window.parent.postMessage(payload, '*');
            });
        }
    });
</script>
"""

html_content = html_content.replace('</head>', f'{css_fix}</head>')
html_content = html_content.replace('</body>', f'{custom_js}</body>')

with open("carte_prix_immobiliers.html", "w", encoding="utf-8") as f:
    f.write(html_content)