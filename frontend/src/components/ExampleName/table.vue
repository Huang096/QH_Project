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
  <div id="gene-table">
    <vue-good-table
      :columns="columns"
      :rows="genes"
      :sort-options="{ enabled: true }"
      :search-options="{ enabled: true, placeholder: 'Search for genes' }"
      :pagination-options="{
        enabled: true,
        mode: 'records',
        perPage: 10,
        nextLabel: 'Next',
        prevLabel: 'Previous',
        rowsPerPageLabel: 'Rows per page',
        ofLabel: 'of'
      }"
      style-class="vgt-table striped"
    >
      <template v-slot:table-row="{ row, column }">
        <span v-if="column.field === 'gene'">
          <!-- 特殊处理 gene 列 -->
          <span v-for="geneInfo in row.gene" :key="geneInfo.type" :style="{ color: getGeneColor(geneInfo.type) }" :title="`${geneInfo.type} Gene`">
            {{ geneInfo.value }}<span v-if="geneInfo !== row.gene[row.gene.length - 1]">; </span>
          </span>
        </span>
        <span v-else-if="column.field === 'link'">
          <router-link :to="`/genes/${row[column.field]}`">{{ row[column.field] }}</router-link>
        </span>
        <span v-else>
          {{ row[column.field] }}
        </span>
      </template>
    </vue-good-table>
  </div>
</template>

<script>
import { VueGoodTable } from 'vue-good-table-next';
import 'vue-good-table-next/dist/vue-good-table-next.css';

export default {
  name: 'GeneTable',
  components: {
    VueGoodTable,
  },
  props: {
    genes: {
      type: Array,
      required: true
    },
    columns: {
      type: Array,
      required: true
    }
  },
  methods: {
    getGeneColor(type) {
      switch (type) {
        case 'Knock Out': return 'red';
        case 'Overexpress': return 'blue';
        case 'Heterologous': return 'green';
        default: return 'black'; // 提供默认颜色，防止未识别类型
      }
    }
  },
  mounted() {
    console.log("Mounted - Columns:", this.columns);
    console.log("Mounted - Genes:", this.genes);
  },
  updated() {
    console.log("Updated - Columns:", this.columns);
    console.log("Updated - Genes:", this.genes);
  }
};
</script>
