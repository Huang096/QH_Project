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
      <div v-else-if="keggRef">
        <h3 class="title is-3">Gene: {{ keggRef.product }}</h3>
        <div class="columns">
          <div class="table-template column is-8-desktop">
            <div class="table-container">
              <table class="table main-table is-fullwidth">
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">
                    Kegg
                  </td>
                  <td>{{ keggRef.product }}</td>
                </tr>
                <h3 class="title is-3 title-no-wrap">Cross references</h3>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">
                    NCBI Protein
                  </td>
                  <td>{{ keggRef.ncbi_protein }}</td>
                </tr>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">
                    UniProtKB
                  </td>
                  <td>{{ keggRef.uniptotkb }}</td>
                </tr>
              </table>
            </div>
          </div>
        </div>
      </div>

      <h3 class="title is-3">Test Search Table</h3>
      <!-- 新静态表格 -->
      <div class="columns">
        <div class="table-template column is-8-desktop">
          <div class="table-container">
            <table class="table main-table is-fullwidth vgt-table striped">
              <!-- 表头 -->
              <thead>
                <tr>
                  <th class="has-background-primary has-text-black">Gene</th>
                  <th class="has-background-primary has-text-black">Organism</th>
                  <th class="has-background-primary has-text-black">Domain</th>
                  <th class="has-background-primary has-text-black">Reaction</th>
                  <th class="has-background-primary has-text-black">Compound</th>
                </tr>
                <tr>
                  <!-- New filter input fields -->
                  <th><input type="text" class="filter-input" placeholder="Filter Gene"></th>
                  <th><input type="text" class="filter-input" placeholder="Filter Organism"></th>
                  <th><input type="text" class="filter-input" placeholder="Filter Domain"></th>
                  <th><input type="text" class="filter-input" placeholder="Filter Reaction"></th>
                  <th><input type="text" class="filter-input" placeholder="Filter Compound"></th>

                </tr>
              </thead>
              <!-- 表格主体 -->
              <tbody>
                <!-- 静态数据行 -->
                <tr>
                  <td>taes</td>
                  <td>E</td>
                  <td>RO3460</td>
                  <td>C00074</td>
                  <td>9.7563</td>
                </tr>
                <!-- 更多静态数据行... -->
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'GeneInfoPage',
  data() {
    return {
      keggRef: null, // 用于存储keggRef的详细信息
      //data: [],
      notFound: false,
    };
  },
  created() {
    this.fetchGeneData();
  },
  methods: {
    fetchGeneData() {
      const apiUrl = `http://localhost:3000/api/gene/xylitol`;
      axios.get(apiUrl)
        .then(response => {
          console.log("Complete response received:", response.data);
          this.keggRef = response.data.keggRef; // 直接使用 response.data.keggRef
          this.notFound = false;
        })
        .catch(error => {
          console.error('Error fetching gene details:', error);
          this.notFound = true;
        });
    }
  }
};
</script>


<style scoped>
.title-no-wrap {
  white-space: nowrap;
}

.main-table th {
  min-width: 120px; /* 这里的数值根据你的实际内容和设计需求进行调整 */
  white-space: nowrap; /* 防止内容换行 */
}
</style>

