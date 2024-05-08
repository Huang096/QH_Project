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
const { getProductDataFromDB } = require('./services/doiServices'); // 确保路径正确

const router = express.Router();

router.get('/product/:name', async (req, res) => {
  try {
    const name = decodeURIComponent(req.params.name);
    console.log('Received GENE:', req.params.name); // 查看原始接收的DOI
    const productDetail = await getProductDataFromDB(name);
    console.log('Article Detail:', productDetail); // 打印查询结果
    if (productDetail) {
      res.json(productDetail);
    } else {
      res.status(404).send('DOI not found');
    }
  } catch (error) {
    console.error('Error fetching GENE details:', error);
    res.status(500).send('Internal server error');
  }
});

module.exports = router;