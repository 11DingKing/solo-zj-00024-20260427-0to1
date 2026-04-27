<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api/client';
  import { auth } from '$lib/stores/auth';

  let albums = [];
  let loading = true;
  let error = '';
  let showCreateModal = false;
  let newAlbum = {
    title: '',
    description: '',
    is_public: false
  };
  let creating = false;

  async function loadAlbums() {
    try {
      loading = true;
      const response = await api.get('/albums/');
      albums = response.results || [];
    } catch (err) {
      error = err.message || 'Failed to load albums';
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadAlbums();
  });

  async function createAlbum() {
    if (!newAlbum.title.trim()) {
      return;
    }

    try {
      creating = true;
      const album = await api.post('/albums/', newAlbum);
      albums = [album, ...albums];
      showCreateModal = false;
      newAlbum = { title: '', description: '', is_public: false };
    } catch (err) {
      error = err.message || 'Failed to create album';
    } finally {
      creating = false;
    }
  }

  async function deleteAlbum(id) {
    if (!confirm('Are you sure you want to delete this album?')) {
      return;
    }

    try {
      await api.delete(`/albums/${id}/`);
      albums = albums.filter(a => a.id !== id);
    } catch (err) {
      error = err.message || 'Failed to delete album';
    }
  }

  function openCreateModal() {
    showCreateModal = true;
  }

  function closeCreateModal() {
    showCreateModal = false;
    newAlbum = { title: '', description: '', is_public: false };
  }
</script>

<div class="albums-page">
  <div class="container">
    <div class="page-header">
      <h1>My Albums</h1>
      <button class="btn btn-primary" on:click={openCreateModal}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        New Album
      </button>
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
        <h3>No albums yet</h3>
        <p>Create your first album to start organizing your photos</p>
        <button class="btn btn-primary" on:click={openCreateModal}>Create Album</button>
      </div>
    {:else}
      <div class="albums-grid">
        {#each albums as album}
          <div class="album-card card">
            <a href="/albums/{album.id}" class="album-link">
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
                <div class="album-badge" class:public={album.is_public}>
                  {album.is_public ? 'Public' : 'Private'}
                </div>
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
                </div>
              </div>
            </a>
            <div class="album-actions">
              <button class="btn btn-outline btn-sm" on:click={() => goto(`/albums/${album.id}`)}>
                View
              </button>
              <button class="btn btn-danger btn-sm" on:click={() => deleteAlbum(album.id)}>
                Delete
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  {#if showCreateModal}
    <div class="modal-overlay" on:click={closeCreateModal}>
      <div class="modal card" on:click|stopPropagation>
        <div class="modal-header">
          <h2>Create New Album</h2>
          <button class="close-btn" on:click={closeCreateModal}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        <form on:submit|preventDefault={createAlbum} class="modal-body">
          <div class="form-group">
            <label class="form-label">Album Name *</label>
            <input
              type="text"
              class="form-input"
              bind:value={newAlbum.title}
              placeholder="Enter album name"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">Description</label>
            <textarea
              class="form-textarea"
              bind:value={newAlbum.description}
              placeholder="Describe your album"
            />
          </div>
          <div class="form-group">
            <label class="checkbox">
              <input type="checkbox" bind:checked={newAlbum.is_public} />
              <span>Make this album public</span>
            </label>
          </div>
          {#if error}
            <p class="error">{error}</p>
          {/if}
        </form>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={closeCreateModal}>Cancel</button>
          <button class="btn btn-primary" on:click={createAlbum} disabled={creating || !newAlbum.title.trim()}>
            {creating ? 'Creating...' : 'Create Album'}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .page-header h1 {
    font-size: 24px;
    font-weight: 600;
    color: #1f2937;
  }

  .page-header button {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .page-header button svg {
    width: 20px;
    height: 20px;
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
    margin-bottom: 16px;
  }

  .albums-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 24px;
  }

  .album-card {
    display: flex;
    flex-direction: column;
  }

  .album-link {
    display: block;
    text-decoration: none;
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
    background: rgba(107, 114, 128, 0.9);
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
  }

  .album-badge.public {
    background: rgba(37, 99, 235, 0.9);
  }

  .album-info {
    padding: 16px;
    flex: 1;
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

  .album-actions {
    display: flex;
    gap: 8px;
    padding: 0 16px 16px;
  }

  .btn-sm {
    padding: 6px 12px;
    font-size: 13px;
    flex: 1;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
  }

  .modal {
    width: 100%;
    max-width: 480px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #e5e7eb;
  }

  .modal-header h2 {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
  }

  .close-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px;
    color: #6b7280;
  }

  .close-btn:hover {
    color: #1f2937;
  }

  .close-btn svg {
    width: 24px;
    height: 24px;
  }

  .modal-body {
    padding: 20px;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 20px;
    border-top: 1px solid #e5e7eb;
  }
</style>
