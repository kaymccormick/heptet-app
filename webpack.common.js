/* Webpack configuration - common */

const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin')
const AppPlugin = require('./js/AppPlugin')
const App = require('./js/App');
const webpack = require('webpack')
const merge = require('webpack-merge');

const app = new App({});
const context = __dirname
const plugins = [
    new AppPlugin({context}, app),
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery'
    }),
];

const commonConfig = {
    resolve: {modules: ['.', 'node_modules']},
    plugins,
    node: {
        fs: "empty" // avoids error messages
    },
    module: {
        rules: [
            //{parser: {amd: false}},
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader',
                    'postcss-loader',
                ]
            },
            {
                test: /\.(png|svg|jpe?g|gif)$/,
                use: [
                    'file-loader'
                ]

            }
        ]

    }
};

module.exports =
    Promise.all([
        Promise.resolve(commonConfig),
        app.get_entry_points().then(entry_points => {
            const entry = Object.create(null);
            for (const ep of entry_points) {
                entry[ep.key] = ep.fspath;
            }
            return {entry};
        })]).then(configs => merge(...configs));

