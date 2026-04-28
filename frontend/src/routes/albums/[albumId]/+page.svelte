<script>
  import { onMount, afterUpdate } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api/client';
  import BatchActionModal from '$lib/components/BatchActionModal.svelte';

  let album = null;
  let photos = [];
  let allTags = [];
  let loading = true;
  let error = '';
  
  let selectedPhotos = new Set();
  let showUploadModal = false;
  let showBatchModal = false;
  let batchAction = null;
  
  let uploadFiles = [];
  let uploading = false;
  let uploadProgress = {};
  
  let currentTag = null;
  let pageNum = 1;
  let hasMore = true;
  let loadingMore = false;

  $: albumId = $page.params.albumId;

  async function loadAlbum() {
    try {
      album = await api.get(`/albums/${albumId}/`);
    } catch (err) {
      error = err.message || 'Failed to load album';
    }
  }

  async function loadPhotos(append = false) {
    try {
      if (append) {
        loadingMore = true;
      } else {
        loading = true;
        pageNum = 1;
        hasMore = true;
      }

      let url = `/photos/?album_id=${albumId}&page=${pageNum}`;
      if (currentTag) {
        url += `&tag=${encodeURIComponent(currentTag)}`;
      }

      const response = await api.get(url);
      
      if (append) {
        photos = [...photos, ...(response.results || [])];
      } else {
        photos = response.results || [];
      }
      
      hasMore = !!response.next;
      pageNum++;
    } catch (err) {
      error = err.message || 'Failed to load photos';
    } finally {
      loading = false;
      loadingMore = false;
    }
  }

  async function loadTags() {
    try {
      const tags = await api.get('/photos/tags/');
      allTags = tags || [];
    } catch (err) {
      console.error('Failed to load tags:', err);
    }
  }

  onMount(() => {
    loadAlbum();
    loadPhotos();
    loadTags();
  });

  function togglePhotoSelection(photoId) {
    if (selectedPhotos.has(photoId)) {
      selectedPhotos.delete(photoId);
    } else {
      selectedPhotos.add(photoId);
    }
    selectedPhotos = new Set(selectedPhotos);
  }

  function toggleSelectAll() {
    if (selectedPhotos.size === photos.length) {
      selectedPhotos.clear();
    } else {
      selectedPhotos = new Set(photos.map(p => p.id));
    }
    selectedPhotos = new Set(selectedPhotos);
  }

  function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    uploadFiles = files.map(file => ({
      file,
      name: file.name,
      size: file.size,
      progress: 0,
      status: 'pending'
    }));
  }

  async function uploadPhotos() {
    if (uploadFiles.length === 0) return;
    
    uploading = true;
    
    for (let i = 0; i < uploadFiles.length; i++) {
      const uploadItem = uploadFiles[i];
      const formData = new FormData();
      formData.append('album', albumId);
      formData.append('original_image', uploadItem.file);
      
      try {
        uploadItem.status = 'uploading';
        uploadFiles = [...uploadFiles];
        
        const result = await api.upload('/photos/', formData, (percent) => {
          uploadItem.progress = percent;
          uploadFiles = [...uploadFiles];
        });
        
        uploadItem.status = 'success';
        photos = [result, ...photos];
      } catch (err) {
        uploadItem.status = 'error';
        uploadItem.error = err.message;
      }
      
      uploadFiles = [...uploadFiles];
    }
    
    uploading = false;
  }

  function clearUploadQueue() {
    uploadFiles = [];
    showUploadModal = false;
  }

  async function batchMove(targetAlbumId) {
    try {
      await api.post('/photos/batch/move/', {
        photo_ids: Array.from(selectedPhotos),
        target_album_id: targetAlbumId
      });
      
      photos = photos.filter(p => !selectedPhotos.has(p.id));
      selectedPhotos.clear();
      selectedPhotos = new Set(selectedPhotos);
      showBatchModal = false;
      batchAction = null;
    } catch (err) {
      error = err.message || 'Failed to move photos';
    }
  }

  async function batchDelete() {
    if (!confirm(`Are you sure you want to delete ${selectedPhotos.size} photos?`)) {
      return;
    }
    
    try {
      await api.post('/photos/batch/delete/', {
        photo_ids: Array.from(selectedPhotos)
      });
      
      photos = photos.filter(p => !selectedPhotos.has(p.id));
      selectedPhotos.clear();
      selectedPhotos = new Set(selectedPhotos);
      showBatchModal = false;
      batchAction = null;
    } catch (err) {
      error = err.message || 'Failed to delete photos';
    }
  }

  async function batchTag(tagNames) {
    try {
      await api.post('/photos/batch/tag/', {
        photo_ids: Array.from(selectedPhotos),
        tags: tagNames
      });
      
      loadTags();
      loadPhotos();
      selectedPhotos.clear();
      selectedPhotos = new Set(selectedPhotos);
      showBatchModal = false;
      batchAction = null;
    } catch (err) {
      error = err.message || 'Failed to tag photos';
    }
  }

  function filterByTag(tag) {
    currentTag = tag === currentTag ? null : tag;
    loadPhotos();
  }

  function loadMore() {
    if (hasMore && !loadingMore) {
      loadPhotos(true);
    }
  }

  function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }
</script>

<div class="album-detail-page">
  <div class="container">
    {#if album}
      <div class="album-header">
        <div class="album-info">
          <a href="/albums" class="back-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Back to Albums
          </a>
          <h1>{album.title}</h1>
          {#if album.description}
            <p class="album-description">{album.description}</p>
          {/if}
          <div class="album-meta">
            <span class="badge" class:public={album.is_public}>
              {album.is_public ? 'Public' : 'Private'}
            </span>
            <span class="photo-count">{photos.length} photos</span>
          </div>
        </div>
        <div class="album-actions">
          <button class="btn btn-primary" on:click={() => showUploadModal = true}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            Upload Photos
          </button>
          {#if selectedPhotos.size > 0}
            <div class="batch-actions">
              <span class="selected-count">{selectedPhotos.size} selected</span>
              <button class="btn btn-outline" on:click={() => { batchAction = 'move'; showBatchModal = true; }}>
                Move
              </button>
              <button class="btn btn-outline" on:click={() => { batchAction = 'tag'; showBatchModal = true; }}>
                Tag
              </button>
              <button class="btn btn-danger" on:click={() => { batchAction = 'delete'; showBatchModal = true; }}>
                Delete
              </button>
              <button class="btn btn-secondary" on:click={() => { selectedPhotos.clear(); selectedPhotos = new Set(selectedPhotos); }}>
                Clear
              </button>
            </div>
          {/if}
        </div>
      </div>

      {#if allTags.length > 0}
        <div class="tag-filter">
          <span class="filter-label">Filter by tag:</span>
          <button
            class="tag-btn"
            class:active={!currentTag}
            on:click={() => filterByTag(null)}
          >
            All
          </button>
          {#each allTags as tag}
            <button
              class="tag-btn"
              class:active={currentTag === tag.name}
              on:click={() => filterByTag(tag.name)}
            >
              {tag.name}
            </button>
          {/each}
        </div>
      {/if}

      {#if selectedPhotos.size > 0}
        <button class="btn btn-outline select-all-btn" on:click={toggleSelectAll}>
          {selectedPhotos.size === photos.length ? 'Deselect All' : 'Select All'}
        </button>
      {/if}

      {#if loading && photos.length === 0}
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Loading photos...</p>
        </div>
      {:else if photos.length === 0}
        <div class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
          <h3>No photos yet</h3>
          <p>Upload your first photo to this album</p>
          <button class="btn btn-primary" on:click={() => showUploadModal = true}>
            Upload Photos
          </button>
        </div>
      {:else}
        <div class="photos-grid">
          {#each photos as photo}
            <div class="photo-item" class:selected={selectedPhotos.has(photo.id)}>
              <input
                type="checkbox"
                class="photo-checkbox"
                checked={selectedPhotos.has(photo.id)}
                on:change={() => togglePhotoSelection(photo.id)}
              />
              <a href="/photos/{photo.id}" class="photo-link">
                <img
                  src="http://localhost:8000{photo.thumbnail_medium}"
                  alt={photo.title || 'Photo'}
                  loading="lazy"
                />
              </a>
              {#if photo.tags && photo.tags.length > 0}
                <div class="photo-tags">
                  {#each photo.tags.slice(0, 3) as tag}
                    <span class="mini-tag">{tag.name}</span>
                  {/each}
                  {#if photo.tags.length > 3}
                    <span class="mini-tag">+{photo.tags.length - 3}</span>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>

        {#if hasMore}
          <div class="load-more">
            <button
              class="btn btn-outline"
              disabled={loadingMore}
              on:click={loadMore}
            >
              {loadingMore ? 'Loading...' : 'Load More'}
            </button>
          </div>
        {/if}
      {/if}
    {/if}

    {#if error}
      <p class="error">{error}</p>
    {/if}
  </div>

  {#if showUploadModal}
    <div class="modal-overlay" on:click={clearUploadQueue}>
      <div class="modal card" on:click|stopPropagation>
        <div class="modal-header">
          <h2>Upload Photos</h2>
          <button class="close-btn" on:click={clearUploadQueue}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="upload-area">
            <input
              type="file"
              id="photo-upload"
              multiple
              accept="image/*"
              on:change={handleFileSelect}
              class="file-input"
            />
            <label for="photo-upload" class="upload-label">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              <p>Click or drag photos here to upload</p>
              <p class="upload-hint">Maximum 10MB per file</p>
            </label>
          </div>

          {#if uploadFiles.length > 0}
            <div class="upload-queue">
              <h4>Queue ({uploadFiles.length} files)</h4>
              {#each uploadFiles as item}
                <div class="queue-item" class:success={item.status === 'success'} class:error={item.status === 'error'}>
                  <span class="file-name">{item.name}</span>
                  <span class="file-size">{formatFileSize(item.size)}</span>
                  {#if item.status === 'uploading'}
                    <div class="progress-bar">
                      <div class="progress-fill" style="width: {item.progress}%"></div>
                    </div>
                  {:else if item.status === 'success'}
                    <span class="status-success">✓ Done</span>
                  {:else if item.status === 'error'}
                    <span class="status-error">✗ {item.error}</span>
                  {/if}
                </div>
              {/each}
            </div>
          {/if}
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={clearUploadQueue}>Cancel</button>
          <button
            class="btn btn-primary"
            disabled={uploading || uploadFiles.length === 0}
            on:click={uploadPhotos}
          >
            {uploading ? 'Uploading...' : `Upload ${uploadFiles.length} Photos`}
          </button>
        </div>
      </div>
    </div>
  {/if}

  {#if showBatchModal}
    <BatchActionModal
      {batchAction}
      {selectedPhotos}
      currentAlbumId={albumId}
      on:close={() => { showBatchModal = false; batchAction = null; }}
      on:move={batchMove}
      on:delete={batchDelete}
      on:tag={batchTag}
    />
  {/if}
</div>

<style>
  .album-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    gap: 24px;
  }

  .back-link {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 12px;
  }

  .back-link:hover {
    color: #2563eb;
  }

  .back-link svg {
    width: 16px;
    height: 16px;
  }

  .album-info h1 {
    font-size: 28px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
  }

  .album-description {
    font-size: 16px;
    color: #6b7280;
    margin-bottom: 12px;
  }

  .album-meta {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .badge {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    background: #e5e7eb;
    color: #6b7280;
  }

  .badge.public {
    background: #dbeafe;
    color: #1d4ed8;
  }

  .photo-count {
    font-size: 14px;
    color: #6b7280;
  }

  .album-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: flex-end;
  }

  .album-actions button {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .album-actions button svg {
    width: 20px;
    height: 20px;
  }

  .batch-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .selected-count {
    font-size: 14px;
    font-weight: 500;
    color: #2563eb;
  }

  .tag-filter {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }

  .filter-label {
    font-size: 14px;
    font-weight: 500;
    color: #374151;
  }

  .tag-btn {
    padding: 6px 14px;
    border: 1px solid #d1d5db;
    border-radius: 16px;
    background: white;
    font-size: 14px;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s;
  }

  .tag-btn:hover {
    border-color: #2563eb;
    color: #2563eb;
  }

  .tag-btn.active {
    background: #2563eb;
    border-color: #2563eb;
    color: white;
  }

  .select-all-btn {
    margin-bottom: 16px;
  }

  .loading-state,
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

  .photos-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }

  @media (max-width: 1024px) {
    .photos-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  @media (max-width: 768px) {
    .photos-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 480px) {
    .photos-grid {
      grid-template-columns: 1fr;
    }
  }

  .photo-item {
    break-inside: avoid;
    margin-bottom: 16px;
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    background: #f3f4f6;
    transition: transform 0.2s;
  }

  .photo-item:hover {
    transform: scale(1.02);
  }

  .photo-item.selected {
    outline: 3px solid #2563eb;
  }

  .photo-checkbox {
    position: absolute;
    top: 12px;
    left: 12px;
    z-index: 10;
    width: 20px;
    height: 20px;
    cursor: pointer;
  }

  .photo-link {
    display: block;
  }

  .photo-link img {
    width: 100%;
    display: block;
    background: #e5e7eb;
  }

  .photo-tags {
    position: absolute;
    bottom: 8px;
    left: 8px;
    right: 8px;
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }

  .mini-tag {
    padding: 2px 8px;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    border-radius: 10px;
    font-size: 11px;
  }

  .load-more {
    text-align: center;
    margin-top: 32px;
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
    max-width: 640px;
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

  .upload-area {
    position: relative;
  }

  .file-input {
    position: absolute;
    opacity: 0;
    width: 100%;
    height: 100%;
    cursor: pointer;
  }

  .upload-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    border: 2px dashed #d1d5db;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .upload-label:hover {
    border-color: #2563eb;
    background: #eff6ff;
  }

  .upload-label svg {
    width: 48px;
    height: 48px;
    color: #9ca3af;
    margin-bottom: 12px;
  }

  .upload-label p {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 4px;
  }

  .upload-hint {
    font-size: 12px;
    color: #9ca3af;
  }

  .upload-queue {
    margin-top: 20px;
  }

  .upload-queue h4 {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 12px;
  }

  .queue-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #f9fafb;
    border-radius: 6px;
    margin-bottom: 8px;
  }

  .queue-item.success {
    background: #f0fdf4;
  }

  .queue-item.error {
    background: #fef2f2;
  }

  .file-name {
    flex: 1;
    font-size: 14px;
    color: #374151;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .file-size {
    font-size: 12px;
    color: #9ca3af;
  }

  .progress-bar {
    width: 80px;
    height: 6px;
    background: #e5e7eb;
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: #2563eb;
    transition: width 0.2s;
  }

  .status-success {
    font-size: 12px;
    color: #16a34a;
  }

  .status-error {
    font-size: 12px;
    color: #dc2626;
  }

  .error {
    color: #dc2626;
    font-size: 14px;
    margin-top: 16px;
  }
</style>
