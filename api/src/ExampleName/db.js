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

/*
const { Pool } = require('pg');

// 用你的数据库连接信息替换以下占位符

const pool = new Pool({
  user: 'postgres',
  host: '34.41.142.156',
  database: 'qinghuadb',
  password: 'qinghua',
  port: 5432,
});

app.get('/api/src/ExampleName/articleCard.js', async (req, res) => {
  try {
    const queryText = 'SELECT * FROM article_detail;'; // 获取所有文章详情
    const dbRes = await pool.query(queryText);
    res.json(dbRes.rows); // 发送查询结果作为响应
  } catch (err) {
    console.error('查询失败', err.stack);
    res.status(500).send('服务器错误');
  }
});

pool.query(queryText, (err, res) => {
  if (err) {
    console.error('查询失败', err.stack);
  } else {
    console.log('数据库中的表有：');
    res.rows.forEach(row => console.log(row.tablename));
  }
  pool.end(); // 关闭数据库连接
});
*/

const postgres = require('postgres');

const sql = postgres(
  `postgres://postgres:qinghua@34.41.142.156:5432/qinghuadb`
);

/*
async function testConnection() {
  try {
    // 执行一个简单的查询来测试连接
    const result = await sql`SELECT NOW() as current_time;`; // 获取当前时间
    // 也可以使用 SELECT 1 来测试
    // const result = await sql`SELECT 1;`;

    console.log('数据库连接成功，当前时间是:', result[0].current_time);
  } catch (error) {
    console.error('数据库连接测试失败:', error.message);
  }
}

testConnection();
*/
export default sql;