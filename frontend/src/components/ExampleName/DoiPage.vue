// Copyright 2024 huangzheheng // // Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License. // You may obtain a copy of the
License at // // https://www.apache.org/licenses/LICENSE-2.0 // // Unless required by applicable law
or agreed to in writing, software // distributed under the License is distributed on an "AS IS"
BASIS, // WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. // See the
License for the specific language governing permissions and // limitations under the License.
<template>
  <div class="section extended-section">
    <div class="container is-fullhd">
      <div v-if="notFound" class="columns is-centered">
        <div class="column has-text-centered is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile">
          <div class="box has-background-light content">
            <p class="title is-size-5">Not Found</p>
            <p>There might be a typo in the DOI or the article does not exist.</p>
          </div>
        </div>
      </div>
      <div v-else-if="article">
        <h3 class="title is-3">DOI: {{ article.doi }}</h3>
        <div class="columns">
          <div class="table-template column is-8-desktop">
            <div class="table-container">
              <table class="table main-table is-fullwidth">
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">Year</td>
                  <td>{{ article.time || 'NA' }}</td>
                </tr>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">Title</td>
                  <td>{{ article.title || 'NA' }}</td>
                </tr>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">Key words</td>
                  <td>{{ article.source_title || 'NA' }}</td>
                </tr>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">Abstract</td>
                  <td>{{ article.abstract || 'NA' }}</td>
                </tr>
              </table>
            </div>
          </div>
        </div>
        <div class="field columns">
          <div class="column"></div>
          <div class="column is-narrow">
            <ExportTSV
              :filename="`Doi for ${article?.doi}.tsv`"
              :format-function="formatToTSV"
              :disabled="!genesData.length"
            ></ExportTSV>
          </div>
        </div>
        <article-card v-for="dataEntry in cardData" :key="dataEntry.id" :article-data="dataEntry"></article-card>
        <gene-table :genes = genesData :columns = columnsData></gene-table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ArticleCard from './articleCard.vue';
import GeneTable from './table.vue';
import ExportTSV from '@/components/shared/ExportTSV.vue';

export default {
  name: 'DetailsPage',
  components: {
    ArticleCard,
    'gene-table':GeneTable,
    ExportTSV,
  },
  data() {
    return {
      article: null,
      notFound: false,
      genesData: [],
      columnsData: [
        { label: 'Doi', field: 'doi' },
        { label: 'Organism', field: 'organism' },
        { label: 'Gene', field: 'gene' },
        { label: 'Product', field: 'product' },
        { label: 'Product tilter', field: 'product_tilter' },
        { label: 'Time', field: 'time' },
      ]
    };
  },
  created() {
    this.fetchArticleData();
  },
  methods: {
    fetchArticleData() {
      const encodedDoi = encodeURIComponent(this.$route.params.id);
      console.log('Encoded DOI:', encodedDoi);
      const apiUrl = `http://localhost:3000/api/doi/${encodedDoi}`;
      axios.get(apiUrl)
        .then(response => {
          console.log("Complete response received:", response.data);
          if(response.data.article){
            console.log("Article details received:", response.data.article);
            console.log("Data entries received:", response.data.data);
            console.log('Genes Data:', this.genesData);
            console.log('Columns Data:', this.columnsData);
            this.article = response.data.article;
            this.cardData = response.data.data;
            this.genesData = response.data.data.map(entry => ({
              doi: entry.doi,
              gene: [
                { type: 'Knock Out', value: entry.knock_out_gene || 'NA' },
                { type: 'Overexpress', value: entry.overexpress_gene || 'NA' },
                { type: 'Heterologous', value: entry.heterologous_gene || 'NA' }
              ],
              organism: entry.organism,
              product: entry.product,
              product_tilter: entry.product_titer,
              time: entry.time
            }));
          }else{
            this.notFound = true;
          }
        })
        .catch(error => {
          console.error('Error fetching article details:', error);
          this.notFound = true;
        });
    },
    formatToTSV() {
      let tsvContent = this.columnsData.map(col => col.label).join('\t') + '\n'; // 创建标题行
      tsvContent += this.genesData.map(entry => {
        return this.columnsData.map(column => {
          if (column.field === 'gene') {
            return entry.gene.map(g => `${g.type}: ${g.value}`).join('; ');
          } else {
            return entry[column.field];
          }
        }).join('\t');
      }).join('\n');
      return tsvContent;
    }
  }
};
</script>


<style lang="scss">
/* Your existing styles can go here */
</style>
