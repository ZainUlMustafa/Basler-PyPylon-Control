const fs = require('fs');
async function processing() {
   const imageCount =  await getImageCount('../data/62d690207384085634ff9848/meta.txt');
   console.log(imageCount);

}

async function getImageCount(dir) {
    const meta = fs.readFileSync(`${dir}`, { encoding: 'utf8' });
    const metaList = meta.toString().trim().split('\n');
    const lastIndexMeta = metaList[metaList.length - 1];
    const imageCount = lastIndexMeta.split(',')[0];
    return imageCount ? Number(imageCount) : 0;
}

async function main() {
    await processing();
}


main();