(function () {
  const STORAGE_KEY = 'loveJunckTheme';
  const root = document.documentElement;

  function applyTheme(theme) {
    const dark = theme === 'dark';
    root.classList.toggle('dark-mode', dark);
    const button = document.getElementById('theme-toggle');
    if (button) {
      button.setAttribute('aria-pressed', String(dark));
      button.innerHTML = dark
        ? '<i class="fa-solid fa-sun" aria-hidden="true"></i><span>Modo claro</span>'
        : '<i class="fa-solid fa-moon" aria-hidden="true"></i><span>Modo escuro</span>';
      button.setAttribute('aria-label', dark ? 'Ativar modo claro' : 'Ativar modo escuro');
    }
  }

  let savedTheme = 'light';
  try { savedTheme = localStorage.getItem(STORAGE_KEY) || 'light'; } catch (_) {}
  if (savedTheme === 'dark') root.classList.add('dark-mode');

  function addToggle() {
    if (document.getElementById('theme-toggle')) return;
    const button = document.createElement('button');
    button.id = 'theme-toggle';
    button.className = 'theme-toggle';
    button.type = 'button';
    button.addEventListener('click', function () {
      const nextTheme = root.classList.contains('dark-mode') ? 'light' : 'dark';
      applyTheme(nextTheme);
      try { localStorage.setItem(STORAGE_KEY, nextTheme); } catch (_) {}
    });
    document.body.appendChild(button);
    applyTheme(root.classList.contains('dark-mode') ? 'dark' : 'light');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addToggle, { once: true });
  } else {
    addToggle();
  }
})();
