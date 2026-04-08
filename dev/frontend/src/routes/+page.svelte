<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  onMount(async () => {
    const res = await fetch('http://127.0.0.1:8000/api/auth/me', { credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      if (data) {
        goto('/estimer');
      } else {
        goto('/login');
      }
    } else {
      goto('/login');
    }
  });
</script>

<div class="flex items-center justify-center min-h-[50vh]">
  <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
</div>