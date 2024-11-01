import os.path
import unittest
from src.article_analysis import identify_criminals
from src.helper_stuff import *
from src import log
from src.site_scrapping import scrap_text_from_article

# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':

    serialize_small_table(["Juck", "Jonh"], "/".join(__file__.split("/")[:-2])+"/test.csv")
