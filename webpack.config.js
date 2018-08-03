const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const PugLoader = require('pug-loader');
const webpack = require('webpack');

function p(compilation, assets, options) {
    return {
        compilation: compilation,
        webpack: compilation.getStats().toJson(),
        webpackConfig: compilation.options,
        htmlWebpackPlugin: {
            files: assets,
            options: options
        },
        'mine': {'extends_temlate_filename': 'layout2.jinja'}

    };
}


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
            title: 'Output Management',
            template: 'src/assets/layout2.html',
            // output this layout2 template
            filename: '../templates/main_template.jinja2',
//                templateParameters: p,
            chunks: ['app'],
            inject: false
        })
        ,
        new HtmlWebpackPlugin({
            title: 'Output Management',
            template: 'src/assets/domain_list_layout.html',
            filename: '../templates/domain_list_layout.jinja2',
            // output this layout2 template
//               templateParameters: function() { x = p(a, b, c); x.data = { extends: 'layout2.jinja2' }; return x; },
            inject: false
        })
    ],
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'email_mgmt_app/static')
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
