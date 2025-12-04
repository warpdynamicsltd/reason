import unittest

from reason.tools.math.transform import str_to_var, var_to_str


class TestStrToVar(unittest.TestCase):
    def test_alphanumeric_unchanged(self):
        """Test that alphanumeric characters remain unchanged."""
        self.assertEqual(str_to_var("hello"), "hello")
        self.assertEqual(str_to_var("Hello123"), "Hello123")
        self.assertEqual(str_to_var("abc123XYZ"), "abc123XYZ")

    def test_underscore_encoding(self):
        """Test that underscores are encoded as double underscores."""
        self.assertEqual(str_to_var("hello_world"), "hello__world")
        self.assertEqual(str_to_var("_private"), "__private")
        self.assertEqual(str_to_var("test__double"), "test____double")
        self.assertEqual(str_to_var("___"), "______")

    def test_space_encoding(self):
        """Test that spaces are encoded correctly."""
        self.assertEqual(str_to_var("hello world"), "hello_u20_world")
        self.assertEqual(str_to_var(" "), "_u20_")

    def test_special_chars_ascii(self):
        """Test encoding of special ASCII characters."""
        self.assertEqual(str_to_var("test@email.com"), "test_u40_email_u2e_com")
        self.assertEqual(str_to_var("hello!"), "hello_u21_")
        self.assertEqual(str_to_var("a+b=c"), "a_u2b_b_u3d_c")
        self.assertEqual(str_to_var("$100"), "_u24_100")

    def test_unicode_bmp(self):
        """Test encoding of Unicode characters in Basic Multilingual Plane."""
        # Greek letter alpha (U+03B1)
        self.assertEqual(str_to_var("α"), "_u03b1_")
        # Emoji (U+1F600) - beyond BMP
        self.assertEqual(str_to_var("😀"), "_u0001f600_")

    def test_mixed_content(self):
        """Test strings with mixed alphanumeric, underscores, and special chars."""
        self.assertEqual(str_to_var("func_name!"), "func__name_u21_")
        self.assertEqual(str_to_var("test-case_1"), "test_u2d_case__1")
        self.assertEqual(str_to_var("a_b@c.d"), "a__b_u40_c_u2e_d")

    def test_empty_string(self):
        """Test encoding of empty string."""
        self.assertEqual(str_to_var(""), "")

    def test_only_special_chars(self):
        """Test strings containing only special characters."""
        self.assertEqual(str_to_var("!!!"), "_u21__u21__u21_")
        self.assertEqual(str_to_var("@#$"), "_u40__u23__u24_")


class TestVarToStr(unittest.TestCase):
    def test_alphanumeric_unchanged(self):
        """Test that alphanumeric characters remain unchanged."""
        self.assertEqual(var_to_str("hello"), "hello")
        self.assertEqual(var_to_str("Hello123"), "Hello123")
        self.assertEqual(var_to_str("abc123XYZ"), "abc123XYZ")

    def test_underscore_decoding(self):
        """Test that double underscores are decoded to single underscores."""
        self.assertEqual(var_to_str("hello__world"), "hello_world")
        self.assertEqual(var_to_str("__private"), "_private")
        self.assertEqual(var_to_str("test____double"), "test__double")
        self.assertEqual(var_to_str("______"), "___")

    def test_space_decoding(self):
        """Test that encoded spaces are decoded correctly."""
        self.assertEqual(var_to_str("hello_u20_world"), "hello world")
        self.assertEqual(var_to_str("_u20_"), " ")

    def test_special_chars_ascii(self):
        """Test decoding of special ASCII characters."""
        self.assertEqual(var_to_str("test_u40_email_u2e_com"), "test@email.com")
        self.assertEqual(var_to_str("hello_u21_"), "hello!")
        self.assertEqual(var_to_str("a_u2b_b_u3d_c"), "a+b=c")
        self.assertEqual(var_to_str("_u24_100"), "$100")

    def test_unicode_bmp(self):
        """Test decoding of Unicode characters in Basic Multilingual Plane."""
        # Greek letter alpha (U+03B1)
        self.assertEqual(var_to_str("_u03b1_"), "α")
        # Emoji (U+1F600) - beyond BMP
        self.assertEqual(var_to_str("_u0001f600_"), "😀")

    def test_mixed_content(self):
        """Test decoding strings with mixed content."""
        self.assertEqual(var_to_str("func__name_u21_"), "func_name!")
        self.assertEqual(var_to_str("test_u2d_case__1"), "test-case_1")
        self.assertEqual(var_to_str("a__b_u40_c_u2e_d"), "a_b@c.d")

    def test_empty_string(self):
        """Test decoding of empty string."""
        self.assertEqual(var_to_str(""), "")

    def test_only_special_chars(self):
        """Test decoding strings containing only special characters."""
        self.assertEqual(var_to_str("_u21__u21__u21_"), "!!!")
        self.assertEqual(var_to_str("_u40__u23__u24_"), "@#$")

    def test_invalid_encoding_trailing_underscore(self):
        """Test that invalid encoding with trailing underscore raises error."""
        with self.assertRaises(ValueError):
            var_to_str("test_")

    def test_invalid_encoding_no_closing_underscore(self):
        """Test that invalid encoding without closing underscore raises error."""
        with self.assertRaises(ValueError):
            var_to_str("test_u20")

    def test_invalid_encoding_unknown_pattern(self):
        """Test that invalid encoding pattern raises error."""
        with self.assertRaises(ValueError):
            var_to_str("test_x")


class TestRoundTrip(unittest.TestCase):
    def test_round_trip_simple(self):
        """Test that encoding and decoding returns the original string."""
        original = "hello_world"
        encoded = str_to_var(original)
        decoded = var_to_str(encoded)
        self.assertEqual(decoded, original)

    def test_round_trip_special_chars(self):
        """Test round trip with special characters."""
        original = "test@email.com"
        encoded = str_to_var(original)
        decoded = var_to_str(encoded)
        self.assertEqual(decoded, original)

    def test_round_trip_mixed(self):
        """Test round trip with mixed content."""
        test_strings = [
            "simple",
            "with_underscore",
            "with spaces",
            "special!@#$%",
            "unicode_αβγ",
            "emoji_😀_test",
            "complex_test@case.name!123",
            "",
            "___",
            "!!!",
        ]
        for original in test_strings:
            with self.subTest(original=original):
                encoded = str_to_var(original)
                decoded = var_to_str(encoded)
                self.assertEqual(decoded, original)

    def test_round_trip_all_printable_ascii(self):
        """Test round trip with various printable ASCII characters."""
        # Test common special characters
        special_chars = "!\"#$%&'()*+,-./:;<=>?@[\\]^`{|}~"
        for char in special_chars:
            with self.subTest(char=char):
                encoded = str_to_var(char)
                decoded = var_to_str(encoded)
                self.assertEqual(decoded, char)


if __name__ == "__main__":
    unittest.main()