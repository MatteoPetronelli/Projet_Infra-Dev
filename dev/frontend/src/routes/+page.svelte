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

<style>
  @keyframes popIn {
    0% { opacity: 0; transform: scale(0.95); }
    100% { opacity: 1; transform: scale(1); }
  }
  .animate-pop {
    animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
  }
</style>

<main class="min-h-screen bg-gray-50 text-gray-900 p-8">
  <div class="max-w-6xl mx-auto space-y-8">
    
    <header class="text-center">
      <div class="inline-block bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-4">
        Bêta v1.0
      </div>
      <h1 class="text-5xl font-black text-gray-900 tracking-tight">Ymmo <span class="text-blue-600">Analytics</span></h1>
      <p class="text-gray-500 mt-2 text-lg">L'expertise immobilière propulsée par l'IA</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <div class="bg-white p-8 rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100">
        <h2 class="text-2xl font-bold mb-8 flex items-center gap-2">
          <span class="w-2 h-8 bg-blue-600 rounded-full"></span>
          Configuration
        </h2>
        
        <form onsubmit={estimerPrix} class="space-y-6">
          <div class="space-y-1">
            <label for="typeBien" class="text-xs font-bold text-gray-400 uppercase ml-1">Type de propriété</label>
            <select id="typeBien" bind:value={estMaison} class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500 transition">
              <option value={1}>Maison individuelle</option>
              <option value={0}>Appartement</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label for="surfaceInput" class="text-xs font-bold text-gray-400 uppercase ml-1">Surface (m²)</label>
              <input id="surfaceInput" type="number" bind:value={surface} min="9" max="500" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500 transition" required />
            </div>
            <div class="space-y-1">
              <label for="piecesInput" class="text-xs font-bold text-gray-400 uppercase ml-1">Pièces</label>
              <input id="piecesInput" type="number" bind:value={pieces} min="1" max="20" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500 transition" required />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label for="latInput" class="text-xs font-bold text-gray-400 uppercase ml-1">Latitude</label>
              <input id="latInput" type="number" step="any" bind:value={lat} class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500 transition" required />
            </div>
            <div class="space-y-1">
              <label for="lonInput" class="text-xs font-bold text-gray-400 uppercase ml-1">Longitude</label>
              <input id="lonInput" type="number" step="any" bind:value={lon} class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500 transition" required />
            </div>
          </div>

          <button type="submit" disabled={chargement} class="w-full bg-gray-900 text-white py-4 rounded-2xl hover:bg-blue-600 transition-all transform hover:-translate-y-1 active:scale-95 font-bold shadow-lg shadow-blue-200 disabled:opacity-50">
            {#if chargement}
              <span class="inline-block animate-spin mr-2">◌</span> Analyse en cours...
            {:else}
              Lancer l'estimation
            {/if}
          </button>
        </form>

        {#if prix !== null}
          <div class="mt-10 p-6 bg-blue-600 rounded-3xl text-center text-white animate-pop shadow-2xl shadow-blue-300">
            <p class="text-blue-200 text-sm font-semibold uppercase tracking-widest mb-2">Estimation suggérée</p>
            <p class="text-4xl font-black">{prix.toLocaleString('fr-FR')} €</p>
            <div class="mt-4 pt-4 border-t border-blue-500/50 flex justify-between items-center text-xs opacity-80">
              <span>Indice de confiance</span>
              <span class="bg-blue-400 px-2 py-1 rounded-md font-bold text-white">67% (R²)</span>
            </div>
          </div>
        {/if}
      </div>

      <div class="lg:col-span-2 bg-white rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100 overflow-hidden h-150 relative">
        <div class="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur px-3 py-2 rounded-xl border border-gray-100 shadow-sm text-xs font-bold text-gray-600 italic">
          Carte interactive - Cliquez pour analyser
        </div>
        <iframe 
          src="/carte_prix_immobiliers.html" 
          title="Carte interactive des prix immobiliers"
          class="w-full h-full border-0"
        ></iframe>
      </div>

    </div>
  </div>
</main>