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
            <p><span class="is-block">Probably there is a typo in the identifier in the URL.</span></p>
          </div>
        </div>
      </div>
      <div v-else-if="articleInfo">
        <h3 class="title is-3">DOI:  {{ articleInfo.doi }}</h3>
        <div class="columns">
          <div class="table-template column is-8-desktop">
            <div class="table-container">
              <table class="table main-table is-fullwidth">
                <tr v-for="(value, key) in articleInfo" :key="key">
                  <td class="td-key has-background-primary has-text-white-bis is-capitalized">
                    {{ key.replace('_', ' ') }}
                  </td>
                  <td>{{ value }}</td>
                </tr>
              </table>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <p>Loading...</p>
      </div>
    </div>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  name: 'DetailsPage',
  data() {
    return {
      articleInfo: null, // Will hold the dynamic data once it's fetched
      notFound: false,
    };
  },
  created() {
    this.fetchArticleData();
  },
  methods: {
    fetchArticleData() {
      const encodedDoi = encodeURIComponent(this.$route.params.doi);
      const apiUrl = `http://localhost:3000/api/doi/${encodedDoi}`;
      axios.get(apiUrl)
        .then(response => {
          console.log('Received data:', response.data);  // 查看接收到的数据
          this.articleInfo = response.data;
          this.notFound = false;
        })
        .catch(error => {
          console.error('Error fetching article details:', error);
          this.notFound = true;
        });
    }
  }
};
</script>
