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
const context = path.resolve(__dirname, "src");
const plugins = [
    new AppPlugin({app: app, context}),
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery'
    }),
];

const commonConfig = {
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

module.exports = new Promise((resolve, reject) => {
    app.get_entry_points().then(entry_points => {
        const entry = Object.create(null);
        for(var i = 0; i < entry_points.length; i++) {
            entry[entry_points[i].key] = entry_points[i].fspath;
        }
        resolve(merge(commonConfig, { entry }));
    }).catch(reject);
});
