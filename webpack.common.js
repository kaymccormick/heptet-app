/* Webpack configuration - common */

const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin')
const AppEntryPlugin = require('./AppEntryPlugin');

const webpack = require('webpack')
const AppPlugin = require('./AppPlugin')

const entry_points = require('./entry_point')
const context =  path.resolve(__dirname, "src");
const plugins = [
    new AppPlugin({entry_points, context }),
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery'
    }),
];

module.exports = {
    //entry: entry_points,
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
