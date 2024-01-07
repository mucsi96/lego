import { readFile, stat, mkdir } from "fs/promises";
import { finished } from "stream/promises";
import { PDFDocument } from "pdf-lib";
import { createWriteStream } from "fs";
import { Readable } from "stream";
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
  if (!await exists(path)) {
    if (!await exists(dirname(path))) await mkdir(dirname(path));

    const fetchResponse = await fetch(url);
    if (!fetchResponse.body) {
      throw new Error("Response had no body");
    }
    const dest = createWriteStream(path);
    await finished(Readable.fromWeb(fetchResponse.body).pipe(dest));
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
