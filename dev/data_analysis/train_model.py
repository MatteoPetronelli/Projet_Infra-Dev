import polars as pl
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

chemin_fichier = "data/processed/dvf_clean.csv"
df = pl.read_csv(chemin_fichier)

df = df.filter(
    (pl.col("valeur_fonciere") >= 20000) &
    (pl.col("valeur_fonciere") <= 2000000) &
    (pl.col("surface_reelle_bati") >= 9) &
    (pl.col("surface_reelle_bati") <= 500)
)

df = df.with_columns(
    (pl.col("type_local") == "Maison").cast(pl.Int32).alias("est_maison")
)

X = df.select(["surface_reelle_bati", "nombre_pieces_principales", "longitude", "latitude", "est_maison"]).to_numpy()
y = df.select("valeur_fonciere").to_numpy().ravel()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Entraînement du modèle en cours...")
modele = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
modele.fit(X_train, y_train)

y_pred = modele.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n--- NOUVEAUX RÉSULTATS ---")
print(f"Marge d'erreur moyenne (MAE) : {mae:,.2f} €")
print(f"Score de précision (R2)      : {r2:.2f}")

joblib.dump(modele, "data/processed/modele_ymmo.pkl")
print("Modèle exporté avec succès dans data/processed/modele_ymmo.pkl")