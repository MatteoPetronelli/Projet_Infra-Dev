<script lang="ts">
  import { onMount } from 'svelte';
  import { slide } from 'svelte/transition';
  import Chart from 'chart.js/auto';

  let stats = $state<{agences: number, transactions: number | string, performance: string}>({
    agences: 12,
    transactions: "...",
    performance: "67% R2"
  });

  let usersList = $state<any[]>([]);
  let feedback = $state({ message: '', type: 'success' });
  let currentAdmin = $state<{ email: string; pole: string } | null>(null);
  let idASupprimer = $state<string | null>(null);

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
  let telechargementEnCours = $state(false);

  let chartCanvas = $state<HTMLCanvasElement | null>(null);
  let chartInstance: Chart | null = null;

  $effect(() => {
    if (reportData && reportData.performances && reportData.performances.length > 0 && chartCanvas) {
      if (chartInstance) chartInstance.destroy();
      
      chartInstance = new Chart(chartCanvas, {
        type: 'bar',
        data: {
          labels: reportData.performances.map((p: any) => p.agence),
          datasets: [{
            label: 'Volume d\'estimations',
            data: reportData.performances.map((p: any) => p.requetes),
            backgroundColor: 'rgba(59, 130, 246, 0.8)',
            hoverBackgroundColor: 'rgba(96, 165, 250, 1)',
            borderRadius: 6,
            borderSkipped: false
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { 
              grid: { color: 'rgba(255, 255, 255, 0.05)' }, 
              ticks: { color: '#9ca3af', font: { family: 'monospace' } } 
            },
            x: { 
              grid: { display: false }, 
              ticks: { color: '#9ca3af', font: { size: 10 } } 
            }
          }
        }
      });
    }
  });

  async function chargerStatsInitiales() {
    try {
      const res = await fetch('http://localhost:8000/api/stats-immobilieres', { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        stats.transactions = data.total_ventes || 0;
      }
    } catch (err) {
      console.error(err);
    }
  }

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
      if (res.ok) {
        reportData = await res.json();
      }
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
      if (res.ok) {
        let data = await res.json();
        
        if (data.tendances_globales) {
          data.tendances_globales = data.tendances_globales.replace(/(\d+(\.\d+)?)/, (match: string) => {
            return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(parseFloat(match));
          });
          data.tendances_globales = data.tendances_globales.replace(' euros', '');
        }
        
        analysisData = data;
      }
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

  async function telechargerPDF() {
    const element = document.getElementById('rapport-export');
    if (!element) return;

    const actionArea = document.getElementById('pdf-actions');
    if (actionArea) actionArea.style.display = 'none';
    
    telechargementEnCours = true;

    try {
      const htmlToImage = await import('html-to-image');
      const { jsPDF } = await import('jspdf');

      const dataUrl = await htmlToImage.toPng(element, { 
        quality: 0.98, 
        backgroundColor: '#111827',
        pixelRatio: 2
      });

      const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
      const imgProps = pdf.getImageProperties(dataUrl);
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

      pdf.addImage(dataUrl, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save('Rapport_Ymmo_Analytics.pdf');
      
    } catch (error) {
      console.error(error);
    } finally {
      if (actionArea) actionArea.style.display = 'flex';
      telechargementEnCours = false;
    }
  }

  async function saveRole(u: any) {
    if (u.pole === u.initialPole) {
      feedback = { message: "Aucune modification à sauvegarder.", type: 'success' };
      setTimeout(() => feedback.message = '', 3000);
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/api/admin/users/role', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email: u.email, pole: u.pole })
      });

      if (res.ok) {
        u.initialPole = u.pole; 
        feedback = { message: `Privilèges de ${u.email} mis à jour.`, type: 'success' };
      } else {
        const err = await res.json();
        u.pole = u.initialPole; 
        feedback = { message: err.detail || "Action refusée", type: 'error' };
      }
    } catch (error) {
      u.pole = u.initialPole;
      feedback = { message: "Erreur de communication avec le serveur", type: 'error' };
    }
    
    setTimeout(() => feedback.message = '', 4000);
  }

  async function chargerDonneesInitiales() {
    try {
      const authRes = await fetch('http://localhost:8000/api/auth/me', { credentials: 'include' });
      if (authRes.ok) currentAdmin = await authRes.json();

      const usersRes = await fetch('http://localhost:8000/api/admin/users', { credentials: 'include' });
      if (usersRes.ok) {
        const rawUsers = await usersRes.json();
        usersList = rawUsers.map((u: any) => ({ ...u, initialPole: u.pole }));
      }
    } catch (err) {
      console.error("Erreur d'initialisation", err);
    }
  }

  function peutSupprimer(targetUser: any): boolean {
    if (!currentAdmin) return false;
    if (currentAdmin.email === targetUser.email) return false;

    const roleValide = targetUser.initialPole || targetUser.pole;

    if (currentAdmin.pole === "Direction") return true;
    if (currentAdmin.pole === "IT et Support" && roleValide === "Utilisateur") return true;
    
    return false;
  }

  async function supprimerUtilisateur(targetEmail: string) {
    try {
      const res = await fetch(`http://localhost:8000/api/admin/users/${targetEmail}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (res.ok) {
        usersList = usersList.filter(u => u.email !== targetEmail);
        feedback = { message: "Compte utilisateur supprimé avec succès.", type: 'success' };
      } else {
        const err = await res.json();
        feedback = { message: err.detail || "Erreur lors de la suppression.", type: 'error' };
      }
    } catch (error) {
      feedback = { message: "Serveur indisponible.", type: 'error' };
    }
    idASupprimer = null;
    setTimeout(() => feedback.message = '', 3000);
  }

  onMount(() => {
    chargerAudit();
    chargerStatsInitiales();
    chargerDonneesInitiales();
  });
</script>

<div class="space-y-8 animate-pop">
  
  <div class="flex items-center justify-between bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
    <div>
      <h1 class="text-2xl font-black text-gray-900">Tableau de Bord Administrateur</h1>
      <p class="text-gray-500 text-sm mt-1">Gérez votre infrastructure IA et vos données analytiques.</p>
    </div>
    <div class="hidden md:flex items-center gap-3 bg-gray-50 px-4 py-2 rounded-xl border border-gray-200">
      <div class="w-3 h-3 rounded-full {auditData ? 'bg-green-500 animate-pulse' : 'bg-red-500'}"></div>
      <span class="text-xs font-bold text-gray-600 tracking-wider uppercase">Serveur En Ligne</span>
    </div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div class="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 flex items-center justify-between">
      <div>
        <p class="text-xs font-black text-gray-400 uppercase mb-1">Réseau</p>
        <p class="text-2xl font-black text-gray-900">{stats.agences} Agences</p>
        <p class="text-xs text-green-500 font-bold mt-2 flex items-center gap-1">
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
          VPN IPSec Actif
        </p>
      </div>
      <div class="bg-gray-50 p-4 rounded-2xl text-gray-400">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
      </div>
    </div>
    
    <div class="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 flex items-center justify-between">
      <div>
        <p class="text-xs font-black text-gray-400 uppercase mb-1">Volume</p>
        <p class="text-2xl font-black text-gray-900">{typeof stats.transactions === 'number' ? stats.transactions.toLocaleString('fr-FR') : stats.transactions}</p>
        <p class="text-xs text-blue-500 font-bold mt-2 flex items-center gap-1">
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"></path></svg>
          Base DuckDB (Parquet)
        </p>
      </div>
      <div class="bg-blue-50 p-4 rounded-2xl text-blue-400">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>
      </div>
    </div>
    
    <div class="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 flex items-center justify-between">
      <div>
        <p class="text-xs font-black text-gray-400 uppercase mb-1">IA Interne</p>
        <p class="text-2xl font-black text-gray-900">{stats.performance}</p>
        <p class="text-xs text-purple-500 font-bold mt-2 flex items-center gap-1">
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.381z" clip-rule="evenodd"></path></svg>
          Modèle XGBoost v1.0
        </p>
      </div>
      <div class="bg-purple-50 p-4 rounded-2xl text-purple-400">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
      </div>
    </div>
  </div>

  <div class="bg-gray-900 p-10 rounded-3xl text-white shadow-2xl border-l-4 border-blue-500 transition-all duration-300">
    <div class="flex justify-between items-start mb-8">
      <div>
        <h2 class="text-2xl font-bold">Contrôle Siège Social</h2>
        <p class="text-gray-400 text-sm mt-1">Gestion des privilèges et actions de maintenance</p>
      </div>
      <button onclick={chargerAudit} class="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2">
        <svg class="w-4 h-4 {chargementAudit ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
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
        <h3 class="font-bold text-blue-400 mb-4 uppercase text-xs tracking-widest flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
          Reporting Stratégique
        </h3>
        <div class="space-y-4">
          <button onclick={genererRapport} class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-blue-600/50 transition-colors border border-white/5 group flex justify-between items-center">
            <div>
              <p class="text-sm font-bold text-white group-hover:text-blue-100">{chargementReport ? 'Extraction...' : (reportData ? 'Masquer le rapport' : 'Rapport consolidé')}</p>
              <p class="text-xs text-gray-500 group-hover:text-blue-200 mt-1">Export et statistiques de vente globales</p>
            </div>
            <svg class="w-5 h-5 text-gray-600 group-hover:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
          </button>
          <button onclick={chargerAnalyse} class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-blue-600/50 transition-colors border border-white/5 group flex justify-between items-center">
            <div>
              <p class="text-sm font-bold text-white group-hover:text-blue-100">{chargementAnalysis ? 'Analyse...' : (analysisData ? 'Masquer l\'analyse' : 'Analyse des biens')}</p>
              <p class="text-xs text-gray-500 group-hover:text-blue-200 mt-1">Identification des tendances de prix</p>
            </div>
            <svg class="w-5 h-5 text-gray-600 group-hover:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
          </button>
        </div>
      </div>

      <div class="bg-white/5 border border-white/10 p-6 rounded-2xl">
        <h3 class="font-bold text-blue-400 mb-4 uppercase text-xs tracking-widest flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
          Maintenance Systèmes
        </h3>
        <div class="space-y-4">
          <button onclick={() => demandeReentrainement = true} class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-red-600/50 transition-colors border border-white/5 group flex justify-between items-center">
            <div>
              <p class="text-sm font-bold text-white group-hover:text-red-100">{chargementRetrain ? 'Initialisation...' : 'Gestion du Re-entraînement'}</p>
              <p class="text-xs text-gray-500 group-hover:text-red-200 mt-1">Injecter les nouvelles ventes DVF dans l'IA</p>
            </div>
            <svg class="w-5 h-5 text-gray-600 group-hover:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          </button>
          <button onclick={chargerLogs} class="w-full text-left p-4 rounded-xl bg-white/5 hover:bg-blue-600/50 transition-colors border border-white/5 group flex justify-between items-center">
            <div>
              <p class="text-sm font-bold text-white group-hover:text-blue-100">{chargementLogs ? 'Lecture...' : (logsData ? 'Masquer les logs' : 'Audit de sécurité réseau')}</p>
              <p class="text-xs text-gray-500 group-hover:text-blue-200 mt-1">Journal des connexions au portail interne</p>
            </div>
            <svg class="w-5 h-5 text-gray-600 group-hover:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
          </button>
        </div>
      </div>
    </div>

    <div class="bg-gray-50 p-8 rounded-3xl border border-gray-200 mt-8 shadow-inner">
      {#if feedback.message}
        <div 
          transition:slide={{ duration: 300 }} 
          class="mb-6 px-6 py-3 rounded-xl font-bold shadow-sm flex items-center justify-between border 
          {feedback.type === 'success' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'}"
        >
          <span>{feedback.message}</span>
          <button onclick={() => feedback.message = ''} aria-label="Fermer" class="opacity-50 hover:opacity-100 font-black">&times;</button>
        </div>
      {/if}

      <h3 class="font-black text-gray-800 mb-6 flex items-center gap-2">
        <span class="w-2 h-6 bg-blue-600 rounded-full"></span> 
        Gestion des Accès
      </h3>
      
      <div class="overflow-x-auto">
        <table class="w-full text-left bg-white rounded-2xl overflow-hidden shadow-sm">
          <thead>
            <tr class="text-xs uppercase text-gray-400 border-b border-gray-100 bg-gray-50/50">
              <th class="p-4">Email de l'agent</th>
              <th class="p-4">Pôle assigné</th>
              <th class="p-4 text-right">Actions de sécurité</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            {#each usersList as u}
              <tr class="hover:bg-gray-50/80 transition-colors">
                <td class="p-4 text-sm font-medium text-gray-900">{u.email}</td>
                
                <td class="p-4">
                  {#if currentAdmin?.pole === 'Direction'}
                    <select bind:value={u.pole} class="bg-gray-100 text-sm p-2 rounded-lg text-gray-700 font-bold border-none focus:ring-2 focus:ring-blue-500 outline-none">
                      <option value="Utilisateur">Utilisateur</option>
                      <option value="Direction">Direction</option>
                      <option value="IT et Support">IT et Support</option>
                    </select>
                  {:else}
                    <span class="px-3 py-1 text-xs font-bold rounded-full border 
                      {u.initialPole === 'Direction' ? 'bg-purple-50 text-purple-700 border-purple-200' : 
                      u.initialPole === 'IT et Support' ? 'bg-blue-50 text-blue-700 border-blue-200' : 
                      'bg-gray-100 text-gray-700 border-gray-200'}">
                      {u.initialPole}
                    </span>
                  {/if}
                </td>

                <td class="p-4 flex gap-2 justify-end">
                  {#if currentAdmin?.pole === 'Direction'}
                    <button onclick={async () => await saveRole(u)} class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-black px-4 py-2 rounded-xl transition">
                      Mettre à jour
                    </button>
                  {/if}
                  
                  {#if peutSupprimer(u)}
                    <button onclick={() => idASupprimer = u.email} class="bg-red-600 hover:bg-red-700 text-white text-xs font-black px-4 py-2 rounded-xl transition">
                      Révoquer
                    </button>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>

    {#if idASupprimer !== null}
      <div class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-pop">
        <div class="bg-white p-8 rounded-3xl text-center shadow-2xl max-w-sm w-full border border-gray-100">
          <div class="w-12 h-12 bg-red-50 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-black">!</div>
          <h3 class="font-black text-xl text-gray-900 mb-2">Confirmer la révocation</h3>
          <p class="text-gray-500 text-sm mb-6 leading-relaxed">
            Voulez-vous vraiment supprimer l'accès réseau de <span class="font-bold text-gray-900">{idASupprimer}</span> ? Cette action est définitive.
          </p>
          <div class="flex gap-3 justify-center">
            <button onclick={() => idASupprimer = null} class="px-5 py-2.5 rounded-xl font-bold text-gray-500 bg-gray-100 hover:bg-gray-200 transition">Annuler</button>
            <button onclick={async () => await supprimerUtilisateur(idASupprimer as string)} class="bg-red-600 text-white px-5 py-2.5 rounded-xl font-black hover:bg-red-700 transition shadow-lg shadow-red-200">Confirmer</button>
          </div>
        </div>
      </div>
    {/if}

    {#if analysisData}
      <div class="mt-8 animate-pop">
        <div class="bg-white/5 border border-white/10 rounded-2xl overflow-hidden p-6 relative">
          <div class="absolute top-0 right-0 p-6 opacity-10 pointer-events-none">
            <svg class="w-24 h-24 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path></svg>
          </div>
          <h4 class="font-bold text-lg text-white mb-2">Analyse Stratégique du Marché</h4>
          <p class="text-sm text-blue-200 bg-blue-900/40 p-4 rounded-xl border border-blue-500/30 mb-6 flex items-start gap-3">
            <svg class="w-5 h-5 shrink-0 mt-0.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span class="leading-relaxed font-medium">{analysisData.tendances_globales}</span>
          </p>
          
          {#if analysisData.top_regions && analysisData.top_regions.length > 0}
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 relative z-10">
              {#each analysisData.top_regions as region}
                <div class="bg-black/30 border border-white/5 p-4 rounded-xl hover:bg-black/40 transition-colors">
                  <p class="font-bold text-white mb-3 text-lg flex items-center gap-2">
                    <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                    {region.ville}
                  </p>
                  <div class="flex justify-between items-center text-xs bg-white/5 p-2 rounded-lg">
                    <span class="text-gray-400">Demande:</span>
                    <span class="font-bold {region.demande === 'Très Forte' ? 'text-green-400' : 'text-yellow-400'}">{region.demande}</span>
                  </div>
                  <div class="flex justify-between items-center text-xs mt-2 bg-white/5 p-2 rounded-lg">
                    <span class="text-gray-400">Recherche N°1:</span>
                    <span class="text-white font-mono font-bold bg-blue-500/20 px-2 py-0.5 rounded text-[10px]">{region.type_populaire}</span>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    {/if}

    {#if reportData}
      <div class="mt-8 animate-pop">
        <div id="rapport-export" class="bg-[#111827] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
          <div class="p-8 border-b border-white/10 flex flex-col md:flex-row md:justify-between md:items-center bg-linear-to-r from-blue-900/20 to-transparent gap-4">
            <div>
              <h4 class="font-black text-2xl text-white">Statistiques Globales Base DVF</h4>
              <p class="text-sm text-blue-300/80 mt-1 font-mono">Période : {reportData.periode}</p>
            </div>
            <div class="flex items-center gap-6">
              <div id="pdf-actions">
                <button onclick={telechargerPDF} disabled={telechargementEnCours} class="bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2">
                  {#if telechargementEnCours}
                    <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                    Génération...
                  {:else}
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    Télécharger PDF
                  {/if}
                </button>
              </div>
              <div class="md:text-right border-l border-white/10 pl-6">
                <p class="text-4xl font-black text-blue-400 tracking-tight">{typeof reportData.volume_global === 'number' ? reportData.volume_global.toLocaleString('fr-FR') : reportData.volume_global}</p>
                <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">Transactions Indexées</p>
              </div>
            </div>
          </div>
          
          {#if reportData.performances && reportData.performances.length > 0}
            <div class="p-8 border-b border-white/10 bg-black/40">
              <div class="h-72 w-full">
                <canvas bind:this={chartCanvas}></canvas>
              </div>
            </div>
            
            <div class="overflow-x-auto p-4 bg-[#111827]">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="text-xs uppercase tracking-widest text-gray-500 border-b border-white/10">
                    <th class="p-4 font-bold">Catégorie de bien</th>
                    <th class="p-4 font-bold text-center">Volume des ventes</th>
                    <th class="p-4 font-bold text-center">Taux d'erreur IA</th>
                    <th class="p-4 font-bold text-right">Prix Moyen / m²</th>
                  </tr>
                </thead>
                <tbody class="text-sm">
                  {#each reportData.performances as perf}
                    <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td class="p-4 font-bold text-white flex items-center gap-3">
                        <div class="w-8 h-8 rounded-full bg-blue-900/50 flex items-center justify-center text-blue-400 text-xs">
                          {perf.agence.substring(0, 2).toUpperCase()}
                        </div>
                        {perf.agence}
                      </td>
                      <td class="p-4 text-gray-300 font-mono text-center bg-black/20">{perf.requetes.toLocaleString('fr-FR')}</td>
                      <td class="p-4 text-center">
                        <span class="px-2.5 py-1 rounded-md text-xs font-bold border {perf.taux_erreur < 7 ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'}">
                          {perf.taux_erreur}%
                        </span>
                      </td>
                      <td class="p-4 font-mono text-xs text-right font-bold {perf.tendance.includes('+') ? 'text-green-400' : 'text-red-400'}">
                        {perf.tendance}
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {/if}
        </div>
      </div>
    {/if}

    {#if logsData}
      <div class="mt-8 animate-pop">
        <div class="bg-black/40 border border-gray-700 rounded-2xl overflow-hidden p-6 shadow-inner">
          <div class="flex justify-between items-center mb-6">
            <div>
              <h4 class="font-bold text-lg text-white flex items-center gap-2">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
                Journal d'Événements Sécurisé
              </h4>
              <p class="text-xs text-gray-500 mt-1">Données en direct issues de DuckDB</p>
            </div>
            <span class="px-3 py-1 bg-green-500/10 text-green-400 text-[10px] uppercase tracking-widest font-bold rounded-full border border-green-500/20 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
              Connecté
            </span>
          </div>
          <div class="space-y-3 font-mono text-xs">
            {#if logsData.logs && logsData.logs.length > 0}
              {#each logsData.logs as log}
                <div class="flex items-center justify-between p-3 bg-gray-900/80 rounded-lg border border-gray-800 hover:border-gray-600 transition-colors">
                  <div class="flex items-center gap-6">
                    <span class="text-gray-500 w-32">{log.timestamp}</span>
                    <span class="{log.action === 'LOGIN_FAILED' ? 'text-red-400' : (log.action === 'LOGIN_SUCCESS' ? 'text-green-400' : 'text-blue-400')} font-bold w-32 tracking-wider flex items-center gap-1.5">
                      {#if log.action === 'LOGIN_FAILED'}
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                      {:else if log.action === 'LOGIN_SUCCESS'}
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                      {:else}
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                      {/if}
                      {log.action}
                    </span>
                    <span class="text-gray-300 w-48 truncate">{log.user}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-gray-600">IP:</span>
                    <span class="text-gray-400 bg-black/50 px-2 py-1 rounded border border-white/5">{log.ip}</span>
                  </div>
                </div>
              {/each}
            {:else}
              <div class="text-center p-8 text-gray-500 border border-dashed border-gray-700 rounded-xl bg-gray-900/50">
                <svg class="w-8 h-8 mx-auto mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path></svg>
                Aucun événement enregistré pour le moment.
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

{#if demandeReentrainement}
  <div class="fixed inset-0 bg-gray-900/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-pop">
    <div class="bg-gray-900 rounded-3xl shadow-2xl w-full max-w-md overflow-hidden p-8 text-center border border-gray-700 relative">
      <div class="absolute top-0 left-0 w-full h-1 bg-yellow-500"></div>
      <div class="w-20 h-20 bg-yellow-500/10 text-yellow-500 border-4 border-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
      </div>
      <h3 class="font-black text-2xl text-white mb-3">Re-entraînement IA</h3>
      <p class="text-gray-400 text-sm mb-8 leading-relaxed">
        Cette opération va compiler les nouvelles données massives DVF et consommer d'importantes ressources serveur (CPU/RAM). Voulez-vous continuer ?
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