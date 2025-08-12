export async function startRun() {
  const res = await fetch('http://localhost:59002/run/start', { method: 'POST' });
  return res.json();
}

export async function updateParty(runId, party) {
  const res = await fetch(`http://localhost:59002/party/${runId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ party })
  });
  return res.json();
}

export async function fetchMap(runId) {
  const res = await fetch(`http://localhost:59002/map/${runId}`);
  return res.json();
}

export async function getPlayers() {
  const res = await fetch('http://localhost:59002/players');
  return res.json();
}

export async function battleRoom(runId, action = '') {
  const res = await fetch(`http://localhost:59002/rooms/${runId}/battle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action })
  });
  return res.json();
}

export async function shopRoom(runId, action = '') {
  const res = await fetch(`http://localhost:59002/rooms/${runId}/shop`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action })
  });
  return res.json();
}

export async function restRoom(runId, action = '') {
  const res = await fetch(`http://localhost:59002/rooms/${runId}/rest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action })
  });
  return res.json();
}
