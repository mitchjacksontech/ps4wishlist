# project/server/tests/test_prodapi.py

import os
import unittest


class TestTarget(unittest.TestCase):
    def test_product_by_title(self):
        from project.prodapi.target import ProductByTitle;
        r=ProductByTitle("No Man's Sky")
        self.assertTrue('title' in r)
        self.assertIn("No Man's Sky", r['title'])

    def test_product_by_title_with_bad_data(self):
        from project.prodapi.target import ProductByTitle;
        r=ProductByTitle("fake_game_name")
        self.assertTrue(r is None)

    def test_product_by_id(self):
        from project.prodapi.target import ProductById;
        r=ProductById("23940687")
        self.assertTrue(r)
        self.assertIn("Dark Souls",r['title'])


class TestPSN(unittest.TestCase):
    def test_product_by_title(self):
        from project.prodapi.psn import ProductByTitle;
        r=ProductByTitle("No Man's Sky")
        self.assertTrue('title' in r)
        self.assertIn("No Man's Sky", r['title'])

    def test_product_by_title_with_bad_data(self):
        from project.prodapi.psn import ProductByTitle;
        r=ProductByTitle("fake_game_name")
        self.assertTrue(r is None)

    def test_product_by_title_with_blank_data(self):
        from project.prodapi.psn import ProductByTitle;
        r=ProductByTitle("")
        self.assertTrue(r is None)
        with self.assertRaises(TypeError):
            r=ProductByTitle()

    def test_product_by_id(self):
        from project.prodapi.psn import ProductById;
        r=ProductById("UP0002-CUSA01842_00-OWORIGINS0000000")
        self.assertTrue(r)
        self.assertIn("Overwatch", r['title'])

    def test_product_by_id_with_bad_data(self):
        from project.prodapi.psn import ProductById;
        r=ProductById("bad_psn_id")
        self.assertTrue(r is None)
        with self.assertRaises(TypeError):
            r=ProductById()


class TestWalMart(unittest.TestCase):
    def test_fail_wo_env_var(self):
        swp_env = os.getenv('WALMART_API_KEY', None)
        if 'WALMART_API_KEY' in os.environ:
            del os.environ['WALMART_API_KEY']

        with self.assertRaises(EnvironmentError):
            import project.prodapi.walmart
        if swp_env:
            os.environ['WALMART_API_KEY'] = swp_env

    @unittest.skipUnless(
        'WALMART_API_KEY' in os.environ,
        'environment variable WALMART_API_KEY not set'
    )
    def test_product_by_upc(self):
        from project.prodapi.walmart import ProductByUPC
        r = ProductByUPC('722674120142')
        self.assertTrue('title' in r)
        self.assertIn('Dark Souls', r['title'])

    @unittest.skipUnless(
        'WALMART_API_KEY' in os.environ,
        'environment variable WALMART_API_KEY not set'
    )
    def test_product_by_upc_with_bad_data(self):
        from project.prodapi.walmart import ProductByUPC
        r = ProductByUPC('12345')
        self.assertTrue(r is None)

    @unittest.skipUnless(
        'WALMART_API_KEY' in os.environ,
        'environment variable WALMART_API_KEY not set'
    )
    def test_proeuct_by_upc_with_missing_params(self):
        from project.prodapi.walmart import ProductByUPC
        with self.assertRaises(TypeError):
            r = ProductByUPC()


class TestBestBuy(unittest.TestCase):
    def test_fail_wo_env_var(self):
        # set case for empty env var
        swp_env = os.getenv('BESTBUY_API_KEY', None)
        if 'BESTBUY_API_KEY' in os.environ:
            del os.environ['BESTBUY_API_KEY']

        # should fail
        with self.assertRaises(EnvironmentError):
            import project.prodapi.bestbuy

        # restore env var
        if swp_env:
            os.environ['BESTBUY_API_KEY'] = swp_env

    @unittest.skipUnless(
        'BESTBUY_API_KEY' in os.environ,
        'environment variable BESTBUY_API_KEY not set')
    def test_product_by_upc(self):
        from project.prodapi.bestbuy import ProductByUPC
        r = ProductByUPC('722674120142')
        self.assertTrue('title' in r)
        self.assertTrue('store_url' in r)
        self.assertIn("Dark Souls", r['title'])

    @unittest.skipUnless(
        'BESTBUY_API_KEY' in os.environ,
        'environment variable BESTBUY_API_KEY not set')
    def test_product_by_upc_with_bad_data(self):
        from project.prodapi.bestbuy import ProductByUPC
        r = ProductByUPC('123456789012')
        self.assertEqual(r,None)

    @unittest.skipUnless(
        'BESTBUY_API_KEY' in os.environ,
        'environment variable BESTBUY_API_KEY not set')
    def test_product_by_upc_with_bad_params(self):
        from project.prodapi.bestbuy import ProductByUPC
        with self.assertRaises(TypeError):
            ProductByUPC()


class TestAmazon(unittest.TestCase):

    @unittest.skip("Not sure why this breaks all other tests")
    def test_fail_wo_env_var(self):
        # temporarily sideline env variables
        ak = ['AMAZON_ACCESS_KEY','AMAZON_SECRET_KEY','AMAZON_ASSOC_TAG']
        sk = {}
        for k in ak:
            sk[k] = os.getenv(k,None)
            if k in os.environ:
                del os.environ[k]

        # should fail
        with self.assertRaises(EnvironmentError):
            import project.prodapi.amazon

        # restore env var
        for k in ak:
            if sk[k]:
                os.environ[k] = sk[k]

    @unittest.skipUnless(
        'AMAZON_ACCESS_KEY' in os.environ,
        'environment variable AMAZON_ACCESS_KEY not set'
    )
    def test_product_by_upc(self):
        from project.prodapi.amazon import ProductByUPC
        r = ProductByUPC('722674120142')
        self.assertTrue('title' in r)
        self.assertIn('Dark Souls',r['title'])

    @unittest.skipUnless(
        'AMAZON_ACCESS_KEY' in os.environ,
        'environment variable AMAZON_ACCESS_KEY not set'
    )
    def test_product_by_upc_with_bad_data(self):
        from project.prodapi.amazon import ProductByUPC
        r=ProductByUPC('234234')
        self.assertTrue(r is None)

    @unittest.skipUnless(
        'AMAZON_ACCESS_KEY' in os.environ,
        'environment variable AMAZON_ACCESS_KEY not set'
    )
    def test_product_search(self):
        from project.prodapi.amazon import ProductSearch
        r=ProductSearch('Dark Souls 3')
        self.assertTrue(r)
        self.assertIn('Dark Souls',r[0]['title'])

    @unittest.skipUnless(
        'AMAZON_ACCESS_KEY' in os.environ,
        'environment variable AMAZON_ACCESS_KEY not set'
    )
    def test_product_search_with_bad_search(self):
        from project.prodapi.amazon import ProductSearch
        r=ProductSearch(';lkjwe9ijklsadfjsdf')
        self.assertTrue(r is None)

    @unittest.skipUnless(
        'AMAZON_ACCESS_KEY' in os.environ,
        'environment variable AMAZON_ACCESS_KEY not set'
    )
    def test_product_by_id(self):
        from project.prodapi.amazon import ProductById
        r=ProductById("B00Z9LUFHS")
        self.assertTrue(r)
        self.assertIn('Dark Souls',r['title'])

    @unittest.skipUnless(
        'AMAZON_ACCESS_KEY' in os.environ,
        'environment variable AMAZON_ACCESS_KEY not set'
    )
    def test_product_by_id_with_bad_data(self):
        from project.prodapi.amazon import ProductById
        r=ProductById("asdfasdfsfd")
        self.assertTrue(r is None)


if __name__ == '__main__':
    unittest.main()
