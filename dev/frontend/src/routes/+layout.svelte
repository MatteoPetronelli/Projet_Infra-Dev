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
      <header class="text-center flex flex-col items-center">
        <h1 class="text-5xl font-black text-gray-900 tracking-tight">Ymmo <span class="text-blue-600">Analytics</span></h1>
        
        {#if user}
          <nav class="mt-6 flex items-center gap-4 bg-white px-6 py-2 rounded-2xl shadow-sm border border-gray-100 animate-pop">
            <a href="/estimer" class="text-sm font-bold {($page.url.pathname as string) === '/estimer' ? 'text-blue-600' : 'text-gray-400'}">Estimateur</a>
            
            {#if user.pole === "Direction" || user.pole === "IT et Support"}
              <a href="/admin" class="text-sm font-bold {($page.url.pathname as string) === '/admin' ? 'text-blue-600' : 'text-gray-400'}">Siege</a>
            {/if}
            
            <div class="w-px h-6 bg-gray-100 mx-2"></div>
            <button onclick={logout} class="text-xs font-black text-red-400 uppercase">Quitter</button>
          </nav>
        {/if}
      </header>

      {@render children()}
    {:else}
      <div class="flex items-center justify-center h-64">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    {/if}
  </div>
</main>