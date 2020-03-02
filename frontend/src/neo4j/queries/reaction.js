import postStatement from '../http';
import handleSingleResponse from '../responseHandlers/single';

const getReaction = async (id) => {
  const statement = `
MATCH (r:Reaction)-[:V1]-(rs:ReactionState)
MATCH (r)-[:V1]-(:Metabolite)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
MATCH (r)<-[:V1]-(re:Metabolite)-[:V1]-(res:MetaboliteState)
MATCH (r)-[:V1]->(pr:Metabolite)-[:V1]-(prs:MetaboliteState)
MATCH (r)-[:V1]-(s:Subsystem)-[:V1]-(ss:SubsystemState)
MATCH (r)-[:V1]-(g:Gene)-[:V1]-(gs:GeneState)
MATCH (r)-[:V1]-(e:ExternalDb)
MATCH (r)-[:V1]-(p:PubmedReference)
WHERE r.id="${id}"
RETURN
  r.id as id,
  rs.reversible as reversible,
  rs.lowerBound as lowerBound,
  rs.upperBound as upperBound,
  rs.geneRule as geneRule,
  rs.ec as ec,
  COLLECT(DISTINCT({id: c.id, name: cs.name})) as compartments,
  COLLECT(DISTINCT({id: s.id, name: ss.name})) as subsystems,
  COLLECT(DISTINCT({id: g.id, name: gs.name})) as genes,
  e.dbName as externalDbName,
  e.url as externalDbUrl,
  e.externalId as externalDbId,
  p.pubmedId as pubmedId,
  COLLECT(DISTINCT({id: re.id, name: res.name})) as reactants,
  COLLECT(DISTINCT({id: pr.id, name: prs.name})) as products
`;

  const response = await postStatement(statement);
  return handleSingleResponse(response);
};

export default getReaction;
