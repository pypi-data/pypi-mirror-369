import hashlib
import hmac
from typing import Optional, Tuple

from ulid import ULID


class Rigid:
    def __init__(self, secret_key: bytes, signature_length: int = 8):
        """
        Initialize Rigid generator with HMAC integrity.

        Args:
            secret_key: Secret key for HMAC generation
            signature_length: Number of signature bytes to include (default 8)
        """
        self.secret_key = secret_key
        self.signature_length = signature_length

    def generate(self, metadata: Optional[str] = None) -> str:
        """
        Generate a ULID with HMAC signature.

        Args:
            metadata: Optional metadata to include in HMAC (e.g., user_id, resource_type)

        Returns:
            String in format: "ULID-SIGNATURE" or "ULID-SIGNATURE-METADATA"
        """
        # Generate ULID
        ulid = ULID()
        ulid_str = str(ulid)

        # Create message for HMAC (ULID + optional metadata)
        message = ulid_str
        if metadata:
            message = f"{ulid_str}:{metadata}"

        # Generate HMAC signature
        signature = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()[:self.signature_length]

        # Encode signature to base32 (matching ULID's encoding style)
        # Using Crockford's base32 for consistency with ULID
        sig_b32 = self._encode_base32(signature)

        # Combine components
        if metadata:
            return f"{ulid_str}-{sig_b32}-{metadata}"
        return f"{ulid_str}-{sig_b32}"

    def verify(self, secure_ulid: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify the integrity of a secure ULID.

        Args:
            secure_ulid: The secure ULID string to verify

        Returns:
            Tuple of (is_valid, ulid_str, metadata)
        """
        try:
            parts = secure_ulid.split('-')

            if len(parts) == 2:
                ulid_str, provided_sig = parts
                metadata = None
                message = ulid_str
            elif len(parts) == 3:
                ulid_str, provided_sig, metadata = parts
                message = f"{ulid_str}:{metadata}"
            else:
                return False, None, None

            # Validate ULID format
            try:
                ULID.from_str(ulid_str)
            except:
                return False, None, None

            # Recreate signature
            expected_sig = hmac.new(
                self.secret_key,
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()[:self.signature_length]

            expected_sig_b32 = self._encode_base32(expected_sig)

            # Constant-time comparison to prevent timing attacks
            is_valid = hmac.compare_digest(expected_sig_b32, provided_sig)

            return is_valid, ulid_str if is_valid else None, metadata if is_valid else None

        except Exception:
            return False, None, None

    def extract_ulid(self, secure_ulid: str) -> Optional[ULID]:
        """
        Extract and return the ULID object if the secure ULID is valid.

        Args:
            secure_ulid: The secure ULID string

        Returns:
            ULID object if valid, None otherwise
        """
        is_valid, ulid_str, _ = self.verify(secure_ulid)
        if is_valid and ulid_str:
            return ULID.from_str(ulid_str)
        return None

    def extract_timestamp(self, secure_ulid: str) -> Optional[float]:
        """
        Extract the timestamp from a secure ULID if valid.

        Returns:
            Unix timestamp if valid, None otherwise
        """
        ulid_obj = self.extract_ulid(secure_ulid)
        if ulid_obj:
            return ulid_obj.timestamp
        return None

    @staticmethod
    def _encode_base32(data: bytes) -> str:
        """
        Encode bytes to Crockford's base32 (matching ULID encoding).
        """
        # Crockford's base32 alphabet (excluding I, L, O, U to avoid confusion)
        alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

        # Convert bytes to integer
        num = int.from_bytes(data, byteorder='big')

        # Convert to base32
        if num == 0:
            return alphabet[0]

        result = []
        while num:
            num, remainder = divmod(num, 32)
            result.append(alphabet[remainder])

        return ''.join(reversed(result))


__all__ = ['Rigid']
