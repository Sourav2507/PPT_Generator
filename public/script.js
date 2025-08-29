// Helpers
function escapeHtml(s){ if(!s) return ''; return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]); }

async function postForm(path, form) {
  const res = await fetch(path, { method: 'POST', body: form });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || 'Request failed');
  }
  return res;
}

// Preview outline (JSON) without generating PPT
async function previewOutline() {
  const text = document.getElementById('inputText').value.trim();
  const guidance = document.getElementById('inputGuidance').value.trim();
  const provider = document.getElementById('inputProvider').value;
  const apiKey = document.getElementById('inputApiKey').value.trim();

  if (!text || !apiKey) return alert('Provide text and API key for preview');

  const form = new FormData();
  form.append('text', text);
  form.append('guidance', guidance);
  form.append('provider', provider);
  form.append('api_key', apiKey);

  document.getElementById('status').textContent = 'Generating outline...';
  try {
    const res = await postForm('/api/outline', form);
    const json = await res.json();
    const container = document.getElementById('outlinePreview');
    container.innerHTML = '';
    const slides = json.slides || [];
    slides.slice(0, 50).forEach((s, i) => {
      const div = document.createElement('div');
      div.className = 'mb-2';
      div.innerHTML = `<strong>${i+1}. ${escapeHtml(s.title || 'Untitled')}</strong><ul>${(s.bullets||[]).map(b=>'<li>'+escapeHtml(b)+'</li>').join('')}</ul>`;
      container.appendChild(div);
    });
    document.getElementById('status').textContent = `Outline ${slides.length} slides`;
  } catch (e) {
    alert('Preview failed: ' + e.message);
    document.getElementById('status').textContent = '';
  }
}

// Generate PPTX and download
async function generatePPT() {
  const text = document.getElementById('inputText').value.trim();
  const guidance = document.getElementById('inputGuidance').value.trim();
  const provider = document.getElementById('inputProvider').value;
  const apiKey = document.getElementById('inputApiKey').value.trim();
  const fileEl = document.getElementById('inputTemplate');
  const file = fileEl.files[0];

  if (!text || !apiKey || !file) return alert('Provide text, API key, and template file');

  const form = new FormData();
  form.append('text', text);
  form.append('guidance', guidance);
  form.append('provider', provider);
  form.append('api_key', apiKey);
  form.append('template', file);

  const btn = document.getElementById('generateBtn');
  btn.disabled = true; btn.textContent = 'Generating...';
  document.getElementById('status').textContent = 'Generating presentation...';

  try {
    const res = await fetch('/api/generate', { method: 'POST', body: form });
    if (!res.ok) throw new Error(await res.text());
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'SlideGenius_Output.pptx';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    document.getElementById('status').textContent = 'Download started';
  } catch (e) {
    alert('Generation failed: ' + e.message);
    document.getElementById('status').textContent = '';
  } finally {
    btn.disabled = false; btn.textContent = 'Generate PPT';
  }
}

document.getElementById('previewBtn').addEventListener('click', previewOutline);
document.getElementById('generateBtn').addEventListener('click', generatePPT);
