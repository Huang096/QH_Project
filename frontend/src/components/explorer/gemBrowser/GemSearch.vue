<template>
  <div class="column is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile">
    <div class="control">
      <div id="input-wrapper">
        <p class="control has-icons-right has-icons-left">
        <input id="search" class="input" type="text"
          v-model="searchTermString" @input="searchDebounce"
          placeholder="Search by metabolite (uracil), gene (SULT1A3), or reaction (ATP => cAMP + PPi) or subsystem"
          @keyup.esc="showResults = false"
          @focus="showResults = true"
          @blur="showResults = false"
          ref="searchInput">
          <span class="has-text-info icon is-small is-right" v-show="showSearchCharAlert" style="width: 200px">
            Type at least 2 characters
          </span>
          <span class="icon is-medium is-left">
            <i class="fa fa-search"></i>
          </span>
        </p>
        <router-link :to="{ name: 'search', query: { term: this.searchTermString } }">Global search</router-link>
      </div>
      <div id="searchResults" v-show="showResults && searchTermString.length > 1" ref="searchResults">
        <div id="asn" class="notification is-large is-unselectable has-text-centered clickable" v-show="searchResults.length !== 0 && !showLoader" @mousedown.prevent="globalSearch">
          Limited to 50 results per type. Click to search all integrated GEMs
        </div>
        <div class="resList" v-show="!showLoader">
          <template v-if="searchResults.length !== 0" v-for="(k, i1) in resultsOrder">
            <div v-for="(r, i2) in searchResults[k]" class="searchResultSection">
              <hr class="is-marginless" v-if="i2 !== 0">
              <div class="clickable" @mousedown.prevent="goToTab(k, r.id || r.name_id || r.name)">
                 <b class="is-capitalized">{{ k }}: </b><label class="clickable" v-html="formatSearchResultLabel(k, r, searchTermString)"></label>
              </div>
            </div>
            <hr class="bhr" v-if="searchResults[k].length !== 0">
          </template>
        </div>
        <div v-show="showLoader" class="has-text-centered">
          <a class="button is-primary is-inverted is-outlined is-large is-loading"></a>
        </div>
        <div v-show="!showLoader && noResult" class="has-text-centered notification is-marginless">
          {{ messages.searchNoResult }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import Loader from '@/components/Loader';
import _ from 'lodash';
import { sortResults } from '../../../helpers/utils';
import { chemicalFormula, chemicalReaction } from '../../../helpers/chemical-formatters';
import { default as EventBus } from '../../../event-bus';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'gem-search',
  props: {
    searchTerm: {
      default: '',
    },
    model: {
      default: '',
    },
  },
  components: {
    Loader,
  },
  data() {
    return {
      errorMessage: '',
      resultsOrder: ['metabolite', 'gene', 'reaction', 'subsystem', 'compartment'],
      searchResults: [],
      searchTermString: '',
      showSearchCharAlert: false,
      showResults: true,
      showLoader: false,
      noResult: false,
      messages,

      itemKeys: {
        human1: {
          gene: ['id', 'name'],
          reaction: ['id', 'equation'],
          metabolite: ['id', 'name', 'compartment'],
          subsystem: ['name', 'system'],
          compartment: ['name'],
        },
        yeast8: {
          gene: ['id', 'name'],
          reaction: ['id', 'equation'],
          metabolite: ['id', 'name', 'compartment'],
          subsystem: ['name', 'system'],
          compartment: ['name'],
        },
      },
    };
  },
  mounted() {
    $('#search').focus();
  },
  methods: {
    searchDebounce: _.debounce(function e() {
      this.noResult = false;
      this.showSearchCharAlert = this.searchTermString.length === 1;
      this.showLoader = true;
      if (this.searchTermString.length > 1) {
        this.showResults = true;
        this.search(this.searchTermString);
      }
    }, 700),
    search(searchTerm) {
      this.searchTermString = searchTerm;
      const url = `${this.model.database_name}/search/${searchTerm}`;
      axios.get(url)
      .then((response) => {
        const localResults = {
          metabolite: [],
          gene: [],
          reaction: [],
          subsystem: [],
          compartment: [],
        };

        for (const model of Object.keys(response.data)) {
          const resultsModel = response.data[model];
          for (const resultType of ['metabolite', 'gene', 'reaction', 'subsystem', 'compartment']) {
            if (resultsModel[resultType]) {
              localResults[resultType] = localResults[resultType].concat(
                resultsModel[resultType].map(
                (e) => {
                  const d = e; d.model = { id: model, name: resultsModel.name }; return d;
                })
              );
            }
          }
        }
        this.searchResults = localResults;

        this.noResult = true;
        for (const k of Object.keys(this.searchResults)) {
          if (this.searchResults[k].length) {
            this.showSearchCharAlert = false;
            this.noResult = false;
            break;
          }
        }
        this.showLoader = false;
        // sort result by exact matched first, then by alpha order
        for (const k of Object.keys(localResults)) {
          if (localResults[k].length) {
            localResults[k].sort((a, b) => this.sortResults(a, b, this.searchTermString));
          }
        }
        this.$refs.searchResults.scrollTop = 0;
      })
      .catch(() => {
        this.searchResults = [];
        this.noResult = true;
        this.showLoader = false;
      });
    },
    goToTab(type, id) {
      this.searchTerm = '';
      this.searchTermString = '';
      this.searchResults = [];
      EventBus.$emit('GBnavigateTo', type, id);
    },
    globalSearch() {
      this.$router.push({ name: 'search', query: { term: this.searchTermString } });
    },
    formatSearchResultLabel(type, element, searchTerm) {
      const re = new RegExp(`(${searchTerm})`, 'ig');
      let s = '';
      for (const key of this.itemKeys[this.model.database_name][type]) {
        if (element[key]) {
          if (key === 'equation') {
            s = `${s} ‒ ${chemicalReaction(element[key].replace(re, '<b>$1</b>'), element.is_reversible)}`;
          } else {
            // do not HL the compartment name
            s = key === 'compartment' ? `${s} ‒ ${element[key]}` : `${s} ‒ ${element[key].replace(re, '<b>$1</b>')}`;
          }
        }
      }
      if (!s.toLowerCase().includes(searchTerm.toLowerCase())) {
        // add info in the label containing the search string
        for (const k of ['hmdb_id', 'uniprot_id', 'ncbi_id', 'formula', 'pubchem_id', 'aliases', 'name']) {
          if (element[k] && element[k].toLowerCase().includes(searchTerm.toLowerCase())) {
            s = `${s} ‒ ${element[k].replace(re, '<b>$1</b>')}`;
          }
        }
      }
      if (s.length !== 0) {
        return s.slice(2);
      }
      return s;
    },
    chemicalFormula,
    sortResults,
  },
};
</script>

<style lang="scss">

#input-wrapper {
  position: relative; /* for absolute child element */
}

#searchResults {
  background: white;
  position: absolute;
  top: 37px;
  overflow-x: hidden;
  width: 100%;
  border: 1px solid lightgray;
  border-top: 0;
  margin-top: -2px;
  z-index: 30;

  #asn {
    padding: 4px;
  }

  .resList {
      max-height: 22rem;
      overflow-y: auto;
  }

  hr {
    &.bhr {
      margin: 5px 7px;
      padding: 0;
      border-top: 3px double #000000;
    }
  }
  .bhr:last-child {
    display: none;
  }

  .searchResultSection {
    padding: 0px 10px;
    div {
      padding: 7px 0px;
    }
    div:hover, label:hover {
      color: #00549E;
    }
  }
}

</style>