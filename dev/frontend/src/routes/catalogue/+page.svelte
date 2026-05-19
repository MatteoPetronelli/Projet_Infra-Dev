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
  let userPole = $state<string | null>(null);

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
    try {
      const res = await fetch('http://localhost:8000/api/auth/me', { credentials: 'include' });
      if (res.ok) {
        const u = await res.json();
        userPole = u.pole;
      }
    } catch (err) { console.error("Non connecté"); }
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
        afficherNotification('Annonce créée avec succès', 'success');
      } else {
        afficherNotification('Erreur lors de la création', 'error');
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
      const res = await fetch(`http://localhost:8000/api/biens/${idASupprimer}`, { method: 'DELETE' });
      if (res.ok) {
        biens = biens.filter(b => b.id !== idASupprimer);
        afficherNotification('Annonce supprimée définitivement', 'success');
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
      <p class="text-gray-500 mt-1">Gérez les annonces de votre agence</p>
    </div>
    
    {#if userPole === "Direction" || userPole === "IT et Support"}
      <button onclick={() => modaleOuverte = true} class="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold shadow-lg shadow-blue-200 hover:bg-blue-700 transition">
        + Ajouter un bien
      </button>
    {/if}
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
    <button onclick={reinitialiserFiltres} class="px-6 py-3 rounded-xl font-bold text-gray-500 bg-gray-100 hover:bg-gray-200 transition h-12">Effacer</button>
  </div>

  {#if chargement}
    <div class="flex justify-center p-10"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>
  {:else if biensFiltres.length === 0}
    <div class="bg-gray-50 p-10 rounded-2xl text-center text-gray-500 border border-dashed border-gray-200 font-bold">Aucun bien trouvé.</div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each biensFiltres as bien}
        <div class="bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 transition-all">
          <div class="h-48 bg-gray-200 relative">
            <div class="absolute top-4 left-4 px-3 py-1 bg-white/90 backdrop-blur-sm rounded-lg text-xs font-black shadow-sm">{bien.type_bien}</div>
          </div>
          <div class="p-6">
            <h3 class="font-bold text-lg text-gray-900 truncate">{bien.titre}</h3>
            <p class="text-gray-400 text-sm mb-4">{bien.ville}</p>
            <div class="flex justify-between items-center border-t border-gray-50 pt-4">
              <span class="text-xl font-black text-blue-600">{bien.prix.toLocaleString('fr-FR')} EUR</span>
              {#if userPole === "Direction" || userPole === "IT et Support"}
                <button onclick={() => idASupprimer = bien.id} class="text-xs font-bold text-red-400 hover:text-red-600 transition">Supprimer</button>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

{#if modaleOuverte}
  <div class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-xl p-6">
      <div class="flex justify-between items-center mb-6">
        <h3 class="font-black text-xl text-gray-900">Nouveau bien</h3>
        <button onclick={fermerModale} aria-label="Fermer" class="text-2xl">&times;</button>
      </div>
      <form onsubmit={ajouterBien} class="space-y-4">
        <input type="text" bind:value={nouveauBien.titre} placeholder="Titre" class="w-full bg-gray-50 p-4 rounded-xl border-none" required />
        <div class="grid grid-cols-2 gap-4">
          <input type="text" bind:value={nouveauBien.ville} placeholder="Ville" class="w-full bg-gray-50 p-4 rounded-xl border-none" required />
          <select bind:value={nouveauBien.type_bien} class="w-full bg-gray-50 p-4 rounded-xl border-none">
            <option value="Appartement">Appartement</option>
            <option value="Maison">Maison</option>
          </select>
        </div>
        <div class="flex gap-2">
            <input type="number" bind:value={nouveauBien.prix} placeholder="Prix" class="w-full bg-gray-50 p-4 rounded-xl border-none" required />
            <input type="number" bind:value={nouveauBien.surface} placeholder="m2" class="w-full bg-gray-50 p-4 rounded-xl border-none" required />
        </div>
        <button type="submit" class="w-full bg-blue-600 text-white p-4 rounded-xl font-bold">Valider</button>
      </form>
    </div>
  </div>
{/if}

{#if idASupprimer !== null}
  <div class="fixed inset-0 bg-gray-900/40 z-50 flex items-center justify-center p-4">
    <div class="bg-white p-8 rounded-3xl text-center shadow-2xl">
      <h3 class="font-black text-xl mb-4">Confirmer ?</h3>
      <div class="flex gap-4">
        <button onclick={() => idASupprimer = null} class="px-6 py-2 rounded-xl bg-gray-100">Annuler</button>
        <button onclick={confirmerSuppression} class="px-6 py-2 rounded-xl bg-red-500 text-white">Supprimer</button>
      </div>
    </div>
  </div>
{/if}

{#if notification}
  <button onclick={fermerNotification} aria-label="Fermer la notification" class="fixed bottom-5 right-5 z-50 px-6 py-4 rounded-2xl bg-white shadow-2xl border {notification.type === 'success' ? 'border-green-200' : 'border-red-200'}">
    {notification.message}
  </button>
{/if}