<script lang="ts">
  import { onMount } from 'svelte';

  let stats = $state({
    agences: 12,
    transactions: 1450,
    performance: "67% R2"
  });

  let auditData = $state<any>(null);
  let chargement = $state(false);

  async function chargerAudit() {
    chargement = true;
    try {
      const res = await fetch('http://localhost:8000/api/admin/audit', { credentials: 'include' });
      if (res.ok) {
        auditData = await res.json();
      }
    } catch (err) {
      console.error(err);
    } finally {
      chargement = false;
    }
  }

  onMount(() => {
    chargerAudit();
  });
</script>

<div class="space-y-8 animate-pop">
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div class="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
      <p class="text-xs font-black text-gray-400 uppercase mb-1">Reseau</p>
      <p class="text-2xl font-black text-gray-900">{stats.agences} Agences</p>
      <p class="text-xs text-green-500 font-bold mt-2">VPN IPSec Actif</p>
    </div>
    <div class="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
      <p class="text-xs font-black text-gray-400 uppercase mb-1">Volume</p>
      <p class="text-2xl font-black text-gray-900">{stats.transactions} Ventes</p>
      <p class="text-xs text-blue-500 font-bold mt-2">Base de donnees centralisee</p>
    </div>
    <div class="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
      <p class="text-xs font-black text-gray-400 uppercase mb-1">IA Interne</p>
      <p class="text-2xl font-black text-gray-900">{stats.performance}</p>
      <p class="text-xs text-purple-500 font-bold mt-2">Modele XGBoost v1.0</p>
    </div>
  </div>

  <div class="bg-gray-900 p-10 rounded-3xl text-white shadow-2xl border-l-4 border-blue-500">
    <div class="flex justify-between items-start mb-8">
      <div>
        <h2 class="text-2xl font-bold">Controle Siege Social</h2>
        <p class="text-gray-400 text-sm mt-1">Gestion des privileges et infrastructure</p>
      </div>
      <button onclick={chargerAudit} class="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-xl text-xs font-bold transition-all">
        {chargement ? 'Actualisation...' : 'Actualiser'}
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white/5 border border-white/10 p-6 rounded-2xl">
        <h3 class="font-bold text-blue-400 mb-4 uppercase text-xs tracking-widest">Reporting Strategique</h3>
        <div class="space-y-4">
          <button class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors border border-white/5">
            <p class="text-sm font-bold text-white">Rapport consolidé des 12 agences</p>
            <p class="text-xs text-gray-500 mt-1">Export PDF des performances mensuelles</p>
          </button>
          <button class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors border border-white/5">
            <p class="text-sm font-bold text-white">Analyse des biens populaires</p>
            <p class="text-xs text-gray-500 mt-1">Identification des zones a fort potentiel</p>
          </button>
        </div>
      </div>

      <div class="bg-white/5 border border-white/10 p-6 rounded-2xl">
        <h3 class="font-bold text-blue-400 mb-4 uppercase text-xs tracking-widest">Maintenance Systemes</h3>
        <div class="space-y-4">
          <button class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors border border-white/5">
            <p class="text-sm font-bold text-white">Gestion du Re-entrainement</p>
            <p class="text-xs text-gray-500 mt-1">Injecter les nouvelles ventes DVF</p>
          </button>
          <button class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors border border-white/5">
            <p class="text-sm font-bold text-white">Audit de securite reseau</p>
            <p class="text-xs text-gray-500 mt-1">Journal des connexions VPN et authentifications</p>
          </button>
        </div>
      </div>
    </div>

    {#if auditData}
      <div class="mt-8 p-4 bg-blue-600/20 border border-blue-500/30 rounded-2xl">
        <p class="text-xs font-mono text-blue-300">Statut Serveur : {auditData.status}</p>
      </div>
    {/if}
  </div>
</div>