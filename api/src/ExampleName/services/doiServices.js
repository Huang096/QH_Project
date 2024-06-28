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
async function getDoiDataFromDB(pmid, pool) {
  try {
    const pmidQuery = 'SELECT doi FROM doitopmid WHERE TRIM(pmid) = TRIM($1)';
    const pmidResults = await pool.query(pmidQuery, [pmid]);

    if (pmidResults.rows.length === 0) {
      throw new Error('No matching DOI found for the given PMID');
    }

    const doiId = pmidResults.rows[0].doi;

    const articleQuery =
      'SELECT * FROM article_detail WHERE TRIM(doi) = TRIM($1)';
    const articleResults = await pool.query(articleQuery, [doiId]);

    // 查询第二个表，可能返回多条记录
    const dataQuery = 'SELECT * FROM data WHERE TRIM(doi) = TRIM($1)';
    const dataResults = await pool.query(dataQuery, [doiId]);

    // 组合结果
    const article = articleResults.rows[0]; // 取第一条记录
    const articleData = dataResults.rows; // 取所有匹配的记录

    // console.log("Article data:", article);
    // console.log("Article additional data:", articleData);

    console.log({
      pmid,
      article,
      data: articleData,
    });

    return {
      pmid,
      article,
      data: articleData,
    };
  } catch (err) {
    console.error('Error executing query', err.stack);
    throw err; // 传递错误以便可以进一步处理
  }
}

async function getGeneDataFromDB(searchInput, pool) {
  try {
    // 从 crossRef 表中根据 kegg 列查找
    const crossRefQuery = `SELECT * FROM crossRef WHERE TRIM(kegg) ILIKE TRIM(LOWER($1));`;
    const crossRefResults = await pool.query(crossRefQuery, [
      `%${searchInput}%`,
    ]);

    let dataResults = { rows: [] };
    // 如果从 crossRef 表中找到数据，则查询 data 表中的详细基因信息
    if (crossRefResults.rows.length > 0) {
      const { kegg } = crossRefResults.rows[0]; // 假设 kegg 字段也存在于 data 表中且作为连接键
      const dataQuery = `
                SELECT * FROM data
                WHERE
                    TRIM(knock_out_gene) ILIKE TRIM(LOWER($1)) OR
                    TRIM(overexpress_gene) ILIKE TRIM(LOWER($1)) OR
                    TRIM(heterologous_gene) ILIKE TRIM(LOWER($1));
            `;
      dataResults = await pool.query(dataQuery, [`%${kegg}%`]); // 模糊查找基于 kegg
    }

    // 查询 doitopmid 表以获取 pmid
    const pmidQuery = `SELECT doi, pmid FROM doitopmid WHERE doi IN (${dataResults.rows
      .map(row => `'${row.doi}'`)
      .join(',')})`;
    const pmidResults = await pool.query(pmidQuery);

    // 创建一个 doi 到 pmid 的映射
    const doiToPmidMap = {};
    pmidResults.rows.forEach(row => {
      doiToPmidMap[row.doi] = row.pmid;
    });

    // 组合结果
    const geneInfo = crossRefResults.rows[0]; // 取第一条记录，假设它包含你需要的所有字段
    const refData = dataResults.rows.map(row => ({
      ...row,
      doi: doiToPmidMap[row.doi] || 'NA', // 将 doi 替换为 pmid，如果找不到 pmid，则保持原来的 doi
    }));

    return {
      geneInfo,
      data: refData,
    };
  } catch (err) {
    console.error('Error executing query', err.stack);
    throw err; // 传递错误以便可以进一步处理
  }
}

async function getOrganismDataFromDB(orgName, pool) {
  try {
    const organismQuery =
      'SELECT * FROM orginfo WHERE LOWER(organism) = TRIM(LOWER($1));';
    const organismResults = await pool.query(organismQuery, [orgName]);

    const dataQuery = 'SELECT * FROM data WHERE TRIM(strain) = TRIM($1)';
    const dataResults = await pool.query(dataQuery, [orgName]);

    // 查询 doitopmid 表以获取 pmid
    const pmidQuery = `SELECT doi, pmid FROM doitopmid WHERE doi IN (${dataResults.rows
      .map(row => `'${row.doi}'`)
      .join(',')})`;
    const pmidResults = await pool.query(pmidQuery);

    // 创建一个 doi 到 pmid 的映射
    const doiToPmidMap = {};
    pmidResults.rows.forEach(row => {
      doiToPmidMap[row.doi] = row.pmid;
    });

    // 组合结果
    const orgInfo = organismResults.rows[0]; // 取第一条记录
    const orgData = dataResults.rows.map(row => ({
      ...row,
      doi: doiToPmidMap[row.doi] || row.doi, // 将 doi 替换为 pmid，如果找不到 pmid，则保持原来的 doi
    }));

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
    const productQuery =
      'SELECT * FROM productinfo WHERE TRIM(product) = TRIM($1)';
    const productResults = await pool.query(productQuery, [productName]);

    const dataQuery = 'SELECT * FROM data WHERE TRIM(product) = TRIM($1)';
    const dataResults = await pool.query(dataQuery, [productName]);

    // 查询 doitopmid 表以获取 pmid
    const pmidQuery = `SELECT doi, pmid FROM doitopmid WHERE doi IN (${dataResults.rows
      .map(row => `'${row.doi}'`)
      .join(',')})`;
    const pmidResults = await pool.query(pmidQuery);

    // 创建一个 doi 到 pmid 的映射
    const doiToPmidMap = {};
    pmidResults.rows.forEach(row => {
      doiToPmidMap[row.doi] = row.pmid;
    });

    // 组合结果
    const productInfo = productResults.rows[0]; // 取第一条记录
    const productData = dataResults.rows.map(row => ({
      ...row,
      doi: doiToPmidMap[row.doi] || row.doi, // 将 doi 替换为 pmid，如果找不到 pmid，则保持原来的 doi
    }));

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
