

"""
testData.py

Unit tests for pyGMs data/model loader functions

Version 0.3.0 (2025-08-15)
(c) 2015-2021 Alexander Ihler under the FreeBSD license; see license.txt for details.
"""

import unittest
import numpy as np
import sys
sys.path.append('../../')
import pyGMs as gm
from pyGMs.data import models
import tempfile


class testFactor(unittest.TestCase):
    
    def setUp(self):
        return

    def testInitialCache(self): 
        from pyGMs.data import models
        self.assertTrue('alchemy' in models.keys())

    def testGetModelStats(self):
        from pyGMs.data import models
        self.assertTrue('smokers_10' in models['alchemy'].keys())
        self.assertEqual(models['alchemy']['smokers_10'].max_states, 2)

    def testSubIndex(self):
        from pyGMs.data import models
        self.assertEqual(models['alchemy/smokers_10'].max_states, 2)

    def testProvidedCache(self):
        from pyGMs.data import models
        new_cache = tempfile.TemporaryDirectory()
        models.set_cache( new_cache.name )
        self.assertEqual(models.cache, new_cache.name)
        self.assertEqual(models['alchemy/smokers_10'].max_states, 2)
        self.assertEqual(models.cache, new_cache.name)
        models.set_cache(None)
        new_cache.cleanup()

if __name__ == '__main__':
    unittest.main()



