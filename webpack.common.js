/* Webpack configuration - common */

const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin')
const AppEntryPlugin = require('./AppEntryPlugin');

const {
    NodeJsInputFileSystem,
    CachedInputFileSystem,
    ResolverFactory
} = require('enhanced-resolve');

const webpack = require('webpack')
const AppPlugin = require('./AppPlugin')

const entry_points = require('./entry_point')
const my_plugin = new AppPlugin({entry_points})
const plugins = [
    my_plugin,
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery'
    }),
];

module.exports = {
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

            },
            {
                test: /\.pug$/,
                use: ['pug-loader']
            }
            ,
            {
                test: /\.twig$/,
                loader: "twig-loader",
                options: {
                    // See options section below
                },
            }
            ,

        ]

    }

};

