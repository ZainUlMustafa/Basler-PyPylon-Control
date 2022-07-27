const path = require('path');
const fs = require('fs');
const { time } = require('console');
// const { default: axios } = require('axios');
const axios = require('axios').default;

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

const configPath = '.'
const dataPath = '.'
const configDoc = `${configPath}/configs/config.json`
const settingDoc = `${configPath}/configs/setting/aidaw.json`
const statusDoc = `${configPath}/configs/status/aidaw.json`

const debug = true
const sleeper = 500

// get the target, reach it, and get a new target
async function processing() {
    if (!fs.existsSync(configDoc)) {
        sleep(sleeper, function () { });
        return updateStatus(-3)
    }
    const configData = JSON.parse(fs.readFileSync(configDoc, { encoding: 'utf-8' }))
    const { proid, operationStatus } = configData;

    if (proid === "-1" || proid === "") {
        sleep(sleeper, function () { });
        return updateStatus(-2)
    }
    if (operationStatus != "1") {
        sleep(sleeper, function () { });
        return updateStatus(-2);
    }

    // access the meta.txt
    // var metaData = fs.readFileSync(`${dataPath}/data/${proid}/meta.txt`, { encoding: 'utf8' });
    var procMetaData = "0"

    const procMetaDoc = `${dataPath}/data/${proid}/proc_meta.txt`
    if (fs.existsSync(procMetaDoc)) {
        procMetaData = fs.readFileSync(procMetaDoc, { encoding: 'utf8' });
        if (procMetaData === "") procMetaData = 0;
    } else {
        updateStatus(-3)

    }

    const metaDoc = `${dataPath}/data/${proid}/meta.txt`
    const targetToAchieve = await getImageCount(metaDoc); //45
    // bugLog(targetToAchieve)

    var grabbingCount = Number(procMetaData) //0
    if (grabbingCount === targetToAchieve) {
        updateStatus(5)
        sleep(sleeper, function () { }); 
        return
    }

    updateStatus(4);
    bugLog(`Starting from: ${grabbingCount}`)

    // if (grabbingCount < targetToAchieve) updateStatus(1)
    while (grabbingCount <= targetToAchieve) {
        var start = new Date().getTime();
        if (!fs.existsSync(`${dataPath}/data/${proid}/orig_json/${grabbingCount}.json`)) {
            sleep(sleeper, function () { });
            return updateStatus(-4)
        }
        const imageJsonPath = `/data/${proid}/orig_json/${grabbingCount}.json`;
        const lowResImagePath = `/data/${proid}/orig_low_res/${grabbingCount}.jpg`;
        const grabTimestamp = await getImageTimestamp(grabbingCount, metaDoc)
        // console.log(grabbingCount, grabTimestamp)
        // console.log(grabbingCount, "grab");
        const geoResp = await axios.get(`http://localhost:3100/getBestGeoTime?tmq=${grabTimestamp}&proid=${proid}&diffAllowedMs=11`);
        console.log(geoResp.data);

        // await axios.post('http://localhost:4000/imagesPath', {
        //     imageId: grabbingCount,
        //     imageDirectory: imageJsonPath,
        //     proid,
        //     lrImageDirectory: lowResImagePath,

        // });
        // var imageJsonData = fs.readFileSync(`${dataPath}/data/${proid}/orig_json/${grabbingCount}.json`, { encoding: 'utf8' });

        //  begin to achieve the target
        sleep(sleeper, function () { });
        updateProcMeta(grabbingCount, procMetaDoc)
        grabbingCount += 1
        var stop = new Date().getTime();

        // sleep(sleeper, function () { });
        console.log(`Exec time: ${stop - start} ms`)
    }

    sleep(sleeper, function () { });
}

function updateProcMeta(count, path) {
    fs.writeFileSync(path, `${count}`)
}

function updateStatus(status) {
    const allStatuses = {
        "999": "Ended",
        "5": "Waiting for new target",
        "4": "Reading new target",
        "3": "Image watcher reviving",
        "2": "Image saved on db",
        "1": "Images processing and saving started",
        "0": "Script started",
        "-1": "Config not found",
        "-2": "Config not valid",
        "-3": "Proc meta not found, init it!",
        "-4": "Image not found, waiting for it!",
        "-999": "Unexpected error"
    }

    const statusData = {
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

async function getImageCount(dir) {
    const meta = fs.readFileSync(`${dir}`, { encoding: 'utf8' });
    const metaList = meta.toString().trim().split('\n');
    const lastIndexMeta = metaList[metaList.length - 1];
    const imageCount = lastIndexMeta.split(',')[0];
    return imageCount ? Number(imageCount) : 0;
}

async function getImageTimestamp(imageCount, dir) {
    const meta = fs.readFileSync(`${dir}`, { encoding: 'utf8' });
    const metaList = meta.toString().trim().split('\n');
    const lastIndexMeta = metaList[imageCount];
    const imageTimestamp = lastIndexMeta.split(',')[1];
    return imageTimestamp ? Number(imageTimestamp) : 0;
}

async function main() {
    while (true) {
        try {
            // process.on('SIGINT', function () {
            //    updateStatus(999);
            //     process.exit();
            // });
            await processing()

        } catch (err) {
            sleep(sleeper, function () { });
            updateStatus(3)
        }

    }
}


main();

