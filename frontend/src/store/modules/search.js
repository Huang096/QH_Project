import searchApi from '@/api/search';
import { sortResults } from '@/helpers/utils';

const data = {
  categories: [
    'metabolite',
    'gene',
    'reaction',
    'subsystem',
    'compartment',
  ],
  globalResults: {},
  results: {},
  searchTermString: '',
};

const categorizeResults = (results) => {
  const categorizedResults = data.categories.reduce((obj, category) => ({ ...obj, [category]: [] }), {});
  Object.keys(results).forEach((model) => {
    const resultsModel = results[model];
    data.categories.filter(resultType => resultsModel[resultType])
      .forEach((resultType) => {
        categorizedResults[resultType] = categorizedResults[resultType].concat(
          resultsModel[resultType].map(
            (e) => {
              const d = e; d.model = { id: model, name: resultsModel.name }; return d;
            })
        );
      });
  });
  return categorizedResults;
};

const getters = {
  globalResultsEmpty: state => Object.keys(state.globalResults).length === 0,

  categorizedGlobalResults: state => categorizeResults(state.globalResults),

  categorizedGlobalResultsCount: (state, _getters) => Object.fromEntries( // eslint-disable-line no-unused-vars
    Object.entries(_getters.categorizedGlobalResults).map(([k, v]) => [k, v.length])),

  categorizedAndSortedResults: (state) => {
    if (Object.keys(state.results).length === 0) {
      return {};
    }

    const results = categorizeResults(state.results);

    // TODO: consider rewriting this return so it's more readable
    return Object.fromEntries(Object.entries(results).map(([k, v]) => [k, (() => {
      if (v === 0) {
        return v;
      }
      return v.sort((a, b) => sortResults(a, b, state.searchTermString));
    })()]));
  },
};

const actions = {
  async globalSearch({ commit }, searchTerm) {
    const results = await searchApi.globalSearch(searchTerm);
    commit('setGlobalResults', results);
  },
  async search({ state, commit }, { model, metabolitesAndGenesOnly }) {
    console.warn(`TODO: use real model: ${model} and metabolitesAndGenesOnly: ${metabolitesAndGenesOnly}`);
    const payload = {
      version: '1_3_0',
      searchTerm: state.searchTermString,
      model: 'HumanGem',
      limit: 50,
    };
    const results = await searchApi.search(payload);
    commit('setResults', results);
  },
  setSearchTermString({ commit }, searchTermString) {
    commit('setSearchTermString', searchTermString);
  },
  clearGlobalSearchResults({ commit }) {
    commit('setGlobalResults', {});
  },
  clearSearchResults({ commit }) {
    commit('setResults', {});
  },
};

const mutations = {
  setGlobalResults: (state, globalResults) => {
    state.globalResults = globalResults;
  },
  setResults: (state, results) => {
    state.results = results;
  },
  setSearchTermString: (state, searchTermString) => {
    state.searchTermString = searchTermString;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
