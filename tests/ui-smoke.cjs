// Prueba de integración de interfaz con un puente Python simulado; no escanea redes.
const { chromium } = require('playwright');
const { readFileSync } = require('node:fs');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const assert = require('node:assert/strict');

(async () => {
  const root = path.resolve(__dirname, '..');
  const fixture = JSON.parse(execFileSync(process.env.PYTHON || 'python', [
    '-c', 'import json,app; print(json.dumps(app.WssApi().scan_networks_demo()))',
  ], { cwd: root, encoding: 'utf8' }));
  const browser = await chromium.launch({ headless: true, channel: process.env.WSS_BROWSER_CHANNEL || 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.route('https://**/*', route => route.abort());
    await page.setContent('<html><body></body></html>');
    await page.evaluate(fixture => {
      window.testScanMode = 'success';
      window.pywebview = { api: {
        get_platform_info: async () => ({ system: 'Windows', scan_available: true }),
        scan_networks: async () => window.testScanMode === 'empty'
          ? { ok: true, results: [], metadata: fixture.metadata }
          : window.testScanMode === 'failure'
            ? { ok: false, error: 'Captura no disponible' } : fixture,
        scan_networks_demo: async () => fixture,
      } };
    }, fixture);
    await page.setContent(readFileSync(path.join(root, 'index.html'), 'utf8'), { waitUntil: 'domcontentloaded' });
    assert.deepEqual(await page.locator('.flow .fkey').allTextContents(), ['01 · AU', '02 · EN', '03 · EX', '04 · AN', '05 · BM']);
    assert.equal(await page.locator('.flow-step').count(), 5);
    for (const [preset, score] of [['e1', '1.0'], ['e2', '2.0'], ['e3', '7.5'], ['e4', '9.5'], ['e5', '10.0']]) {
      await page.locator(`[data-preset="${preset}"]`).click();
      assert.equal(await page.locator('#score-num').textContent(), score);
      assert.match(await page.locator('#vector-output').textContent(), /^WSS:2\.0\/AU:[\d.]+\/EN:[\d.]+$/);
      const aligned = preset === 'e1' || preset === 'e2';
      assert.equal(await page.locator('#vector-alignment').textContent(), aligned ? 'Alineada (ALIGNED)' : 'Desviada (DEVIANT)');
    }
    await page.locator('[data-preset="e2"]').click();
    const originalVector = await page.locator('#vector-output').textContent();
    const originalContext = await page.locator('#vector-exposure').textContent();
    await page.locator('#rssi-slider').fill('-90');
    assert.equal(await page.locator('#score-num').textContent(), '2.0');
    assert.equal(await page.locator('#vector-output').textContent(), originalVector);
    assert.notEqual(await page.locator('#vector-exposure').textContent(), originalContext);
    assert.equal(await page.locator('#vector-exposure').textContent(), 'RSSI -90 dBm · Baja');
    if (process.env.WSS_UI_SCREENSHOT_DIR) {
      await page.locator('#como-funciona').scrollIntoViewIfNeeded();
      await page.locator('.flow').screenshot({ path: path.join(process.env.WSS_UI_SCREENSHOT_DIR, 'flow-wss2.png'), animations: 'disabled' });
      await page.locator('.vector-box').screenshot({ path: path.join(process.env.WSS_UI_SCREENSHOT_DIR, 'vector-wss2.png'), animations: 'disabled' });
    }
    await page.locator('[data-view="view-real"]').click();
    await page.getByRole('button', { name: 'Escanear redes de este equipo', exact: true }).click();
    const toggle = page.locator('.technical-toggle').first();
    await toggle.click();
    const close = page.getByRole('button', { name: 'Cerrar informe técnico', exact: true });
    assert(await close.isVisible());
    await page.locator('#detail-drawer-body').evaluate(el => { el.scrollTop = el.scrollHeight; });
    assert(await close.isVisible());
    await close.click();
    assert.equal(await page.locator('#detail-panel').isVisible(), false);
    assert.equal(await toggle.getAttribute('aria-expanded'), 'false');
    assert(await toggle.evaluate(el => document.activeElement === el));
    await toggle.click();
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#detail-panel').isVisible(), false);
    await page.setViewportSize({ width: 390, height: 640 });
    await toggle.click();
    const box = await close.boundingBox();
    assert(box && box.x >= 0 && box.y >= 0 && box.x + box.width <= 390 && box.y + box.height <= 640);
    if (process.env.WSS_UI_SCREENSHOT_DIR) {
      await page.screenshot({ path: path.join(process.env.WSS_UI_SCREENSHOT_DIR, 'technical-panel.png') });
    }
    await close.click();
    await page.evaluate(() => { window.testScanMode = 'empty'; });
    await page.getByRole('button', { name: 'Escanear redes de este equipo', exact: true }).click();
    assert.equal(await page.locator('.net-card').count(), 0);
    await page.evaluate(() => { window.testScanMode = 'success'; });
    await page.getByRole('button', { name: 'Escanear redes de este equipo', exact: true }).click();
    assert((await page.locator('.net-card').count()) > 0);
    await page.evaluate(() => { window.testScanMode = 'failure'; });
    await page.getByRole('button', { name: 'Escanear redes de este equipo', exact: true }).click();
    assert.equal(await page.locator('.net-card').count(), 0);
    assert.deepEqual(errors, []);
    console.log('Interfaz: cinco escenarios WSS 2.0, señal independiente, cierre, Escape, foco, pantalla estrecha y escaneos vacíos/fallidos: OK.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
