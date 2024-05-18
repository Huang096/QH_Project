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
const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');

// eslint-disable-next-line import/extensions
const { getDoiDataFromDB } = require('./src/ExampleName/services/doiServices');
const { getGeneDataFromDB } = require('./src/ExampleName/services/doiServices');
const { getOrganismDataFromDB} = require('./src/ExampleName/services/doiServices');
const { getProductDataFromDB} = require('./src/ExampleName/services/doiServices')

// 创建 Express 应用实例
const app = express();

// 允许跨源资源共享
app.use(cors());

// 配置数据库连接池
const pool = new Pool({
  user: 'postgres',
  host: '34.41.142.156',
  database: 'qinghuadb',
  password: 'qinghua',
  port: 5432,
});

app.get('/api/doi/:id', async (req, res) => {
  try {
    const doi = decodeURIComponent(req.params.id);
    // console.log('Decoded DOI:', doi);
    const result = await getDoiDataFromDB(doi, pool);
    // console.log('Complete result:', result);
    if (result.article) {
      res.json(result);
    } else {
      res.status(404).json({ message: 'DOI not found' });
    }
  } catch (error) {
    console.error('Error fetching DOI details:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

app.get('/api/gene/:name', async (req, res) => {
  console.log('API /api/gene/:name called with name:', req.params.name); // 确认路由被调用
  try {
    const name = decodeURIComponent(req.params.name);
    console.log('Received GENE name:', name); // 输出解码后的名称
    const productDetail = await getGeneDataFromDB(name, pool);
    console.log('Gene Detail:', productDetail); // 输出获取的详情
    if (productDetail) {
      res.json(productDetail);
    } else {
      res.status(404).json({ message: 'Gene not found' });
    }
  } catch (error) {
    console.error('Error fetching gene details:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

app.get('/api/organism/:name', async (req, res) => {
  console.log('API /api/organism/:name called with name:', req.params.name); // 确认路由被调用
  try {
    const name = decodeURIComponent(req.params.name);
    console.log('Received ORGANISM name:', name); // 输出解码后的名称
    const organismDetail = await getOrganismDataFromDB(name, pool);
    console.log('Organism Detail:', organismDetail); // 输出获取的详情
    if (organismDetail) {
      res.json(organismDetail);
    } else {
      res.status(404).json({ message: 'Organism not found' });
    }
  } catch (error) {
    console.error('Error fetching organism details:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

app.get('/api/product/:name', async (req, res) => {
  console.log('API /api/product/:name called with name:', req.params.name); // 确认路由被调用
  try {
    const name = decodeURIComponent(req.params.name);
    console.log('Received product name:', name); // 输出解码后的名称
    const productDetail = await getProductDataFromDB(name, pool);
    console.log('Gene Detail:', productDetail); // 输出获取的详情
    if (productDetail) {
      res.json(productDetail);
    } else {
      res.status(404).json({ message: 'Product not found' });
    }
  } catch (error) {
    console.error('Error fetching product details:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});


// 设置监听端口
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
