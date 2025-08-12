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
