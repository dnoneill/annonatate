from iiif.static import IIIFStatic
from IIIFpres import iiifpapi3
from PIL import Image
import os
from pdf2image import convert_from_path
from iiif_prezi.factory import ManifestFactory
import yaml

files = [('images/Screenshot20230424at45014PM.png', 'Screenshot 2023-04-24 at 4.50.14 PM')]
manifestlabel = '''test'''
dst = os.path.join('img/derivatives/iiif/', 'test') + '/'
baseurl = os.path.join('https://dnoneill.github.io/annonatate/', dst)
data = []
allfiles = []
for idx, filedict in enumerate(files):
    file = filedict[0]
    filepath,ext = file.rsplit('.', 1)
    if ext == 'pdf':
        images = convert_from_path(file)
        for i in range(len(images)):
            imagefilename = filepath + '-' + str(i) +'.jpg'
            images[i].save(imagefilename, 'JPEG')
            allfiles.append([imagefilename, filedict[1]])
        os.remove(file)
    elif ext != 'jpg' and ext != 'jpeg':
        os.system('convert {} {}.jpg'.format(file, filepath))
        allfiles.append(('%s.jpg'%filepath, filedict[1]))
        os.remove(file)
    else:
        allfiles.append(filedict)

def convertImage(filedict):
    file = filedict[0]
    filepath,ext = file.rsplit('.', 1)
    filename = os.path.basename(filepath)
    if ext != 'jpg' and ext != 'jpeg':
        os.system('convert {} {}.jpg'.format(file, filepath))
    sg = IIIFStatic(prefix=baseurl, dst=dst)
    sggenerate = sg.generate(file)
    img = Image.open(file)
    data.append((filename, img.width, img.height, os.path.join(baseurl, filename),'/full/full/0/default.jpg', filedict[1]))
    iiiffulldir = os.path.join(dst, filename, 'full/full')
    if not os.path.isdir(iiiffulldir):
        os.mkdir(iiiffulldir)
        iiiffulldir = os.path.join(iiiffulldir, '0')
        os.mkdir(iiiffulldir)
    else:
        iiiffulldir = os.path.join(iiiffulldir, '0')
    os.system('mv {} {}'.format(file, os.path.join(iiiffulldir, 'default.jpg')))
    return done

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    future_to_url = {executor.submit(convertImage, filedict): filedict for filedict in allfiles}
    for future in concurrent.futures.as_completed(future_to_url):
        print(future_to_url)
    
    iiifpapi3.BASE_URL = baseurl
manifest = iiifpapi3.Manifest()
manifest.set_id(extendbase_url='manifest.json')
manifest.add_label('en',manifestlabel)
manifest.add_behavior('paged')
description = manifest.add_summary('en', '''''')
manifest.set_viewingDirection('left-to-right')
rights = ''''''
if rights:
    try:
        manifest.set_rights(rights)
    except:
        manifest.add_metadata('rights', rights, 'en', 'en')

data = tuple(data)
for idx,d in enumerate(data):
    idx+=1
    canvas = manifest.add_canvas_to_items()
    canvas.set_id(extendbase_url='canvas/test-%s'%idx)
    canvas.set_height(d[2])
    canvas.set_width(d[1])
    canvas.add_label('en', d[5])
    filteredallfiles = [f for f in os.listdir(os.path.join(dst, d[0], 'full')) if f != 'full' and int(f.split(',')[0]) > 70]
    filteredallfiles.sort()
    size = filteredallfiles[0] if len(filteredallfiles) > 0 else '80,'
    thumbnail = canvas.add_thumbnail()
    thumbnail.set_id('{}/full/{}/0/default.jpg'.format(d[3], size))
    annopage = canvas.add_annotationpage_to_items()
    annopage.set_id(extendbase_url='page/p%s/1' %idx)
    annotation = annopage.add_annotation_to_items(target=canvas.id)
    annotation.set_id(extendbase_url='annotation/p%s-image'%str(idx).zfill(4))
    annotation.set_motivation('painting')
    annotation.body.set_id(''.join(d[3:5]))
    annotation.body.set_type('Image')
    annotation.body.set_format('image/jpeg')
    annotation.body.set_width(d[1])
    annotation.body.set_height(d[2])
    s = annotation.body.add_service()
    s.set_id(d[3])
    s.set_type('ImageService2')
    s.set_profile('level1')

manifestpath = os.path.join(dst, 'manifest.json')
manifest.json_save(manifestpath)
headerinfo = {}
headerinfo['title']= manifestlabel
headerinfo['added']= '''2023-05-11 17&#58;57&#58;07.035605'''
headerinfo['thumbnail'] = manifest.items[0].thumbnail[0].id
filecontents = open(manifestpath).read()
with open(manifestpath, 'w') as f:
    f.write('''---\n{}---\n'''.format(yaml.dump(headerinfo)))
    f.write(filecontents)
