<script lang="ts">
  let prix = $state<number | null>(null);

  const estimerPrix = async () => {
    const response = await fetch('http://127.0.0.1:8000/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        surface_reelle_bati: 120.0,
        nombre_pieces_principales: 5,
        longitude: 5.9072,
        latitude: 46.1709,
        est_maison: 1
      })
    });
    const data = await response.json();
    prix = data.prix_estime;
  };
</script>

<main class="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-50 text-gray-900">
  <h1 class="text-4xl font-bold mb-8">Ymmo - Estimation Immobilière</h1>
  
  <button
    onclick={estimerPrix}
    class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
  >
    Estimer le prix (Test API)
  </button>

  {#if prix !== null}
    <div class="mt-6 p-6 bg-white rounded-xl shadow-lg">
      <p class="text-xl">
        Prix estimé : <span class="font-bold text-3xl text-green-600">{prix.toLocaleString('fr-FR')} €</span>
      </p>
    </div>
  {/if}
</main>