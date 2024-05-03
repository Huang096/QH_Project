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

const { Pool } = require('pg');
const { getDoiDataFromDB } = require('./doiServices'); // 确保路径正确
const { getGeneDataFromDB } = require('./doiServices');
const { getOrganismDataFromDB} = require('./doiServices');
const { getProductDataFromDB } = require('./doiServices');

// 配置 PostgreSQL 连接池
const pool = new Pool({
  user: 'postgres',
  host: '34.41.142.156',
  database: 'qinghuadb',
  password: 'qinghua',
  port: 5432,
});

async function testGetGeneData() {
  try {
    const productName = 'isopropanol'; // 使用一个已知存在于数据库的DOI
    const result = await getProductDataFromDB(productName, pool);
    console.log('Result:', result);
  } catch (error) {
    console.error('Failed to fetch DOI details:', error);
  }
}

testGetGeneData();
