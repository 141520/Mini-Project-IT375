// Global helpers
window.getToken = () => localStorage.getItem('token') ||
  document.cookie.split('; ').find(r => r.startsWith('access_token='))?.split('=')[1];

// ===== Dark mode toggle =====
(function() {
  const btn = document.getElementById('themeToggle');
  if (!btn) return;
  btn.addEventListener('click', () => {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.theme = isDark ? 'dark' : 'light';
  });
})();

// ===== Dice roll sound (Web Audio — no file needed) =====
window.playDiceSound = function() {
  try {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    const ctx = new AC();
    const duration = 0.35;
    const buf = ctx.createBuffer(1, ctx.sampleRate * duration, ctx.sampleRate);
    const data = buf.getChannelData(0);
    // noise burst with multiple "clack" peaks to sound like dice
    for (let i = 0; i < data.length; i++) {
      const t = i / data.length;
      const env = Math.pow(1 - t, 1.5);
      let clack = 0;
      [0.0, 0.12, 0.22].forEach(peak => {
        const d = Math.abs(t - peak);
        if (d < 0.04) clack += (Math.random() * 2 - 1) * (1 - d / 0.04);
      });
      data[i] = (clack + (Math.random() * 2 - 1) * 0.3) * env * 0.5;
    }
    const src = ctx.createBufferSource();
    src.buffer = buf;
    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = 1800;
    filter.Q.value = 0.8;
    src.connect(filter).connect(ctx.destination);
    src.start();
    src.onended = () => ctx.close();
  } catch (e) { /* silent */ }
};
