import fitz
from PIL import Image, ImageOps

file_path = "AI\\AI Notes long answer.pdf"
output_path =  file_path.split(".pdf")[:-1][0] + "_dark.pdf"

def pixmap_to_pil(pix):
    mode = "RGBA" if pix.alpha else "RGB"
    img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255,255,255))
        background.paste(img, mask=img.split()[3])
        return background
    return img

def convert_pdf_to_dark_high_quality(input_pdf, output_pdf, zoom=3.0, dpi=100):
    doc = fitz.open(input_pdf)
    pil_images = []
    mat = fitz.Matrix(zoom, zoom)

    for page_num, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = pixmap_to_pil(pix)
        inverted = ImageOps.invert(img)
        pil_images.append(inverted.convert("RGB"))
        pix = None

    if not pil_images:
        raise RuntimeError("No pages found in PDF.")
    first, rest = pil_images[0], pil_images[1:]
    first.save(output_pdf,"PDF",save_all=True,append_images=rest,resolution=dpi)

if __name__ == "__main__":
    convert_pdf_to_dark_high_quality(file_path, output_path)
