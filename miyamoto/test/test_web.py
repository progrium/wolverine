from twisted.trial import unittest
from miyamoto.web import MiyamotoResource

class TestIndex(unittest.TestCase):
    def testReadsTemplate(self):
        html = MiyamotoResource().index()
        self.assertIn("<h2>Create subscription</h2>", html)
        
