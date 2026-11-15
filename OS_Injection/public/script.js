const form = document.getElementById('pingForm');
const hostInput = document.getElementById('host');
const pingBtn = document.getElementById('pingBtn');
const clearBtn = document.getElementById('clearBtn');
const cmdBox = document.getElementById('command');
const outBox = document.getElementById('output');

async function runPing(e) {
  e.preventDefault();
  const host = hostInput.value.trim();
  if (!host) return;

  pingBtn.disabled = true;
  pingBtn.textContent = 'Running...';
  outBox.textContent = 'Executing ping command...';

  try {
    const res = await fetch('/api/ping', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ host })
    });
    const data = await res.json();
    cmdBox.textContent = data.command || '-';
    outBox.textContent = data.output || '(No output)';
  } catch (err) {
    outBox.textContent = 'Request failed: ' + err.message;
  } finally {
    pingBtn.disabled = false;
    pingBtn.textContent = 'Run Ping';
  }
}

function clearOutput() {
  cmdBox.textContent = '-';
  outBox.textContent = 'Waiting for input...';
}

form.addEventListener('submit', runPing);
if (clearBtn) clearBtn.addEventListener('click', clearOutput);
