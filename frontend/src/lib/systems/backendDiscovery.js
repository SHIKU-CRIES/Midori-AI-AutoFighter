// Backend discovery system for Docker environments
// Automatically detects which backend service is available and sets the API base URL

import { browser } from '$app/environment';

let discoveredApiBase = null;
let discoveryPromise = null;

// List of possible backend service names in order of preference
const BACKEND_SERVICES = [
  'backend',           // Default backend
  'backend-llm-cuda',  // CUDA-enabled LLM backend
  'backend-llm-amd',   // AMD-enabled LLM backend  
  'backend-llm-cpu'    // CPU-only LLM backend
];

// Fallback for local development
const DEFAULT_BACKEND = (typeof window !== 'undefined' && browser)
  ? `${location.protocol}//${location.hostname}:59002`
  : 'http://localhost:59002';

/**
 * Checks if a backend service is available by making a health check request
 * @param {string} serviceUrl - The base URL to test
 * @returns {Promise<{available: boolean, flavor?: string}>}
 */
async function checkBackendAvailability(serviceUrl) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
    
    const response = await fetch(`${serviceUrl}/`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: controller.signal,
      cache: 'no-store'
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data = await response.json();
      return { 
        available: true, 
        flavor: data.flavor || 'unknown'
      };
    }
    
    return { available: false };
  } catch {
    // Network error, timeout, or other failure
    return { available: false };
  }
}

/**
 * Discovers the available backend service by trying each possible service name
 * @returns {Promise<string>} The discovered API base URL
 */
async function discoverBackend() {
  // If we're not in a browser environment, use the env var or default
  if (!browser) {
    return import.meta.env.VITE_API_BASE || DEFAULT_BACKEND;
  }
  
  // If VITE_API_BASE is explicitly set, use it directly (for local development)
  if (import.meta.env.VITE_API_BASE) {
    return import.meta.env.VITE_API_BASE;
  }
  
  console.log('🔍 Discovering available backend service...');
  
  // Try each backend service in order
  for (const serviceName of BACKEND_SERVICES) {
    const serviceUrl = `http://${serviceName}:59002`;
    console.log(`🔍 Checking ${serviceName}...`);
    
    const result = await checkBackendAvailability(serviceUrl);
    
    if (result.available) {
      console.log(`✅ Found ${serviceName} (flavor: ${result.flavor})`);
      return serviceUrl;
    }
  }
  
  // If no Docker services are available, fall back to localhost
  console.log('🔍 No Docker backend services found, checking localhost...');
  const localhostResult = await checkBackendAvailability(DEFAULT_BACKEND);
  
  if (localhostResult.available) {
    console.log(`✅ Using localhost backend (flavor: ${localhostResult.flavor})`);
    return DEFAULT_BACKEND;
  }
  
  // Nothing is available - return default and let the app handle the error
  console.warn('⚠️ No backend services are available');
  return DEFAULT_BACKEND;
}

/**
 * Gets the API base URL, performing discovery if needed
 * @returns {Promise<string>} The API base URL to use
 */
export async function getApiBase() {
  // Return cached result if we already discovered it
  if (discoveredApiBase) {
    return discoveredApiBase;
  }
  
  // If discovery is already in progress, wait for it
  if (discoveryPromise) {
    return discoveryPromise;
  }
  
  // Start discovery process
  discoveryPromise = discoverBackend().then(apiBase => {
    discoveredApiBase = apiBase;
    return apiBase;
  });
  
  return discoveryPromise;
}

/**
 * Resets the discovery cache (useful for testing or reconnection scenarios)
 */
export function resetDiscovery() {
  discoveredApiBase = null;
  discoveryPromise = null;
}

/**
 * Gets the currently discovered API base without triggering discovery
 * @returns {string|null} The cached API base or null if not yet discovered
 */
export function getCachedApiBase() {
  return discoveredApiBase;
}