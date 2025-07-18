const CACHE_NAME = 'electrochemical-workstation-v1.0.0';
const urlsToCache = [
  '/',
  '/static/css/app.css',
  '/static/js/app.js',
  '/static/js/chunk-vendors.js',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// 安装事件 - 缓存资源
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// 激活事件 - 清理旧缓存
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// 拦截请求 - 缓存优先策略
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 如果在缓存中找到，返回缓存版本
        if (response) {
          return response;
        }
        
        // 否则从网络获取
        return fetch(event.request).then(response => {
          // 检查是否是有效响应
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // 克隆响应，因为它是一个流
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
          
          return response;
        });
      })
  );
});

// 处理后台同步（可选）
self.addEventListener('sync', event => {
  if (event.tag === 'experiment-data-sync') {
    event.waitUntil(syncExperimentData());
  }
});

// 处理推送通知（可选）
self.addEventListener('push', event => {
  if (event.data) {
    const notificationData = event.data.json();
    event.waitUntil(
      self.registration.showNotification(notificationData.title, {
        body: notificationData.body,
        icon: '/icons/icon-192x192.png',
        badge: '/icons/icon-72x72.png',
        tag: 'experiment-notification'
      })
    );
  }
});

// 同步实验数据的函数
async function syncExperimentData() {
  try {
    // 这里可以实现后台数据同步逻辑
    console.log('Syncing experiment data...');
    
    // 示例：向后端API发送数据
    const response = await fetch('/api/experiments/sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        // 从IndexedDB获取待同步的数据
        timestamp: Date.now()
      })
    });
    
    if (response.ok) {
      console.log('Data sync successful');
    } else {
      console.error('Data sync failed');
    }
  } catch (error) {
    console.error('Error syncing data:', error);
  }
}
