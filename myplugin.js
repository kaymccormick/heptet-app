const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const {exec} = require('child_process');


class MyPlugin {
    constructor(options) {
        this.options = options;
    }


    apply(compiler) {

        exec('process_views --virtual -c development.ini', (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                return;
            }

            const entry = JSON.parse(stdout);

            this.entry = entry
            console.log("here");

        });

        const emit = (compilation, callback) => {
            // console.log("here");
            // for (var key in this.entry) {
            //     if (this.entry.hasOwnProperty(key)) {
            //         //this.addFileToAssets(this.entry[key].content, key, compilation)
            //     }
            // }
            //
            return callback()
        };

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
        var plugin = {name: 'MyPlugin'};
        compiler.hooks.beforeRun.tapAsync(plugin, beforeRun);
        compiler.hooks.emit.tapAsync(plugin, emit);
    }

    addFileToAssets(content, basename, compilation) {
        compilation.assets[basename] = {
            source: () => content,
            size: () => len(content)
        };
        return new Promise.resolve(basename);
    }

}

module.exports = MyPlugin;
