// Service Worker for Telega2Go PWA
const CACHE_NAME = 'telega2go-v1.1.0';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png'
];

// Offline form data storage
const OFFLINE_FORMS_KEY = 'offline_forms';

// Install event - cache resources
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching files');
        return cache.addAll(urlsToCache);
      })
      .catch((error) => {
        console.error('Service Worker: Cache failed', error);
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  // ✅ CRITICAL: Always bypass cache for API requests (network-only)
  // Also skip for non-GET methods (POST/PUT/DELETE) - they cannot be cached
  if (event.request.url.includes('/api/') || event.request.method !== 'GET') {
    event.respondWith(
      fetch(event.request)
        .catch((error) => {
          // If network fails, return error response instead of undefined
          console.error('Service Worker: API request failed', error);
          return new Response(
            JSON.stringify({ error: 'Network request failed' }),
            {
              status: 503,
              statusText: 'Service Unavailable',
              headers: { 'Content-Type': 'application/json' }
            }
          );
        })
    );
    return; // Don't proceed with cache logic for API requests or non-GET methods
  }
  
  // For non-API requests, use cache-first strategy
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version if available
        if (response) {
          return response;
        }
        
        // Fetch from network for non-API requests
        return fetch(event.request)
        .then((response) => {
          // Don't cache if response is not ok
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // ✅ CRITICAL: Only cache GET requests (POST/PUT/DELETE cannot be cached)
          // Also skip caching for non-GET methods to avoid "Request method 'POST' is unsupported" error
          if (event.request.method !== 'GET') {
            return response;
          }
          
          // Cache successful GET responses only
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
          
          return response;
        })
          .catch((error) => {
            console.error('Service Worker: Fetch failed', error);
            // If both cache and network fail, show offline page for documents
            if (event.request.destination === 'document') {
              return caches.match('/');
            }
            // For other requests, return error response
            return new Response('Network error', {
              status: 503,
              statusText: 'Service Unavailable'
            });
          });
      })
      .catch((error) => {
        console.error('Service Worker: Cache match failed', error);
        // Fallback: try to fetch from network
        return fetch(event.request)
          .catch(() => {
            // Last resort: return offline page for documents
            if (event.request.destination === 'document') {
              return caches.match('/');
            }
            return new Response('Offline', { status: 503 });
          });
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Deleting old cache', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Background sync for offline form submissions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('Service Worker: Background sync triggered');
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Handle offline form submissions when back online
  console.log('Service Worker: Performing background sync');
  
  try {
    const offlineForms = await getOfflineForms();
    if (offlineForms.length > 0) {
      console.log(`Service Worker: Found ${offlineForms.length} offline forms to sync`);
      
      for (const form of offlineForms) {
        try {
          const response = await fetch(form.url, {
            method: form.method,
            headers: form.headers,
            body: form.body
          });
          
          if (response.ok) {
            console.log('Service Worker: Successfully synced offline form');
            await removeOfflineForm(form.id);
          }
        } catch (error) {
          console.error('Service Worker: Failed to sync offline form:', error);
        }
      }
    }
  } catch (error) {
    console.error('Service Worker: Background sync failed:', error);
  }
}

// Offline form storage functions
async function getOfflineForms() {
  try {
    const data = await caches.open('offline-forms').then(cache => cache.match('forms'));
    return data ? await data.json() : [];
  } catch {
    return [];
  }
}

async function saveOfflineForm(formData) {
  try {
    const cache = await caches.open('offline-forms');
    const forms = await getOfflineForms();
    forms.push({
      id: Date.now().toString(),
      ...formData,
      timestamp: new Date().toISOString()
    });
    await cache.put('forms', new Response(JSON.stringify(forms)));
  } catch (error) {
    console.error('Service Worker: Failed to save offline form:', error);
  }
}

async function removeOfflineForm(formId) {
  try {
    const cache = await caches.open('offline-forms');
    const forms = await getOfflineForms();
    const updatedForms = forms.filter(form => form.id !== formId);
    await cache.put('forms', new Response(JSON.stringify(updatedForms)));
  } catch (error) {
    console.error('Service Worker: Failed to remove offline form:', error);
  }
}

// Message handling for offline form storage
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SAVE_OFFLINE_FORM') {
    saveOfflineForm(event.data.formData);
  }
});
