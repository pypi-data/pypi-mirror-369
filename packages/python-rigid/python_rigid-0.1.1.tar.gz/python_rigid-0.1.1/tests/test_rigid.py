import time
import unittest

from ulid import ULID

from rigid import Rigid


class TestRigid(unittest.TestCase):
    def setUp(self):
        self.secret_key = b"test_secret_key_123456789"
        self.rigid = Rigid(self.secret_key)

    def test_init_with_default_signature_length(self):
        rigid = Rigid(b"test_key")
        self.assertEqual(rigid.secret_key, b"test_key")
        self.assertEqual(rigid.signature_length, 8)

    def test_init_with_custom_signature_length(self):
        rigid = Rigid(b"test_key", signature_length=16)
        self.assertEqual(rigid.secret_key, b"test_key")
        self.assertEqual(rigid.signature_length, 16)

    def test_generate_without_metadata(self):
        secure_ulid = self.rigid.generate()
        parts = secure_ulid.split('-')
        self.assertEqual(len(parts), 2)

        ulid_str, signature = parts
        self.assertEqual(len(ulid_str), 26)
        self.assertGreater(len(signature), 0)

        ULID.from_str(ulid_str)

    def test_generate_with_metadata(self):
        metadata = "user_123"
        secure_ulid = self.rigid.generate(metadata=metadata)
        parts = secure_ulid.split('-')
        self.assertEqual(len(parts), 3)

        ulid_str, signature, returned_metadata = parts
        self.assertEqual(len(ulid_str), 26)
        self.assertGreater(len(signature), 0)
        self.assertEqual(returned_metadata, metadata)

        ULID.from_str(ulid_str)

    def test_verify_valid_ulid_without_metadata(self):
        secure_ulid = self.rigid.generate()
        is_valid, ulid_str, metadata = self.rigid.verify(secure_ulid)

        self.assertTrue(is_valid)
        self.assertIsNotNone(ulid_str)
        self.assertEqual(len(ulid_str), 26)
        self.assertIsNone(metadata)

    def test_verify_valid_ulid_with_metadata(self):
        test_metadata = "test_metadata"
        secure_ulid = self.rigid.generate(metadata=test_metadata)
        is_valid, ulid_str, metadata = self.rigid.verify(secure_ulid)

        self.assertTrue(is_valid)
        self.assertIsNotNone(ulid_str)
        self.assertEqual(len(ulid_str), 26)
        self.assertEqual(metadata, test_metadata)

    def test_verify_invalid_ulid_wrong_secret(self):
        secure_ulid = self.rigid.generate()

        different_rigid = Rigid(b"different_secret_key")
        is_valid, ulid_str, metadata = different_rigid.verify(secure_ulid)

        self.assertFalse(is_valid)
        self.assertIsNone(ulid_str)
        self.assertIsNone(metadata)

    def test_verify_malformed_ulid_single_part(self):
        is_valid, ulid_str, metadata = self.rigid.verify("invalid_format")

        self.assertFalse(is_valid)
        self.assertIsNone(ulid_str)
        self.assertIsNone(metadata)

    def test_verify_malformed_ulid_too_many_parts(self):
        is_valid, ulid_str, metadata = self.rigid.verify("part1-part2-part3-part4")

        self.assertFalse(is_valid)
        self.assertIsNone(ulid_str)
        self.assertIsNone(metadata)

    def test_verify_invalid_ulid_format(self):
        is_valid, ulid_str, metadata = self.rigid.verify("INVALID_ULID-SIGNATURE")

        self.assertFalse(is_valid)
        self.assertIsNone(ulid_str)
        self.assertIsNone(metadata)

    def test_verify_tampered_signature(self):
        secure_ulid = self.rigid.generate()
        parts = secure_ulid.split('-')
        tampered_ulid = f"{parts[0]}-TAMPERED"

        is_valid, ulid_str, metadata = self.rigid.verify(tampered_ulid)

        self.assertFalse(is_valid)
        self.assertIsNone(ulid_str)
        self.assertIsNone(metadata)

    def test_verify_tampered_ulid(self):
        secure_ulid = self.rigid.generate()
        parts = secure_ulid.split('-')

        valid_ulid = ULID()
        tampered_ulid = f"{str(valid_ulid)}-{parts[1]}"

        is_valid, ulid_str, metadata = self.rigid.verify(tampered_ulid)

        self.assertFalse(is_valid)
        self.assertIsNone(ulid_str)
        self.assertIsNone(metadata)

    def test_extract_ulid_valid(self):
        secure_ulid = self.rigid.generate()
        original_ulid_str = secure_ulid.split('-')[0]

        extracted_ulid = self.rigid.extract_ulid(secure_ulid)

        self.assertIsNotNone(extracted_ulid)
        self.assertIsInstance(extracted_ulid, ULID)
        self.assertEqual(str(extracted_ulid), original_ulid_str)

    def test_extract_ulid_invalid(self):
        extracted_ulid = self.rigid.extract_ulid("invalid-signature")

        self.assertIsNone(extracted_ulid)

    def test_extract_timestamp_valid(self):
        before_generation = time.time()
        secure_ulid = self.rigid.generate()
        after_generation = time.time()

        timestamp = self.rigid.extract_timestamp(secure_ulid)

        self.assertIsNotNone(timestamp)
        self.assertLess(abs(timestamp - before_generation), 1)

    def test_extract_timestamp_invalid(self):
        timestamp = self.rigid.extract_timestamp("invalid-signature")

        self.assertIsNone(timestamp)

    def test_encode_base32_zero(self):
        result = Rigid._encode_base32(b'\x00')
        self.assertEqual(result, '0')

    def test_encode_base32_non_zero(self):
        result = Rigid._encode_base32(b'\x01\x02\x03')
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        for char in result:
            self.assertIn(char, "0123456789ABCDEFGHJKMNPQRSTVWXYZ")

    def test_encode_base32_different_inputs(self):
        result1 = Rigid._encode_base32(b'\x01')
        result2 = Rigid._encode_base32(b'\x02')

        self.assertNotEqual(result1, result2)

    def test_different_signature_lengths(self):
        rigid_short = Rigid(self.secret_key, signature_length=4)
        rigid_long = Rigid(self.secret_key, signature_length=16)

        ulid_short = rigid_short.generate()
        ulid_long = rigid_long.generate()

        short_sig_len = len(ulid_short.split('-')[1])
        long_sig_len = len(ulid_long.split('-')[1])

        self.assertLess(short_sig_len, long_sig_len)

    def test_signature_length_consistency(self):
        rigid = Rigid(self.secret_key, signature_length=12)

        ulid1 = rigid.generate()
        ulid2 = rigid.generate()

        sig1_len = len(ulid1.split('-')[1])
        sig2_len = len(ulid2.split('-')[1])

        self.assertEqual(sig1_len, sig2_len)

    def test_metadata_with_special_characters(self):
        metadata = "user:123@domain.com"
        secure_ulid = self.rigid.generate(metadata=metadata)

        is_valid, ulid_str, extracted_metadata = self.rigid.verify(secure_ulid)

        self.assertTrue(is_valid)
        self.assertEqual(extracted_metadata, metadata)

    def test_empty_metadata(self):
        secure_ulid = self.rigid.generate(metadata="")
        parts = secure_ulid.split('-')

        self.assertEqual(len(parts), 2)

    def test_timing_attack_resistance(self):
        valid_ulid = self.rigid.generate()

        start1 = time.perf_counter()
        self.rigid.verify(valid_ulid)
        time1 = time.perf_counter() - start1

        start2 = time.perf_counter()
        self.rigid.verify("01FHQB0AM4-INVALID")
        time2 = time.perf_counter() - start2

        time_diff = abs(time1 - time2)
        self.assertLess(time_diff, 0.001)

    def test_generate_uniqueness(self):
        ulids = set()
        for _ in range(100):
            secure_ulid = self.rigid.generate()
            self.assertNotIn(secure_ulid, ulids)
            ulids.add(secure_ulid)

    def test_cross_verification_different_instances(self):
        rigid1 = Rigid(self.secret_key)
        rigid2 = Rigid(self.secret_key)

        secure_ulid = rigid1.generate()
        is_valid, ulid_str, metadata = rigid2.verify(secure_ulid)

        self.assertTrue(is_valid)
        self.assertIsNotNone(ulid_str)

    def test_ulid_ordering(self):
        ulids = []
        for _ in range(10):
            secure_ulid = self.rigid.generate()
            ulid_obj = self.rigid.extract_ulid(secure_ulid)
            ulids.append(str(ulid_obj))
            time.sleep(0.001)

        sorted_ulids = sorted(ulids)
        self.assertEqual(ulids, sorted_ulids)


if __name__ == '__main__':
    unittest.main()
