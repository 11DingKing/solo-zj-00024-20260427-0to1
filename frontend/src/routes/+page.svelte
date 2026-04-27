<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';

  let albums = [];
  let loading = true;
  let error = '';
  let searchQuery = '';
  let sortBy = '-created_at';
  let page = 1;
  let totalPages = 1;
  let hasNext = false;
  let hasPrev = false;

  async function loadAlbums() {
    try {
      loading = true;
      let url = `/albums/public/?page=${page}&ordering=${sortBy}`;
      if (searchQuery) {
        url += `&search=${encodeURIComponent(searchQuery)}`;
      }
      const response = await api.get(url);
      albums = response.results || [];
      totalPages = Math.ceil(response.count / 20);
      hasNext = !!response.next;
      hasPrev = !!response.previous;
    } catch (err) {
      error = err.message || 'Failed to load albums';
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadAlbums();
  });

  function handleSearch() {
    page = 1;
    loadAlbums();
  }

  function handleSortChange() {
    page = 1;
    loadAlbums();
  }

  function goToPage(newPage) {
    page = newPage;
    loadAlbums();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  $: if (searchQuery === '') {
    // 搜索为空时也触发加载
  }
</script>

<div class="home-page">
  <div class="hero-section">
    <div class="container">
      <h1>Photo Gallery</h1>
      <p class="hero-subtitle">Share and organize your memories</p>
    </div>
  </div>

  <div class="container">
    <div class="filter-bar">
      <div class="search-box">
        <input
          type="text"
          class="form-input"
          placeholder="Search public albums..."
          bind:value={searchQuery}
          on:keyup={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button class="btn btn-primary" on:click={handleSearch}>Search</button>
      </div>
      <div class="sort-box">
        <label class="form-label">Sort by:</label>
        <select class="form-input" bind:value={sortBy} on:change={handleSortChange}>
          <option value="-created_at">Newest First</option>
          <option value="created_at">Oldest First</option>
          <option value="title">Title (A-Z)</option>
          <option value="-title">Title (Z-A)</option>
        </select>
      </div>
    </div>

    {#if loading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading albums...</p>
      </div>
    {:else if error}
      <div class="error-state">
        <p class="error">{error}</p>
        <button class="btn btn-primary" on:click={loadAlbums}>Try Again</button>
      </div>
    {:else if albums.length === 0}
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
        <h3>No public albums yet</h3>
        <p>Be the first to share your photo collection!</p>
      </div>
    {:else}
      <div class="albums-grid">
        {#each albums as album}
          <a href="/albums/{album.id}" class="album-card card">
            <div class="album-cover">
              {#if album.cover_image}
                <img src="http://localhost:8000{album.cover_image}" alt={album.title} />
              {:else}
                <div class="placeholder-cover">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                </div>
              {/if}
              <div class="album-badge">Public</div>
            </div>
            <div class="album-info">
              <h3 class="album-title">{album.title}</h3>
              {#if album.description}
                <p class="album-desc">{album.description.slice(0, 100)}{album.description.length > 100 ? '...' : ''}</p>
              {/if}
              <div class="album-meta">
                <span class="photo-count">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                  {album.photo_count || 0} photos
                </span>
                {#if album.owner}
                  <span class="owner">by {album.owner.username}</span>
                {/if}
              </div>
            </div>
          </a>
        {/each}
      </div>

      {#if totalPages > 1}
        <div class="pagination">
          <button
            class="btn btn-outline"
            disabled={!hasPrev}
            on:click={() => goToPage(page - 1)}
          >
            Previous
          </button>
          <span class="page-info">Page {page} of {totalPages}</span>
          <button
            class="btn btn-outline"
            disabled={!hasNext}
            on:click={() => goToPage(page + 1)}
          >
            Next
          </button>
        </div>
      {/if}
    {/if}
  </div>
</div>

<style>
  .hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 48px 0;
    margin: -24px -24px 32px;
    text-align: center;
  }

  .hero-section h1 {
    font-size: 36px;
    font-weight: 700;
    color: white;
    margin-bottom: 8px;
  }

  .hero-subtitle {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.9);
  }

  .filter-bar {
    display: flex;
    gap: 24px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }

  .search-box {
    display: flex;
    gap: 12px;
    flex: 1;
    min-width: 300px;
  }

  .search-box input {
    flex: 1;
  }

  .sort-box {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .sort-box label {
    margin-bottom: 0;
    white-space: nowrap;
  }

  .sort-box select {
    width: 180px;
  }

  .loading-state,
  .error-state,
  .empty-state {
    text-align: center;
    padding: 64px 20px;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e5e7eb;
    border-top-color: #2563eb;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .empty-state svg {
    width: 64px;
    height: 64px;
    color: #d1d5db;
    margin-bottom: 16px;
  }

  .empty-state h3 {
    font-size: 18px;
    color: #374151;
    margin-bottom: 8px;
  }

  .empty-state p {
    color: #6b7280;
  }

  .albums-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 24px;
  }

  .album-card {
    display: block;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .album-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
  }

  .album-cover {
    position: relative;
    height: 200px;
    background: #f3f4f6;
    overflow: hidden;
  }

  .album-cover img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .placeholder-cover {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #e5e7eb 0%, #f3f4f6 100%);
  }

  .placeholder-cover svg {
    width: 64px;
    height: 64px;
    color: #9ca3af;
  }

  .album-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    background: rgba(37, 99, 235, 0.9);
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
  }

  .album-info {
    padding: 16px;
  }

  .album-title {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
  }

  .album-desc {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 12px;
    line-height: 1.4;
  }

  .album-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    color: #9ca3af;
  }

  .photo-count {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .photo-count svg {
    width: 16px;
    height: 16px;
  }

  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
    margin-top: 32px;
  }

  .page-info {
    font-size: 14px;
    color: #6b7280;
  }
</style>
