"""
testNotebooks.py

Unit tests verifying functionality of (some) pyGMs jupyter notebooks

Version 0.1.1 (2022-04-06)
(c) 2019- Alexander Ihler under the FreeBSD license; see license.txt for details.
"""

import unittest
import numpy as np
import time
import sys
sys.path.append('../../')

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

notebook_path = '../notebooks/'

notebooks = [
##    'pyGM_CSP_1.ipynb',           # slow
    'pyGM_CSP_2.ipynb',             # 3 sec ; local search methods
    'pyGM_BayesNet.ipynb',          # 4 sec ; simple burglary model
    'Demo - Search.ipynb',          # 3 sec ; A* search
    'Demo - Mean Field.ipynb',      # 4 sec 
    'Demo - LoopyBP.ipynb',         # 4 sec
    'pyGM Inference Methods.ipynb', # 7 sec
    'Gaussian Graphical Models.ipynb',   ## TODO: incomplete notebook...
    'pyGM_Learning_Basics.ipynb',   # 4 sec
    'pyGM_ChowLiu.ipynb',           # 4 sec
    'pyGM-MonteCarlo.ipynb',        # 8 sec
##    'Demo - MonteCarlo.ipynb',    # 80sec  (slow)
    'pyGM_HMM.ipynb',               # 5 sec
    'Wildcatter.ipynb',           # 4 sec
    'POMDP-LIMID.ipynb'             # 5 sec
]



def run_notebook(notebook_filename, verbose=True):
    if verbose: 
      sys.stdout.write('Running notebook "{}"...'.format(notebook_filename))
      sys.stdout.flush()
    with open(notebook_path + notebook_filename) as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    tic = time.time()
    
    try:
        #np.seterr(divide='ignore')
        out = ep.preprocess(nb, {'metadata': {'path': '../notebooks'}})
    except:
        out = None
        print('Error while executing notebook "{}".\n'.format(notebook_filename))
        raise
    if verbose: sys.stdout.write("   done; {} seconds\n".format(time.time()-tic))


class testNotebooks(unittest.TestCase):

  def setUp(self):
    return

  def testAll(self):
    for n in notebooks:
      run_notebook(n)





if __name__ == '__main__':
  unittest.main()



