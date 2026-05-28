<script lang="ts">
  let email = $state("");
  let password = $state("");
  let passwordConfirm = $state("");
  let isRegistering = $state(false);
  let feedbackMessage = $state({ text: "", type: "" });

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();

    if (isRegistering && password !== passwordConfirm) {
      feedbackMessage = { text: "Les mots de passe ne correspondent pas", type: "error" };
      return;
    }

    feedbackMessage = { text: "Traitement...", type: "info" };
    
    const endpoint = isRegistering ? 'http://localhost:8000/api/auth/register' : 'http://localhost:8000/api/auth/login';
    const payload = isRegistering ? { email, password } : { email, password };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        if (isRegistering) {
          feedbackMessage = { text: "Compte créé ! Vous pouvez vous connecter.", type: "success" };
          isRegistering = false;
        } else {
          const userData = await res.json();
          window.location.href = (userData.pole === "Direction" || userData.pole === "IT et Support") ? '/admin' : '/estimer';
        }
      } else {
        const error = await res.json();
        let errorMessage = "Erreur lors de l'opération";

        if (typeof error.detail === 'string') {
          errorMessage = error.detail;
        }
        else if (Array.isArray(error.detail)) {
          errorMessage = error.detail[0].msg.includes('8 characters') 
            ? "Le mot de passe doit contenir au moins 8 caractères." 
            : "Veuillez vérifier les champs saisis.";
        }

        feedbackMessage = { text: errorMessage, type: "error" };
      }
    } catch (err) {
      feedbackMessage = { text: "Serveur indisponible", type: "error" };
    }
  }
</script>

<div class="max-w-md mx-auto bg-white p-10 rounded-3xl shadow-xl border border-gray-100 mt-20 animate-pop">
  <h2 class="text-2xl font-black mb-2 text-center">{isRegistering ? "Créer un compte" : "Accès Agence"}</h2>
  
  {#if feedbackMessage.text}
    <div class="mb-4 p-3 text-sm font-bold rounded-xl text-center {feedbackMessage.type === 'error' ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}">
      {feedbackMessage.text}
    </div>
  {/if}

  <form onsubmit={handleSubmit} class="space-y-4">
    <input type="email" bind:value={email} placeholder="Email professionnel" class="w-full bg-gray-50 border-none rounded-xl py-4 px-4" required />
    <input type="password" bind:value={password} placeholder="Mot de passe" class="w-full bg-gray-50 border-none rounded-xl py-4 px-4" required />
    {#if isRegistering}
      <input type="password" bind:value={passwordConfirm} placeholder="Confirmer mot de passe" class="w-full bg-gray-50 p-4 rounded-xl" required />
    {/if}
    <button type="submit" class="w-full bg-blue-600 text-white py-4 rounded-2xl font-black">{isRegistering ? "S'inscrire" : "S'authentifier"}</button>
  </form>

  <button onclick={() => isRegistering = !isRegistering} class="w-full mt-4 text-xs font-bold text-gray-400 underline">{isRegistering ? "Déjà un compte ? Connexion" : "Pas de compte ? S'inscrire"}</button>
</div>