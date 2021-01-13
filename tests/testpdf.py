from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import os
import io

path = os.path.dirname(os.path.abspath(__file__))

c = canvas.Canvas('myfile.pdf', pagesize=(1121,793))

buf = io.BytesIO()
im = Image.open(path + "\\images\\Pg1.jpg")
im.save(buf, "jpeg")
image = ImageReader(buf)
c.drawImage(image, 0,0,1121, 793)
c.showPage()
buf = io.BytesIO()
im = Image.open(path + "\\images\\A3M.jpg")
im.save(buf, "jpeg")
image = ImageReader(buf)
c.drawImage(image, 0,0,1121, 693)

c.save()
y = 2