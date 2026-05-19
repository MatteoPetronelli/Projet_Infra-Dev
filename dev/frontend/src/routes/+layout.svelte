<script lang="ts">
  import "../app.css";
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';

  let { children } = $props();

  let user = $state<{ email: string; pole: string } | null>(null);
  let initialized = $state(false);

  onMount(async () => {
    try {
      const res = await fetch('http://localhost:8000/api/auth/me', { credentials: 'include' });
      if (res.ok) {
        user = await res.json();
        if ($page.url.pathname === '/login' || $page.url.pathname === '/') {
          goto('/estimer');
        }
      } else {
        user = null;
        if ($page.url.pathname !== '/login') {
          goto('/login');
        }
      }
    } catch (err) {
      user = null;
      if ($page.url.pathname !== '/login') goto('/login');
    } finally {
      initialized = true;
    }
  });

  async function logout() {
    await fetch('http://localhost:8000/api/auth/logout', { method: 'POST', credentials: 'include' });
    user = null;
    goto('/login');
  }
</script>

<main class="min-h-screen bg-gray-50 text-gray-900 p-8">
  <div class="max-w-6xl mx-auto space-y-8">
    {#if initialized}
      <header class="flex flex-col items-center">
        <h1 class="text-5xl font-black text-gray-900 tracking-tight">Ymmo <span class="text-blue-600">Analytics</span></h1>
        
        {#if user}
          <nav class="mt-6 flex flex-col md:flex-row items-center justify-between w-full bg-white p-2 rounded-2xl shadow-sm border border-gray-100 animate-pop">
            
            <div class="flex items-center gap-6 px-4 py-2">
              <a href="/estimer" class="text-sm font-bold transition-colors {($page.url.pathname as string) === '/estimer' ? 'text-blue-600' : 'text-gray-400 hover:text-gray-600'}">Estimateur</a>
              <a href="/catalogue" class="text-sm font-bold transition-colors {($page.url.pathname as string) === '/catalogue' ? 'text-blue-600' : 'text-gray-400 hover:text-gray-600'}">Catalogue</a>
              
              {#if user.pole === "Direction" || user.pole === "IT et Support"}
                <a href="/admin" class="text-sm font-bold transition-colors {($page.url.pathname as string) === '/admin' ? 'text-blue-600' : 'text-gray-400 hover:text-gray-600'}">Siège</a>
              {/if}
            </div>
            
            <div class="flex items-center gap-4 px-4 py-2 border-t md:border-t-0 md:border-l border-gray-100 mt-2 md:mt-0 pt-3 md:pt-2 w-full md:w-auto justify-center md:justify-end">
              <div class="text-right hidden sm:block">
                <p class="text-sm font-bold text-gray-900">{user.email}</p>
                <p class="text-xs text-blue-600 font-mono font-bold uppercase tracking-widest">{user.pole}</p>
              </div>
              
              <div 
                class="w-10 h-10 rounded-xl bg-linear-to-br from-blue-600 to-blue-800 flex items-center justify-center text-white font-bold shadow-md shadow-blue-900/20"
                aria-label="Avatar utilisateur"
              >
                {user.email.substring(0, 2).toUpperCase()}
              </div>
              
              <button 
                onclick={logout} 
                aria-label="Se déconnecter"
                class="p-2 bg-gray-50 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
              </button>
            </div>

          </nav>
        {/if}
      </header>

      {@render children()}
    {:else}
      <div class="flex items-center justify-center h-64">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" aria-label="Chargement"></div>
      </div>
    {/if}
  </div>
</main>