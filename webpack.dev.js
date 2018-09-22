/* Webpack configuration - dev */

const path = require('path');
const merge = require('webpack-merge');
const common = require('./webpack.common.js');
//const app = require('app.js')
const entry = require('./entry_point')

module.exports = merge(common, {
    mode: 'development', // https://webpack.js.org/concepts/mode/
    devtool: 'inline-source-map',
    output: {
        filename: '[name].js',
        // output things to here so they become part of our dist
        path: path.resolve(__dirname, 'email_mgmt_app/build/dist'),
        publicPath: '/build/dist',
    },
    entry,

    devServer: {
        proxy: {
            "/app": {
                target: 'http://localhost:6543',
                pathRewrite: {'^/app': ''}
            }
        }
    }
});

