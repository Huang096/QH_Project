import fetch from 'node-fetch';

describe('data overlay', () => {
  test('should return at least one data type, that includes at least one data source', async () => {
    const res = await fetch(`${API_BASE}/data-overlay/Human-GEM`);

    const data = await res.json();
    expect(Object.values(data).length).toBeGreaterThan(0);
    expect(Object.values(data)[0].length).toBeGreaterThan(0);
  });

  test('should return a TSV file for a given data source', async () => {
    const res = await fetch(
      `${API_BASE}/data-overlay/Human-GEM/transcriptomics/hpaRna.tsv`
    );

    const contentType = res.headers.get('content-type');
    expect(contentType).toContain('text/tsv');
  });
});