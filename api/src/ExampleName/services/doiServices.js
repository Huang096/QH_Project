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

// 定义获取基因详细信息的函数
async function getDoiDataFromDB(doiId, pool) {
    try {
        const articleQuery = 'SELECT * FROM article_detail WHERE TRIM(doi) = TRIM($1)';
        const articleResults = await pool.query(articleQuery, [doiId]);

        // 查询第二个表，可能返回多条记录
        const dataQuery = 'SELECT * FROM data WHERE TRIM(doi) = TRIM($1)';
        const dataResults = await pool.query(dataQuery, [doiId]);

        // 组合结果
        const article = articleResults.rows[0]; // 取第一条记录
        const articleData = dataResults.rows; // 取所有匹配的记录

        // console.log("Article data:", article);
        // console.log("Article additional data:", articleData);

        return {
            article,
            data: articleData
        };
    } catch (err) {
        console.error('Error executing query', err.stack);
        throw err; // 传递错误以便可以进一步处理
    }
}

async function getGeneDataFromDB(productName, pool) {
    try {
        const articleQuery = 'SELECT * FROM crossRef WHERE TRIM(product) = TRIM($1)';
        const articleResults = await pool.query(articleQuery, [productName]);

        // 查询第二个表，可能返回多条记录
        const dataQuery = 'SELECT * FROM data WHERE TRIM(doi) = TRIM($1)';
        const dataResults = await pool.query(dataQuery, [productName]);

        // 组合结果
        const keggRef = articleResults.rows[0]; // 取第一条记录
        const refInfo = dataResults.rows; // 取所有匹配的记录

        // console.log("Article data:", article);
        // console.log("Article additional data:", articleData);

        return {
            keggRef,
            data: refInfo
        };
    } catch (err) {
        console.error('Error executing query', err.stack);
        throw err; // 传递错误以便可以进一步处理
    }
}

async function getOrganismDataFromDB(orgName, pool) {
    try {
        const organismQuery = 'SELECT * FROM orginfo WHERE TRIM(organism) = TRIM($1)';
        const organismResults = await pool.query(organismQuery, [orgName]);

        const dataQuery = 'SELECT * FROM data WHERE TRIM(organism) = TRIM($1)';
        const dataResults = await pool.query(dataQuery, [orgName]);

        console.log('Organism Results:', organismResults.rows);
        console.log('Data Results:', dataResults.rows);

        // 组合结果
        const orgInfo = organismResults.rows[0]; // 取第一条记录
        const orgData = dataResults.rows;

        return {
          orgInfo,
          data: orgData,
        };
    } catch (err) {
        console.error('Error executing query', err.stack);
        throw err; // 传递错误以便可以进一步处理
    }
}

async function getProductDataFromDB(productName, pool) {
    try {
        const productQuery = 'SELECT * FROM productinfo WHERE TRIM(product) = TRIM($1)';
        const productResults = await pool.query(productQuery, [productName]);

        const dataQuery = 'SELECT * FROM data WHERE TRIM(product) = TRIM($1)';
        const dataResults = await pool.query(dataQuery, [productName]);

        // 组合结果
        const productInfo = productResults.rows[0]; // 取第一条记录
        const productData = dataResults.rows;

        return {
          productInfo,
          data: productData,
        };
    } catch (err) {
        console.error('Error executing query', err.stack);
        throw err; // 传递错误以便可以进一步处理
    }
}

module.exports = {
    getDoiDataFromDB,
    getGeneDataFromDB,
    getOrganismDataFromDB,
    getProductDataFromDB
};
