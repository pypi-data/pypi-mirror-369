"""
Tests for Base58 class.

This module contains comprehensive tests for the Base58 class
including encoding/decoding and validation functionality.
"""

import random
import threading
import time
import unittest
import pytest
from splurge_tools.base58 import Base58
from splurge_tools.exceptions import SplurgeValidationError


class TestBase58Encoding(unittest.TestCase):
    """Test cases for Base58 encoding functionality."""
    
    def test_encode_simple_string(self):
        """Test encoding a simple string."""
        data = b"Hello World"
        encoded = Base58.encode(data)
        self.assertIsInstance(encoded, str)
        self.assertGreater(len(encoded), 0)
        
        # Verify round-trip
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, data)
    
    def test_encode_single_byte(self):
        """Test encoding a single byte."""
        data = b"A"
        encoded = Base58.encode(data)
        self.assertIsInstance(encoded, str)
        
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, data)
    
    def test_encode_zero_bytes(self):
        """Test encoding zero bytes."""
        data = b"\x00"
        encoded = Base58.encode(data)
        self.assertEqual(encoded, "1")
        
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, data)
    
    def test_encode_all_zero_bytes(self):
        """Test encoding all zero bytes."""
        data = b"\x00\x00\x00"
        encoded = Base58.encode(data)
        self.assertEqual(encoded, "111")
        
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, data)
    
    def test_encode_mixed_zero_and_data(self):
        """Test encoding data with leading zeros."""
        data = b"\x00\x00\x01\x02"
        encoded = Base58.encode(data)
        self.assertIsInstance(encoded, str)
        
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, data)
    
    def test_encode_large_data(self):
        """Test encoding large data."""
        data = b"x" * 500  # Reduced from 1000 to 500 bytes for faster testing
        encoded = Base58.encode(data)
        self.assertIsInstance(encoded, str)
        
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, data)
    
    def test_encode_very_large_data(self):
        """Test encoding very large data."""
        data = b"x" * 2000  
        encoded = Base58.encode(data)
        self.assertIsInstance(encoded, str)
        
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, data)
    
    def test_encode_unicode_bytes(self):
        """Test encoding unicode bytes."""
        data = "Hello🚀World".encode('utf-8')
        encoded = Base58.encode(data)
        self.assertIsInstance(encoded, str)
        
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, data)
    
    def test_encode_bytearray_input(self):
        """Test encoding bytearray input."""
        data = bytearray(b"Hello World")
        encoded = Base58.encode(data)
        self.assertIsInstance(encoded, str)
        
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, bytes(data))
    
    def test_encode_boundary_values(self):
        """Test encoding boundary values."""
        # Test with single byte values
        for i in range(256):
            data = bytes([i])
            encoded = Base58.encode(data)
            decoded = Base58.decode(encoded)
            self.assertEqual(decoded, data)
    
    def test_encode_empty_data_raises_error(self):
        """Test that encoding empty data raises error."""
        with self.assertRaises(SplurgeValidationError):
            Base58.encode(b"")


class TestBase58Decoding(unittest.TestCase):
    """Test cases for Base58 decoding functionality."""
    
    def test_decode_simple_string(self):
        """Test decoding a simple string."""
        string = "JxF12TrwUP45BMd"
        decoded = Base58.decode(string)
        self.assertEqual(decoded, b"Hello World")
    
    def test_decode_single_character(self):
        """Test decoding a single character."""
        decoded = Base58.decode("1")
        self.assertEqual(decoded, b"\x00")
    
    def test_decode_zero_bytes(self):
        """Test decoding zero bytes."""
        decoded = Base58.decode("111")
        self.assertEqual(decoded, b"\x00\x00\x00")
    
    def test_decode_all_ones(self):
        """Test decoding all ones (all zero bytes)."""
        length = 10
        string = "1" * length
        decoded = Base58.decode(string)
        self.assertEqual(decoded, b"\x00" * length)
    
    def test_decode_very_long_string(self):
        """Test decoding a very long string."""
        length = 500  
        string = "1" * length
        decoded = Base58.decode(string)
        self.assertEqual(decoded, b"\x00" * length)
    
    def test_decode_boundary_characters(self):
        """Test decoding boundary characters."""
        self.assertEqual(Base58.decode("1"), b"\x00")  # First character
        self.assertEqual(Base58.decode("z"), b"9")  # Last character
    
    def test_decode_empty_string_raises_error(self):
        """Test that decoding empty string raises error."""
        with self.assertRaises(SplurgeValidationError):
            Base58.decode("")
    
    def test_decode_invalid_characters_raises_error(self):
        """Test that decoding invalid characters raises error."""
        with self.assertRaises(SplurgeValidationError):
            Base58.decode("invalid!")
    
    def test_decode_malformed_strings(self):
        """Test decoding malformed strings."""
        invalid_strings = [
            "0",  # Invalid character
            "O",  # Invalid character
            "I",  # Invalid character
            "l",  # Invalid character
        ]
        
        for string in invalid_strings:
            with self.assertRaises(SplurgeValidationError):
                Base58.decode(string)
    
    def test_decode_unicode_strings(self):
        """Test decoding unicode strings."""
        with self.assertRaises(SplurgeValidationError):
            Base58.decode("Hello🚀World")
    
    def test_round_trip_encoding(self):
        """Test round-trip encoding and decoding."""
        test_data = [
            b"Hello World",
            b"",
            b"\x00\x01\x02\x03",
            b"x" * 100,
            b"Unicode: \xf0\x9f\x9a\x80",  # Rocket emoji in UTF-8
        ]
        
        for data in test_data:
            if data:  # Skip empty data as it raises error
                encoded = Base58.encode(data)
                decoded = Base58.decode(encoded)
                self.assertEqual(decoded, data)


class TestBase58Validation(unittest.TestCase):
    """Test cases for Base58 validation functionality."""
    
    def test_valid_base58_strings(self):
        """Test validation of valid base-58 strings."""
        valid_strings = [
            "1",
            "z",
            "JxF12TrwUP45BMd",
            "111",
            "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
        ]
        
        for string in valid_strings:
            self.assertTrue(Base58.is_valid_base58(string))
    
    def test_invalid_base58_strings(self):
        """Test validation of invalid base-58 strings."""
        invalid_strings = [
            "",
            "0",
            "O",
            "I",
            "l",
            "invalid!",
            "Hello World",
            "🚀",
        ]
        
        for string in invalid_strings:
            self.assertFalse(Base58.is_valid_base58(string))
    
    def test_edge_cases(self):
        """Test edge cases for validation."""
        # Test with None
        self.assertFalse(Base58.is_valid_base58(None))
        
        # Test with non-string types
        self.assertFalse(Base58.is_valid_base58(123))
        self.assertFalse(Base58.is_valid_base58(b"bytes"))
        self.assertFalse(Base58.is_valid_base58(["list"]))
    
    def test_validation_with_unicode_strings(self):
        """Test validation with unicode strings."""
        self.assertFalse(Base58.is_valid_base58("Hello🚀World"))
    
    def test_validation_with_non_string_inputs(self):
        """Test validation with non-string inputs."""
        non_string_inputs = [
            None,
            123,
            b"bytes",
            ["list"],
            {"dict": "value"},
            (1, 2, 3),
        ]
        
        for input_val in non_string_inputs:
            self.assertFalse(Base58.is_valid_base58(input_val))


class TestBase58Integration(unittest.TestCase):
    """Integration tests for Base58 encoding/decoding."""
    
    def test_cryptographic_key_encoding(self):
        """Test encoding/decoding cryptographic keys."""
        # Simulate a cryptographic key
        key = b"\x00" * 32  # 32-byte key
        encoded = Base58.encode(key)
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, key)
    
    def test_bitcoin_address_style_encoding(self):
        """Test encoding/decoding in Bitcoin address style."""
        # Simulate a public key hash (20 bytes)
        public_key_hash = b"\x00" * 20
        encoded = Base58.encode(public_key_hash)
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, public_key_hash)
    
    def test_random_binary_data(self):
        """Test encoding/decoding random binary data."""
        for _ in range(10):
            # Generate random data of varying lengths
            length = random.randint(1, 100)
            data = bytes(random.randint(0, 255) for _ in range(length))
            
            encoded = Base58.encode(data)
            decoded = Base58.decode(encoded)
            self.assertEqual(decoded, data)
    
    def test_concurrent_encoding_decoding(self):
        """Test concurrent encoding and decoding operations."""
        def encode_decode_worker():
            data = b"Hello World"
            for _ in range(100):
                encoded = Base58.encode(data)
                decoded = Base58.decode(encoded)
                self.assertEqual(decoded, data)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=encode_decode_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
    
    def test_memory_efficiency(self):
        """Test memory efficiency with large data."""
        # Test with large data to ensure no memory leaks
        data = b"x" * 2000  
        for _ in range(50):  
            encoded = Base58.encode(data)
            decoded = Base58.decode(encoded)
            self.assertEqual(decoded, data)
    
    def test_performance_with_large_data(self):
        """Test performance with large data."""
        data = b"x" * 1000  
        start_time = time.time()
        
        for _ in range(50):  
            encoded = Base58.encode(data)
            decoded = Base58.decode(encoded)
            self.assertEqual(decoded, data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in reasonable time (less than 5 seconds)
        self.assertLess(duration, 5.0)


class TestBase58ErrorHandling(unittest.TestCase):
    """Test cases for error handling and edge cases."""
    
    def test_encoding_with_none_input(self):
        """Test encoding with None input."""
        with self.assertRaises(SplurgeValidationError):
            Base58.encode(None)
    
    def test_encoding_with_string_input(self):
        """Test encoding with string input (should fail)."""
        with self.assertRaises(TypeError):
            Base58.encode("Hello World")    
    
    def test_decoding_with_none_input(self):
        """Test decoding with None input."""
        with self.assertRaises(SplurgeValidationError):
            Base58.decode(None)
    
    def test_decoding_with_bytes_input(self):
        """Test decoding with bytes input (should fail)."""
        with self.assertRaises(TypeError):
            Base58.decode(b"Hello World")
    
    def test_validation_with_complex_objects(self):
        """Test validation with complex objects."""
        class TestObject:
            def __str__(self):
                return "Hello World"
        
        obj = TestObject()
        self.assertFalse(Base58.is_valid_base58(obj))
    
    def test_encoding_with_very_small_data(self):
        """Test encoding with very small data."""
        data = b"\x00"
        encoded = Base58.encode(data)
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, data)
    
    def test_encoding_with_minimum_values(self):
        """Test encoding with minimum values."""
        min_bytes = b"\x00" * 10
        encoded = Base58.encode(min_bytes)
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, min_bytes)
    
    def test_encoding_with_maximum_values(self):
        """Test encoding with maximum values."""
        max_bytes = b"\xff" * 10
        encoded = Base58.encode(max_bytes)
        decoded = Base58.decode(encoded)
        self.assertEqual(decoded, max_bytes)


# Pytest compatibility - these functions allow pytest to still work
def pytest_raises(exception_type, match=None):
    """Helper function to maintain pytest compatibility."""
    if hasattr(pytest, 'raises'):
        return pytest.raises(exception_type, match=match)
    else:
        # Fallback for unittest
        class ContextManager:
            def __init__(self, exception_type, match=None):
                self.exception_type = exception_type
                self.match = match
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:
                    raise AssertionError(f"{self.exception_type.__name__} was not raised")
                if not issubclass(exc_type, self.exception_type):
                    return False
                if self.match and self.match not in str(exc_val):
                    raise AssertionError(f"Exception message '{str(exc_val)}' does not contain '{self.match}'")
                return True
        
        return ContextManager(exception_type, match)


if __name__ == '__main__':
    # Run with unittest
    unittest.main(verbosity=2) 