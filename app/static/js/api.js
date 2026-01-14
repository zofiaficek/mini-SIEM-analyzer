/**
 * api.js
 * Wrapper na Fetch API z obsługą CSRF
 */
// Zadanie dodatkowe 5 - stworzenie własnego tokena i użycia funkcji securedFetch
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
}
/**
 * FUNKCJA BAZOWA: securedFetch
 * To serce naszej komunikacji z backendem. 
 * Automatyzuje powtarzalne czynności i dba o bezpieczeństwo.
 */
async function securedFetch(url, options = {}) {
    // Konstruujemy nagłówki żądania
    const headers = {
        'Content-Type': 'application/json', // Informujemy serwer, że wysyłamy JSON
        'X-CSRFToken': getCsrfToken(),      // Dodajemy token CSRF do nagłówka
        ...options.headers                  // Pozwalamy na nadpisanie/dodanie innych nagłówków
    };

    // Wykonujemy faktyczne połączenie
    const res = await fetch(url, { ...options, headers });
    
    // Globalna obsługa błędów HTTP
    if (!res.ok) {
        // Próbujemy wyciągnąć komunikat błędu wysłany przez Flask
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || `Błąd HTTP ${res.status}`);
    }
    
    // Obsługa odpowiedzi "No Content" 
    if (res.status === 204) return null;

    // Zwracamy sparsowany obiekt JavaScript
    return await res.json();
}
//-----------------------------------------------------------------------------------


// --- HOSTS (GOTOWE - WZÓR) ---
/*export async function fetchHosts() {
    const res = await fetch('/api/hosts');
    return await res.json();
}

export async function createHost(data) {
    return await securedFetch('/api/hosts', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

export async function updateHost(id, data) {
    return await securedFetch(`/api/hosts/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

export async function removeHost(id) {
    return await securedFetch(`/api/hosts/${id}`, { method: 'DELETE' });
}

// --- MONITORING / LOGI (GOTOWE) ---
export async function checkHostStatus(id, osType) {
    const endpoint = (osType === 'LINUX') 
        ? `/api/hosts/${id}/ssh-info` 
        : `/api/hosts/${id}/windows-info`;
        
    const res = await fetch(endpoint);
    if (!res.ok) throw new Error('Błąd pobierania statusu');
    return await res.json();
}

export async function triggerLogFetch(hostId) {
    return await securedFetch(`/api/hosts/${hostId}/logs`, { method: 'POST' });
}

// ===============================================================
// TODO: ZADANIE 4 - KOMUNIKACJA FRONTEND-BACKEND
// ===============================================================
// Brakuje funkcji do obsługi Rejestru IP oraz Alertów.
// Panel Admina i Dashboard będą rzucać błędy, dopóki tego nie uzupełnisz.
// Wzoruj się na funkcjach z sekcji HOSTS powyżej.


// Fetch - funkcja przegladarki ktora wysyla zapytanie pod konkretny adres (zdefiniowany w hosts.py)
export async function fetchIPs() {
    // 1. Wykonaj fetch GET na '/api/ips'
    // 2. Zwróć json
    const res = await fetch('/api/ips');
    return await res.json();
}

export async function createIP(data) {
    // 1. Wykonaj fetch POST na '/api/ips' z danymi (body)
    // 2. Obsłuż błędy (!res.ok)
    const res = await securedFetch('/api/ips', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },    // to co jest w body jest w JSON
        body: JSON.stringify(data)  //zamienia obiekt JS data na tekst
    });
    if(!res.ok) throw new Error((await res.json()).error || 'Błąd dodawania IP');
    return await res.json();    //zmienia JSON na obiekt JS
}

export async function updateIP(id, data) {
    // PUT na /api/ips/<id>
    const res = await securedFetch(`/api/ips/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },    // to co jest w body jest w JSON
        body: JSON.stringify(data)      //zamienia obiekt JS data na tekst
    });
    if(!res.ok) throw new Error((await res.json()).error || 'Błąd edycji IP');
    return await res.json();    //zmienia JSON na obiekt JS
}

export async function removeIP(id) {
    // DELETE na /api/ips/<id>
    const res = await securedFetch(`/api/ips/${id}`, { method: 'DELETE' });
    if(!res.ok) throw new Error((await res.json()).error || 'Błąd usuwania IP');
}

export async function fetchAlerts() {
    // GET na /api/alerts
    const res = await fetch('/api/alerts');
    if(!res.ok) throw new Error((await res.json()).error || 'Błąd pobierania alertów');
    return await res.json();

}*/

// --- HOSTY ---
export async function fetchHosts() {
    return await securedFetch('/api/hosts');
}

export async function createHost(data) {
    return await securedFetch('/api/hosts', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

export async function updateHost(id, data) {
    return await securedFetch(`/api/hosts/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

export async function removeHost(id) {
    return await securedFetch(`/api/hosts/${id}`, { 
        method: 'DELETE' 
    });
}

// --- MONITORING ---
export async function checkHostStatus(id, osType) {
    const endpoint = (osType === 'LINUX') 
        ? `/api/hosts/${id}/ssh-info` 
        : `/api/hosts/${id}/windows-info`;
    return await securedFetch(endpoint);
}

export async function triggerLogFetch(hostId) {
    return await securedFetch(`/api/hosts/${hostId}/logs`, { 
        method: 'POST' 
    });
}

// --- REJESTR IP (ZADANIE 4) ---
export async function fetchIPs() {
    return await securedFetch('/api/ips');
}

export async function createIP(data) {
    return await securedFetch('/api/ips', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

export async function updateIP(id, data) {
    return await securedFetch(`/api/ips/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

export async function removeIP(id) {
    return await securedFetch(`/api/ips/${id}`, { 
        method: 'DELETE' 
    });
}

// --- ALERTY ---
export async function fetchAlerts() {
    return await securedFetch('/api/alerts');
}
