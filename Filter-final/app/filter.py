import base64
import os
import re
from io import BytesIO
from PIL import Image, ImageFilter, ImagePalette, ImageEnhance
from app import app

UPLOAD_FOLDER = os.path.basename('uploads')

# add image filters
def filter_image(filename, filter):
    # strip off prefix from JavaScript File Reader
    image_str = re.sub('^data:image/.+;base64,', '', filename)
    # save decoded Base64 string to bytes object, to simulate file I/O
    in_buffer = BytesIO(base64.b64decode(image_str))
    # Use bytes object to create PIL Image object
    im = Image.open(in_buffer)
    enhancer = ImageEnhance.Contrast(im)
    if filter == 'b':
        out = im.filter(ImageFilter.GaussianBlur())
    elif filter == 'g':
        out = im.convert('L')
    elif filter == 'c':
        out = im.filter(ImageFilter.CONTOUR)
    elif filter == 'd':
        out = enhancer.enhance(2)
    elif filter == 's':
        if im.mode != "L":
            im = im.convert("L")
        # Uses make_linear_ramp to create sepia tone palette
        im.putpalette(ImagePalette.sepia("#e5d8ac"))
        out = im
    
    # out.save(UPLOAD_FOLDER + "\\" + outfile + ".png")
    # Use Python Bytes object to simulate file I/O
    out_buffer = BytesIO()
    # Save image into object as a PNG file
    out.save(out_buffer, format="PNG")
    # Read object into string
    image_str = out_buffer.getvalue()
    # Encode bytes object as base64
    out_str = str(b"data:image/png;base64," + base64.b64encode(image_str))
    # strip off Python syntax using regex
    reg = re.sub("^b(?P<quote>['\"])(.*?)(?P=quote)", r'\2', out_str)
    return reg
    

# take Base64 image as input
# return tuple of image and its thumbnail and 
def filter_and_thumbnail(filename):
    # strip off prefix from JavaScript File Reader
    image_str = re.sub('^data:image/.+;base64,', '', filename)
    # save decoded Base64 string to bytes object
    in_buffer = BytesIO(base64.b64decode(image_str))
    # Use bytes object to create PIL Image object
    im = Image.open(in_buffer).convert('RGB')

    # Copy original image and create thumbbnail
    out = im.copy()
    out_thumbnail = im.copy()
    out_thumbnail.thumbnail(app.config['THUMBNAIL_SIZE'])
    
    # Open new bytes object
    out_buffer = BytesIO()
    # Save image into object as a PNG file
    out.save(out_buffer, format="PNG")
    # Read object into string variable
    image_str = out_buffer.getvalue()
    # Encode as Base64 string
    out_str = str(b"data:image/png;base64," + base64.b64encode(image_str))
    reg1 = re.sub("^b(?P<quote>['\"])(.*?)(?P=quote)", r'\2', out_str)
    
    # Open second bytes object
    th_buffer = BytesIO()
    # Save thumbnail image as JPEG
    out_thumbnail.save(th_buffer, format="JPEG")
    image_str = th_buffer.getvalue()                     
    out_str = str(b"data:image/png;base64," + base64.b64encode(image_str))
    reg2 = re.sub("^b(?P<quote>['\"])(.*?)(?P=quote)", r'\2', out_str)
    return (reg1, reg2)
