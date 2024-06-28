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
          <div
            class="column has-text-centered is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile"
          >
            <div class="box has-background-light content">
              <p class="title is-size-5">
                not found.
              </p>
              <p>
                <span class="is-block">
                  Probably there is a typo in the identifier in the URL.
                </span>
              </p>
            </div>
          </div>
        </div>
        <div v-else>
          <h3 class="title is-3">Product:  {{ productInfo ? productInfo.product : '' }}</h3>
          <div class="columns">
            <div class="table-template column is-8-desktop">
              <div class="table-container">
                <table class="table main-table is-fullwidth">
                  <tr>
                    <td class="td-key has-background-primary has-text-white-bis is-capitalized">
                      Cross reference ID
                    </td>
                    <td>{{ productInfo?.crossrefid }}</td>
                  </tr>
                  <tr>
                    <td class="td-key has-background-primary has-text-white-bis is-capitalized">
                      MetaNetx
                    </td>
                    <td>{{ productDetail?.metanetx }}</td>
                  </tr>
                  <tr>
                    <td class="td-key has-background-primary has-text-white-bis is-capitalized">
                      SMILES
                    </td>
                    <td>{{ productDetail?.smiles }}</td>
                  </tr>
                </table>
              </div>
            </div>
            <div class="column is-4 has-text-centered">
              <RDKitImage v-if="productDetail?.smiles" :smiles="productDetail.smiles" />
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
            ></ExportTSV>
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
import RDKitImage from '@/components/shared/RDKitImage.vue';


export default {
  name: 'ProductPage',
  components: {
    'gene-table':GeneTable,
    ExportTSV,
    RDKitImage,
  },
  data() {
    return {
      productInfo: null, // 用于存储product的详细信息
      notFound: false,
      genesData: [],
      columnsData: [
        { label: 'Product', field: 'product' },
        { label: 'Pmid', field: 'doi' },
        { label: 'Organism', field: 'organism' },
        { label: 'Gene', field: 'gene' },
        { label: 'Product tilter', field: 'product_tilter' },
        { label: 'Time', field: 'time' },
      ]
    };
  },
  created() {
    this.fetchProductData();
  },
  methods: {
    fetchProductData() {
      const encodedGene = encodeURIComponent(this.$route.params.name);
      const apiUrl = `http://localhost:3000/api/product/${encodedGene}`;
      axios.get(apiUrl)
        .then(response => {
          //console.log("Complete response received:", response.data);
          this.productInfo = response.data.productInfo;
          this.productDetail = response.data.productDetail
          this.notFound = false;
          this.genesData = response.data.data.map(entry => ({
              // doi: entry.pmid || "NA",
              doi: entry.doi,
              gene: [
                { type: 'Knock Out', value: entry.knock_out_gene || 'NA' },
                { type: 'Overexpress', value: entry.overexpress_gene || 'NA' },
                { type: 'Heterologous', value: entry.heterologous_gene || 'NA' }
              ],
              organism: entry.strain,
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

<style lang="scss">
.section.extended-section .columns {
  display: flex;
  flex-wrap: wrap;
}

.table-container {
  margin-bottom: 1rem;
}

.column.is-4.has-text-centered {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
