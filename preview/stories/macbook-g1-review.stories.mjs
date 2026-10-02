const frame = (title, src, notes) => `
  <section style="display:grid;gap:12px">
    <header style="display:grid;gap:6px">
      <div style="font:600 18px/1.2 system-ui">${title}</div>
      <div style="font:14px/1.4 system-ui;color:#666">${notes}</div>
      <a href="${src}" target="_blank" rel="noreferrer"
         style="font:600 15px/1 system-ui;color:inherit;text-decoration:underline">
        Open original
      </a>
    </header>
    <a href="${src}" target="_blank" rel="noreferrer"
       style="display:block;overflow:auto;border:1px solid #ddd;background:#f5f5f5">
      <img src="${src}" alt="${title}"
           style="display:block;width:100%;height:auto;max-width:none">
    </a>
  </section>`;

export default {
  title: 'Review/MacBook G1',
  parameters: {
    layout: 'fullscreen',
    controls: { disable: true },
  },
};

export const CalibrationOverlays = {
  name: 'Calibration overlays',
  render: () => {
    const root = document.createElement('main');
    root.style.cssText = [
      'box-sizing:border-box',
      'display:grid',
      'gap:28px',
      'padding:16px',
      'max-width:1600px',
      'margin:0 auto',
      'background:#fff',
      'color:#111',
    ].join(';');

    root.innerHTML = `
      <header style="display:grid;gap:8px">
        <h1 style="margin:0;font:700 24px/1.15 system-ui">MacBook Pro 14 M5 — G1 calibration</h1>
        <p style="margin:0;font:14px/1.45 system-ui;color:#555">
          PROVISIONAL. Inspect the colored bounds against the Apple reference.
          Tap an image or “Open original” for native full-resolution zoom.
        </p>
      </header>
      ${frame(
        'Deck',
        '/g1/macbook/deck_calibration_overlay.png',
        'Check trackpad bounds, speaker fields and Touch ID.'
      )}
      ${frame(
        'Display',
        '/g1/macbook/display_calibration_overlay.png',
        'Check display opening, notch, camera and outer-lid cross-check.'
      )}
    `;
    return root;
  },
};
