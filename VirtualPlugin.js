module.exports = class VirtualPlugin {
    constructor(source, options, target) {
        this.source = source;
        this.options = Array.isArray(options) ? options : [options];
        this.target = target;
    }

    apply(resolver) {
        const target = resolver.ensureHook(this.target);
        console.log("!!! i am here");
        resolver.getHook(this.source).tapAsync("VirtualPlugin", (request, resolveContext, callback) => {
            console.log("req: ", request.request);
            const innerRequest = request.request || request.path;
            if (!innerRequest) return callback();
            if(innerRequest.startsWith("app_entry_point:")) {
                console.log("yay " + innerRequest);
            }
            for (const item of this.options) {

                // if (innerRequest === item.name || (!item.onlyModule && startsWith(innerRequest, item.name + "/"))) {
                //     if (innerRequest !== item.alias && !startsWith(innerRequest, item.alias + "/")) {
                //         const newRequestStr = item.alias + innerRequest.substr(item.name.length);
                //         const obj = Object.assign({}, request, {
                //             request: newRequestStr
                //         });
                //         return resolver.doResolve(target, obj, "aliased with mapping '" + item.name + "': '" + item.alias + "' to '" + newRequestStr + "'", resolveContext, (err, result) => {
                //             if (err) return callback(err);
                //
                //             // Don't allow other aliasing or raw request
                //             if (result === undefined) return callback(null, null);
                //             callback(null, result);
                //         });
                //     }
                // }
            }
            return callback();
        });
    }
};
