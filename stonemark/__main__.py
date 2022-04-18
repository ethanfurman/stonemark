from __future__ import print_function
from scription import *
from antipathy import Path
from . import Document


@Command(
        source=Spec('name of source file to convert', type=Path),
        target=Spec('name of output file [default: source base name with .html extension]', default='', type=Path),
        )
def stonemark(source, target):
    if not source.exists():
        abort("'%s' does not exist" % source)
    if target == '':
        target = source.strip_ext() + '.html'
    elif target.isdir():
        target += source.filename.strip_ext() + '.html'
    with open(source) as f:
        text = f.read()
    doc = Document(text).to_html()
    with open(target, 'wb') as f:
        f.write(doc)

Run()
