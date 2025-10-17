// Minimal JS placeholder: handle simple UI behaviors
document.addEventListener('click', (e) => {
  const el = e.target;
  if (el.matches('[data-copy]')) {
    const text = el.getAttribute('data-copy');
    if (text) navigator.clipboard.writeText(text);
  }
});

