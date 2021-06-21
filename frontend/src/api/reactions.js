import axios from 'axios';
import { constructCompartmentStr, reformatChemicalReactionHTML } from '@/helpers/utils';

const formatGeneRule = (reaction) => {
  const { geneRule, genes } = reaction;

  if (!geneRule) {
    return null;
  }
  return geneRule.split(/\s+/).map((w) => {
    if (w.match(/and|or/)) {
      return w;
    }

    let gid = w;
    let prefix = '';
    let suffix = '';

    if (gid.slice(0, 2) === '((') {
      gid = gid.slice(2);
      prefix = '((';
    } else if (gid.slice(0, 1) === '(') {
      gid = gid.slice(1);
      prefix = '(';
    } else if (gid.slice(-2) === '))') {
      gid = gid.slice(0, -2);
      suffix = '))';
    } else if (gid.slice(-1) === ')') {
      gid = gid.slice(0, -1);
      suffix = ')';
    }

    const gene = genes.find(g => g.id === gid);
    return `${prefix}${gene.name}${suffix}`;
  }).join(' ');
};

const fetchReactionData = async ({ id, model, version }) => {
  const params = { model, version };
  let { data } = await axios.get(`/reactions/${id}`, { params });

  data = {
    ...data,
    compartment_str: data.compartments.map(c => c.name).join(', '),
    reactants: data.metabolites.filter(m => m.outgoing),
    products: data.metabolites.filter(m => !m.outgoing),
    geneRule: formatGeneRule(data),
  };

  return {
    ...data,
    equation: reformatChemicalReactionHTML(data, true, model.short_name),
  };
};

const fetchRelatedReactionsForReaction = async ({ id, model, version, limit }) => {
  const params = { model, version, limit };
  const { data } = await axios.get(`/reactions/${id}/related-reactions`, { params });
  return data.sort((a, b) => (a.compartment_str < b.compartment_str ? -1 : 1)).map(r => ({
    ...r,
    compartment_str: constructCompartmentStr(r),
    reactants: r.metabolites.filter(m => m.outgoing),
    products: r.metabolites.filter(m => !m.outgoing),
  }));
};

const fetchRelatedReactions = async (resourceType, id, model, version, limit) => {
  const params = { model, version, limit };
  const { data } = await axios.get(`/${resourceType}s/${id}/related-reactions`, { params });
  return data.map(r => ({
    ...r,
    compartment_str: constructCompartmentStr(r),
    subsystem_str: r.subsystems.map(s => s.name).join(', '),
    reactants: r.metabolites.filter(m => m.outgoing),
    products: r.metabolites.filter(m => !m.outgoing),
  }));
};

const fetchRelatedReactionsForGene = async ({ id, model, version, limit }) => fetchRelatedReactions('gene', id, model, version, limit);

const fetchRelatedReactionsForMetabolite = async ({ id, model, version, limit }, allCompartments) => fetchRelatedReactions('metabolite', id, model, version, limit, allCompartments);

const fetchRelatedReactionsForSubsystem = async ({ id, model, version, limit }) => fetchRelatedReactions('subsystem', id, model, version, limit);

export default {
  fetchReactionData,
  fetchRelatedReactionsForReaction,
  fetchRelatedReactionsForGene,
  fetchRelatedReactionsForMetabolite,
  fetchRelatedReactionsForSubsystem,
};
