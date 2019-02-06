#!/usr/bin/env python
import barcode

from barcode.writer import ImageWriter

from docx import Document
from docx.shared import Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

barcode.PROVIDED_BARCODES
[u'code39', u'code128', u'ean', u'ean13', u'ean8', u'gs1', u'gtin',
  u'isbn', u'isbn10', u'isbn13', u'issn', u'jan', u'pzn', u'upc', u'upca']

EAN = barcode.get_barcode_class('code128')

# ean = EAN(u'5901234123457')
#
# fullname = ean.save('ean13_barcode')

ean = EAN(u'X12001R01', writer=ImageWriter())
save_options={'font_size':20,
              'text_distance':2,
              'module_height':15,
              'module_width':0.3}
fullname = ean.save('code128', options=save_options)

document = Document('word_document.docx')

for paragraph in document.paragraphs:
    if 'The barcode(s) above provides confirmation' in paragraph.text:
        p=paragraph.insert_paragraph_before('')
        p=p.insert_paragraph_before('')
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r=p.add_run()
        r.add_picture('code128.png',width=Cm(5))

# p= document.add_paragraph('test')
# p=p.insert_paragraph_before('')
# r = p.add_run()
# r.add_picture('code128.png',width=Inches(2))


#document.add_picture('code128.png', width=Inches(2))
document.save('word_document_new.docx')