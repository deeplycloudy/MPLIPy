Matplotlib / IPython / jQuery UI interaction
============================================

The examples below show a methodology for creating a (cross-platform) user-interface for a Matplotlib plot within an IPython notebook.

Based on the callbacks example from the IPython-in-depth tutorial from SciPy 2012.

About the Examples
==================

IB4D_pipeline.py
----------------

The example demonstrates how to use a coroutine-based pipeline approach to processing from initial dataset to a subsetted, transformed, or otherwise filtered plot of the data. This pipeline is triggered every time the user ceases interacting with the plot, reselecting and synchronizing the data across all four plots.

The four-dimensional (space and time) nature of the data is a complicated visualization task, and the pipeline is an experiment in finding a good API for doing several things:

	- concisely telling the data to represent itself on multiple axes
	- making sure that if data appear on one plot, they are represented on all others
	- making it possible to insert other data transformations, like a map projection
	- respond to user interaction

pipeline-ui.ipynb
-----------------

The IPython notebook _pipeline-ui_ demonstrates how to embed a jQuery-based user interface in an IPython notebook. Interaction with the plot or UI is indicated visually in both the UI and the plot.

Some knowledge of JavaScript is necessary to set up the bridge between Matplotlib and IPython. However, HTML/CSS/js layout tools are now quite mature, and make it easy for the scientist to sketch up an interface with non-specialist tools. IPython solves most of the hard parts of writing the cross-language bridge, too.


Future
======

Refinements to both the data pipeline and the JavaScript/IPython UI bridge APIs are welcome.