/* Webpack configuration - common */

const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin')
const webpack = require('webpack')
const MyPlugin = require('./myplugin')


entry_points = require('./entry_point')
my_plugin = new MyPlugin({entry_points})
plugins_ = [
    my_plugin,
    //  new MyPlugin({}),
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
        },
        {
            from: 'src/assets/manifest.json',
            to: path.resolve
            (__dirname, 'email_mgmt_app/build/manifest.json')
        }
    ]),
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery'
    }),
]

// for (var key in entry_points) {
//     if (entry_points.hasOwnProperty(key)) {
//         html_ =
//             // all of this data can be supplied by entry point
//             // if we wish!
//             new HtmlWebpackPlugin({
//                 title: '',
//                 template: 'src/assets/entry_point_generic.html',
//                 filename: path.resolve(__dirname, 'email_mgmt_app/build/templates/entry_point/' + key + '.jinja2'),
//                 inject: false,
//                 chunks: [key],
//             })
//         plugins_.push(html_)
//     }
// }
// console.log(html_)
module.exports = {
    plugins: plugins_,
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

