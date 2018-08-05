const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const PugLoader = require('pug-loader');
const webpack = require('webpack');

module.exports = {
    mode: 'development',
    entry:
        {
            app: './src/index.js',
            domainList: './src/domain_list.js'
            //testcode: './src/testcode/index.js'
        },
    devtool: 'inline-source-map',
    plugins: [
        // new webpack.ProvidePlugin({
        //     $: "jquery",
        //     jQuery: "jquery",
        //     'window.jQuery': 'jquery',
        //     'window.$': 'jquery'
        // }),
        new HtmlWebpackPlugin({
            title: '',
            template: 'src/assets/main_layout.html',
            filename: path.resolve(__dirname, 'build/templates/main_layout.jinja2'),
            chunks: ['app'],
            inject: false
        })
        ,
        new HtmlWebpackPlugin({
            title: '',
            template: 'src/assets/domain_list_layout.html',
            filename: path.resolve(__dirname, 'build/templates/domain_list_layout.jinja2'),
            inject: false
        })
    ],
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'build/dist'),
        publicPath: '../dist/',
    },
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
                    'css-loader'
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
}

;
