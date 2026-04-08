<script lang="ts">
  import { onMount } from 'svelte';

  let surface = $state<number>(80);
  let pieces = $state<number>(4);
  let estMaison = $state<number>(1);
  let lat = $state<number>(46.1709);
  let lon = $state<number>(5.9072);
  
  let prix = $state<number | null>(null);
  let chargement = $state<boolean>(false);

  onMount(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data && event.data.lat && event.data.lon) {
        lat = event.data.lat;
        lon = event.data.lon;
        surface = event.data.surface;
        pieces = event.data.pieces;
        estMaison = event.data.est_maison;
        prix = null; 
      }
    };

    window.addEventListener('message', handleMessage);
    
    return () => window.removeEventListener('message', handleMessage);
  });

  const estimerPrix = async (e: SubmitEvent) => {
    e.preventDefault();
    chargement = true;
    
    const response = await fetch('http://127.0.0.1:8000/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        surface_reelle_bati: surface,
        nombre_pieces_principales: pieces,
        longitude: lon,
        latitude: lat,
        est_maison: estMaison
      })
    });
    
    const data = await response.json();
    prix = data.prix_estime;
    chargement = false;
  };
</script>

<main class="min-h-screen bg-gray-50 text-gray-900 p-8">
  <div class="max-w-6xl mx-auto space-y-8">
    
    <header class="text-center">
      <h1 class="text-4xl font-extrabold text-gray-900">Ymmo Analytics</h1>
      <p class="text-gray-500 mt-2">Estimation par Intelligence Artificielle</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <h2 class="text-xl font-bold mb-6">Paramètres du bien</h2>
        
        <form onsubmit={estimerPrix} class="space-y-4">
          <div>
            <label for="typeBien" class="block text-sm font-medium text-gray-700">Type de bien</label>
            <select id="typeBien" bind:value={estMaison} class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option value={1}>Maison</option>
              <option value={0}>Appartement</option>
            </select>
          </div>

          <div>
            <label for="surfaceInput" class="block text-sm font-medium text-gray-700">Surface (m²)</label>
            <input id="surfaceInput" type="number" bind:value={surface} min="1" max="10000" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" required />
          </div>

          <div>
            <label for="piecesInput" class="block text-sm font-medium text-gray-700">Nombre de pièces</label>
            <input id="piecesInput" type="number" bind:value={pieces} min="1" max="500" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" required />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="latInput" class="block text-sm font-medium text-gray-700">Latitude</label>
              <input id="latInput" type="number" step="any" bind:value={lat} class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" required />
            </div>
            <div>
              <label for="lonInput" class="block text-sm font-medium text-gray-700">Longitude</label>
              <input id="lonInput" type="number" step="any" bind:value={lon} class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" required />
            </div>
          </div>

          <button type="submit" disabled={chargement} class="w-full mt-6 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-50">
            {chargement ? 'Calcul en cours...' : 'Estimer le prix'}
          </button>
        </form>

        {#if prix !== null}
          <div class="mt-8 p-4 bg-green-50 border border-green-200 rounded-xl text-center animate-fade-in">
            <p class="text-sm text-green-800 font-medium mb-1">Valeur estimée</p>
            <p class="text-3xl font-bold text-green-600">{prix.toLocaleString('fr-FR')} €</p>
          </div>
        {/if}
      </div>

      <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden h-150">
        <iframe 
          src="/carte_prix_immobiliers.html" 
          title="Carte interactive des prix immobiliers"
          class="w-full h-full border-0"
        ></iframe>
      </div>

    </div>
  </div>
</main>