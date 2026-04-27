<script>
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';

  let username = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin(e) {
    e.preventDefault();
    error = '';
    loading = true;

    try {
      await auth.login(username, password);
      const redirect = $page.url.searchParams.get('redirect') || '/';
      goto(redirect);
    } catch (err) {
      error = err.message || 'Login failed. Please check your credentials.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="auth-page">
  <div class="auth-card">
    <h1>Welcome Back</h1>
    <p class="subtitle">Sign in to your account</p>

    <form on:submit={handleLogin} class="auth-form">
      <div class="form-group">
        <label class="form-label" for="username">Username</label>
        <input
          type="text"
          id="username"
          class="form-input"
          bind:value={username}
          required
          placeholder="Enter your username"
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
          placeholder="Enter your password"
        />
      </div>

      {#if error}
        <p class="error">{error}</p>
      {/if}

      <button type="submit" class="btn btn-primary btn-full" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
    </form>

    <div class="auth-footer">
      Don't have an account? <a href="/register">Register</a>
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
