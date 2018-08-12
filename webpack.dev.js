/* Webpack configuration - dev */

const path = require('path');
const merge = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'development', // https://webpack.js.org/concepts/mode/
    devtool: 'inline-source-map',
    output: {
        filename: '[name].[contenthash].js',
        // output things to here so they become part of our dist
        path: path.resolve(__dirname, 'email_mgmt_app/build/dist'),
        publicPath: '/build/dist',
    },
    entry: {
        app: './src/index.prod.js',
        domainList: './src/domain_list.js'
    },
    devServer: {
        contentBase: './dist'
    }
});
