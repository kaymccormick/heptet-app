const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const PugLoader = require('pug-loader');

module.exports = {
    mode: 'development',
    entry:
        {
            app: './src/index.js'
            //testcode: './src/testcode/index.js'
        },
    devtool: 'inline-source-map',
    plugins: [
        new HtmlWebpackPlugin({
            title: 'Output Management',
            template: 'src/assets/layout2.html',
            // output this layout2 template
            filename: '../templates/layout2.jinja2',
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
            {parser: {amd: false}},
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
        ]

    }
}

;
