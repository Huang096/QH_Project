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
    <gene-details-page
      component-type="gene"
      :component-id="geneName"
      :enzymes-table-initial-filter="enzymesTableInitialFilter"
    />
  </template>

  <script>
  import GeneDetailsPage from '@/components/ExampleName/GeneDetailsPage.vue';

  export default {
    name: 'GenePage',
    components: {
      GeneDetailsPage
    },
    data() {
      return {
        geneName: this.$route.params.name,
      };
    },
    computed: {
      enzymesTableInitialFilter() {
        return { gene_name: this.geneName };
      },
    },
  };
  </script>

  <style lang="scss">
  /* 你的样式 */
  </style>

