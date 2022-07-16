const path = require('path');
const fs = require('fs');
const { time } = require('console');

configDoc = './configs/config.json'
settingDoc = './configs/setting/aidaw.json'
statusDoc = './configs/status/aidaw.json'

// get the target, reach it, and get a new target
function main() {
    while(true) {
        var start = new Date().getTime();
        sleep(200, function() {});
        var stop = new Date().getTime();

        console.log(`Exec time: ${stop-start} ms`)
    }
}

function add(a,b) {
    console.log(a+b)
    return a+b
}

function sleep(time, callback) {
    var stop = new Date().getTime();
    while(new Date().getTime() < stop + time);
    callback();
}

main()


