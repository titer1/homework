import os
import sys
import math
import glob
import subprocess
from struct import unpack, pack
from PIL import Image


def screen_size():
    output = subprocess.check_output("xrandr | grep \\* | cut -d' ' -f4", shell=True)
    return map(int, output.strip().split('x', 1))

def read_labels(fname):
    with open(fname) as f:
        magic, total = unpack('>2I', f.read(4*2))
        assert magic == 2049
        return unpack('%dB' % total, f.read(total))

def read_images(fname):
    with open(fname) as f:
        magic, total, rows, cols = unpack('>4I', f.read(4*4))
        assert magic == 2051
        pixels = rows * cols
        fmt = '%dB' % pixels
        return (rows, cols), [ unpack(fmt, f.read(pixels))
            for _ in xrange(total) ]

def create_image(data, size, reverse=False):
    fmt = '%dB' % len(data)
    if reverse:
        data = [ (255-i) for i in data ]
    buf = pack(fmt, *data)
    im = Image.fromstring('L', size, buf)
    return im

def guess_grid(screen_size, image_size, n):
    screen_weight, screen_height = screen_size
    image_weight, image_height = image_size
    scale = 1
    while True:
        if scale <= 0:
            break
        weight, height = int(image_weight*scale), int(image_height*scale)
        cols = screen_weight / weight
        rows = screen_height / height
        if cols * rows >= n:
            rows = int(math.ceil(float(n)/cols))
            return (rows, cols), (weight, height)
        scale -= .05
    return

def grid(images):
    n = len(images)
    assert n > 0

    ss = map(lambda i:int(i*.9), screen_size())
    (rows, cols), (w, h) = guess_grid(ss, images[0].size, n)
    print 'show %d images by (%d, %d)' % (n, rows, cols)
    size = (w*cols, h*rows)

    im = Image.new(images[0].mode, size)
    for r in range(rows):
        for c in range(cols):
            i = r*cols+c
            if i >= n:
                break
            im.paste(images[i].resize((w, h)), (w*c, h*r))
    return im

def dump(data, fname):
    with open(fname, 'w') as f:
        for im in data:
            line = ' '.join([ str(p) for p in im ])
            f.write(line+'\n')

def write_numbers():
    n = 16
    labels = read_labels('MNIST/t10k-labels-idx1-ubyte')[:n]
    size, data = read_images('MNIST/t10k-images-idx3-ubyte')
    data = data[:n]
    dump(data, 'numbers.txt')

def load_faces():
    index = {}
    for fname in sorted(glob.glob('yalefaces/subject*')):
        bname = os.path.basename(fname) 
        subject, condition = bname.split('.', 1)
        im = Image.open(fname).convert('L')
        index.setdefault(subject, []).append(im)
        index.setdefault(condition, []).append(im)
        index.setdefault('all', []).append(im)
    return index

def convert_faces():
    with open('yalefaces/all.txt', 'w') as f:
        for fname in glob.glob('yalefaces/subject*'):
            im = Image.open(fname).convert('L')
            bname = os.path.basename(fname)
            subject, condition = bname.split('.', 1)
            pixels = map(str, im.getdata())
            print >> f, '%s %s %s' % (subject, condition, ' '.join(pixels))

def load_txt_face(line):
    data = [int(float(i)) for i in line.split()]
    return create_image(data, (320, 243))

def show_eigenface():
    faces = [ load_txt_face(line).resize((320/4, 243/4))
        for line in open('eigenfaces.txt') ]
    grid(faces, 10, 13).show()

def browse_faces():
    idx = load_faces()
    subjects = sorted([g[len('subject'):] for g in idx if g.startswith('subject')])
    groups = ['subject[%s-%s]'%(subjects[0], subjects[-1])]
    groups.extend([g for g in idx if not g.startswith('subject')])

    while True:
        print 'Available groups:', ' '.join(groups)
        group = raw_input('input: ')
        if group in ('q', 'exit', 'quit'):
            print 'Bye!'
            break
        if group in idx:
            grid(idx[group]).show()


browse_faces()
#show_eigenface()
#write_yalefaces()
#show_eigenface('eigenface.txt')
#show_eigenface('meanface.txt')
#convert_faces()

#TODO:
# numpy for input, output