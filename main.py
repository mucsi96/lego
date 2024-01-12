from os import makedirs, path
import shutil
from requests import get
import fitz

def download_pdf(url: str, save_path: str) -> None:
    response = get(url)
    with open(save_path, 'wb') as pdf_file:
        pdf_file.write(response.content)
    
def extract_images_from_pdf(pdf_path: str, output_folder: str) -> None:
    document = fitz.open(pdf_path)
    for page_number in range(document.page_count):
        images = document.get_page_images(page_number)
        for image in images:
            xref = image[0]
            name = image[7]
            extracted_image = document.extract_image(xref)
            with open(path.join(output_folder, f'image_{page_number+1}_{name}.{extracted_image["ext"]}'), 'wb') as img_file:
                img_file.write(extracted_image["image"])
                
        
    # with open(pdf_path, 'rb') as pdf_file:
        # pdf_reader = PdfReader(pdf_file)
        # for page in pdf_reader.pages:
        #     for img in page.images:
        #         img.image.save(path.join(output_folder, f'image_{page.page_number}_{img.name}'))
                
            # if '/Resources' in page:
            #     for obj_id in page.Resources.XObject:
            #         x_object = page.Resources.XObject[obj_id]
            #         if x_object.Subtype == '/Image':
            #             img = x_object.toPillow()

def main():
    pdf_url = 'https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6429215.pdf'
    pdf_path = '.cache/10305-lions-knights-castle.pdf'
    output_folder = 'images'
    
    shutil.rmtree(output_folder)
    
    makedirs(path.dirname(pdf_path), exist_ok=True)
    makedirs(output_folder)
    
    if not path.exists(pdf_path):
        download_pdf(pdf_url, pdf_path)
    extract_images_from_pdf(pdf_path, output_folder)
    
if __name__ == "__main__":
    main()
    