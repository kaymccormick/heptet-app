/* Webpack configuration - prod */

const path = require('path');
const merge = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'production',
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'build/dist'),
        publicPath: 'https://mnt.heptet.us/dist/',
    },
        entry: {
        app: './src/index.prod.js',
        domainList: './src/domain_list.prod.js'},

});

