const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const {exec, spawn} = require('child_process');
const AppEntryPlugin = require('./AppEntryPlugin')
const AppVirtualFileSystem = require('./AppVirtualFileSystem')
const VirtualPlugin = require('./VirtualPlugin')
const {
    NodeJsInputFileSystem,
    CachedInputFileSystem,
    ResolverFactory
} = require('enhanced-resolve');


// create a resolver
const myResolver = ResolverFactory.createResolver({
    // Typical usage will consume the `NodeJsInputFileSystem` + `CachedInputFileSystem`, which wraps the Node.js `fs` wrapper to add resilience + caching.
    fileSystem: new AppVirtualFileSystem(),
    extensions: ['.js', '.json']
    /* any other resolver options here. Options/defaults can be seen below */
});


class AppPlugin {
    constructor(options) {
        this.options = options;
    }

    apply(compiler) {
        spwan()

        exec('process_views --virtual -c development.ini', (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                return;
            }

            const entry = JSON.parse(stdout);

            this.entry = entry;

        });

        const emit = (compilation, callback) => {
            for (var key in this.entry) {
                if (this.entry.hasOwnProperty(key)) {
                    this.addFileToAssets(this.entry[key].content, key, compilation)
                }
            }

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
        var plugin = {name: 'AppPlugin'};
        compiler.hooks.normalModuleFactory.tap(plugin, nmf => {
            nmf.hooks.beforeResolve.tap(plugin, result => {
                if (!result) return;
                console.log("result is ", result);
                return result;
            });
        });
        //         new VirtualPlugin("resolve", {}, "parsed-resolve").apply()
        //
        //         console.log(result.request);
        //     });
        // });
        compiler.hooks.beforeRun.tapAsync(plugin, beforeRun);
        compiler.hooks.emit.tapAsync(plugin, emit);
        compiler.hooks.entryOption.tap(plugin, (context, entry) => {
            const ep = this.options.entry_points;
            for (var key in ep) {
                if (ep.hasOwnProperty(key)) {
                    new AppEntryPlugin(context, 'app_entry_point:' + key, key).apply(compiler);
                }
            }
            return true;
        });
        compiler.hooks.afterResolvers.tap(plugin, compiler => {
            compiler.resolverFactory.hooks.resolver.for("normal").tap(plugin, resolver => {
                console.log("making virtual plugin");
                new VirtualPlugin("described-resolve", {entry_points: this.options.entry_points}, "resolve").apply(resolver);
            })
        })

    }

    addFileToAssets(content, basename, compilation) {
        compilation.assets[basename] = {
            source: () => content,
            size: () => content.length,
        };
        return Promise.resolve(basename);
    }

}

module.exports = AppPlugin;