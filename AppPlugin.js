const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const {exec, spawn} = require('child_process');
const AppEntryPlugin = require('./AppEntryPlugin');
const AppVirtualFileSystem = require('./AppVirtualFileSystem');
const VirtualPlugin = require('./VirtualPlugin');
const request = require('request');

const axios = require('axios');

const {
    NodeJsInputFileSystem,
    CachedInputFileSystem,
    ResolverFactory
} = require('enhanced-resolve');

class AppPlugin {
    constructor(options) {
        this.options = options;
    }

    apply(compiler) {
        const me = this;

        // exec('venv/scripts/pserve.cmd', 'development.ini', (err, stdout, stderr) => {
        //     console.log(err);
        //     });
        //this.process_child = spawn('venv/scripts/pserve.cmd', ['development.ini']);

        // this.process_child = spwan('venv/scripts/process_views',['--virtual','-c','development.ini', '--pipe']);
        // #this.process_child.stdin.write('entry_points_json')
        //
        //
        //
        // exec('process_views --virtual -c development.ini', (error, stdout, stderr) => {
        //     if (error) {
        //         console.error(`exec error: ${error}`);
        //         return;
        //     }
        //
        //     const entry = JSON.parse(stdout);
        //
        //     this.entry = entry;
        //
        // });
        const entryOption = (context, entry) => {
            return new Promise(function (resolve, reject) {
                axios.get('http://localhost:6643/entry_points_json', {
                    transform_response: function (response) {
                        return JSON.parse(response);
                    }
                }).then(function (data) {
                    const entry_points = data.data.entry_points;
                    for (let i = 0; i < entry_points.length; i++) {
                        const ep = entry_points[i];
                        console.log(ep);
                        new AppEntryPlugin(context, compiler.resolverFactory, ep.fspath, ep.key).apply(compiler)
                    }
                    me.entry_points = entry_points;
                    resolve()
                });
            });

            // const ep = this.options.entry_points;
            // for (var key in ep) {
            //     if (ep.hasOwnProperty(key)) {
            //         new AppEntryPlugin(context, 'app_entry_point:' + key, key).apply(compiler);
            //     }
            // }
            // return true;
        };

        const emit = (compilation, callback) => {
            const entry_points = me.entry_points;
            for (let i = 0; i < entry_points.length; i++) {
                const ep = entry_points[i];
                this.addFileToAssets(ep.content, ep.key, compilation)
                const h = new HtmlWebpackPlugin({
                    title: '',
                    template: 'src/assets/entry_point_generic.html',
                    filename: path.resolve(__dirname, 'email_mgmt_app/build/templates/entry_point/' + key + '.jinja2'),
                    inject: false,
                    chunks: [key],
                });
                h.apply(compiler);
            }
            return callback()
        };

        // const beforeRun = (compiler, callback) => {
        // }
        //
        // const beforeCompile = (compiler, callback) => {
        // }

        //
        // let context;
        var plugin = {name: 'AppPlugin'};
        compiler.hooks.normalModuleFactory.tap(plugin, nmf => {
            nmf.hooks.beforeResolve.tap(plugin, result => {
                if (!result) return;
                return result;
            });
        });
        //compiler.hooks.beforeRun.tapAsync(plugin, beforeRun);
        compiler.hooks.emit.tapAsync(plugin, emit);

        compiler.hooks.entryOption.tap(plugin, entryOption);
        compiler.hooks.afterResolvers.tap(plugin, compiler => {
            compiler.resolverFactory.hooks.resolver.for("normal").tap(plugin, resolver => {
                console.log("making virtual plugin");
                new VirtualPlugin("described-resolve", {entry_points: this.options.entry_points}, "resolve").apply(resolver);
            })
        })
        //compiler.hooks.beforeCompile.tap(plugin, beforeCompile);
        //compiler.hooks.done.tap(plugin, done);

    }

    addFileToAssets(content, basename, compilation) {
        compilation.assets[basename] = {
            source: () => content,
            size: () => content.length,
        };
        return Promise.resolve(basename);
    }

}

module
    .exports = AppPlugin;
