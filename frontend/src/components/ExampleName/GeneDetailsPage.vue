<!--
 Copyright 2024 huangzheheng
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
     https://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

<template>
  <div class="section extended-section">
    <div class="container is-fullhd">
      <div v-if="notFound" class="columns is-centered">
        <div class="column has-text-centered is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile">
          <div class="box has-background-light content">
            <p class="title is-size-5">not found.</p>
            <p><span class="is-block"> Probably there is a typo in the identifier in the URL. </span></p>
          </div>
        </div>
      </div>
      <div v-else-if="geneInfo">
        <h3 class="title is-3">Gene: {{ geneInfo.kegg }}</h3>
        <div class="columns">
          <div class="table-template column is-8-desktop">
            <div class="table-container">
              <table class="table main-table is-fullwidth">
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">
                    Kegg
                  </td>
                  <td>{{ geneInfo.kegg }}</td>
                </tr>
                <h3 class="title is-3 title-no-wrap">Cross references</h3>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">
                    NCBI Protein
                  </td>
                  <td>{{ geneInfo.ncbi_protein }}</td>
                </tr>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">
                    UniProtKB
                  </td>
                  <td>{{ geneInfo.uniptotkb }}</td>
                </tr>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="field columns">
        <div class="column"></div>
          <div class="column is-narrow">
            <ExportTSV
              :filename="`Product for ${productInfo?.product}.tsv`"
              :format-function="formatToTSV"
              :disabled="!genesData.length"
            >
          </ExportTSV>
        </div>
      </div>

      <gene-table :genes = genesData :columns = columnsData></gene-table>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import GeneTable from './table.vue';
import ExportTSV from '@/components/shared/ExportTSV.vue';

export default {
  name: 'GeneInfoPage',
  components: {
    'gene-table':GeneTable,
    ExportTSV,
  },
  data() {
    return {
      geneInfo: null, // 用于存储geneInfo的详细信息
      //data: [],
      notFound: false,
      genesData: [],
      columnsData: [
        { label: 'Gene', field: 'gene' },
        { label: 'Organism', field: 'strain' },
        { label: 'Product', field: 'product' },
        { label: 'Doi', field: 'doi' },
        { label: 'Product tilter', field: 'product_tilter' },
        { label: 'Time', field: 'time' },
      ]
    };
  },
  created() {
    this.fetchGeneData();
  },
  methods: {
    fetchGeneData() {
      const encodedGene = encodeURIComponent(this.$route.params.name); // 使用当前路由的参数
      const apiUrl = `http://localhost:3000/api/gene/${encodedGene}`;
      axios.get(apiUrl)
        .then(response => {
          console.log("Complete response received:", response.data);
          this.geneInfo = response.data.geneInfo; // 直接使用 response.data.geneInfo
          this.notFound = false;
          this.genesData = response.data.data.map(entry => ({
              strain: entry.strain,
              doi: entry.doi,
              gene: [
                { type: 'Knock Out', value: entry.knock_out_gene || 'NA' },
                { type: 'Overexpress', value: entry.overexpress_gene || 'NA' },
                { type: 'Heterologous', value: entry.heterologous_gene || 'NA' }
              ],
              product: entry.product,
              product_tilter: entry.product_titer,
              time: entry.time
            }));
        })
        .catch(error => {
          console.error('Error fetching gene details:', error);
          this.notFound = true;
        });
    },
    formatToTSV() {
      let tsvContent = this.columnsData.map(col => col.label).join('\t') + '\n'; // 创建标题行
      tsvContent += this.genesData.map(entry => {
        return this.columnsData.map(column => {
          if (column.field === 'gene') {
            // 特殊处理gene字段，因为它是一个数组
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



