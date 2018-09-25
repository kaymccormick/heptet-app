const axios = require('axios');
module.exports = class App {
    constructor(config) {
        this.config = config;
    }

    get_entry_points() {
        return new Promise(function (resolve, reject) {
            axios.get('http://localhost:6643/entry_points_json', {
                transform_response: function (response) {
                    return JSON.parse(response);
                }
            }).then(function (data) {
                //me.entry_points = entry_points;
                resolve(data.data.entry_points)
            });
        });
    }
};


