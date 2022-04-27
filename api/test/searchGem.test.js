import driver from 'neo4j/driver';
import { search } from 'neo4j/queries/search';

describe('search', () => {
  afterAll(async () => {
    await driver.close();
  });

  test('gem search should have max 50 results per component type', async () => {
    const data = await search({
      searchTerm: 'H2O',
      model: 'HumanGem',
      version: HUMAN_GEM_VERSION,
    });

    expect(Object.keys(data)).toContain('Human-GEM');

    const { metabolite } = data['Human-GEM'];
    expect(metabolite.length).toBeGreaterThan(0);
    expect(metabolite.length).toBeLessThan(51);
  });

  test('gem search should receive sensible ranking scores', async () => {
    const [data1, data2] = await Promise.all([
      search({
        searchTerm: 'POLR3F',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'Asparaginyl-Cysteinyl',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
    ]);

    const { gene } = data1['Human-GEM'];

    const { metabolite } = data2['Human-GEM'];

    const [firstGene] = gene.sort((a, b) => b.score - a.score);
    const [firstMetabolite] = metabolite.sort((a, b) => b.score - a.score);

    expect(firstGene.name).toBe('POLR3F');
    expect(firstGene.score).toBeGreaterThan(0);
    expect(firstMetabolite.name).toMatch(/Asparaginyl-Cysteinyl/);
    expect(firstMetabolite.score).toBeGreaterThan(0);
  });

  test('gem search with special characters should not fail', async () => {
    const [data1, data2] = await Promise.all([
      search({
        searchTerm: 'rna/dna: (met)',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'cy\\|+ {zinc}! glyco/mg',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
    ]);
    for (const data of [data1, data2]) {
      const { name } = data['Human-GEM'];
      expect(name).toEqual('Human-GEM');
    }
  });

  test('gem search for metabolite name gives valid score for metabolites', async () => {
    const [data1, data2] = await Promise.all([
      search({
        searchTerm: 'pyridoxine',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: '3(R)-hydroxy-(2S,6R,10)-trimethyl-hendecanoyl',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
    ]);
    const [data1Metabolite] = data1['Human-GEM'].metabolite.sort(
      (a, b) => b.score - a.score
    );
    expect(data1Metabolite.score).toBeGreaterThan(0);

    const [data2Metabolite] = data2['Human-GEM'].metabolite.sort(
      (a, b) => b.score - a.score
    );
    expect(data2Metabolite.score).toBeGreaterThan(0);
  });

  test('gem search for metabolite id gives matches', async () => {
    const data = await search({
      searchTerm: 'MAM01513s',
      model: 'HumanGem',
    });
    expect(data['Human-GEM'].metabolite.length).toBeGreaterThan(0);
  });

  test('gem search for metabolite formula gives matches', async () => {
    const data = await search({
      searchTerm: 'C21H44NO7P',
      model: 'HumanGem',
    });
    expect(data['Human-GEM'].metabolite.length).toBeGreaterThan(0);
  });

  test('gem search by gene name, alternate name or id finds the gene', async () => {
    const data = await search({
      searchTerm: 'NEURL1B',
      model: 'HumanGem',
      version: HUMAN_GEM_VERSION,
    });

    const data2 = await search({
      searchTerm: 'neuralized E3 ubiquitin protein ligase 1B',
      model: 'HumanGem',
      version: HUMAN_GEM_VERSION,
    });

    const data3 = await search({
      searchTerm: 'ENSG00000214357',
      model: 'HumanGem',
      version: HUMAN_GEM_VERSION,
    });
    const [firstGene] = data['Human-GEM'].gene.sort(
      (a, b) => b.score - a.score
    );
    const [firstGene2] = data2['Human-GEM'].gene.sort(
      (a, b) => b.score - a.score
    );
    const [firstGene3] = data3['Human-GEM'].gene.sort(
      (a, b) => b.score - a.score
    );
    expect(firstGene.name).toEqual('NEURL1B');
    expect(firstGene2.name).toEqual('NEURL1B');
    expect(firstGene3.name).toEqual('NEURL1B');
  });
});
