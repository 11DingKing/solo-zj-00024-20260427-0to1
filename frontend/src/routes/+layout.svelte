<script>
  import { page } from '$app/stores';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let user = null;
  let isAuthenticated = false;

  $: {
    const unsub = auth.subscribe((state) => {
      user = state.user;
      isAuthenticated = state.isAuthenticated;
    });
  }

  function handleLogout() {
    auth.logout();
    goto('/');
  }
</script>

<nav class="navbar">
  <div class="container nav-container">
    <a href="/" class="logo">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
      </svg>
      Photo Gallery
    </a>

    <div class="nav-links">
      <a href="/" class:active={$page.url.pathname === '/'}>Home</a>
      {#if isAuthenticated}
        <a href="/albums" class:active={$page.url.pathname.startsWith('/albums')}>Albums</a>
        <a href="/timeline" class:active={$page.url.pathname === '/timeline'}>Timeline</a>
        <div class="user-menu">
          <span class="username">{user?.username}</span>
          <button class="btn btn-outline" on:click={handleLogout}>Logout</button>
        </div>
      {:else}
        <a href="/login" class:active={$page.url.pathname === '/login'}>Login</a>
        <a href="/register" class="btn btn-primary" class:active={$page.url.pathname === '/register'}>Register</a>
      {/if}
    </div>
  </div>
</nav>

<main class="main-content">
  <slot />
</main>

<style>
  .navbar {
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 64px;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 20px;
    font-weight: 600;
    color: #1f2937;
  }

  .logo svg {
    width: 28px;
    height: 28px;
    color: #2563eb;
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 24px;
  }

  .nav-links a {
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    transition: color 0.2s;
  }

  .nav-links a:hover,
  .nav-links a.active {
    color: #2563eb;
  }

  .user-menu {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .username {
    font-size: 14px;
    font-weight: 500;
    color: #374151;
  }

  .main-content {
    min-height: calc(100vh - 64px);
    padding: 24px 0;
  }
</style>
