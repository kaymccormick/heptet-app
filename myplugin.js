const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin');

class MyPlugin {
    constructor(options) {
	this.options = options;
    }

    apply(compiler) {
        // console.log("i like food");
        const beforeRun = (compiler, callback) => {
            const ep = this.options.entry_points;
            for (var key in ep) {

                if (ep.hasOwnProperty(key)) {
                    const h = new HtmlWebpackPlugin({
                        title: '',
                        template: 'src/assets/entry_point_generic.html',
                        filename: path.resolve(__dirname, 'email_mgmt_app/build/templates/entry_point/' + key + '.jinja2'),
                        inject: false,
                        chunks: [key],
                    });
                    h.apply(compiler);
                }
            }
            return callback();
        };
        //
        // let context;
        var plugin = { name: 'MyPlugin' };
        compiler.hooks.beforeRun.tapAsync(plugin, beforeRun);
    }
}
module.exports = MyPlugin;
