============
Contributing
============

Welcome to ``otcyto`` contributor's guide.

This document focuses on getting any potential contributor familiarized
with the development processes, but `other kinds of contributions`_ are also
appreciated.

Issue Reports
=============

If you experience bugs or general issues with ``otcyto``, please have a look
on the `github issues`. If you don't see anything useful there, please feel
free to fire an issue report.

.. tip::
   Please don't forget to include the closed issues in your search.
   Sometimes a solution was already reported, and the problem is considered
   **solved**.

New issue reports should include information about your programming environment
(e.g., operating system, Python version) and steps to reproduce the problem.
Please try also to simplify the reproduction steps to a very minimal example
that still illustrates the problem you are facing. By removing other factors,
you help us to identify the root cause of the issue.


Documentation Improvements
==========================

You can help improve ``otcyto`` docs by making them more readable and coherent, or
by adding missing information and correcting mistakes.

``otcyto`` documentation uses mkdocs_ as its main documentation compiler.
This means that the docs are kept in the same repository as the project code, and
that any documentation update is done in the same way was a code contribution.

.. tip::
    Please notice that the `GitHub web interface`_ provides a quick way of
    propose changes in ``otcyto``'s files. While this mechanism can
    be tricky for normal code contributions, it works perfectly fine for
    contributing to the docs, and can be quite handy.

    If you are interested in trying this method out, please navigate to
    the ``docs`` folder in the source repository_, find which file you
    would like to propose changes and click in the little pencil icon at the
    top, to open `GitHub's code editor`_. Once you finish editing the file,
    please write a message in the form at the bottom of the page describing
    which changes have you made and what are the motivations behind them and
    submit your proposal.

When working on documentation changes in your local machine, you can
compile them using |mkdocs|_::

    uv run mkdocs serve

and preview in your web browser(``http://127.0.0.1:8000/``)


Submit an issue
---------------

Before you work on any non-trivial code contribution it's best to first create
an `issue`.

Create an environment
---------------------

Before you start coding, we recommend creating an isolated `virtual
environment`_ to avoid any problems with your installed Python packages.


I have used `uv` to create a virtual environment, but you can use any other
tool you prefer, such as |virtualenv|_ or Miniconda_.

To set up the environment with uv, you can run the following command in the root
directory of the project::

    uv venv
    uv sync


otherwise, can easily be done via either |virtualenv|_::

    virtualenv <PATH TO VENV>
    source <PATH TO VENV>/bin/activate

or Miniconda_::

    conda create -n otcyto python=3 six virtualenv pytest pytest-cov
    conda activate otcyto

Clone the repository
--------------------

#. Create an user account on |the repository service| if you do not already have one.
#. Fork the project repository_: click on the *Fork* button near the top of the
   page. This creates a copy of the code under your account on |the repository service|.
#. Clone this copy to your local disk::

    git clone git@github.com:YourLogin/otcyto.git
    cd otcyto

#. You should run::

    uv sync


Implement your changes
----------------------

#. Create a branch to hold your changes::

    git checkout -b my-feature

   and start making changes. Never work on the main branch!

#. Start your work on this branch. Don't forget to add docstrings_ to new
   functions, modules and classes, especially if they are part of public APIs.

#. Add yourself to the list of contributors in ``AUTHORS.rst``.

#. When you're done editing, do::

    git add <MODIFIED FILES>
    git commit

   to record your changes in git_.

   Please make sure to see the validation messages from |pre-commit|_ and fix
   any eventual issues.
   This should automatically use ruff_ to check/fix the code style
   in a way that is compatible with the project.

   .. important:: Don't forget to add unit tests and documentation in case your
      contribution adds an additional feature and is not just a bugfix.

#. Please check that your changes don't break any unit tests with::

    uv run pytest

Submit your contribution
------------------------

#. If everything works fine, push your local branch to |the repository service| with::

    git push -u origin my-feature

#. Go to the web page of your fork and click |contribute button|
   to send your changes for review.


Maintainer tasks
================

Releases
--------

If you are part of the group of maintainers and have correct user permissions
on PyPI_, the following steps can be used to release a new version for
``otcyto``:

#. We make use of GitHub Actions defined in ``.github/workflows/publish.yml``
   to automatically build the documentation and the distribution files.
   If you want to test the release process, you can run the workflow manually
   from the Actions tab in the GitHub web interface.
#. Make sure all unit tests are successful.
#. Tag the current commit on the main branch with a release tag, e.g., ``v1.2.3``.
#. Push the new tag to the upstream repository_, e.g., ``git push upstream v1.2.3``
#. Clean up the ``dist`` and ``build`` folders with ``tox -e clean``
   (or ``rm -rf dist build``)
   to avoid confusion with old builds and Sphinx docs.
#. Run ``tox -e build`` and check that the files in ``dist`` have
   the correct version (no ``.dirty`` or git_ hash) according to the git_ tag.
   Also check the sizes of the distributions, if they are too big (e.g., >
   500KB), unwanted clutter may have been accidentally included.
#. Run ``tox -e publish -- --repository pypi`` and check that everything was
   uploaded to PyPI_ correctly.



.. [#contrib1] Even though, these resources focus on open source projects and
   communities, the general ideas behind collaborating with other developers
   to collectively create software are general and can be applied to all sorts
   of environments, including private companies and proprietary code bases.


.. <-- start -->
.. |the repository service| replace:: GitHub
.. |contribute button| replace:: "Create pull request"

.. _repository: https://github.com/ggrlab/otcyto
.. _issue tracker: https://github.com/ggrlab/otcyto/issues
.. <-- end -->


.. |virtualenv| replace:: ``virtualenv``
.. |pre-commit| replace:: ``pre-commit``


.. _docstrings: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
.. _ruff: https://docs.astral.sh/ruff/
.. _git: https://git-scm.com
.. _GitHub's fork and pull request workflow: https://guides.github.com/activities/forking/
.. _guide created by FreeCodeCamp: https://github.com/FreeCodeCamp/how-to-contribute-to-open-source
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _MyST: https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html
.. _other kinds of contributions: https://opensource.guide/how-to-contribute
.. _pre-commit: https://pre-commit.com/
.. _PyPI: https://pypi.org/
.. _PyScaffold's contributor's guide: https://pyscaffold.org/en/stable/contributing.html
.. _Pytest can drop you: https://docs.pytest.org/en/stable/how-to/failures.html#using-python-library-pdb-with-pytest
.. _Python Software Foundation's Code of Conduct: https://www.python.org/psf/conduct/
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/
.. _virtual environment: https://realpython.com/python-virtual-environments-a-primer/
.. _virtualenv: https://virtualenv.pypa.io/en/stable/

.. _GitHub web interface: https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files
.. _GitHub's code editor: https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files
