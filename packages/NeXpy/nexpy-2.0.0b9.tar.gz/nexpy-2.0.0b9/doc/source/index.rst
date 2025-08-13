.. NeXpy documentation master file, created by
   sphinx-quickstart on Sun Aug 11 13:18:51 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: /images/nexpy-logo.png

NeXpy: A Python GUI to analyze NeXus data
=========================================

NeXpy provides a high-level python interface to HDF5 files, particularly those
stored as `NeXus data <http://www.nexusformat.org/>`_, within a simple GUI. It 
is designed to provide an intuitive interactive toolbox allowing users both to 
access existing NeXus files and to create new NeXus-conforming data structures 
without expert knowledge of the file format. The underlying Python API for 
reading and writing NeXus files is provided by the `nexusformat 
<https://github.com/nexpy/nexusformat>`_ package, which utilizes 
`h5py <http://www.h5py.org/>`_.

.. toctree::
   :maxdepth: 2

   includeme
   pythonshell
   pythongui
   readers
   examples
   treeapi

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

