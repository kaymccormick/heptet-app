const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');

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
         filename: '../templates/layout2.html',
         template: 'src/assets/layout2.html'
     })
   ],
    output: {
	filename: '[name].bundle.js',
	path: path.resolve(__dirname, 'static')
    },
     module: {
     rules: [
           { parser: { amd: false } },
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
	 }
     ]
      
     }
}
;
