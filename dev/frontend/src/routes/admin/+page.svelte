<script lang="ts">
  import { onMount } from 'svelte';

  let stats = $state({
    agences: 12,
    transactions: 1450,
    performance: "67% R2"
  });

  let auditData = $state<any>(null);
  let reportData = $state<any>(null);
  let logsData = $state<any>(null);
  let analysisData = $state<any>(null);
  let retrainStatus = $state<any>(null);
  
  let chargementAudit = $state(false);
  let chargementReport = $state(false);
  let chargementLogs = $state(false);
  let chargementAnalysis = $state(false);
  let chargementRetrain = $state(false);
  let demandeReentrainement = $state(false);

  async function chargerAudit() {
    chargementAudit = true;
    try {
      const res = await fetch('http://localhost:8000/api/admin/audit', { credentials: 'include' });
      if (res.ok) auditData = await res.json();
    } catch (err) {
      console.error(err);
    } finally {
      chargementAudit = false;
    }
  }

  async function genererRapport() {
    if (reportData) { reportData = null; return; }
    chargementReport = true;
    try {
      const res = await fetch('http://localhost:8000/api/admin/reports', { credentials: 'include' });
      if (res.ok) reportData = await res.json();
    } catch (err) {
      console.error(err);
    } finally {
      chargementReport = false;
    }
  }

  async function chargerLogs() {
    if (logsData) { logsData = null; return; }
    chargementLogs = true;
    try {
      const res = await fetch('http://localhost:8000/api/admin/logs', { credentials: 'include' });
      if (res.ok) logsData = await res.json();
    } catch (err) {
      console.error(err);
    } finally {
      chargementLogs = false;
    }
  }

  async function chargerAnalyse() {
    if (analysisData) { analysisData = null; return; }
    chargementAnalysis = true;
    try {
      const res = await fetch('http://localhost:8000/api/admin/analysis', { credentials: 'include' });
      if (res.ok) analysisData = await res.json();
    } catch (err) {
      console.error(err);
    } finally {
      chargementAnalysis = false;
    }
  }

  async function lancerReentrainement() {
    demandeReentrainement = false;
    chargementRetrain = true;
    try {
      const res = await fetch('http://localhost:8000/api/admin/retrain', { 
        method: 'POST',
        credentials: 'include' 
      });
      if (res.ok) retrainStatus = await res.json();
    } catch (err) {
      console.error(err);
    } finally {
      chargementRetrain = false;
      setTimeout(() => { retrainStatus = null; }, 8000);
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

  <div class="bg-gray-900 p-10 rounded-3xl text-white shadow-2xl border-l-4 border-blue-500 transition-all duration-300">
    <div class="flex justify-between items-start mb-8">
      <div>
        <h2 class="text-2xl font-bold">Controle Siege Social</h2>
        <p class="text-gray-400 text-sm mt-1">Gestion des privileges et infrastructure</p>
      </div>
      <button onclick={chargerAudit} class="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-xl text-xs font-bold transition-all">
        {chargementAudit ? 'Actualisation...' : 'Actualiser Statut'}
      </button>
    </div>

    {#if retrainStatus}
      <div class="mb-8 p-4 bg-blue-900/50 border border-blue-500 rounded-2xl flex items-center justify-between animate-pop">
        <div>
          <p class="font-bold text-blue-300">{retrainStatus.message}</p>
          <p class="text-xs text-blue-400/80 mt-1">{retrainStatus.details}</p>
        </div>
        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-400"></div>
      </div>
    {/if}

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white/5 border border-white/10 p-6 rounded-2xl">
        <h3 class="font-bold text-blue-400 mb-4 uppercase text-xs tracking-widest">Reporting Strategique</h3>
        <div class="space-y-4">
          <button onclick={genererRapport} class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-blue-600/50 transition-colors border border-white/5 group">
            <p class="text-sm font-bold text-white group-hover:text-blue-100">{chargementReport ? 'Extraction...' : (reportData ? 'Masquer le rapport' : 'Rapport consolide des 12 agences')}</p>
            <p class="text-xs text-gray-500 group-hover:text-blue-200 mt-1">Export et performances mensuelles</p>
          </button>
          <button onclick={chargerAnalyse} class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-blue-600/50 transition-colors border border-white/5 group">
            <p class="text-sm font-bold text-white group-hover:text-blue-100">{chargementAnalysis ? 'Analyse...' : (analysisData ? 'Masquer l\'analyse' : 'Analyse des biens populaires')}</p>
            <p class="text-xs text-gray-500 group-hover:text-blue-200 mt-1">Identification des zones a fort potentiel</p>
          </button>
        </div>
      </div>

      <div class="bg-white/5 border border-white/10 p-6 rounded-2xl">
        <h3 class="font-bold text-blue-400 mb-4 uppercase text-xs tracking-widest">Maintenance Systemes</h3>
        <div class="space-y-4">
          <button onclick={() => demandeReentrainement = true} class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-red-600/50 transition-colors border border-white/5 group">
            <p class="text-sm font-bold text-white group-hover:text-red-100">{chargementRetrain ? 'Initialisation...' : 'Gestion du Re-entrainement'}</p>
            <p class="text-xs text-gray-500 group-hover:text-red-200 mt-1">Injecter les nouvelles ventes DVF dans l'IA</p>
          </button>
          <button onclick={chargerLogs} class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-blue-600/50 transition-colors border border-white/5 group">
            <p class="text-sm font-bold text-white group-hover:text-blue-100">{chargementLogs ? 'Lecture...' : (logsData ? 'Masquer les logs' : 'Audit de securite reseau')}</p>
            <p class="text-xs text-gray-500 group-hover:text-blue-200 mt-1">Journal des connexions VPN et authentifications</p>
          </button>
        </div>
      </div>
    </div>

    {#if analysisData}
      <div class="mt-8 animate-pop">
        <div class="bg-white/5 border border-white/10 rounded-2xl overflow-hidden p-6">
          <h4 class="font-bold text-lg text-white mb-2">Analyse Strategique du Marche</h4>
          <p class="text-sm text-blue-300 bg-blue-900/30 p-3 rounded-xl border border-blue-800/50 mb-6">{analysisData.tendances_globales}</p>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            {#each analysisData.top_regions as region}
              <div class="bg-black/30 border border-white/5 p-4 rounded-xl">
                <p class="font-bold text-white mb-1">{region.ville}</p>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-gray-400">Demande:</span>
                  <span class="font-bold {region.demande === 'Tres Forte' ? 'text-green-400' : 'text-yellow-400'}">{region.demande}</span>
                </div>
                <div class="flex justify-between items-center text-xs mt-2 pt-2 border-t border-white/5">
                  <span class="text-gray-400">Recherche No 1:</span>
                  <span class="text-white font-mono">{region.type_populaire}</span>
                </div>
              </div>
            {/each}
          </div>
        </div>
      </div>
    {/if}

    {#if reportData}
      <div class="mt-8 animate-pop">
        <div class="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
          <div class="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
            <div>
              <h4 class="font-bold text-lg text-white">Performances du Reseau</h4>
              <p class="text-xs text-gray-400 mt-1">Periode : {reportData.periode}</p>
            </div>
            <div class="text-right">
              <p class="text-2xl font-black text-blue-400">{reportData.precision_moyenne}%</p>
              <p class="text-xs text-gray-400">Precision Moyenne IA</p>
            </div>
          </div>
          
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-white/5 text-xs uppercase tracking-widest text-gray-400 border-b border-white/10">
                  <th class="p-4 font-bold">Agence</th>
                  <th class="p-4 font-bold">Estimations (Vol.)</th>
                  <th class="p-4 font-bold">Marge d'erreur</th>
                  <th class="p-4 font-bold">Activite</th>
                </tr>
              </thead>
              <tbody class="text-sm">
                {#each reportData.performances as perf}
                  <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td class="p-4 font-bold text-white">{perf.agence}</td>
                    <td class="p-4 text-gray-300">{perf.requetes}</td>
                    <td class="p-4">
                      <span class="px-2 py-1 rounded-md text-xs font-bold {perf.taux_erreur < 7 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}">
                        {perf.taux_erreur}%
                      </span>
                    </td>
                    <td class="p-4 font-mono text-xs {perf.tendance.includes('+') ? 'text-green-400' : 'text-red-400'}">
                      {perf.tendance}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    {/if}

    {#if logsData}
      <div class="mt-8 animate-pop">
        <div class="bg-black/40 border border-gray-700 rounded-2xl overflow-hidden p-6 shadow-inner">
          <div class="flex justify-between items-center mb-6">
            <div>
              <h4 class="font-bold text-lg text-white">Journal d'Evenements</h4>
              <p class="text-xs text-gray-400 mt-1">Surveillance des acces en temps reel</p>
            </div>
            <span class="px-3 py-1 bg-green-500/20 text-green-400 text-xs font-bold rounded-full border border-green-500/30">Connecte au SIEM</span>
          </div>
          <div class="space-y-3 font-mono text-xs">
            {#each logsData.logs as log}
              <div class="flex items-center justify-between p-3 bg-gray-900/80 rounded-lg border border-gray-800 hover:border-gray-600 transition-colors">
                <div class="flex items-center gap-6">
                  <span class="text-gray-500">{log.timestamp}</span>
                  <span class="{log.action === 'LOGIN_FAILED' ? 'text-red-400' : (log.action === 'LOGIN_SUCCESS' ? 'text-green-400' : 'text-blue-400')} font-bold w-32 tracking-wider">
                    {log.action}
                  </span>
                  <span class="text-gray-300 w-48 truncate">{log.user}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-gray-600">IP:</span>
                  <span class="text-gray-400 bg-black/50 px-2 py-1 rounded">{log.ip}</span>
                </div>
              </div>
            {/each}
          </div>
        </div>
      </div>
    {/if}

    {#if auditData}
      <div class="mt-8 flex items-center gap-3 border-t border-white/10 pt-6">
        <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
        <p class="text-xs font-mono text-gray-400">Statut Backend : {auditData.status}</p>
      </div>
    {/if}
  </div>
</div>

{#if demandeReentrainement}
  <div class="fixed inset-0 bg-gray-900/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-pop">
    <div class="bg-gray-900 rounded-3xl shadow-2xl w-full max-w-md overflow-hidden p-8 text-center border border-gray-700">
      <div class="w-16 h-16 bg-yellow-500/10 text-yellow-500 border border-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-6 text-3xl font-black">
        !
      </div>
      <h3 class="font-black text-2xl text-white mb-3">Re-entrainement IA</h3>
      <p class="text-gray-400 text-sm mb-8 leading-relaxed">
        Cette operation va compiler les nouvelles donnees massives DVF et consommer d'importantes ressources serveur. Voulez-vous continuer ?
      </p>
      <div class="flex gap-4 justify-center">
        <button onclick={() => demandeReentrainement = false} class="px-6 py-3 rounded-xl font-bold text-gray-400 hover:text-white hover:bg-gray-800 transition">
          Annuler
        </button>
        <button onclick={lancerReentrainement} class="bg-yellow-500 text-gray-900 px-6 py-3 rounded-xl font-black hover:bg-yellow-400 transition shadow-lg shadow-yellow-500/20">
          Lancer l'apprentissage
        </button>
      </div>
    </div>
  </div>
{/if}