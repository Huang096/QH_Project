
const fs = require('fs'), path = require('path');

try {
  inputDir = process.argv[2]
} catch {
  console.log("Usage: node importYAML.js input_dir");
  return;
}

const getFile = (dirPath, regexpOrString) => {
  if (!fs.existsSync(dirPath)){
    console.log("Error: no dir ", dirPath);
    return;
  }

  var files = fs.readdirSync(dirPath);
  for(var i = 0; i < files.length; i++) {
    var filePath = path.join(dirPath, files[i]);
    var stat = fs.lstatSync(filePath);
    if (!stat.isDirectory() && (regexpOrString === files[i] || (regexpOrString.test && regexpOrString.test(files[i])))) {
        return filePath;
    }
  };
};

const createCsvWriter = require("csv-writer").createObjectCsvWriter;

const idfyString = s => s.toLowerCase().replace(/[^a-z0-9]/g, '_').replace(/_+/g, '_').replace(/^_|_$/, ''); // for subsystems, compartments etc..
const idfyString2 = s => s.toLowerCase().replace(/[^a-z0-9]/g, '_').replace(/_+/g, '_'); // to generate compartmentalizedMetabolite ID from their name

const toLabelCase = (modelName) =>
  modelName.replace('-', ' ').split(/\s/g).map(word => `${word[0].toUpperCase()}${word.slice(1).toLowerCase()}`).join('');

const mergedObjects = data => data.reduce((acc, item) => {
  const [key, value] = Object.entries(item)[0];
    return {
    ...acc,
        [key]: value,
    };
}, {});

const getGeneIdsFromGeneRule = (geneRule) => {
  let idList = [];
  if (geneRule) {
    idList = geneRule.split(/[\s+and\s+|\s+or\s+|(+|)+|\s+]/).filter(e => e);
  }
  return idList;
}

const reformatCompartmentObjets = (data) => {
  return data.map((c) => {
    name = Object.values(c)[0];
    return { compartmentId: idfyString(name), name, letterCode: Object.keys(c)[0] };
  } );
};

const reformatGeneObjets = (data) => {
  return data.map((g) => {
    id = Object.values(g[0])[0];
    return { geneId: id, name: '', alternateName: '', synonyms: '', function: '' };
  } );
};

const reformatCompartmentalizedMetaboliteObjets = (data) => {
  return data.map((m) => {
    m = mergedObjects(m);
    return {
      compartmentalizedMetaboliteId: m.id,
      name: m.name,
      alternateName: '',
      synonyms: '',
      description: '',
      formula: m.formula,
      charge: m.charge,
      isCurrency: false,
      compartment: m.compartment,
    };
  } );
};

const reformatReactionObjets = (data) => {
  return data.map((r) => {
    // reactionId,name,reversible,lowerBound,upperBound,geneRule,ec
    r = mergedObjects(r);
    r.metabolites = mergedObjects(r.metabolites);
    return {
      reactionId: r.id,
      name: r.name,
      metabolites: r.metabolites,
      lowerBound: r.lower_bound,
      upperBound: r.upper_bound,
      geneRule: r.gene_reaction_rule,
      ec: r.eccodes,
      subsystems: r.subsystem,
    };
  } );
};

// find the yaml in the folder
yamlFile = getFile(inputDir, /.*[.](yaml|yml)$/);
if (!yamlFile) {
  console.log("Error: yaml file not found in path ", inputDir);
  return;
}

const yaml = require('js-yaml'),
    filePath = yamlFile;
const outputPath = './data/';

try {
  const [ metadata, metabolites, reactions, genes, compartments ] = yaml.safeLoad(fs.readFileSync(filePath, 'utf8'));
  const model = toLabelCase(metadata.metaData.short_name);
  const version = `V${metadata.metaData.version.replace(/\./g, '_')}`;

  content = { // reformat object as proper key:value objects, rename/add/remove keys
    compartmentalizedMetabolite: reformatCompartmentalizedMetaboliteObjets(metabolites.metabolites),
    reaction: reformatReactionObjets(reactions.reactions),
    gene: reformatGeneObjets(genes.genes),
    compartment: reformatCompartmentObjets(compartments.compartments),
  }

  const componentIdSets = {}; // store for each type of component the sets of existing Ids in the model, excluding compartment
  // use to filter out annotation/external ids for components not in the model
  Object.keys(content).forEach((k) => {
    componentIdSets[k] = new Set(content[k].map(e => e[`${k}Id`]));
  });

  // subsystems are not a section in the yaml file, they are extracted from the reactions info
  const subsystems = []
  componentIdSets.subsystem = new Set();
  content.reaction.forEach((r) => {
    r.subsystems.forEach((name) => {
      const id = idfyString(name);
      if (!(componentIdSets.subsystem.has(id))) {
        subsystems.push({ subsystemId: id, name });
        componentIdSets.subsystem.add(id);
      };
    });
  });
  content.subsystem = subsystems;

  // ===================================== external IDs and annotation -==================================================

  // extract EC code and PMID from reaction annotation file
  const reaction_anno_file = getFile(inputDir, /REACTIONS[.]tsv$/);
  if (!reaction_anno_file) {
    console.log("Error: reaction annotation file not found in path", inputDir);
    return;
  }

  // TODO use one of the csv parsing lib (sync)
  let lines = fs.readFileSync(reaction_anno_file, 
            { encoding: 'utf8', flag: 'r' }).split('\n').filter(Boolean);
  const reactionPMID = [];
  const PMIDS = new Set();
  for (let i = 0; i < lines.length; i++) {
    if (lines[i][0] == '#' || lines[i][0] == '@' || lines[i][0] == '[') {
      continue;
    }
    const [ reactionId, name, ECList, PMIDList ] = lines[i].split('\t').map(e => e.trim());
    // EC are already provided by the YAML (without the 'EC:' prefix)
    if (componentIdSets.reaction.has(reactionId) && PMIDList) { //only keep the ones in the model
      PMIDList.split('; ').forEach((pubmedReferenceId) => {
        reactionPMID.push({ reactionId, pubmedReferenceId });
        PMIDS.add(pubmedReferenceId);
      });
    }
  }

  // create pubmedReferences file
  let csvWriter = createCsvWriter({
    path: `${outputPath}pubmedReferences.csv`,
    header: [{ id: 'id', title: 'id' }],
  });
  csvWriter.writeRecords(Array.from(PMIDS).map(
    (id) => { return { id }; }
  )).then(() => {
    console.log('pubmedReferences file generated.');
  });

  // write reaction pubmed reference file
  csvWriter = createCsvWriter({
    path: `${outputPath}reactionPubmedReferences.csv`,
    header: [{ id: 'reactionId', title: 'reactionId' },
             { id: 'pubmedReferenceId', title: 'pubmedReferenceId' }],
  });
  csvWriter.writeRecords(reactionPMID).then(() => {
    console.log('reactionPubmedReferences file generated.');
  });

  // ============== parse External IDs files
  let extNodeIdTracker = 1
  const externalIdNodes = [];
  const externalIdDBMap = {};

  ['reaction', 'metabolite', 'gene', 'subsystem'].forEach((component) => {
    const externalIdDBComponentRel = [];
    const filename = `${component.toUpperCase()}S_EID.tsv`;
    const extIDFile = getFile(inputDir, filename);
    const IdSetKey = component === 'metabolite' ? 'compartmentalizedMetabolite' : component;
    // extIDFile = getFile(inputDir, /GENES_EID[.]tsv$/);

    if (!extIDFile) {
      console.log(`Warning: cannot find external ID file ${filename} in path`, inputDir);
      return;
    }

    // TODO use one of the csv parsing lib (sync)
    lines = fs.readFileSync(extIDFile, 
              { encoding: 'utf8', flag: 'r' }).split('\n').filter(Boolean);

    for (let i = 0; i < lines.length; i++) {
      if (lines[i][0] == '#' || lines[i][0] == '@' || lines[i][0] == '[') {
        continue;
      }
      const [ id, dbName, externalId, url ] = lines[i].split('\t').map(e => e.trim());
      if (!componentIdSets[IdSetKey].has(id)) { //only keep the ones in the model
        continue;
      }

      const externalDbEntryKey = `${dbName}${externalId}${url}`; // diff url leads to new nodes!

      let node = null;
      if (externalDbEntryKey in externalIdDBMap) {
        node = externalIdDBMap[externalDbEntryKey]; // reuse the node and id
      } else {
        node = { id: extNodeIdTracker, dbName, externalId, url };
        externalIdDBMap[externalDbEntryKey] = node;
        extNodeIdTracker += 1;

        // save the node for externalDBs.csv
        externalIdNodes.push(node);
      }

      // save the association between the node and the current component ID (reaction, gene, etc)
      externalIdDBComponentRel.push({ id, externalDbId: node.id }); // e.g. geneId, externalDbId
    }
    // write the association file
    csvWriter = createCsvWriter({
      path: `${outputPath}${component}ExternalDbs.csv`,
      header: [{ id: `${component}Id`, title: `${component}Id` },
               { id: 'externalDbId', title: 'externalDbId' }],
    });
    csvWriter.writeRecords(externalIdDBComponentRel.map(
      (e) => { return { [`${component}Id`]: e.id, externalDbId: e.externalDbId }; }
    )).then(() => {
      console.log(`${component}ExternalDbs.csv file generated.`);
    });
  });

  if (externalIdNodes.length !== 0) {
    // write the externalDbs file
    csvWriter = createCsvWriter({
      path: `${outputPath}externalDbs.csv`,
      header: Object.keys(externalIdNodes[0]).map(k => Object({ id: k, title: k })),
    });
    csvWriter.writeRecords(externalIdNodes).then(() => {
      console.log('externalDbs file generated.');
    });
  }

 // =====================================

  // write main nodes relationships files =====================================

  // need a map to get the compartment ID from the compartment letter
  const compartmentLetterToIdMap = content.compartment.reduce((entries, c) => {
    return {
      ...entries,
      [c.letterCode]: c.compartmentId,
    };
  }, {});

  csvWriter = createCsvWriter({
    path: `${outputPath}compartmentalizedMetaboliteCompartments.csv`,
    header: [{ id: 'compartmentalizedMetaboliteId', title: 'compartmentalizedMetaboliteId' }, { id: 'compartmentId', title: 'compartmentId' }],
  });

  csvWriter.writeRecords(content.compartmentalizedMetabolite.map(
    (e) => { return { compartmentalizedMetaboliteId: e.compartmentalizedMetaboliteId, compartmentId: compartmentLetterToIdMap[e.compartment] }; }
  )).then(() => {
    console.log('compartmentalizedMetaboliteCompartments file generated.');
  });

  // write metabolite-compartmentalizedMetabolite relationships =====================================
  // generate unique metabolite
  // keep only distinct metabolite (non-compartmentalize) and use the name to generate IDs
  let hm = {}
  const uniqueCompartmentalizedMap = {}
  content.compartmentalizedMetabolite.forEach((m) => {
    const newID = idfyString2(m.name);
    if (!(newID in hm)) {
      hm[newID] = m.name;
      uniqueCompartmentalizedMap[m.compartmentalizedMetaboliteId] = newID;
    } else {
      if (hm[newID] !== m.name) {
        // console.log('Error duplicated ID:' + newID + '(' + m.name + ') collision with ' + hm[newID]);
        uniqueCompartmentalizedMap[m.compartmentalizedMetaboliteId] = newID + '_';
      } else {
        uniqueCompartmentalizedMap[m.compartmentalizedMetaboliteId] = newID;
      }
    }
  })

  const nameSet = new Set();
  const uniqueMetabolites = [];
  content.compartmentalizedMetabolite.forEach((m) => {
    const newID = uniqueCompartmentalizedMap[m.compartmentalizedMetaboliteId];
    if (!(nameSet.has(m.name))) {
      uniqueMetabolites.push({
        metaboliteId: newID,
        name: m.name,
        alternateName: m.alternateName,
        synonyms: m.synonyms,
        description: m.description,
        formula: m.formula,
        charge: m.charge,
        isCurrency: m.isCurrency,
      });
      nameSet.add(m.name);
    }
  })

  // create compartmentalizedMetabolite file
  csvWriter = createCsvWriter({
    path: `${outputPath}compartmentalizedMetabolites.csv`,
    header: [{ id: 'id', title: 'id' }],
  });

  csvWriter.writeRecords(content.compartmentalizedMetabolite.map(
    (e) => { return { id: e.compartmentalizedMetaboliteId }; }
  )).then(() => {
    console.log('compartmentalizedMetabolites file generated.');
  });

  // CM-M relationships
  csvWriter = createCsvWriter({
    path: `${outputPath}compartmentalizedMetaboliteMetabolites.csv`,
    header: [{ id: 'compartmentalizedMetaboliteId', title: 'compartmentalizedMetaboliteId' }, { id: 'metaboliteId', title: 'metaboliteId' }],
  });

  csvWriter.writeRecords(content.compartmentalizedMetabolite.map(
    (e) => { 
      return { compartmentalizedMetaboliteId: e.compartmentalizedMetaboliteId,
               metaboliteId: uniqueCompartmentalizedMap[e.compartmentalizedMetaboliteId] }; }
  )).then(() => {
    console.log('compartmentalizedMetaboliteMetabolites file generated.');
  });

  // delete compartmentlizedMetabolites, add unique metabolites
  content.metabolite = uniqueMetabolites;
  delete content.compartmentalizedMetabolite;

  // write reactants-reaction, reaction-products, reaction-genes, reaction-susbsystems relationships files =====================================
  csvWriterRR = createCsvWriter({
    path: `${outputPath}compartmentalizedMetaboliteReactions.csv`,
    header: [{ id: 'compartmentalizedMetaboliteId', title: 'compartmentalizedMetaboliteId' },
             { id: 'reactionId', title: 'reactionId' },
             { id: 'stoichiometry', title: 'stoichiometry' }],
  });
  csvWriterRP = createCsvWriter({
    path: `${outputPath}reactionCompartmentalizedMetabolites.csv`,
    header: [{ id: 'reactionId', title: 'reactionId' },
             { id: 'compartmentalizedMetaboliteId', title: 'compartmentalizedMetaboliteId' },
             { id: 'stoichiometry', title: 'stoichiometry' }],
  });
  csvWriterRG = createCsvWriter({
    path: `${outputPath}reactionGenes.csv`,
    header: [{ id: 'reactionId', title: 'reactionId' },
             { id: 'geneId', title: 'geneId' }],
  });
  csvWriterRS = createCsvWriter({
    path: `${outputPath}reactionSubsystems.csv`,
    header: [{ id: 'reactionId', title: 'reactionId' },
             { id: 'subsystemId', title: 'subsystemId' }],
  });

  const reactionReactantRecords = [];
  const reactionProductRecords = [];
  const reactionGeneRecords = [];
  const reactionSubsystemRecords = [];
  content.reaction.forEach((r) => {
    Object.entries(r.metabolites).forEach((e) => {
      const [ compartmentalizedMetaboliteId, stoichiometry ] = e;
      if (stoichiometry < 0) {
        reactionReactantRecords.push({ compartmentalizedMetaboliteId, reactionId: r.reactionId, stoichiometry: -stoichiometry });
      } else {
        reactionProductRecords.push({ reactionId: r.reactionId, compartmentalizedMetaboliteId, stoichiometry });
      }
    });
    getGeneIdsFromGeneRule(r.geneRule).forEach((geneId) => {
      reactionGeneRecords.push({ reactionId: r.reactionId, geneId });
    });
    r.subsystems.forEach((name) => {
      reactionSubsystemRecords.push({ reactionId: r.reactionId, subsystemId: idfyString(name) });
    })
  });

  csvWriterRR.writeRecords(reactionReactantRecords).then(() => {
    console.log('compartmentalizedMetaboliteReactions file generated.');
  });
  csvWriterRP.writeRecords(reactionProductRecords).then(() => {
    console.log('reactionCompartmentalizedMetabolites file generated.');
  });
  csvWriterRG.writeRecords(reactionGeneRecords).then(() => {
    console.log('reactionGenes file generated.');
  });
  csvWriterRS.writeRecords(reactionSubsystemRecords).then(() => {
    console.log('reactionSubsystems file generated.');
  });

  // write nodes files =====================================
  Object.keys(content).forEach((k) => {
    const elements = content[k];
    csvWriter = createCsvWriter({
      path: `${outputPath}${k}s.csv`,
      header: [Object({ id: 'id', title: 'id' })],
    });
    csvWriter.writeRecords(elements.map(e => Object({ id: e[`${k}Id`] }))).then(() => {
      console.log(`${k}s file generated.`);
    });
    csvWriter = createCsvWriter({
      path: `${outputPath}${k}States.csv`,
      header: Object.keys(elements[0]).
        // ignore some keys 'metabolites', 'subsystems' are in reactions, 'compartment' is in metabolite
        filter(k => !['metabolites', 'subsystems', 'compartment'].includes(k)).
        map(k => Object({ id: k, title: k })),
    });
    // destructure object to remove the keys
    csvWriter.writeRecords(elements.map(({ subsystems, metabolites, compartment, ...e }) => e)).then(() => {
      console.log(`${k}States file generated.`);
    });
  });

  // TODO generate instructions more auto
  /*
  To use if nodes/indexes exist and cause errors

  MATCH (n)
  DETACH DELETE n;
  DROP INDEX ON :Metabolite(id);
  DROP INDEX ON :CompartmentalizedMetabolite(id);
  DROP INDEX ON :Compartment(id);
  DROP INDEX ON :Reaction(id);
  DROP INDEX ON :Gene(id);
  DROP INDEX ON :Subsystem(id);
  DROP INDEX ON :ExternalDb(id);
  DROP INDEX ON :PubmedReference(id);
  */

  const CypherInstructions = `
CREATE INDEX FOR (n:Metabolite) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///metabolites.csv" AS csvLine
CREATE (n:Metabolite:${model} {id:csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///metaboliteStates.csv" AS csvLine
MATCH (n:Metabolite {id: csvLine.metaboliteId})
CREATE (ns:MetaboliteState {name:csvLine.name,alternateName:csvLine.alternateName,synonyms:csvLine.synonyms,description:csvLine.description,formula:csvLine.formula,charge:toInteger(csvLine.charge),isCurrency:toBoolean(csvLine.isCurrency)})
CREATE (n)-[:${version}]->(ns);

CREATE INDEX FOR (n:CompartmentalizedMetabolite) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///compartmentalizedMetabolites.csv" AS csvLine
CREATE (n:CompartmentalizedMetabolite:${model} {id:csvLine.id});

CREATE INDEX FOR (n:Compartment) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///compartments.csv" AS csvLine
CREATE (n:Compartment:${model} {id:csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///compartmentStates.csv" AS csvLine
MATCH (n:Compartment {id: csvLine.compartmentId})
CREATE (ns:CompartmentState {name:csvLine.name,letterCode:csvLine.letterCode})
CREATE (n)-[:${version}]->(ns);

CREATE INDEX FOR (n:Reaction) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///reactions.csv" AS csvLine
CREATE (n:Reaction:${model} {id:csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///reactionStates.csv" AS csvLine
MATCH (n:Reaction {id: csvLine.reactionId})
CREATE (ns:ReactionState {name:csvLine.name,reversible:toBoolean(csvLine.reversible),lowerBound:toInteger(csvLine.lowerBound),upperBound:toInteger(csvLine.upperBound),geneRule:csvLine.geneRule,ec:csvLine.ec})
CREATE (n)-[:${version}]->(ns);

CREATE INDEX FOR (n:Gene) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///genes.csv" AS csvLine
CREATE (n:Gene:${model} {id:csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///geneStates.csv" AS csvLine
MATCH (n:Gene {id: csvLine.geneId})
CREATE (ns:GeneState {name:csvLine.name,alternateName:csvLine.alternateName,synonyms:csvLine.synonyms,function:csvLine.function})
CREATE (n)-[:${version}]->(ns);

CREATE INDEX FOR (n:Subsystem) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///subsystems.csv" AS csvLine
CREATE (n:Subsystem:${model} {id:csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///subsystemStates.csv" AS csvLine
MATCH (n:Subsystem {id: csvLine.subsystemId})
CREATE (ns:SubsystemState {name:csvLine.name})
CREATE (n)-[:${version}]->(ns);

CREATE INDEX FOR (n:ExternalDb) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///externalDbs.csv" AS csvLine
CREATE (n:ExternalDb {id:csvLine.id,dbName:csvLine.dbName,externalId:csvLine.externalId,url:csvLine.url});

CREATE INDEX FOR (n:PubmedReference) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///pubmedReferences.csv" AS csvLine
CREATE (n:PubmedReference {id:csvLine.id,pubmedId:csvLine.pubmedId});

LOAD CSV WITH HEADERS FROM "file:///compartmentalizedMetaboliteMetabolites.csv" AS csvLine
MATCH (n1:CompartmentalizedMetabolite {id: csvLine.compartmentalizedMetaboliteId}),(n2:Metabolite {id: csvLine.metaboliteId})
CREATE (n1)-[:${version}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///compartmentalizedMetaboliteCompartments.csv" AS csvLine
MATCH (n1:CompartmentalizedMetabolite {id: csvLine.compartmentalizedMetaboliteId}),(n2:Compartment {id: csvLine.compartmentId})
CREATE (n1)-[:${version}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///compartmentalizedMetaboliteReactions.csv" AS csvLine
MATCH (n1:CompartmentalizedMetabolite {id: csvLine.compartmentalizedMetaboliteId}),(n2:Reaction {id: csvLine.reactionId})
CREATE (n1)-[:${version} {stoichiometry:toFloat(csvLine.stoichiometry)}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///reactionCompartmentalizedMetabolites.csv" AS csvLine
MATCH (n1:Reaction {id: csvLine.reactionId}),(n2:CompartmentalizedMetabolite {id: csvLine.compartmentalizedMetaboliteId})
CREATE (n1)-[:${version} {stoichiometry:toFloat(csvLine.stoichiometry)}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///reactionGenes.csv" AS csvLine
MATCH (n1:Reaction {id: csvLine.reactionId}),(n2:Gene {id: csvLine.geneId})
CREATE (n1)-[:${version}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///reactionSubsystems.csv" AS csvLine
MATCH (n1:Reaction {id: csvLine.reactionId}),(n2:Subsystem {id: csvLine.subsystemId})
CREATE (n1)-[:${version}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///reactionPubmedReferences.csv" AS csvLine
MATCH (n1:Reaction {id: csvLine.reactionId}),(n2:PubmedReference {id: csvLine.pubmedReferenceId})
CREATE (n1)-[:${version}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///metaboliteExternalDbs.csv" AS csvLine
MATCH (n1:Metabolite {id: csvLine.metaboliteId}),(n2:ExternalDb {id: csvLine.externalDbId})
CREATE (n1)-[:${version}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///subsystemExternalDbs.csv" AS csvLine
MATCH (n1:Subsystem {id: csvLine.subsystemId}),(n2:ExternalDb {id: csvLine.externalDbId})
CREATE (n1)-[:${version}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///reactionExternalDbs.csv" AS csvLine
MATCH (n1:Reaction {id: csvLine.reactionId}),(n2:ExternalDb {id: csvLine.externalDbId})
CREATE (n1)-[:${version}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///geneExternalDbs.csv" AS csvLine
MATCH (n1:Gene {id: csvLine.geneId}),(n2:ExternalDb {id: csvLine.externalDbId})
CREATE (n1)-[:${version}]->(n2);

`

  console.log(CypherInstructions);

} catch (e) {
  console.log(e);
  return;
}