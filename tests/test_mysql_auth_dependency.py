"""Regression coverage for MySQL SHA-2 password authentication support."""

import unittest


class MySqlAuthenticationDependencyTests(unittest.TestCase):
    def test_pymysql_has_cryptography_for_sha2_authentication(self) -> None:
        """The packaged client must support sha256_password/caching_sha2_password."""
        import pymysql._auth

        self.assertTrue(
            pymysql._auth._have_cryptography,
            "PyMySQL requires cryptography for sha256_password and caching_sha2_password authentication.",
        )


if __name__ == "__main__":
    unittest.main()
