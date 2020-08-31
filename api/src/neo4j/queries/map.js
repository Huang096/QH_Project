import querySingleResult from 'neo4j/queryHandlers/single';
import queryListResult from 'neo4j/queryHandlers/list';

const getMapsListing = async ({ model, version }) => {
  const m = model ? `:${model}` : '';
  const v = version ? `:V${version}` : '';

  const statement = `
MATCH (:CompartmentState)-[${v}]-(c:Compartment${m})
CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[${v}]-(:Compartment${m} {id: $cid})
  RETURN cs { id: $cid, .* } as data
  
  UNION
  
  MATCH (:Compartment${m} {id: $cid})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(r:Reaction)
  RETURN { id: $cid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (csvg:SvgMap)-[${v}]-(:Compartment${m} {id: $cid})
  RETURN { id: $cid, compartmentSVGs: COLLECT(DISTINCT(csvg {.*})) } as data
", {cid:c.id}) yield value
RETURN { compartment: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as data

UNION

MATCH (:SubsystemState)-[${v}]-(s:Subsystem${m})
CALL apoc.cypher.run("
  MATCH (ss:SubsystemState)-[${v}]-(s:Subsystem {id: $sid})
  RETURN ss { id: $sid, .* } as data
  
  UNION
  
  MATCH (:Subsystem${m} {id: $sid})-[${v}]-(r:Reaction)
  RETURN { id: $sid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (:Subsystem${m} {id: $sid})-[${v}]-(ssvg:SvgMap)
  RETURN { id: $sid, subsystemSVGs: COLLECT(DISTINCT(ssvg {.*})) } as data
", {sid:s.id}) yield value
RETURN { subsystem: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as data
`;

  const result = await queryListResult(statement);

  const mapListing = {
    compartments: result.filter(o => !!o.compartment).reduce((l, o) => [...l, o.compartment] , []),
    subsystems: result.filter(o => !!o.subsystem).reduce((l, o) => [...l, o.subsystem] , []),
  };

  return mapListing;
};

const mapSearch = async ({ model, version, searchTerm }) => {
  const m = model ? `:${model}` : '';
  const v = version ? `:V${version}` : '';

  const statement = `
CALL db.index.fulltext.queryNodes("fulltext", "${searchTerm}~")
YIELD node
OPTIONAL MATCH (node)-[${v}]-(parentNode${m})
WHERE node${m} OR parentNode${m}
RETURN [n in COLLECT(DISTINCT(
	CASE
		WHEN EXISTS(node.id) THEN node.id
		ELSE parentNode.id
	END
))[..100] WHERE n IS NOT NULL]`;

  return querySingleResult(statement);
};
export { getMapsListing, mapSearch };
