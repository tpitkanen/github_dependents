import unittest

import load_dependents


class TestBuildUrl(unittest.TestCase):
    def setUp(self) -> None:
        self.expected = "https://github.com/tpitkanen/github_dependents/network/dependents"

    def test_no_dependents(self):
        url = "https://github.com/tpitkanen/github_dependents"
        url = load_dependents._build_url(url)
        self.assertEqual(self.expected, url)

    def test_already_dependents(self):
        url = "https://github.com/tpitkanen/github_dependents/network/dependents"
        url = load_dependents._build_url(url)
        self.assertEqual(self.expected, url)

    def test_unsupported_url(self):
        url = "https://example.org/tpitkanen/github_dependents/network/dependents"
        self.assertRaisesRegex(
            load_dependents.UrlError,
            "Unsupported URL: 'https://example.org/tpitkanen/github_dependents/network/dependents'",
            load_dependents._build_url, url)
