const path = require('path');
const fs = require('fs');
const { time } = require('console');

/*
1. Get the config info to get proid and operation status
2. Check if proid is valid (not empty, not -1) and operation status is 1 (survey is playing)
3. Use proid to access the meta.txt in the data folder and update the target to achieve
4. The system will try to achieve this target taking care of the fact that the images are available in the directory and
4a. If image to fetch is not available in the directory then the system should wait
4b. If the image is available in the directory then do the required processing and save image dir into the mongodb and update the system count
5. When the system has reached its target then it will access the meta.txt again to get a new target
6. If the new target is equal to the current target then wait for the new target to be greater than the current target
7. If the target is greater than the current target then try to achieve the new target
*/

configDoc = './configs/config.json'
settingDoc = './configs/setting/aidaw.json'
statusDoc = './configs/status/aidaw.json'

debug = true
sleeper = 500

// get the target, reach it, and get a new target
function main() {
    if (!fs.existsSync(configDoc)) { 
        sleep(sleeper, function () { });
        return updateStatus(-3)
    }
    configData = JSON.parse(fs.readFileSync(configDoc, { encoding: 'utf-8' }))
    const { proid, operationStatus } = configData;

    if (proid === "-1" || proid === "") {
        sleep(sleeper, function () { });
        return updateStatus(-2)
    }
    if (operationStatus != "1") {
        sleep(sleeper, function () { });
        return updateStatus(-2);
    }

    var start = new Date().getTime();
    sleep(sleeper, function () { });
    var stop = new Date().getTime();

    console.log(`Exec time: ${stop - start} ms`)
}

function updateStatus(status) {
    allStatuses = {
        "999": "Ended",
        "3": "Image watcher reviving",
        "2": "Image saved on db",
        "1": "Image processed",
        "0": "Script started",
        "-1": "Config not found",
        "-2": "Config not valid",
        "-999": "Unexpected error"
    }

    statusData = {
        'status': status,
        'message': allStatuses[status],
    }

    bugLog(statusData)

    fs.writeFileSync(statusDoc, JSON.stringify(statusData))
}

function bugLog(data) {
    if (debug) console.log(data)
}

function sleep(time, callback) {
    var stop = new Date().getTime();
    while (new Date().getTime() < stop + time);
    callback();
}

while (true) {
    try {
        main()
    } catch (err) {
        sleep(sleeper, function () { });
        updateStatus(3)
    }
}


