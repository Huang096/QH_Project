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
        <article-card v-for="dataEntry in data" :key="dataEntry.id" :article-data="dataEntry"></article-card>

      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ArticleCard from './articleCard.vue';

export default {
  name: 'DetailsPage',
  components: {
    ArticleCard
  },
  data() {
    return {
      article: null,
      data: [],
      notFound: false,
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
            this.article = response.data.article;
            this.data = response.data.data;
          }else{
            this.notFound = true;
          }
        })
        .catch(error => {
          console.error('Error fetching article details:', error);
          this.notFound = true;
        });
    }
  }
};
</script>


<style lang="scss">
/* Your existing styles can go here */
</style>
