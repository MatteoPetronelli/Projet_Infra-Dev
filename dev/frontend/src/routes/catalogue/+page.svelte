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
    prix_vente_final?: number;
    date_vente?: string;
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
  
  let modaleVenteOuverte = $state(false);
  let bienAVendre = $state<Bien | null>(null);
  let prixVenteSaisi = $state<number>(0);
  let venteEnCours = $state(false);

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
        credentials: 'include',
        body: JSON.stringify(nouveauBien)
      });
      if (res.ok) {
        const bienCree = await res.json();
        biens = [bienCree, ...biens];
        fermerModale();
        afficherNotification('Annonce créée avec succès', 'success');
      } else {
        const err = await res.json();
        afficherNotification(err.detail || 'Erreur lors de la création', 'error');
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
        method: 'DELETE',
        credentials: 'include'
      });
      if (res.ok) {
        biens = biens.filter(b => b.id !== idASupprimer);
        afficherNotification('Annonce supprimée définitivement', 'success');
      } else {
        const err = await res.json();
        afficherNotification(err.detail || 'Erreur lors de la suppression', 'error');
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

  function ouvrirModaleVente(bien: Bien) {
    bienAVendre = bien;
    prixVenteSaisi = bien.prix;
    modaleVenteOuverte = true;
  }

  function fermerModaleVente() {
    modaleVenteOuverte = false;
    bienAVendre = null;
    prixVenteSaisi = 0;
  }

  async function validerVente(e: SubmitEvent) {
    e.preventDefault();
    if (!bienAVendre) return;
    venteEnCours = true;

    try {
      const res = await fetch(`http://localhost:8000/api/biens/${bienAVendre.id}/vendre`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ prix_vente_final: prixVenteSaisi })
      });

      if (res.ok) {
        const data = await res.json();
        biens = biens.map(b => 
          b.id === bienAVendre!.id 
            ? { ...b, est_vendu: true, prix_vente_final: data.prix_final, date_vente: data.date } 
            : b
        );
        afficherNotification(data.message, 'success');
        fermerModaleVente();
      } else {
        const err = await res.json();
        afficherNotification(err.detail || 'Action refusée', 'error');
      }
    } catch (error) {
      afficherNotification('Erreur de communication avec le serveur', 'error');
    } finally {
      venteEnCours = false;
    }
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
        <div class="bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 transition-all duration-500 relative {bien.est_vendu ? 'opacity-80 grayscale-[0.5]' : ''}">
          <div class="h-48 bg-gray-200 relative overflow-hidden">
            <div class="absolute top-4 left-4 px-3 py-1 bg-white/90 backdrop-blur-sm rounded-lg text-xs font-black shadow-sm z-10">{bien.type_bien}</div>
            
            {#if bien.est_vendu}
              <div class="absolute inset-0 bg-red-900/30 flex items-center justify-center z-20 backdrop-blur-[2px]">
                <span class="bg-red-600 text-white font-black px-8 py-3 rounded-2xl text-2xl -rotate-12 shadow-2xl tracking-widest border-4 border-red-500/50">VENDU</span>
              </div>
            {/if}
          </div>
          
          <div class="p-6">
            <h3 class="font-bold text-lg text-gray-900 truncate">{bien.titre}</h3>
            <p class="text-gray-400 text-sm mb-4">{bien.ville} • {bien.surface} m²</p>
            
            <div class="flex justify-between items-center border-t border-gray-50 pt-4">
              <div>
                {#if bien.est_vendu && bien.prix_vente_final}
                  <span class="block text-xs font-bold text-gray-400 line-through mb-0.5">{bien.prix.toLocaleString('fr-FR')} €</span>
                  <span class="text-xl font-black text-red-600">{bien.prix_vente_final.toLocaleString('fr-FR')} €</span>
                {:else}
                  <span class="text-xl font-black text-blue-600">{bien.prix.toLocaleString('fr-FR')} €</span>
                {/if}
              </div>

              {#if !bien.est_vendu && (userPole === "Direction" || userPole === "IT et Support")}
                <div class="flex gap-2">
                  <button onclick={() => ouvrirModaleVente(bien)} class="text-xs font-black bg-green-100 text-green-700 px-4 py-2 rounded-xl hover:bg-green-200 transition shadow-sm shadow-green-100">
                    Vendre
                  </button>
                  <button onclick={() => idASupprimer = bien.id} class="text-xs font-bold bg-red-50 text-red-400 px-3 py-2 rounded-xl hover:bg-red-100 transition" aria-label="Supprimer">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                  </button>
                </div>
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
        <div class="grid grid-cols-3 gap-2">
            <input type="number" bind:value={nouveauBien.prix} placeholder="Prix (€)" class="w-full bg-gray-50 p-4 rounded-xl border-none" required />
            <input type="number" bind:value={nouveauBien.surface} placeholder="Surface (m²)" class="w-full bg-gray-50 p-4 rounded-xl border-none" required />
            <input type="number" bind:value={nouveauBien.pieces} placeholder="Nb Pièces" class="w-full bg-gray-50 p-4 rounded-xl border-none" required />
        </div>
        <button type="submit" class="w-full bg-blue-600 text-white p-4 rounded-xl font-bold">Valider</button>
      </form>
    </div>
  </div>
{/if}

{#if modaleVenteOuverte && bienAVendre}
  <div class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-pop">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8 border border-gray-100">
      <div class="w-16 h-16 bg-green-50 text-green-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-inner">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      </div>
      <h3 class="font-black text-2xl text-center text-gray-900 mb-2">Conclure la transaction</h3>
      <p class="text-center text-gray-500 text-sm mb-8 truncate px-4">{bienAVendre.titre}</p>

      <form onsubmit={validerVente} class="space-y-6">
        <div>
          <label for="prix_final" class="block text-xs font-black text-gray-400 uppercase mb-3">Prix final négocié (€)</label>
          <div class="relative">
            <input id="prix_final" type="number" bind:value={prixVenteSaisi} class="w-full bg-gray-50 p-4 pl-12 rounded-xl border-none text-xl font-black text-gray-900 focus:ring-2 focus:ring-green-500 outline-none transition-all" required />
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 font-black text-xl">€</span>
          </div>
          <p class="text-xs text-gray-400 mt-2 text-right">Prix catalogue initial : {bienAVendre.prix.toLocaleString('fr-FR')} €</p>
        </div>
        
        <div class="flex gap-3">
          <button type="button" onclick={fermerModaleVente} class="flex-1 px-4 py-3.5 rounded-xl font-bold text-gray-500 bg-gray-100 hover:bg-gray-200 transition">Annuler</button>
          <button type="submit" disabled={venteEnCours} class="flex-1 bg-green-600 text-white p-3.5 rounded-xl font-black shadow-lg shadow-green-200 hover:bg-green-700 transition disabled:opacity-50">
            {venteEnCours ? 'Validation...' : 'Acter la vente'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

{#if idASupprimer !== null}
  <div class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-pop">
    <div class="bg-white p-8 rounded-3xl text-center shadow-2xl max-w-sm w-full border border-gray-100">
      <div class="w-16 h-16 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
      </div>
      <h3 class="font-black text-xl mb-2 text-gray-900">Retirer du catalogue ?</h3>
      <p class="text-gray-500 text-sm mb-6">Cette action effacera le bien de la base de données. Si le bien a été vendu, utilisez le bouton "Vendre" à la place.</p>
      <div class="flex gap-3">
        <button onclick={() => idASupprimer = null} class="flex-1 py-3 rounded-xl font-bold text-gray-500 bg-gray-100 hover:bg-gray-200 transition">Annuler</button>
        <button onclick={confirmerSuppression} class="flex-1 py-3 rounded-xl font-black bg-red-600 text-white hover:bg-red-700 shadow-lg shadow-red-200 transition">Supprimer</button>
      </div>
    </div>
  </div>
{/if}

{#if notification}
  <button onclick={fermerNotification} aria-label="Fermer la notification" class="fixed bottom-5 right-5 z-50 px-6 py-4 rounded-2xl bg-white shadow-2xl border flex items-center gap-3 animate-pop {notification.type === 'success' ? 'border-green-200' : 'border-red-200'}">
    {#if notification.type === 'success'}
      <div class="w-2 h-2 rounded-full bg-green-500"></div>
    {:else}
      <div class="w-2 h-2 rounded-full bg-red-500"></div>
    {/if}
    <span class="font-bold text-gray-800">{notification.message}</span>
  </button>
{/if}