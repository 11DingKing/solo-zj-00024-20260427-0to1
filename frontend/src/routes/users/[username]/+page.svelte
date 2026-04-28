<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api/client';
  import { auth } from '$lib/stores/auth';

  let userProfile = null;
  let albums = [];
  let timeline = [];
  let loading = true;
  let error = '';
  let activeTab = 'albums';
  let isOwnProfile = false;

  $: username = $page.params.username;

  async function loadUserProfile() {
    try {
      loading = true;
      
      const unsub = auth.subscribe((state) => {
        isOwnProfile = state.user?.username === username;
      });
      
      userProfile = await api.get(`/accounts/users/${username}/`);
      
      const albumsResponse = await api.get(`/albums/user/${username}/`);
      albums = albumsResponse.results || [];
      
      const timelineResponse = await api.get(`/photos/timeline/${username}/`);
      timeline = timelineResponse.results?.timeline || [];
      
    } catch (err) {
      error = err.message || 'Failed to load user profile';
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadUserProfile();
  });

  $: if (username) {
    loadUserProfile();
  }
</script>

<div class="profile-page">
  <div class="container">
    {#if loading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading profile...</p>
      </div>
    {:else if error}
      <div class="error-state">
        <p class="error">{error}</p>
        <button class="btn btn-primary" on:click={loadUserProfile}>Try Again</button>
      </div>
    {:else if userProfile}
      <div class="profile-header">
        <div class="profile-avatar">
          {#if userProfile.avatar}
            <img src="http://localhost:8000{userProfile.avatar}" alt={userProfile.username} />
          {:else}
            <div class="avatar-placeholder">
              {userProfile.username.charAt(0).toUpperCase()}
            </div>
          {/if}
        </div>
        <div class="profile-info">
          <h1>{userProfile.username}</h1>
          {#if userProfile.bio}
            <p class="bio">{userProfile.bio}</p>
          {/if}
          <div class="profile-stats">
            <span class="stat">
              <strong>{albums.length}</strong> Albums
            </span>
            <span class="stat">
              <strong>{albums.reduce((acc, a) => acc + (a.photo_count || 0), 0)}</strong> Photos
            </span>
            <span class="stat">
              <strong>{new Date(userProfile.date_joined).getFullYear()}</strong> Joined
            </span>
          </div>
        </div>
        {#if isOwnProfile}
          <div class="profile-actions">
            <button class="btn btn-outline" on:click={() => goto('/albums')}>
              Manage Albums
            </button>
          </div>
        {/if}
      </div>

      <div class="tabs">
        <button
          class="tab-btn"
          class:active={activeTab === 'albums'}
          on:click={() => activeTab = 'albums'}
        >
          Albums ({albums.length})
        </button>
        <button
          class="tab-btn"
          class:active={activeTab === 'timeline'}
          on:click={() => activeTab = 'timeline'}
        >
          Timeline
        </button>
      </div>

      {#if activeTab === 'albums'}
        {#if albums.length === 0}
          <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
            <h3>No albums yet</h3>
            {#if isOwnProfile}
              <p>Create your first album to share with others</p>
              <button class="btn btn-primary" on:click={() => goto('/albums')}>
                Create Album
              </button>
            {:else}
              <p>This user hasn't shared any albums yet</p>
            {/if}
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
            {/each}
          </div>
        {/if}
      {:else if activeTab === 'timeline'}
        {#if timeline.length === 0}
          <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
            <h3>No photos in timeline</h3>
            <p>This user hasn't uploaded any photos yet</p>
          </div>
        {:else}
          <div class="timeline">
            {#each timeline.slice(0, 5) as monthGroup}
              <div class="timeline-group">
                <div class="timeline-header">
                  <h2>{monthGroup.month_name}</h2>
                  <span class="photo-count">{monthGroup.photo_count} photos</span>
                </div>
                <div class="timeline-photos">
                  {#each monthGroup.photos.slice(0, 8) as photo}
                    <a href="/photos/{photo.id}" class="photo-card">
                      <img
                        src="http://localhost:8000{photo.thumbnail_medium}"
                        alt={photo.title || 'Photo'}
                        loading="lazy"
                      />
                    </a>
                  {/each}
                </div>
              </div>
            {/each}
            
            {#if timeline.length > 5 || timeline[0]?.photos.length > 8}
              <div class="view-all-timeline">
                <a href={isOwnProfile ? '/timeline' : `/timeline/${username}`} class="btn btn-outline">
                  View Full Timeline
                </a>
              </div>
            {/if}
          </div>
        {/if}
      {/if}
    {/if}
  </div>
</div>

<style>
  .profile-header {
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 24px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 24px;
  }

  @media (max-width: 640px) {
    .profile-header {
      flex-direction: column;
      text-align: center;
    }
  }

  .profile-avatar {
    flex-shrink: 0;
  }

  .profile-avatar img {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    background: #e5e7eb;
  }

  .avatar-placeholder {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    font-weight: 600;
    color: white;
  }

  .profile-info {
    flex: 1;
  }

  .profile-info h1 {
    font-size: 24px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
  }

  .bio {
    font-size: 16px;
    color: #6b7280;
    margin-bottom: 16px;
  }

  .profile-stats {
    display: flex;
    gap: 24px;
  }

  .stat {
    font-size: 14px;
    color: #6b7280;
  }

  .stat strong {
    display: block;
    font-size: 20px;
    font-weight: 600;
    color: #1f2937;
  }

  .profile-actions {
    flex-shrink: 0;
  }

  .tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 24px;
    background: #f3f4f6;
    padding: 4px;
    border-radius: 8px;
    width: fit-content;
  }

  .tab-btn {
    padding: 10px 20px;
    border: none;
    background: transparent;
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .tab-btn:hover {
    background: #e5e7eb;
    color: #374151;
  }

  .tab-btn.active {
    background: white;
    color: #1f2937;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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

  .timeline {
    display: flex;
    flex-direction: column;
    gap: 32px;
  }

  .timeline-group {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .timeline-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e5e7eb;
  }

  .timeline-header h2 {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
  }

  .timeline-photos {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }

  .photo-card {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    aspect-ratio: 1;
    background: #f3f4f6;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .photo-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .photo-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    background: #e5e7eb;
  }

  .view-all-timeline {
    text-align: center;
    padding-top: 16px;
  }

  .error {
    color: #dc2626;
    font-size: 14px;
    margin-top: 16px;
  }
</style>
