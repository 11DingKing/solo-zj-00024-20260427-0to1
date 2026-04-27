<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api } from '$lib/api/client';
  import { auth } from '$lib/stores/auth';

  let timeline = [];
  let loading = true;
  let error = '';
  let pageNum = 1;
  let hasMore = true;
  let loadingMore = false;
  let user = null;

  $: username = $page.params.username;
  $: isOwnProfile = !username || (auth.subscribe(s => s.user?.username === username));

  async function loadTimeline(append = false) {
    try {
      if (append) {
        loadingMore = true;
      } else {
        loading = true;
        pageNum = 1;
        hasMore = true;
      }

      let url = `/photos/timeline/${username || ''}?page=${pageNum}`;
      if (!username) {
        url = `/photos/timeline/?page=${pageNum}`;
      }

      const response = await api.get(url);
      
      const newTimeline = response.results?.timeline || [];
      
      if (append) {
        timeline = mergeTimelines(timeline, newTimeline);
      } else {
        timeline = newTimeline;
      }
      
      hasMore = !!response.next;
      pageNum++;
    } catch (err) {
      error = err.message || 'Failed to load timeline';
    } finally {
      loading = false;
      loadingMore = false;
    }
  }

  function mergeTimelines(existing, newTimeline) {
    const merged = [...existing];
    
    for (const month of newTimeline) {
      const existingMonth = merged.find(m => m.month === month.month);
      if (existingMonth) {
        existingMonth.photos = [...existingMonth.photos, ...month.photos];
        existingMonth.photo_count = existingMonth.photos.length;
      } else {
        merged.push(month);
      }
    }
    
    return merged.sort((a, b) => b.month.localeCompare(a.month));
  }

  onMount(() => {
    loadTimeline();
  });

  function loadMore() {
    if (hasMore && !loadingMore) {
      loadTimeline(true);
    }
  }
</script>

<div class="timeline-page">
  <div class="container">
    <div class="page-header">
      <h1>
        {#if username}
          {username}'s Timeline
        {:else}
          My Timeline
        {/if}
      </h1>
      <p class="subtitle">Photos organized by date</p>
    </div>

    {#if loading && timeline.length === 0}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading timeline...</p>
      </div>
    {:else if error}
      <div class="error-state">
        <p class="error">{error}</p>
        <button class="btn btn-primary" on:click={loadTimeline}>Try Again</button>
      </div>
    {:else if timeline.length === 0}
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
          <line x1="16" y1="2" x2="16" y2="6" />
          <line x1="8" y1="2" x2="8" y2="6" />
          <line x1="3" y1="10" x2="21" y2="10" />
        </svg>
        <h3>No photos yet</h3>
        <p>Upload photos to see them in your timeline</p>
        {#if !username}
          <a href="/albums" class="btn btn-primary">Go to Albums</a>
        {/if}
      </div>
    {:else}
      <div class="timeline">
        {#each timeline as monthGroup}
          <div class="timeline-group">
            <div class="timeline-header">
              <h2>{monthGroup.month_name}</h2>
              <span class="photo-count">{monthGroup.photo_count} photos</span>
            </div>
            <div class="timeline-photos">
              {#each monthGroup.photos as photo}
                <a href="/photos/{photo.id}" class="photo-card">
                  <img
                    src="http://localhost:8000{photo.thumbnail_medium}"
                    alt={photo.title || 'Photo'}
                    loading="lazy"
                  />
                  {#if photo.exif_datetime_original}
                    <div class="photo-time">
                      {new Date(photo.exif_datetime_original).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric'
                      })}
                    </div>
                  {/if}
                </a>
              {/each}
            </div>
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
  </div>
</div>

<style>
  .page-header {
    text-align: center;
    margin-bottom: 32px;
  }

  .page-header h1 {
    font-size: 28px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
  }

  .subtitle {
    font-size: 16px;
    color: #6b7280;
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

  .timeline {
    display: flex;
    flex-direction: column;
    gap: 48px;
  }

  .timeline-group {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .timeline-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e5e7eb;
  }

  .timeline-header h2 {
    font-size: 20px;
    font-weight: 600;
    color: #1f2937;
  }

  .photo-count {
    font-size: 14px;
    color: #9ca3af;
  }

  .timeline-photos {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }

  @media (max-width: 640px) {
    .timeline-photos {
      grid-template-columns: repeat(2, 1fr);
    }
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
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }

  .photo-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    background: #e5e7eb;
  }

  .photo-time {
    position: absolute;
    bottom: 8px;
    left: 8px;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
  }

  .load-more {
    text-align: center;
    margin-top: 32px;
  }

  .error {
    color: #dc2626;
    font-size: 14px;
    margin-top: 16px;
  }
</style>
