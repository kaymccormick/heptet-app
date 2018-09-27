const axios = require('axios');
module.exports = class App {
    constructor(config) {
        this.config = config;
        this.entry_points = undefined
    }

    get_entry_points() {
        if (this.entry_points) {
            return Promise.resolve(this.entry_points);
        } else {
            const me = this;
            return new Promise(function (resolve, reject) {
                axios.get('http://localhost:6643/entry_points_json', {
                    transform_response: function (response) {
                        return JSON.parse(response);
                    }
                }).then(function (data) {
                    resolve(me.entry_points = data.data.entry_points)
                });
            });
        }
    }
};


