import driver from 'neo4j/driver';
import { search } from 'neo4j/queries/search';

describe('gem search', () => {
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
        searchTerm: 'Polr3f',
        model: 'MouseGem',
        version: MOUSE_GEM_VERSION,
      }),
      search({
        searchTerm: 'Asparaginyl-Cysteinyl',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
    ]);

    const [firstGene] = data1['Mouse-GEM'].gene;
    const [firstMetabolite] = data2['Human-GEM'].metabolite;

    expect(firstGene.id).toBe('Polr3f');
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
        searchTerm: 'coenzyme A',
        model: 'YeastGem',
        version: YEAST_GEM_VERSION,
      }),
      search({
        searchTerm: '3(R)-hydroxy-(2S,6R,10)-trimethyl-hendecanoyl',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
    ]);
    const [data1Metabolite] = data1['Yeast-GEM'].metabolite;
    expect(data1Metabolite.score).toBeGreaterThan(0);

    const [data2Metabolite] = data2['Human-GEM'].metabolite;
    expect(data2Metabolite.score).toBeGreaterThan(0);
  });

  test('gem search for metabolite id gives matches', async () => {
    const [data1, data2] = await Promise.all([
      search({
        searchTerm: 'MAM01513s',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'MAM00715c',
        model: 'FruitflyGem',
        version: FRUITFLY_GEM_VERSION,
      }),
    ]);
    expect(data1['Human-GEM'].metabolite.length).toBeGreaterThan(0);
    expect(data2['Fruitfly-GEM'].metabolite.length).toBeGreaterThan(0);
  });

  test('gem search for metabolite formula gives matches', async () => {
    const [data1, data2] = await Promise.all([
      search({
        searchTerm: 'C21H44NO7P',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'C31H53NO4',
        model: 'ZebrafishGem',
        version: ZEBRAFISH_GEM_VERSION,
      }),
    ]);
    expect(data1['Human-GEM'].metabolite.length).toBeGreaterThan(0);
    expect(data2['Zebrafish-GEM'].metabolite.length).toBeGreaterThan(0);
    expect(data2['Zebrafish-GEM'].metabolite[0].id).toEqual('MAM00130m');
  });

  test('gem search by gene name, alternate name or id finds the gene', async () => {
    const [data1, data2, data3] = await Promise.all([
      search({
        searchTerm: 'NEURL1B',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'neuralized E3 ubiquitin protein ligase 1B',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'ENSG00000214357',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
    ]);
    const [firstGene1] = data1['Human-GEM'].gene;
    const [firstGene2] = data2['Human-GEM'].gene;
    const [firstGene3] = data3['Human-GEM'].gene;

    expect(firstGene1.name).toEqual('NEURL1B');
    expect(firstGene2.name).toEqual('NEURL1B');
    expect(firstGene3.name).toEqual('NEURL1B');
  });

  test('gem search by cross reference finds the gene', async () => {
    const [data1, data2, data3] = await Promise.all([
      search({
        searchTerm: 'ENST00000415826',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: '11145',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'P53816',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
    ]);

    const [firstGene1] = data1['Human-GEM'].gene;
    const [firstGene2] = data2['Human-GEM'].gene;
    const [firstGene3] = data3['Human-GEM'].gene;

    expect(firstGene1.name).toEqual('PLAAT3');
    expect(firstGene2.name).toEqual('PLAAT3');
    expect(firstGene3.name).toEqual('PLAAT3');
  });

  test('gem search by id, EC code and PMID finds the reaction', async () => {
    const [data1, data2, data3] = await Promise.all([
      search({
        searchTerm: 'MAR03893',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: '1.13.11.34',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: '7929234',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
    ]);
    const [firstReaction1] = data1['Human-GEM'].reaction;
    const [firstReaction2] = data2['Human-GEM'].reaction;
    const [firstReaction3] = data3['Human-GEM'].reaction;
    expect(firstReaction1.id).toEqual('MAR03893');
    // Multiple reactions share EC code and PMID
    expect(firstReaction2.id).toEqual('MAR03893');
    expect(firstReaction3.id).toEqual('MAR00973');
  });

  test('gem search by cross reference finds the reaction', async () => {
    const [data1, data2, data3, data4, data5] = await Promise.all([
      search({
        searchTerm: 'RE3476C',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'HMR_0973',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'MNXR103919',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'RCR12105',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
      search({
        searchTerm: 'RE3476C',
        model: 'HumanGem',
        version: HUMAN_GEM_VERSION,
      }),
    ]);

    const [firstReaction1] = data1['Human-GEM'].reaction;
    const [firstReaction2] = data2['Human-GEM'].reaction;
    // Multiple reactions share MetaNetX id
    const [firstReaction3] = data3['Human-GEM'].reaction;
    const [firstReaction4] = data4['Human-GEM'].reaction;
    const [firstReaction5] = data5['Human-GEM'].reaction;

    expect(firstReaction1.id).toEqual('MAR00973');
    expect(firstReaction2.id).toEqual('MAR00973');
    expect(firstReaction3.id).toEqual('MAR03896');
    expect(firstReaction4.id).toEqual('MAR00973');
    expect(firstReaction5.id).toEqual('MAR00973');
  });

  test('gem search on name should find subsystem', async () => {
    const data = await search({
      searchTerm: 'Beta oxidation of even-chain fatty acids (peroxisomal)',
      model: 'HumanGem',
      version: HUMAN_GEM_VERSION,
    });
    const [firstSubsystem] = data['Human-GEM'].subsystem;
    expect(firstSubsystem.name).toEqual(
      'Beta oxidation of even-chain fatty acids (peroxisomal)'
    );
    expect(firstSubsystem.score).toBeGreaterThan(0);
  });

  test('gem search on name should find compartment', async () => {
    const data = await search({
      searchTerm: 'Extracellular',
      model: 'HumanGem',
      version: HUMAN_GEM_VERSION,
    });
    const [firstCompartment] = data['Human-GEM'].compartment;
    expect(firstCompartment.name).toEqual('Extracellular');
    expect(firstCompartment.score).toBeGreaterThan(0);
  });
});
