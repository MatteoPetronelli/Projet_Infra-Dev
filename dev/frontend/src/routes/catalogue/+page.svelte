<script lang="ts">
  import { onMount } from 'svelte';

  type Bien = {
    id: number;
    titre: string;
    prix: number;
    surface: number;
    pieces: number;
    type_bien: string;
    est_vendu: boolean;
    ville: string;
  };

  let biens = $state<Bien[]>([]);
  let chargement = $state(true);

  let filtrePrixMax = $state<number | ''>('');
  let filtreSurfaceMin = $state<number | ''>('');
  let filtreType = $state<string>('Tous');

  let modaleOuverte = $state(false);
  let creationEnCours = $state(false);
  let nouveauBien = $state({
    titre: '',
    prix: 0,
    surface: 0,
    pieces: 0,
    type_bien: 'Appartement',
    ville: ''
  });

  let idASupprimer = $state<number | null>(null);
  let notification = $state<{ message: string; type: 'success' | 'error' } | null>(null);
  let notificationTimer: ReturnType<typeof setTimeout>;

  let biensFiltres = $derived(
    biens.filter(b => {
      const prixFiltre = Number(filtrePrixMax);
      const matchPrix = !filtrePrixMax || isNaN(prixFiltre) || prixFiltre <= 0 || b.prix <= prixFiltre;

      const surfaceFiltre = Number(filtreSurfaceMin);
      const matchSurface = !filtreSurfaceMin || isNaN(surfaceFiltre) || surfaceFiltre <= 0 || b.surface >= surfaceFiltre;

      const matchType = filtreType === 'Tous' || b.type_bien === filtreType;

      return matchPrix && matchSurface && matchType;
    })
  );

  function reinitialiserFiltres() {
    filtrePrixMax = '';
    filtreSurfaceMin = '';
    filtreType = 'Tous';
  }

  function afficherNotification(message: string, type: 'success' | 'error') {
    notification = { message, type };
    if (notificationTimer) clearTimeout(notificationTimer);
    notificationTimer = setTimeout(() => {
      notification = null;
    }, 4000);
  }

  function fermerNotification() {
    notification = null;
    if (notificationTimer) clearTimeout(notificationTimer);
  }

  onMount(async () => {
    chargerBiens();
  });

  async function chargerBiens() {
    try {
      const res = await fetch('http://localhost:8000/api/biens');
      if (res.ok) {
        biens = await res.json();
      }
    } catch (err) {
      console.error(err);
    } finally {
      chargement = false;
    }
  }

  async function ajouterBien(e: SubmitEvent) {
    e.preventDefault();
    creationEnCours = true;
    
    try {
      const res = await fetch('http://localhost:8000/api/biens', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nouveauBien)
      });
      
      if (res.ok) {
        const bienCree = await res.json();
        biens = [...biens, bienCree];
        fermerModale();
        afficherNotification('Annonce creee avec succes', 'success');
      } else {
        afficherNotification('Erreur lors de la creation', 'error');
      }
    } catch (err) {
      afficherNotification('Erreur de connexion au serveur', 'error');
    } finally {
      creationEnCours = false;
    }
  }

  async function confirmerSuppression() {
    if (idASupprimer === null) return;
    
    try {
      const res = await fetch(`http://localhost:8000/api/biens/${idASupprimer}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        biens = biens.filter(b => b.id !== idASupprimer);
        afficherNotification('Annonce supprimee definitivement', 'success');
      } else {
        afficherNotification('Erreur lors de la suppression', 'error');
      }
    } catch (err) {
      afficherNotification('Erreur de connexion au serveur', 'error');
    } finally {
      idASupprimer = null;
    }
  }

  function fermerModale() {
    modaleOuverte = false;
    nouveauBien = { titre: '', prix: 0, surface: 0, pieces: 0, type_bien: 'Appartement', ville: '' };
  }
</script>

<div class="space-y-8 animate-pop relative">
  <div class="flex justify-between items-end">
    <div>
      <h2 class="text-3xl font-black text-gray-900">Catalogue des biens</h2>
      <p class="text-gray-500 mt-1">Gerez les annonces de votre agence</p>
    </div>
    <button onclick={() => modaleOuverte = true} class="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold shadow-lg shadow-blue-200 hover:bg-blue-700 transition">
      + Ajouter un bien
    </button>
  </div>

  <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-wrap gap-4 items-end">
    <div class="flex-1 min-w-50">
      <label for="filtrePrix" class="block text-xs font-bold text-gray-400 uppercase mb-2">Prix Maximum (EUR)</label>
      <input id="filtrePrix" type="number" bind:value={filtrePrixMax} placeholder="Ex: 300000" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500">
    </div>
    <div class="flex-1 min-w-50">
      <label for="filtreSurface" class="block text-xs font-bold text-gray-400 uppercase mb-2">Surface Minimum (m2)</label>
      <input id="filtreSurface" type="number" bind:value={filtreSurfaceMin} placeholder="Ex: 50" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500">
    </div>
    <div class="flex-1 min-w-50">
      <label for="filtreType" class="block text-xs font-bold text-gray-400 uppercase mb-2">Type de bien</label>
      <select id="filtreType" bind:value={filtreType} class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500">
        <option value="Tous">Tous</option>
        <option value="Maison">Maison</option>
        <option value="Appartement">Appartement</option>
      </select>
    </div>
    <button onclick={reinitialiserFiltres} class="px-6 py-3 rounded-xl font-bold text-gray-500 bg-gray-100 hover:bg-gray-200 transition h-12">
      Effacer
    </button>
  </div>

  {#if chargement}
    <div class="flex justify-center p-10"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>
  {:else if biensFiltres.length === 0}
    <div class="bg-gray-50 p-10 rounded-2xl text-center text-gray-500 border border-dashed border-gray-200 font-bold">
      Aucun bien ne correspond a vos criteres.
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each biensFiltres as bien}
        <div class="bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 hover:shadow-xl transition-all group">
          <div class="h-48 bg-gray-200 relative">
            <div class="absolute top-4 left-4 px-3 py-1 bg-white/90 backdrop-blur-sm rounded-lg text-xs font-black shadow-sm">
              {bien.type_bien}
            </div>
            {#if bien.est_vendu}
              <div class="absolute inset-0 bg-white/60 backdrop-blur-sm flex items-center justify-center">
                <span class="px-4 py-2 bg-red-500 text-white font-black rounded-xl uppercase tracking-widest rotate-12 shadow-lg">Vendu</span>
              </div>
            {/if}
          </div>
          
          <div class="p-6">
            <h3 class="font-bold text-lg text-gray-900 truncate" title={bien.titre}>{bien.titre}</h3>
            <p class="text-gray-400 text-sm mb-4">{bien.ville}</p>
            
            <div class="flex items-center gap-4 text-sm font-bold text-gray-700 mb-6">
              <span class="bg-gray-50 px-2 py-1 rounded-lg text-blue-600">Surface : <span class="text-gray-900">{bien.surface} m2</span></span>
              <span class="bg-gray-50 px-2 py-1 rounded-lg text-blue-600">Pieces : <span class="text-gray-900">{bien.pieces}</span></span>
            </div>
            
            <div class="flex justify-between items-center border-t border-gray-50 pt-4">
              <span class="text-xl font-black text-blue-600">{bien.prix.toLocaleString('fr-FR')} EUR</span>
              <button onclick={() => idASupprimer = bien.id} class="text-xs font-bold text-red-400 hover:text-red-600 transition">
                Supprimer
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

{#if modaleOuverte}
  <div class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-pop">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-xl overflow-hidden">
      <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
        <h3 class="font-black text-xl text-gray-900">Nouveau bien immobilier</h3>
        <button onclick={fermerModale} class="text-gray-400 hover:text-gray-900 font-bold text-xl">&times;</button>
      </div>
      
      <form onsubmit={ajouterBien} class="p-6 space-y-6">
        <div>
          <label for="titreBien" class="block text-xs font-bold text-gray-400 uppercase mb-2">Titre de l'annonce</label>
          <input id="titreBien" type="text" bind:value={nouveauBien.titre} required placeholder="Ex: Superbe appartement vue mer" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500">
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="villeBien" class="block text-xs font-bold text-gray-400 uppercase mb-2">Ville</label>
            <input id="villeBien" type="text" bind:value={nouveauBien.ville} required placeholder="Ex: Marseille" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500">
          </div>
          <div>
            <label for="typeBienForm" class="block text-xs font-bold text-gray-400 uppercase mb-2">Type</label>
            <select id="typeBienForm" bind:value={nouveauBien.type_bien} class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500">
              <option value="Appartement">Appartement</option>
              <option value="Maison">Maison</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <div>
            <label for="prixBien" class="block text-xs font-bold text-gray-400 uppercase mb-2">Prix (EUR)</label>
            <input id="prixBien" type="number" bind:value={nouveauBien.prix} required min="1" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500">
          </div>
          <div>
            <label for="surfaceBien" class="block text-xs font-bold text-gray-400 uppercase mb-2">Surface (m2)</label>
            <input id="surfaceBien" type="number" bind:value={nouveauBien.surface} required min="1" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500">
          </div>
          <div>
            <label for="piecesBien" class="block text-xs font-bold text-gray-400 uppercase mb-2">Pieces</label>
            <input id="piecesBien" type="number" bind:value={nouveauBien.pieces} required min="1" class="w-full bg-gray-50 border-none rounded-xl py-3 px-4 focus:ring-2 focus:ring-blue-500">
          </div>
        </div>

        <div class="pt-4 border-t border-gray-100 flex justify-end gap-3">
          <button type="button" onclick={fermerModale} class="px-6 py-3 rounded-xl font-bold text-gray-500 hover:bg-gray-100 transition">Annuler</button>
          <button type="submit" disabled={creationEnCours} class="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold shadow-lg shadow-blue-200 hover:bg-blue-700 transition disabled:opacity-50">
            {creationEnCours ? 'Creation...' : 'Valider'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

{#if idASupprimer !== null}
  <div class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-pop">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-sm overflow-hidden p-6 text-center">
      <div class="w-16 h-16 bg-red-100 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-black">!</div>
      <h3 class="font-black text-xl text-gray-900 mb-2">Confirmer la suppression</h3>
      <p class="text-gray-500 text-sm mb-6">Cette action est irreversible. Le bien sera retire de la base de donnees.</p>
      <div class="flex gap-3 justify-center">
        <button onclick={() => idASupprimer = null} class="px-6 py-3 rounded-xl font-bold text-gray-500 hover:bg-gray-100 transition">Annuler</button>
        <button onclick={confirmerSuppression} class="bg-red-500 text-white px-6 py-3 rounded-xl font-bold hover:bg-red-600 transition shadow-lg shadow-red-200">Supprimer</button>
      </div>
    </div>
  </div>
{/if}

{#if notification}
  <button
    onclick={fermerNotification}
    class="fixed bottom-5 right-5 z-50 animate-pop text-left cursor-pointer transition-transform hover:scale-105 active:scale-95 shadow-2xl rounded-2xl"
    aria-label="Fermer la notification"
  >
    <div class="px-6 py-4 rounded-2xl flex items-center gap-4 border backdrop-blur-md {notification.type === 'success' ? 'bg-green-50/95 border-green-200 text-green-700' : 'bg-red-50/95 border-red-200 text-red-700'}">
      <div class="w-6 h-6 rounded-full flex items-center justify-center font-black text-xs {notification.type === 'success' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}">
        {notification.type === 'success' ? 'V' : '!'}
      </div>
      <span class="font-bold text-sm pr-2">{notification.message}</span>
      <span class="text-xs opacity-40 hover:opacity-100 transition-opacity font-black">&times;</span>
    </div>
  </button>
{/if}