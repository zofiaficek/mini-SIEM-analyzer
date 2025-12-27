/**
 * Wrapper na Fetch API do komunikacji z backendem Flask
 */

// --- HOSTS (GOTOWE - WZÓR) ---
export async function fetchHosts() {
    const res = await fetch('/api/hosts');
    return await res.json();
}
export async function createHost(data) {
    const res = await fetch('/api/hosts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if(!res.ok) throw new Error((await res.json()).error);
    return await res.json();
}
export async function updateHost(id, data) {
    const res = await fetch(`/api/hosts/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if(!res.ok) throw new Error('Błąd edycji hosta');
    return await res.json();
}
export async function removeHost(id) {
    await fetch(`/api/hosts/${id}`, { method: 'DELETE' });
}

// --- MONITORING / LOGI (GOTOWE) ---
export async function checkHostStatus(id, osType) {
    const endpoint = (osType === 'LINUX') 
        ? `/api/hosts/${id}/ssh-info` 
        : `/api/hosts/${id}/windows-info`;
        
    const res = await fetch(endpoint);
    if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || `Błąd HTTP ${res.status}`);
    }
    return await res.json();
}

export async function triggerLogFetch(hostId) {
    const res = await fetch(`/api/hosts/${hostId}/logs`, {
        method: 'POST'
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'Błąd pobierania logów');
    }
    return await res.json();
}

/**
 * Pobiera listę wszystkich adresów IP z rejestru
 */
export async function fetchIPs() {
    const res = await fetch('/api/ips');
    if (!res.ok) throw new Error('Błąd pobierania rejestru IP');
    return await res.json();
}

/**
 * Dodaje nowy adres IP do rejestru (np. ręczne banowanie)
 */
export async function createIP(data) {
    const res = await fetch('/api/ips', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'Błąd dodawania IP');
    }
    return await res.json();
}

/**
 * Aktualizuje status lub notatki dla danego adresu IP
 */
export async function updateIP(id, data) {
    const res = await fetch(`/api/ips/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Błąd edycji wpisu IP');
    return await res.json();
}

/**
 * Usuwa wpis z rejestru IP
 */
export async function removeIP(id) {
    const res = await fetch(`/api/ips/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Błąd usuwania IP');
    return await res.json();
}

/**
 * Pobiera ostatnie alerty bezpieczeństwa do Dashboardu
 */
export async function fetchAlerts() {
    const res = await fetch('/api/alerts');
    if (!res.ok) throw new Error('Błąd pobierania alertów');
    return await res.json();
}