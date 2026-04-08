<script lang="ts">
  let loginEmail = $state("");
  let loginPassword = $state("");
  let errorMessage = $state("");

  async function handleLogin(e: SubmitEvent) {
    e.preventDefault();
    errorMessage = "";
    
    try {
      const res = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email: loginEmail, password: loginPassword })
      });

      if (res.ok) {
        window.location.href = '/estimer';
      } else {
        errorMessage = "Identifiants incorrects";
      }
    } catch (err) {
      errorMessage = "Erreur de connexion au serveur";
    }
  }
</script>

<div class="max-w-md mx-auto bg-white p-10 rounded-3xl shadow-xl border border-gray-100 mt-20">
  <h2 class="text-2xl font-bold mb-2 text-center">Acces Agence</h2>
  <p class="text-gray-400 text-center text-sm mb-8">Veuillez vous identifier pour acceder aux outils</p>
  
  {#if errorMessage}
    <div class="mb-4 p-3 bg-red-50 text-red-600 text-sm font-bold rounded-xl text-center">
      {errorMessage}
    </div>
  {/if}

  <form onsubmit={handleLogin} class="space-y-4">
    <input type="email" name="email" bind:value={loginEmail} placeholder="Email professionnel" autocomplete="username" class="w-full bg-gray-50 border-none rounded-xl py-4 px-4 focus:ring-2 focus:ring-blue-500 transition" required />
    <input type="password" name="password" bind:value={loginPassword} placeholder="Mot de passe" autocomplete="current-password" class="w-full bg-gray-50 border-none rounded-xl py-4 px-4 focus:ring-2 focus:ring-blue-500 transition" required />
    <button type="submit" class="w-full bg-blue-600 text-white py-4 rounded-2xl hover:bg-blue-700 transition-all font-bold shadow-lg shadow-blue-100">S'authentifier</button>
  </form>
</div>