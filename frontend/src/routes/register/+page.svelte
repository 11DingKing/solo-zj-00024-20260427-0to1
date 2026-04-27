<script>
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let username = '';
  let email = '';
  let password = '';
  let password2 = '';
  let error = '';
  let loading = false;

  async function handleRegister(e) {
    e.preventDefault();
    error = '';

    if (password !== password2) {
      error = 'Passwords do not match';
      return;
    }

    loading = true;

    try {
      await auth.register({
        username,
        email,
        password,
        password2
      });
      goto('/albums');
    } catch (err) {
      error = err.message || 'Registration failed. Please try again.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="auth-page">
  <div class="auth-card">
    <h1>Create Account</h1>
    <p class="subtitle">Start organizing your photo collection</p>

    <form on:submit={handleRegister} class="auth-form">
      <div class="form-group">
        <label class="form-label" for="username">Username</label>
        <input
          type="text"
          id="username"
          class="form-input"
          bind:value={username}
          required
          placeholder="Choose a username"
        />
      </div>

      <div class="form-group">
        <label class="form-label" for="email">Email</label>
        <input
          type="email"
          id="email"
          class="form-input"
          bind:value={email}
          required
          placeholder="Enter your email"
        />
      </div>

      <div class="form-group">
        <label class="form-label" for="password">Password</label>
        <input
          type="password"
          id="password"
          class="form-input"
          bind:value={password}
          required
          placeholder="Create a password"
        />
      </div>

      <div class="form-group">
        <label class="form-label" for="password2">Confirm Password</label>
        <input
          type="password"
          id="password2"
          class="form-input"
          bind:value={password2}
          required
          placeholder="Confirm your password"
        />
      </div>

      {#if error}
        <p class="error">{error}</p>
      {/if}

      <button type="submit" class="btn btn-primary btn-full" disabled={loading}>
        {loading ? 'Creating account...' : 'Create Account'}
      </button>
    </form>

    <div class="auth-footer">
      Already have an account? <a href="/login">Sign in</a>
    </div>
  </div>
</div>

<style>
  .auth-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
  }

  .auth-card {
    width: 100%;
    max-width: 420px;
    padding: 32px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .auth-card h1 {
    font-size: 24px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
  }

  .subtitle {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 24px;
  }

  .auth-form {
    margin-bottom: 24px;
  }

  .btn-full {
    width: 100%;
    padding: 12px;
    font-size: 16px;
  }

  .auth-footer {
    text-align: center;
    font-size: 14px;
    color: #6b7280;
  }

  .auth-footer a {
    color: #2563eb;
    font-weight: 500;
  }

  .auth-footer a:hover {
    text-decoration: underline;
  }
</style>
