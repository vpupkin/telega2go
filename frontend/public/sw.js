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
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        if (response) {
          return response;
        }
        
        // For API requests, try network first, then cache
        if (event.request.url.includes('/api/')) {
          return fetch(event.request)
            .then((response) => {
              // Cache successful API responses
              if (response.status === 200) {
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then((cache) => {
                  cache.put(event.request, responseClone);
                });
              }
              return response;
            })
            .catch(() => {
              // Return cached API response if available
              return caches.match(event.request);
            });
        }
        
        // For other requests, fetch from network
        return fetch(event.request);
      })
      .catch(() => {
        // If both cache and network fail, show offline page
        if (event.request.destination === 'document') {
          return caches.match('/');
        }
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
