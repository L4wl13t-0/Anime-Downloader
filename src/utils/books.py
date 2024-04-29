from app import app, mongo
from lxml import etree
import os, zipfile
from pathlib import Path
import shutil

namespaces_xml = {
    "calibre":"http://calibre.kovidgoyal.net/2009/metadata",
    "dc":"http://purl.org/dc/elements/1.1/",
    "dcterms":"http://purl.org/dc/terms/",
    "opf":"http://www.idpf.org/2007/opf",
    "u":"urn:oasis:names:tc:opendocument:xmlns:container",
    "xsi":"http://www.w3.org/2001/XMLSchema-instance",
    "xhtml":"http://www.w3.org/1999/xhtml"
}

def validate_author(author):
    _author = mongo.db.authors.find_one({'author': author})
    if not _author:
        return False
    return True

def validate_category(category):
    return True if mongo.db.books.find_one({'categories': category}) else False

def validate_bookName(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS_BOOKS']

def validate_bookFile(book):
    if book and validate_bookName(book.filename):
        filename = book.filename
        book.save(os.path.join(os.getcwd() + app.config['BOOKS_PATH'], filename))
        return filename
    
def get_epub_cover(epub_file):
    with zipfile.ZipFile(epub_file) as z:
        t = etree.fromstring(z.read('META-INF/container.xml'))
        opf_path = t.xpath('/u:container/u:rootfiles/u:rootfile', namespaces=namespaces_xml)[0].get('full-path')
        t = etree.fromstring(z.read(opf_path))
        cover_href = None

        try:
            cover_id = t.xpath("//opf:metadata/opf:meta[@name='cover']", namespaces=namespaces_xml)[0].get('content')
            title = t.xpath("//dc:title", namespaces=namespaces_xml)[0].text
            cover_href = t.xpath("//opf:manifest/opf:item[@id='%s']" % cover_id, namespaces=namespaces_xml)[0].get('href')
        except IndexError:
            pass

        if not cover_href:
            try:
                cover_href = t.xpath("//opf:manifest/opf:item[@properties='cover-image']", namespaces=namespaces_xml)[0].get('href')
            except IndexError:
                pass

        if not cover_href:
            try:
                cover_page_id = t.xpath("//opf:spine/opf:itemref", namespaces=namespaces_xml)[0].get("idref")
                cover_page_href = t.xpath("//opf:manifest/opf:item[@id='" + cover_page_id + "']", namespaces=namespaces_xml)[0].get("href")
                cover_page_path = os.path.join(os.path.dirname(opf_path), cover_page_href)
                t = etree.fromstring(z.read(cover_page_path))
                cover_href = t.xpath("//xhtml:img", namespaces=namespaces_xml)[0].get("src")
            except IndexError:
                pass

        if not cover_href:
            return 'default.png'
        
        cover_path = f"{os.path.dirname(opf_path)}/{cover_href}"
        source = z.open(cover_path)
        filename = f"{title}{Path(cover_id).suffix}"
        target = open(os.path.join(os.getcwd() + app.config['COVERS_PATH'], filename), "wb")
        with source, target:
            shutil.copyfileobj(source, target)

        return filename