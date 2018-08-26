/* Webpack configuration - dev */

const path = require('path');
const merge = require('webpack-merge');
const common = require('./webpack.common.js');
entry_points = require('./entry_points')

entry_ = {}
for(i = 0; i < entry_points.list.length; i++) {
    ep = entry_points.list[i]
    entry_[ep] = './src/entry_point/' + ep + '.js'
}


module.exports = merge(common, {
    mode: 'development', // https://webpack.js.org/concepts/mode/
    devtool: 'inline-source-map',
    output: {
        filename: '[name].[contenthash].js',
        // output things to here so they become part of our dist
        path: path.resolve(__dirname, 'email_mgmt_app/build/dist'),
        publicPath: '/build/dist',
    },
    entry: entry_,

    devServer: {
        contentBase: './dist'
    }
});
