"""
DahNAY FreightFlow Engine: ISO 6346 Container & UN/LOCODE Checksum Validator
Enforces international standards on container serial numbers and sea ports.
"""

import re
from typing import Tuple, Optional

# UN/LOCODE database mapping for major Indian and international ports
UN_LOCODE_MAP = {
    "INMAA": "Chennai Port, India",
    "INTUT": "V.O. Chidambaranar Port (Tuticorin), India",
    "INNSA": "Jawaharlal Nehru Port (Nhava Sheva), India",
    "INMUN": "Mundra Port, India",
    "INCOK": "Cochin Port, India",
    "AEJEA": "Jebel Ali Port, Dubai, UAE",
    "SGSIN": "Port of Singapore, Singapore",
    "USNYC": "Port of New York and New Jersey, USA",
    "NLRTM": "Port of Rotterdam, Netherlands"
}

# ISO 6346 character value mapping (skips multiples of 11: 11, 22, 33)
ISO6346_LETTER_VALS = {
    'A': 10, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16, 'G': 17, 'H': 18, 'I': 19, 'J': 20,
    'K': 21, 'L': 23, 'M': 24, 'N': 25, 'O': 26, 'P': 27, 'Q': 28, 'R': 29, 'S': 30, 'T': 31,
    'U': 32, 'V': 34, 'W': 35, 'X': 36, 'Y': 37, 'Z': 38
}


class ContainerValidator:
    """Computes and validates ISO 6346 checksums for intermodal shipping containers."""

    @staticmethod
    def validate_container_number(container_no: str) -> Tuple[bool, Optional[int]]:
        """
        Validates container number against ISO 6346 standard.
        Format: 4 Letters (Owner + 'U') + 6 Digits (Serial) + 1 Check Digit (e.g., MSCU9081245).
        Returns (is_valid, computed_check_digit).
        """
        clean_no = re.sub(r'[^A-Z0-9]', '', container_no.upper())
        if len(clean_no) != 11:
            return False, None

        letters = clean_no[:4]
        digits = clean_no[4:10]
        check_digit_given = int(clean_no[10])

        total_sum = 0
        # Calculate sum for letters (indices 0 to 3)
        for i, char in enumerate(letters):
            if char not in ISO6346_LETTER_VALS:
                return False, None
            val = ISO6346_LETTER_VALS[char]
            total_sum += val * (2 ** i)

        # Calculate sum for serial digits (indices 4 to 9)
        for i, char in enumerate(digits):
            val = int(char)
            total_sum += val * (2 ** (i + 4))

        computed_digit = (total_sum % 11) % 10
        is_valid = (computed_digit == check_digit_given)
        return is_valid, computed_digit


class PortLocationValidator:
    """Validates and normalizes maritime port names against the UN/LOCODE standard."""

    @staticmethod
    def resolve_port(port_name_or_code: str) -> Tuple[str, str]:
        """
        Resolves a port string to its official UN/LOCODE and formal port name.
        """
        upper_text = port_name_or_code.upper()
        
        # Check direct 5-letter code
        for code, name in UN_LOCODE_MAP.items():
            if code in upper_text or name.split()[0].upper() in upper_text:
                return code, name

        if "CHENNAI" in upper_text or "MADRAS" in upper_text:
            return "INMAA", "Chennai Port, India"
        if "JEBEL" in upper_text or "DUBAI" in upper_text:
            return "AEJEA", "Jebel Ali Port, Dubai, UAE"
        if "TUTICORIN" in upper_text:
            return "INTUT", "Tuticorin Port, India"
        if "NHAVA" in upper_text or "JNPT" in upper_text or "MUMBAI" in upper_text:
            return "INNSA", "Nhava Sheva Port, India"

        return "UNKNOWN", port_name_or_code
