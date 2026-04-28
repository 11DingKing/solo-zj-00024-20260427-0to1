<script>
  import { onMount, afterUpdate } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api/client';
  import { browser } from '$app/environment';

  let photo = null;
  let loading = true;
  let error = '';
  let tagsInput = '';
  let editing = false;
  let editTitle = '';
  let editDescription = '';
  let mapContainer = null;
  let map = null;

  $: photoId = $page.params.photoId;

  async function loadPhoto() {
    try {
      loading = true;
      photo = await api.get(`/photos/${photoId}/`);
      if (photo.title) editTitle = photo.title;
      if (photo.description) editDescription = photo.description;
    } catch (err) {
      error = err.message || 'Failed to load photo';
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadPhoto();
  });

  afterUpdate(() => {
    if (photo && photo.has_gps && mapContainer && !map && browser) {
      initMap();
    }
  });

  function initMap() {
    if (typeof window !== 'undefined' && window.L) {
      map = window.L.map('photo-map').setView(
        [photo.exif_gps_latitude, photo.exif_gps_longitude],
        15
      );

      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);

      window.L.marker([photo.exif_gps_latitude, photo.exif_gps_longitude])
        .addTo(map)
        .bindPopup('Photo Location');
    }
  }

  function startEditing() {
    editing = true;
  }

  function cancelEditing() {
    editing = false;
    if (photo) {
      editTitle = photo.title || '';
      editDescription = photo.description || '';
    }
  }

  async function saveChanges() {
    try {
      const updated = await api.patch(`/photos/${photoId}/`, {
        title: editTitle || null,
        description: editDescription || null
      });
      photo = updated;
      editing = false;
    } catch (err) {
      error = err.message || 'Failed to save changes';
    }
  }

  async function deletePhoto() {
    if (!confirm('Are you sure you want to delete this photo?')) {
      return;
    }

    try {
      await api.delete(`/photos/${photoId}/`);
      if (photo.album) {
        goto(`/albums/${photo.album.id}`);
      } else {
        goto('/albums');
      }
    } catch (err) {
      error = err.message || 'Failed to delete photo';
    }
  }

  function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function formatFileSize(bytes) {
    if (!bytes) return 'N/A';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function hasExifData(photo) {
    return photo.exif_camera_make ||
           photo.exif_camera_model ||
           photo.exif_lens_model ||
           photo.exif_focal_length ||
           photo.exif_aperture ||
           photo.exif_shutter_speed ||
           photo.exif_iso ||
           photo.exif_flash !== null ||
           photo.exif_white_balance;
  }
</script>

<svelte:head>
  {#if photo && photo.has_gps}
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  {/if}
</svelte:head>

<div class="photo-detail-page">
  <div class="container">
    {#if loading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading photo...</p>
      </div>
    {:else if error}
      <div class="error-state">
        <p class="error">{error}</p>
        <button class="btn btn-primary" on:click={loadPhoto}>Try Again</button>
      </div>
    {:else if photo}
      <div class="photo-header">
        <a href={photo.album ? `/albums/${photo.album.id}` : '/albums'} class="back-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          {photo.album ? `Back to ${photo.album.title}` : 'Back to Albums'}
        </a>
        <div class="photo-actions">
          {#if !editing}
            <button class="btn btn-outline" on:click={startEditing}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
              Edit
            </button>
          {:else}
            <button class="btn btn-secondary" on:click={cancelEditing}>Cancel</button>
            <button class="btn btn-primary" on:click={saveChanges}>Save</button>
          {/if}
          <button class="btn btn-danger" on:click={deletePhoto}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
            Delete
          </button>
        </div>
      </div>

      <div class="photo-content">
        <div class="photo-display">
          <div class="photo-image">
            <a href="http://localhost:8000{photo.original_image}" target="_blank" title="View original">
              <img src="http://localhost:8000{photo.thumbnail_large || photo.original_image}" alt={photo.title || 'Photo'} />
            </a>
            <div class="photo-overlay">
              <span>Click to view original</span>
            </div>
          </div>

          <div class="photo-info-section">
            {#if editing}
              <div class="form-group">
                <label class="form-label">Title</label>
                <input type="text" class="form-input" bind:value={editTitle} placeholder="Add a title" />
              </div>
              <div class="form-group">
                <label class="form-label">Description</label>
                <textarea class="form-textarea" bind:value={editDescription} placeholder="Add a description" />
              </div>
            {:else}
              {#if photo.title}
                <h1>{photo.title}</h1>
              {/if}
              {#if photo.description}
                <p class="photo-description">{photo.description}</p>
              {/if}
            {/if}

            {#if photo.tags && photo.tags.length > 0}
              <div class="photo-tags-section">
                <h3>Tags</h3>
                <div class="tags-list">
                  {#each photo.tags as tag}
                    <span class="tag">{tag.name}</span>
                  {/each}
                </div>
              </div>
            {/if}

            <div class="photo-meta-section">
              <h3>Information</h3>
              <div class="meta-grid">
                <div class="meta-item">
                  <span class="meta-label">Uploaded</span>
                  <span class="meta-value">{formatDate(photo.created_at)}</span>
                </div>
                {#if photo.exif_datetime_original}
                  <div class="meta-item">
                    <span class="meta-label">Taken</span>
                    <span class="meta-value">{formatDate(photo.exif_datetime_original)}</span>
                  </div>
                {/if}
                <div class="meta-item">
                  <span class="meta-label">File Size</span>
                  <span class="meta-value">{formatFileSize(photo.file_size)}</span>
                </div>
                {#if photo.image_width && photo.image_height}
                  <div class="meta-item">
                    <span class="meta-label">Dimensions</span>
                    <span class="meta-value">{photo.image_width} × {photo.image_height}</span>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        </div>

        {#if hasExifData(photo)}
          <div class="exif-section">
            <h2>EXIF Information</h2>
            <div class="exif-grid">
              {#if photo.exif_camera_make || photo.exif_camera_model}
                <div class="exif-item">
                  <span class="exif-label">Camera</span>
                  <span class="exif-value">
                    {[photo.exif_camera_make, photo.exif_camera_model].filter(Boolean).join(' ')}
                  </span>
                </div>
              {/if}
              {#if photo.exif_lens_model}
                <div class="exif-item">
                  <span class="exif-label">Lens</span>
                  <span class="exif-value">{photo.exif_lens_model}</span>
                </div>
              {/if}
              {#if photo.exif_focal_length}
                <div class="exif-item">
                  <span class="exif-label">Focal Length</span>
                  <span class="exif-value">{photo.exif_focal_length}</span>
                </div>
              {/if}
              {#if photo.exif_aperture}
                <div class="exif-item">
                  <span class="exif-label">Aperture</span>
                  <span class="exif-value">{photo.exif_aperture}</span>
                </div>
              {/if}
              {#if photo.exif_shutter_speed}
                <div class="exif-item">
                  <span class="exif-label">Shutter Speed</span>
                  <span class="exif-value">{photo.exif_shutter_speed}</span>
                </div>
              {/if}
              {#if photo.exif_iso}
                <div class="exif-item">
                  <span class="exif-label">ISO</span>
                  <span class="exif-value">{photo.exif_iso}</span>
                </div>
              {/if}
              {#if photo.exif_flash !== null && photo.exif_flash !== undefined}
                <div class="exif-item">
                  <span class="exif-label">Flash</span>
                  <span class="exif-value">{photo.exif_flash ? 'Fired' : 'Not fired'}</span>
                </div>
              {/if}
              {#if photo.exif_white_balance}
                <div class="exif-item">
                  <span class="exif-label">White Balance</span>
                  <span class="exif-value">{photo.exif_white_balance}</span>
                </div>
              {/if}
            </div>
          </div>
        {/if}

        {#if photo.has_gps}
          <div class="map-section">
            <h2>Location</h2>
            <div class="map-info">
              <span class="lat-lng">
              Latitude: {photo.exif_gps_latitude?.toFixed(6)} / Longitude: {photo.exif_gps_longitude?.toFixed(6)}
            </span>
              {#if photo.exif_gps_altitude}
                <span class="altitude">Altitude: {photo.exif_gps_altitude.toFixed(1)}m</span>
              {/if}
            </div>
            <div id="photo-map" class="photo-map" bind:this={mapContainer}></div>
          </div>
        {/if}
      </div>
    {/if}

    {#if error}
      <p class="error">{error}</p>
    {/if}
  </div>
</div>

<style>
  .photo-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .back-link {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    color: #6b7280;
  }

  .back-link:hover {
    color: #2563eb;
  }

  .back-link svg {
    width: 16px;
    height: 16px;
  }

  .photo-actions {
    display: flex;
    gap: 12px;
  }

  .photo-actions button {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .photo-actions button svg {
    width: 18px;
    height: 18px;
  }

  .loading-state,
  .error-state {
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

  .photo-content {
    display: flex;
    flex-direction: column;
    gap: 32px;
  }

  .photo-display {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 32px;
  }

  @media (max-width: 1024px) {
    .photo-display {
      grid-template-columns: 1fr;
    }
  }

  .photo-image {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    background: #f3f4f6;
  }

  .photo-image a {
    display: block;
  }

  .photo-image img {
    width: 100%;
    height: auto;
    display: block;
    background: #e5e7eb;
  }

  .photo-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
    padding: 16px;
    color: white;
    font-size: 14px;
    opacity: 0;
    transition: opacity 0.2s;
  }

  .photo-image:hover .photo-overlay {
    opacity: 1;
  }

  .photo-info-section {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .photo-info-section h1 {
    font-size: 24px;
    font-weight: 600;
    color: #1f2937;
  }

  .photo-description {
    font-size: 16px;
    color: #6b7280;
    line-height: 1.5;
  }

  .photo-tags-section h3,
  .photo-meta-section h3 {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .tag {
    padding: 6px 14px;
    background: #e5e7eb;
    border-radius: 16px;
    font-size: 14px;
    color: #374151;
  }

  .meta-grid {
    display: grid;
    gap: 12px;
  }

  .meta-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #e5e7eb;
  }

  .meta-label {
    font-size: 14px;
    color: #6b7280;
  }

  .meta-value {
    font-size: 14px;
    font-weight: 500;
    color: #1f2937;
  }

  .exif-section,
  .map-section {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .exif-section h2,
  .map-section h2 {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 20px;
  }

  .exif-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
  }

  .exif-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 12px;
    background: #f9fafb;
    border-radius: 8px;
  }

  .exif-label {
    font-size: 12px;
    font-weight: 500;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .exif-value {
    font-size: 14px;
    font-weight: 500;
    color: #1f2937;
  }

  .map-info {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 16px;
    font-size: 14px;
    color: #6b7280;
  }

  .photo-map {
    height: 300px;
    border-radius: 8px;
    overflow: hidden;
  }

  .error {
    color: #dc2626;
    font-size: 14px;
    margin-top: 16px;
  }
</style>
