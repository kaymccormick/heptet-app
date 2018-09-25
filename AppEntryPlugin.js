const AppEntryDependency = require("./AppEntryDependency");
const AppModuleFactory = require("./AppModuleFactory");

class AppEntryPlugin {
    constructor(context, resolverFactory, entry, name) {
        this.context = context;
        this.entry = entry;
        this.name = name;
        this.resolverFactory = resolverFactory
        this.appModuleFactory = new AppModuleFactory(this.context, this.resolverFactory,
            {

            })
    }

    apply(compiler) {
        const plugin = "AppEntryPlugin"
        compiler.hooks.compilation.tap(plugin, (compilation, {normalModuleFactory}) => {

            compilation.dependencyFactories.set(AppEntryDependency, normalModuleFactory);// this.appModuleFactory);
        });
        compiler.hooks.make.tapAsync(plugin, (compilation, callback) => {
                const {entry, name, context} = this;

                const dep = AppEntryPlugin.createDependency(entry, name);
                console.log("!!! entry = ", entry)
                compilation.addEntry(context, dep, name, callback);
            }
        );
    }

    static createDependency(entry, name) {
        const dep = new AppEntryDependency(entry);
        dep.loc = {name};
        return dep;
    }

}

module.exports = AppEntryPlugin;