pyclmuapp: A Python Package for Integration and Execution of Community Land Model Urban (CLMU) in a Containerized Environment
-----------------------------------------------------------------------------------------------------------------------------
|doi| |docs| |GitHub| |license| 

.. |doi| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.14224043.svg
   :target: https://doi.org/10.5281/zenodo.14224043

.. |GitHub| image:: https://img.shields.io/badge/GitHub-pyclmuapp-brightgreen.svg
   :target: https://github.com/envdes/pyclmuapp

.. |docs| image:: https://img.shields.io/badge/docs-pyclmuapp-brightgreen.svg
   :target: https://envdes.github.io/pyclmuapp/

.. |license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://github.com/envdes/pyclmuapp/blob/main/LICENSE

pyclmuapp: Integration and Execution of Community Land Model Urban (CLMU) in a Containerized Environment.

Contributors: `Junjie Yu <https://junjieyu-uom.github.io>`_, `Keith Oleson <https://staff.ucar.edu/users/oleson>`_, `Yuan Sun <https://github.com/YuanSun-UoM>`_, `David Topping <https://research.manchester.ac.uk/en/persons/david.topping>`_, `Zhonghua Zheng <https://zhonghuazheng.com>`_ (zhonghua.zheng@manchester.ac.uk)

Installation
------------
Step 1: create an environment::

    $ conda create -n pyclmuapp python=3.8
    $ conda activate pyclmuapp
    $ conda install -c conda-forge numpy pandas xarray haversine netcdf4 nc-time-axis

Step 2: install from source:: 

    $ git clone https://github.com/envdes/pyclmuapp.git
    $ cd pyclmuapp
    $ python setup.py pyclmuapp

(optional) install using pip::

    $ pip install pyclmuapp
    
Please check `online documentation <https://envdes.github.io/pyclmuapp/>`_ for more information.

Citation
--------

If you use pyclmuapp in your research, please cite the following paper:

Yu, J., Sun, Y., Lindley, S., Jay, C., Topping, D. O., Oleson, K. W., & Zheng, Z. (2025). `Integration and execution of Community Land Model Urban (CLMU) in a containerized environment <https://doi.org/10.1016/j.envsoft.2025.106391>`_. Environmental Modelling & Software, 188, 106391. https://doi.org/10.1016/j.envsoft.2025.106391

.. image:: docs/paper_overview.png
   :alt: pyclmuapp
   :width: 600px
   :align: center

.. code-block:: bibtex

      @article{YU2025pyclmuapp,
      title = {Integration and execution of Community Land Model Urban (CLMU) in a containerized environment},
      journal = {Environmental Modelling & Software},
      volume = {188},
      pages = {106391},
      year = {2025},
      issn = {1364-8152},
      doi = {https://doi.org/10.1016/j.envsoft.2025.106391},
      url = {https://www.sciencedirect.com/science/article/pii/S1364815225000751},
      author = {Junjie Yu and Yuan Sun and Sarah Lindley and Caroline Jay and David O. Topping and Keith W. Oleson and Zhonghua Zheng},
      }

How to ask for help
-------------------
The `GitHub issue tracker <https://github.com/envdes/pyclmuapp/issues>`_ is the primary place for bug reports. 
