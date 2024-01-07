import { readFile, stat, mkdir } from "fs/promises";
import { finished, pipeline } from "stream/promises";
import { PDFDocument } from "pdf-lib";
import { createWriteStream } from "fs";
import { Readable, Transform } from "stream";
import { dirname, join } from "path";

async function exists(file: string) {
  try {
    await stat(file);
    return true;
  } catch {
    return false;
  }
}

async function main(name: string, url: string) {
  const path = join(__dirname, ".cache", name);
  if (!(await exists(path))) {
    if (!(await exists(dirname(path)))) await mkdir(dirname(path));

    const fetchResponse = await fetch(url);
    if (!fetchResponse.body) {
      throw new Error("Response had no body");
    }
    const dest = createWriteStream(path);
    console.log(`Downloading ${name} from ${url}`);
    let chunks = 0;
    await pipeline(
      Readable.fromWeb(fetchResponse.body),
      new Transform({
        transform(chunk, _encoding, callback) {
          chunks++;
          if (chunks % 100 === 0) {
            process.stdout.write(".");
          }
          this.push(chunk);
          callback();
        },
      }),
      dest
    );
  }
  const pdfData = await readFile(path);
  const pdfDoc = await PDFDocument.load(pdfData);
  const pages = pdfDoc.getPages();
  console.log(pages);
}

main(
  "10305-lions-knights-castle.pdf",
  "https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6429215.pdf"
).catch((e) => console.error(e));
