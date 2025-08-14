#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='model_agnostic_toolkit',
      version='1.0.0',
      description='A package for model agnostic interpretable methods. Supports regression and classification.',
      long_description='The Model Agnostic Toolkit is a package for determining the effect of individual features and their interplay toward a target variable for tabular datasets. It includes a multitude of tools for two main applications: individual feature importances (how does a single feature affect the target?) and feature pair interactions (what effects toward the target exist between features?). For more details, please refer to the project documentation.',
      long_description_content_type="text/plain",
      author='Tobias Schulze, Chrismarie Enslin, Daniel Buschmann, Marcos Padrón Hinrichs, Felix Sohnius, Robert H. Schmitt',
      author_email='tobias.schulze@wzl-iqs.rwth-aachen.de',
      packages=find_packages(),
      install_requires=[
          'bunch',
          'jupyter',
          'networkx',
          'numpy==1.23.5',
          'pandas',
          'plotly',
          'tables',
          'scikit-learn>=1.0,<1.3',
          'shap',
          'cdt',
          'pgmpy',
          'pyale',
          'torch',
          'xgboost>=1.2',
          'IPython',
          'PDPbox==0.3.0',
          'joblib',
          'psutil',
          'alibi',
          'charset-normalizer==3.1.0',
          'seaborn',
          'ray'
      ],

      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
      ],
      )