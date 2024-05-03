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
                doi (e.g.
                <router-link :to="`/exampleroute/doi/${encodeURIComponent('10.1016/j.ymben.2013.09.007')}`">10.1016/j.ymben.2013.09.007</router-link>
                )
              </li>
              <li>
                Gene (e.g.
                <router-link to="/exampleroute/gene/xylitol">xylitol</router-link>
                )
              </li>
              <li>
                Organism (e.g.
                <router-link to="/exampleroute/organism/TA1317">TA1317</router-link>
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
      errorMessage: ''
    };
  },
  created() {
    // 使用 debounce 减少搜索时的请求频率
    this.debouncedSearch = debounce(this.search, 300);
  },
  methods: {
    async search() {
      this.searching = true; // 开始搜索
      try {
        const response = await axios.get('/api/search', { params: { query: this.searchTerm } });
        this.searchResults = response.data; // 更新搜索结果
      } catch (error) {
        this.errorMessage = "搜索时发生错误"; // 设置错误消息
      } finally {
        this.searching = false; // 结束搜索
      }
    },
    async handleInputUpdate() {
      // 用户输入时触发搜索
      this.searching = true;
      await this.debouncedSearch();
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