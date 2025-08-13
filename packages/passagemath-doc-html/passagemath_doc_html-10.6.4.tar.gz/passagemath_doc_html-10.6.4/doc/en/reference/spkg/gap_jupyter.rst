.. _spkg_gap_jupyter:

gap_jupyter: Jupyter kernel for GAP
===================================

Description
-----------

Jupyter kernel for GAP

This wrapper-kernel is a Jupyter kernel for the GAP Computer Algebra
System based on the same ideas as the bash wrapper kernel.

License
-------

3-Clause BSD License


Upstream Contact
----------------

-  https://github.com/gap-packages/jupyter-gap


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_gap`
- :ref:`spkg_ipython`

Version Information
-------------------

package-version.txt::

    0.9

version_requirements.txt::

    gap_jupyter >=0.9

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install gap

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install gap-pkg-jupyterkernel

# See https://repology.org/project/gap-jupyterkernel/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
