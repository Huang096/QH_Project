// Copyright 2024 huangzheheng
// 
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// 
//     https://www.apache.org/licenses/LICENSE-2.0
// 
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

<template>
    <div class="card">
      <div class="card-content">
        <div class="content">
            <table class="table is-fullwidth">
                <tbody>
                    <tr v-for="(item, index) in leftColumn" :key="`left-${index}`">
                    <th>{{ item.label }}:</th>
                    <td>{{ item.value }}</td>
                    </tr>
                </tbody>
                <tbody>
                    <tr v-for="(item, index) in rightColumn" :key="`right-${index}`">
                    <th>{{ item.label }}:</th>
                    <td>{{ item.value }}</td>
                    </tr>
                </tbody>
            </table>

        </div>
      </div>
    </div>
  </template>
  

<script>
export default {
    name: 'ArticleCard',
    props: {
        articleData: {
            type: Object,
            required: true
        }
    },
    computed: {
        leftColumn() {
            // 获取所有键，然后选取前13个键形成左列
            return Object.entries(this.articleData)
            .slice(0, 13)
            .map(([key, value]) => ({
                label: this.formatLabel(key),
                value: value || 'NA'
            }));
        },
        rightColumn() {
            // 获取所有键，选取第14个键到第26个键形成右列
            return Object.entries(this.articleData)
            .slice(13)
            .map(([key, value]) => ({
                label: this.formatLabel(key),
                value: value || 'NA'
            }));
        }
    },
    methods: {
        formatLabel(key) {
            return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
    }

}
</script>

<style scoped>
.card {
    border: 2px solid #ccc;  /* 灰色粗边框 */
    box-shadow: 4px 4px 8px rgba(0, 0, 0, 0.1);  /* 轻微的阴影 */
    margin-bottom: 20px;  /* 每张卡片底部的间距 */
    background: white;  /* 白色背景 */
    border-radius: 20px;
}
.card-content {
    overflow-x: auto;
}

.table {
    width: 100%;
    display: table;
    table-layout: fixed;
    border-collapse: separate;
    border-spacing: 20px 0;
}
tbody {
    display: table-cell;
    vertical-align: top;
}

th, td {
    vertical-align: top;
    padding: 8px;
}

th {
    white-space: nowrap;
    width: 1%;
}
td {
    width: auto;
}
</style>
