Setup env
=========
    $ mkvirtualenv pcv
    $ cd jesolem-PCV-790b64d
    $ python setup.py install
    $ python
    >>> import PCV
    $ pip install -r requirements.txt
http://www.mlewislogic.com/2011/09/how-to-install-python-imaging-in-a-virtualenv-with-no-site-packages/

Install flann
=============

TODO
====
* image search
    - too slow when doing kmeans with hundreds of images
    - mahout ? k-means kdtree clustering ? k-means kd forest clustering ? elkan k-means clustering ? coresets ? triangle inequality