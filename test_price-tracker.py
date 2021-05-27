from price_tracker import create_app, utils
import config
import unittest
from datetime import datetime, timedelta


class PriceTrackerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config.TestingConfig)
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_ctx.pop()

    def test_landing(self):
        response = self.client.get("/")
        self.assertIn(b"Save more when shopping online", response.data)


    def test_login(self):
        response = self.client.post("/login", data={"email": "wrong.email@gmail.com", "password": "1234"}, follow_redirects=True)
        self.assertIn(b"Incorrect email/password combination or unverified email", response.data)

        response = self.client.post("/login", data={"email": "alexandre.araiza@gmail.com", "password": "test"}, follow_redirects=True)
        self.assertIn(b"Log out", response.data)


    def test_new_item(self):
        self.client.post("/login", data={"email": "alexandre.araiza@gmail.com", "password": "test"}, follow_redirects=True)

        response = self.client.post("/items/new", data={"name": "test_item", "url": "wrongURL", "current_price": "wrong_price", "currency": "wrong_currency"}, follow_redirects=True)
        self.assertIn(b"Invalid URL", response.data)
        self.assertIn(b"Invalid price", response.data)

        response = self.client.post("/items/new", data={"name": "test_item", "url": "https://www.google.com/", "current_price": "3874272880817877", "currency": "USD"}, follow_redirects=True)
        self.assertIn(b"Could not find the price of <span class='price'>USD3874272880817877.00</span>. <a href='/faq'>Why?</a>", response.data)


    def test_logout(self):
        response = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Save more when shopping online", response.data)

        response = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Save more when shopping online", response.data)


    def test_utils(self):
        self.assertEqual(utils.get_regex_string_from_number(1), "1")
        self.assertEqual(utils.get_regex_string_from_number(10), "1[.,' ]?0")
        self.assertEqual(utils.get_regex_string_from_number(10.01), "1[.,' ]?0[.,' ]01")
        self.assertEqual(utils.get_regex_string_from_number(1000.0001), "1[.,' ]?0[.,' ]?0[.,' ]?0[.,' ]0001")
        self.assertEqual(utils.get_float_from_string("1"), 1.0)
        self.assertEqual(utils.get_float_from_string("1,000,00"), 100000.0)
        self.assertEqual(utils.get_float_from_string("1_000.01"), 1000.01)
        self.assertEqual(utils.get_float_from_string("1000.0001"), 1000.0001)
        self.assertEqual(utils.get_float_from_string("1,000.0001"), 1000.0001)
        self.assertTrue(utils.price_is_in_string(1, "1,00"))
        self.assertTrue(utils.price_is_in_string(1000, "1,,,000"))
        self.assertTrue(utils.price_is_in_string(1000.0001, "1,000.0001"))
        self.assertEqual(utils.get_time_since_month_start(datetime(2021, 7, 2, 12, 0, 0)), timedelta(1, 43200))


if __name__ == "__main__":
    unittest.main()