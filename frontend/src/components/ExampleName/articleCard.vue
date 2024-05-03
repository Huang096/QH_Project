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
    <div class = "card">
        <div class = "card-content">
            <div class = "content">
                <table class = "table is-fullwidth">
                    <tbody>
                        <tr>
                            <th>Strain:</th>
                            <td>{{ articleData.strain || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Strain Type:</th>
                            <td>{{ articleData.strain_type || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Product:</th>
                            <td>{{ articleData.product || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Product Tilter:</th>
                            <td>{{ articleData.product_tilter || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Carbon Source:</th>
                            <td>{{ articleData.carbon_source || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Carbon Source Concentration:</th>
                            <td>{{ articleData.carbon_source_concentration || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Vessel and Feed Mode:</th>
                            <td>{{ articleData.vessel_and_feed_mode || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>PH:</th>
                            <td>{{ articleData.ph || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Time:</th>
                            <td>{{ articleData.time || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Temperature:</th>
                            <td>{{ articleData.temperature || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Parent Strain:</th>
                            <td>{{ articleData.parent_strain || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Knock Out Gene:</th>
                            <td>{{ articleData.knock_out_gene || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Overexpress Gene:</th>
                            <td>{{ articleData.overexpress_gene || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Heterologous Gene:</th>
                            <td>{{ articleData.heterologous_gene || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Medium:</th>
                            <td>{{ articleData.medium || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>SMILES_in:</th>
                            <td>{{ articleData.SMILES_in || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Article Title:</th>
                            <td>{{ articleData.Article_Title || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Publication Year:</th>
                            <td>{{ articleData.Publication_Year || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Tilter Unit:</th>
                            <td>{{ articleData.titer_unit || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Tilter Value:</th>
                            <td>{{ articleData.titer_value || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>Standard Smiles:</th>
                            <td>{{ articleData.standard_smiles || 'NA' }}</td>
                        </tr>
                        <tr>
                            <th>SMILES_in:</th>
                            <td>{{ articleData.SMILES_in || 'NA' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
    export default{
        name: 'ArticleCard',
        props:{
            articleData:{
                type: Object,
                required: true
            }
        }
    }
</script>