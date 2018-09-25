const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const {exec, spawn} = require('child_process');
const AppEntryPlugin = require('./AppEntryPlugin');
const AppVirtualFileSystem = require('./AppVirtualFileSystem');
const VirtualPlugin = require('./VirtualPlugin');
const request = require('request');

const axios = require('axios');
const App = require('./App');

const {
    NodeJsInputFileSystem,
    CachedInputFileSystem,
    ResolverFactory
} = require('enhanced-resolve');

class AppPlugin {
    constructor(options) {
        this.options = options;
        this.app = new App();
    }

    apply(compiler) {
        const me = this;

        const entryOption = (context, entry) => {
            console.log("in entry option");
            const entry_points = me.entry_points;
            if (entry_points) {

                for (let i = 0; i < entry_points.length; i++) {
                    const ep = entry_points[i];
                    new AppEntryPlugin(context, compiler.resolverFactory, ep.fspath, ep.key).apply(compiler)
                }
            }
            console.log("setting me entry points");
        };

        const make = (compilation, callback) => {
            return this.app.get_entry_points().then(entry_points => {
                console.log("ep is ", entry_points);
                for (let i = 0; i < entry_points.length; i++) {
                    const ep = entry_points[i];
                    appPlugin.addFileToAssets(ep.content, ep.key, compilation)
                }
            }).then(callback());
        };

        const appPlugin = this;
        const emit = (compilation, callback) => {
            return this.app.get_entry_points().then(entry_points => {
                console.log("ep is ", entry_points);
                for (let i = 0; i < entry_points.length; i++) {
                    const ep = entry_points[i];
                    appPlugin.addFileToAssets(ep.content, ep.key, compilation)
                    const h = new HtmlWebpackPlugin({
                        title: '',
                        template: 'src/assets/entry_point_generic.html',
                        filename: path.resolve(__dirname, 'email_mgmt_app/build/templates/entry_point/' + ep.key + '.jinja2'),
                        inject: false,
                        chunks: [ep.key],
                    });
                    h.apply(compiler);
                }
            }).then(callback());


//            return callback();
        };

        const beforeRun = (compilation, callback) => {
            console.log('beforerun');
            return callback();
        }

        const afterPlugins = (compiler) => {
//             get_entry_points().then(entry_points => {
//                 console.log("ep is ", entry_points);
//                 for (let i = 0; i < entry_points.length; i++) {
//                     const ep = entry_points[i];
// //                    this.addFileToAssets(ep.content, ep.key, compilation)
//                     const h = new HtmlWebpackPlugin({
//                         title: '',
//                         template: 'src/assets/entry_point_generic.html',
//                         filename: path.resolve(__dirname, 'email_mgmt_app/build/templates/entry_point/' + ep.key + '.jinja2'),
//                         inject: false,
//                         chunks: [ep.key],
//                     });
//                     h.apply(compiler);
//                 }
            //}
            //return callback();
        };
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
        compiler.hooks.afterPlugins.tap(plugin, afterPlugins);
        compiler.hooks.emit.tapAsync(plugin, emit);

        compiler.hooks.entryOption.tap(plugin, entryOption);
        compiler.hooks.afterResolvers.tap(plugin, compiler => {
            compiler.resolverFactory.hooks.resolver.for("normal").tap(plugin, resolver => {
                console.log("making virtual plugin");
                new VirtualPlugin("described-resolve", {entry_points: this.options.entry_points}, "resolve").apply(resolver);
            })
        });
        compiler.hooks.make.tapAsync(plugin, make);
        compiler.hooks.beforeRun.tapAsync(plugin, beforeRun);
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

module.exports = AppPlugin;
