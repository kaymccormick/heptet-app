/* Webpack configuration - common */

const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin')

module.exports = {
    plugins: [
//        new CleanWebpackPlugin(['email_mgmt_app/build/dist']),
        new CopyWebpackPlugin([
            {
                from: 'src/__init__.py',
                to: path.resolve
                (__dirname, 'email_mgmt_app/build/templates/__init__.py')
            },
            {
                from: 'src/__init__.py',
                to: path.resolve
                (__dirname, 'email_mgmt_app/build/__init__.py')
            }
        ]),
        new HtmlWebpackPlugin({
            title: '',
            template: 'src/assets/main_layout.html',
            filename: path.resolve(__dirname, 'email_mgmt_app/build/templates/main_layout.jinja2'),
            chunks: ['app'],
            inject: false
        })
        ,
        new HtmlWebpackPlugin({
            title: '',
            template: 'src/assets/domain_list_layout.html',
            filename: path.resolve(__dirname, 'email_mgmt_app/build/templates/domain_list_layout.jinja2'),
            inject: false
        })
    ],
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

};

