<script>
  import { createEventDispatcher } from 'svelte';
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';

  const dispatch = createEventDispatcher();

  export let batchAction;
  export let selectedPhotos;
  export let currentAlbumId;

  let userAlbums = [];
  let targetAlbumId = null;
  let newTagNames = [];
  let newTagInput = '';
  let loading = false;
  let error = '';

  async function loadUserAlbums() {
    try {
      const response = await api.get('/albums/');
      userAlbums = (response.results || []).filter(a => a.id !== parseInt(currentAlbumId));
    } catch (err) {
      error = err.message || 'Failed to load albums';
    }
  }

  onMount(() => {
    if (batchAction === 'move') {
      loadUserAlbums();
    }
  });

  function addTag() {
    const tag = newTagInput.trim().toLowerCase();
    if (tag && !newTagNames.includes(tag)) {
      newTagNames = [...newTagNames, tag];
      newTagInput = '';
    }
  }

  function removeTag(tag) {
    newTagNames = newTagNames.filter(t => t !== tag);
  }

  function handleClose() {
    dispatch('close');
  }

  async function handleMove() {
    if (!targetAlbumId) return;
    loading = true;
    try {
      dispatch('move', targetAlbumId);
    } finally {
      loading = false;
    }
  }

  async function handleDelete() {
    loading = true;
    try {
      dispatch('delete');
    } finally {
      loading = false;
    }
  }

  async function handleTag() {
    if (newTagNames.length === 0) return;
    loading = true;
    try {
      dispatch('tag', newTagNames);
    } finally {
      loading = false;
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && batchAction === 'tag') {
      addTag();
    }
  }
</script>

<div class="modal-overlay" on:click={handleClose}>
  <div class="modal card" on:click|stopPropagation>
    <div class="modal-header">
      {#if batchAction === 'move'}
        <h2>Move {selectedPhotos.size} Photos</h2>
      {:else if batchAction === 'delete'}
        <h2>Delete {selectedPhotos.size} Photos</h2>
      {:else if batchAction === 'tag'}
        <h2>Tag {selectedPhotos.size} Photos</h2>
      {/if}
      <button class="close-btn" on:click={handleClose}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>

    <div class="modal-body">
      {#if batchAction === 'move'}
        <div class="form-group">
          <label class="form-label">Select Target Album</label>
          {#if userAlbums.length === 0}
            <p class="empty-albums">No other albums available. Create a new album first.</p>
          {:else}
            <select class="form-input" bind:value={targetAlbumId}>
              <option value="">Select an album...</option>
              {#each userAlbums as album}
                <option value={album.id}>{album.title} ({album.photo_count || 0} photos)</option>
              {/each}
            </select>
          {/if}
        </div>
      {:else if batchAction === 'delete'}
        <div class="delete-warning">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            <line x1="10" y1="11" x2="10" y2="17" />
            <line x1="14" y1="11" x2="14" y2="17" />
          </svg>
          <h3>Are you sure?</h3>
          <p>This action cannot be undone. {selectedPhotos.size} photo(s) will be permanently deleted.</p>
        </div>
      {:else if batchAction === 'tag'}
        <div class="form-group">
          <label class="form-label">Add Tags</label>
          <div class="tag-input-container">
            <input
              type="text"
              class="form-input"
              bind:value={newTagInput}
              placeholder="Type a tag and press Enter"
              on:keydown={handleKeyDown}
            />
            <button class="btn btn-primary" type="button" on:click={addTag}>Add</button>
          </div>
          {#if newTagNames.length > 0}
            <div class="selected-tags">
              {#each newTagNames as tag}
                <span class="tag-item">
                  {tag}
                  <button type="button" class="remove-tag" on:click={() => removeTag(tag)}>×</button>
                </span>
              {/each}
            </div>
          {/if}
        </div>
      {/if}

      {#if error}
        <p class="error">{error}</p>
      {/if}
    </div>

    <div class="modal-footer">
      <button class="btn btn-secondary" on:click={handleClose} disabled={loading}>Cancel</button>
      {#if batchAction === 'move'}
        <button
          class="btn btn-primary"
          on:click={handleMove}
          disabled={!targetAlbumId || loading}
        >
          {loading ? 'Moving...' : 'Move Photos'}
        </button>
      {:else if batchAction === 'delete'}
        <button
          class="btn btn-danger"
          on:click={handleDelete}
          disabled={loading}
        >
          {loading ? 'Deleting...' : 'Delete Photos'}
        </button>
      {:else if batchAction === 'tag'}
        <button
          class="btn btn-primary"
          on:click={handleTag}
          disabled={newTagNames.length === 0 || loading}
        >
          {loading ? 'Tagging...' : 'Add Tags'}
        </button>
      {/if}
    </div>
  </div>
</div>

<style>
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

  .empty-albums {
    font-size: 14px;
    color: #9ca3af;
    font-style: italic;
  }

  .delete-warning {
    text-align: center;
    padding: 20px 0;
  }

  .delete-warning svg {
    width: 64px;
    height: 64px;
    color: #dc2626;
    margin-bottom: 16px;
  }

  .delete-warning h3 {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
  }

  .delete-warning p {
    font-size: 14px;
    color: #6b7280;
    line-height: 1.5;
  }

  .tag-input-container {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
  }

  .tag-input-container input {
    flex: 1;
  }

  .selected-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .tag-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: #dbeafe;
    color: #1d4ed8;
    border-radius: 16px;
    font-size: 14px;
  }

  .remove-tag {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 18px;
    color: #1d4ed8;
    padding: 0;
    line-height: 1;
  }

  .remove-tag:hover {
    color: #1e40af;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 20px;
    border-top: 1px solid #e5e7eb;
  }

  .error {
    color: #dc2626;
    font-size: 14px;
    margin-top: 16px;
  }
</style>
