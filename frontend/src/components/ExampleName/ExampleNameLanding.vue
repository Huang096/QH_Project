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
  <div class="extended-section">
    <section class="hero is-primary is-bold py-6">
      <div class="hero-body has-text-centered">
        <p class="is-size-1 title">Name of Database</p>
        <p class="is-size-5">A sentence that could describe the database well</p>
      </div>
    </section>
    <ErrorPanel :message="errorMessage" :hide-error-panel="hideErrorMessage" />
    <div class="section container is-fullhd">
      <div class="columns is-centered pt-6">
        <div
          class="column is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile control"
        >
          <div>
            <p class="control has-icons-right has-icons-left">
              <input
                v-model="searchTerm"
                data-hj-whitelist
                class="input"
                type="text"
                placeholder="search (for genes, please provide the exact KEGG ID)"
                @input="handleInputUpdate()"
                @keyup="handleKeyUp($event)"
              />
              <span class="icon is-medium is-left">
                <i class="fa fa-search is-primary"></i>
              </span>
            </p>
            <div v-if="searchTerm.length > 0" id="quick-search-results" class="is-block">
              <div v-if="searching" class="has-text-centered">
                <a class="button is-primary is-inverted is-outlined is-loading my-1" />
              </div>
              <div v-else>
                <div v-if="searchResults.length === 0" class="p-3">
                  {{ messages.searchNoResult }} for
                  <b>
                    <i>{{ searchTerm }}</i> </b
                  >.
                </div>
                <ul v-else>
                  <li v-for="(r, i) in searchResults" :key="i">
                    <router-link
                      :to="`/gotenzymes/${r.type}/${r.id}`"
                      class="is-flex is-justify-content-space-between px-3 py-2"
                    >
                      <search-highlighter
                        v-if="r.id === r.match"
                        :match-term="r.id"
                        :search-term="searchTerm"
                      />
                      <span v-else>
                        {{ r.id }}
                        <span class="ml-2 is-size-7 is-italic">
                          <search-highlighter :match-term="r.match" :search-term="searchTerm" />
                        </span>
                      </span>
                      <span class="tag is-link is-light">{{ r.type }}</span>
                    </router-link>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="columns is-centered pb-6">
        <div class="column is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile">
          <div class="content">
            <h5 class="title is-5">One can search for a:</h5>
            <ul>
              <li>
                Pmid (e.g.
                <router-link :to="`/exampleroute/pmid/${encodeURIComponent('35350620')}`">35350620</router-link>
                )
              </li>
              <li>
                Gene (e.g.
                <router-link to="/exampleroute/gene/bpr">bpr</router-link>
                )
              </li>
              <li>
                Organism (e.g.
                <router-link to="/exampleroute/organism/HA01">HA01</router-link>
                )
              </li>
              <li>
                Product (e.g.
                <router-link to="/exampleroute/product/isopropanol">Isopropanol</router-link>
                )
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { debounce } from 'vue-debounce';
import SearchHighlighter from '@/components/shared/SearchHighlighter.vue';
import TableOfContents from '@/components/shared/TableOfContents.vue';
import { default as messages } from '@/content/messages';
import Citation from '@/components/about/Citation.vue';
import { default as allCitations } from '@/content/citations';
import ErrorPanel from '@/components/shared/ErrorPanel.vue';
import router from '@/router';
import axios from 'axios';

export default {
  name: 'ExampleNameLandingPage',
  components: {
    SearchHighlighter,
    TableOfContents,
    Citation,
    ErrorPanel,
  },
  data() {
    return {
      searchTerm: '',
      searching: false,
      searchResults: [], // 假设搜索结果是一个对象数组，根据实际情况调整
      errorMessage: '',
      debouncedTimer: null
    };
  },
  methods: {

    isPmid(input) {
      const pmidPattern = /^\d{8}$/;
      return pmidPattern.test(input);
    },

    async isProduct(productName) {
      try {
        const response = await axios.get(`http://localhost:3000/api/product/${encodeURIComponent(productName)}`);
        return response.data && response.data.productInfo; // 检查返回的对象是否包含产品信息
      } catch (error) {
        console.error('Error checking if product:', error);
        return false;
      }
    },

    async isOrganism(productName) {
      try {
        const response = await axios.get(`http://localhost:3000/api/organism/${encodeURIComponent(productName)}`);
        return response.data && response.data.orgInfo; // 检查返回的对象是否包含产品信息
      } catch (error) {
        console.error('Error checking if product:', error);
        return false;
      }
    },

    async isGene(geneName) {
      try {
        const response = await axios.get(`http://localhost:3000/api/gene/${encodeURIComponent(geneName)}`);
        return response.data && response.data.geneInfo; // 检查返回的对象是否包含基因信息
      } catch (error) {
        console.error('Error checking if gene:', error);
        return false;
      }
    },

    handleInputUpdate() {
      clearTimeout(this.debouncedTimer);  // 清除之前的计时器
      this.debouncedTimer = setTimeout(() => {
        this.executeSearch();  // 延迟执行
      }, 2000);  // 2秒无新输入时执行
    },

    handleKeyUp(event) {
      if (event.keyCode === 13) {  // 按下回车键
        clearTimeout(this.debouncedTimer);  // 清除防抖计时器
        this.executeSearch();  // 立即执行搜索
      }
    },

    async executeSearch() {
      // console.log('handleInputUpdate called with:', this.searchTerm);
      if (this.isPmid(this.searchTerm)) {
        router.push(`/exampleroute/pmid/${encodeURIComponent(this.searchTerm)}`);
      }
      else if (await this.isProduct(this.searchTerm)) {
        router.push(`/exampleroute/product/${encodeURIComponent(this.searchTerm)}`);
      }
      else if (await this.isOrganism(this.searchTerm)) {
        router.push(`/exampleroute/organism/${encodeURIComponent(this.searchTerm)}`);
      }
      else if (await this.isGene(this.searchTerm)){
        router.push(`/exampleroute/gene/${encodeURIComponent(this.searchTerm)}`);
      }
      else {
        // 这里处理非 DOI 输入的逻辑，例如显示消息或进行其他类型的搜索
        this.errorMessage = "请输入 Pmid 或进行其他类型的查询";
        // 可以在这里设置一个标志来显示错误或信息
      }
    },
  },
};
</script>

<style lang="scss" scoped>
#quick-search-results {
  border-bottom-left-radius: 3px;
  border-bottom-right-radius: 3px;
  box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%), 0 0 0 1px rgb(10 10 10 / 2%);

  li {
    cursor: pointer;

    &:hover {
      background: $white-bis;
    }

    &:not(:last-child) {
      border-bottom: 1px solid $white-ter;
    }
  }
}
</style>
