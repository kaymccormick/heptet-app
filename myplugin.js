class MyPlugin {
    constructor(options) {
	this.options = options;
    }

    apply(compiler) {
        console.log("i like food");
        let context;
                const emit = (compilation, cb) => {
            debug('starting emit');
            const callback = () => {
                debug('finishing emit');
                cb();
            };

            const globalRef = {
                info,
                debug,
                warning,

                compilation,
                written,
                context,
                inputFileSystem: compiler.inputFileSystem,
                output: compiler.options.output.path,
                ignore: options.ignore || [],
                concurrency: options.concurrency
            };

            if (globalRef.output === '/' &&
                compiler.options.devServer &&
                compiler.options.devServer.outputPath) {
                globalRef.output = compiler.options.devServer.outputPath;
            }

            const tasks = [];

            patterns.forEach((pattern) => {
                tasks.push(
                    Promise.resolve()
                    .then(() => preProcessPattern(globalRef, pattern))
                    // Every source (from) is assumed to exist here
                    .then((pattern) => processPattern(globalRef, pattern))
                );
            });

            Promise.all(tasks)
            .catch((err) => {
                compilation.errors.push(err);
            })
            .then(() => callback());
        };


        var plugin = { name: 'MyPlugin' };
        compiler.hooks.emit.tapAsync(plugin, emit)
	compiler.hooks.shouldEmit.tap('MyPlugin', (compilation) => {
	    return true;
	});
    }
}
module.exports = MyPlugin;
