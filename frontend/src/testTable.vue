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
  <div>
    <gene-table :genes="testGenes" :columns="testColumns"></gene-table>
  </div>
</template>

<script>
import GeneTable from './components/ExampleName/table.vue'; // 确保路径正确

export default {
  name: 'TestGeneTable',
  components: {
    GeneTable
  },
  data() {
    return {
      testGenes: [
        { id: '001', gene: 'BRCA1', description: 'Breast cancer type 1 susceptibility protein' },
        { id: '002', gene: 'TP53', description: 'Tumor protein p53' },
        // 添加更多的测试数据
      ],
      testColumns: [
        { label: 'ID', field: 'id' },
        { label: 'Gene', field: 'gene' },
        { label: 'Description', field: 'description' }
      ],
    };
  },
};
</script>

<style>
/* 你可以在这里添加一些页面特定的样式 */
</style>
