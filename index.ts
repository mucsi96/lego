import { promises } from "fs";
import { PDFDocument } from "pdf-lib";

async function main(name: string, url: string) {
  const fetchResponse = await fetch(url);
  await promises.writeFile(name, await fetchResponse.arrayBuffer());
  const pdfData = await promises.readFile(name);
  const pdfDoc = await PDFDocument.load(pdfData);
  const pages = pdfDoc.getPages();
  console.log(pages);
}

main(
  "10305-lions-knights-castle.pdf",
  "https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6429215.pdf"
).catch((e) => console.error(e));
