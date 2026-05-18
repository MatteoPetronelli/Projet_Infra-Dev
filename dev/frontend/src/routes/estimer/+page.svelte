<script lang="ts">
  import { onMount } from 'svelte';

  let surface = $state<number>(80);
  let pieces = $state<number>(4);
  let estMaison = $state<number>(1);
  let lat = $state<number>(46.1709);
  let lon = $state<number>(5.9072);
  let prix = $state<number | null>(null);
  let chargement = $state<boolean>(false);
  let errorMessage = $state<string>("");

  onMount(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data && event.data.lat && event.data.lon) {
        lat = event.data.lat;
        lon = event.data.lon;
        surface = event.data.surface || surface;
        pieces = event.data.pieces || pieces;
        if (event.data.est_maison !== undefined) {
            estMaison = event.data.est_maison;
        }
        prix = null; 
        errorMessage = "";
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  });

  async function estimerPrix(e: SubmitEvent) {
    e.preventDefault();
    chargement = true;
    errorMessage = "";
    prix = null;
    
    try {
      const response = await fetch('http://localhost:8000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          surface_reelle_bati: surface,
          nombre_pieces_principales: pieces,
          longitude: lon,
          latitude: lat,
          est_maison: estMaison
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        prix = data.prix_estime;
      } else {
        errorMessage = "Erreur lors de l'estimation";
      }
    } catch (err) {
      errorMessage = "Erreur de connexion au serveur";
    } finally {
      chargement = false;
    }
  }
</script>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
  <div class="bg-white p-8 rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100">
    <h2 class="text-2xl font-bold mb-8 flex items-center gap-2">
      <span class="w-2 h-8 bg-blue-600 rounded-full"></span>
      Estimation
    </h2>
    
    {#if errorMessage}
      <div class="mb-6 p-3 bg-red-50 text-red-600 text-sm font-bold rounded-xl text-center">
        {errorMessage}
      </div>
    {/if}

    <form onsubmit={estimerPrix} class="space-y-6">
      <div class="space-y-1">
        <label for="typeBien" class="text-xs font-bold text-gray-400 uppercase ml-1">Type de propriete</label>
        <select name="typeBien" id="typeBien" bind:value={estMaison} class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500 transition">
          <option value={1}>Maison individuelle</option>
          <option value={0}>Appartement</option>
        </select>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="surfaceInput" class="text-xs font-bold text-gray-400 uppercase ml-1">Surface (m2)</label>
          <input name="surface" type="number" bind:value={surface} id="surfaceInput" required autocomplete="off" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500 transition" />
        </div>
        <div class="space-y-1">
          <label for="piecesInput" class="text-xs font-bold text-gray-400 uppercase ml-1">Pieces</label>
          <input name="pieces" type="number" bind:value={pieces} id="piecesInput" required autocomplete="off" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500 transition" />
        </div>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="latInput" class="text-xs font-bold text-gray-400 uppercase ml-1">Latitude</label>
          <input name="latitude" type="number" step="any" bind:value={lat} id="latInput" required autocomplete="off" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500 transition" />
        </div>
        <div class="space-y-1">
          <label for="lonInput" class="text-xs font-bold text-gray-400 uppercase ml-1">Longitude</label>
          <input name="longitude" type="number" step="any" bind:value={lon} id="lonInput" required autocomplete="off" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500 transition" />
        </div>
      </div>
      <button type="submit" disabled={chargement} class="w-full bg-gray-900 text-white py-4 rounded-2xl font-bold hover:bg-blue-600 transition-all disabled:opacity-50">
        {chargement ? 'Calcul...' : 'Estimer'}
      </button>
    </form>
    
    {#if prix !== null}
      <div class="mt-8 p-6 bg-blue-600 rounded-3xl text-center text-white animate-pop">
        <p class="text-sm font-bold text-blue-200 mb-1 uppercase tracking-widest">Valeur estimee</p>
        <p class="text-4xl font-black">{Math.round(prix).toLocaleString('fr-FR')} EUR</p>
      </div>
    {/if}
  </div>
  <div class="lg:col-span-2 bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden h-120 relative">
    <iframe src="/carte_prix_immobiliers.html" title="Carte interactive" class="w-full h-full border-0"></iframe>
  </div>
</div>