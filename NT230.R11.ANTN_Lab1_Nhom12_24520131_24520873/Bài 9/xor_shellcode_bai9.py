#!/usr/bin/env python3
"""
Bai 9 - XOR shellcode offline encoder.

This script only transforms bytes for the lab report/workflow. It does not
patch PE files and does not execute shellcode.

Examples:
  python xor_shellcode_bai9.py --key 0x55
  python xor_shellcode_bai9.py --hex "6A 00 68 66" --key 0x55
  python xor_shellcode_bai9.py --in-bin payload.bin --key 85 --prefix payload
"""

from __future__ import annotations

import argparse
import re
import secrets
import sys
import textwrap
from pathlib import Path


# Shellcode from the previous lab step. Replace with --hex/--in-hex/--in-bin
# when you need to encode another payload.
DEFAULT_SHELLCODE_HEX = """
6A 00 68 66 87 00 01 68 70 87 00 01 6A 00 FF 15
68 12 00 01 8B FF 55 8B EC E9 D5 A1 FF FF 49 00
6E 00 66 00 6F 00 00 00 32 00 34 00 35 00 32 00
30 00 31 00 33 00 31 00 00 00
"""


def parse_hex_blob(value: str) -> bytes:
    """Parse common hex formats: 'AA BB', '0xAA, 0xBB', or '\\xAA\\xBB'."""
    normalized = value.replace("\\x", " ").replace(",", " ")
    tokens = re.findall(r"(?:0x)?[0-9a-fA-F]{2}", normalized)
    if not tokens:
        raise ValueError("No hex bytes found.")
    return bytes(int(token[-2:], 16) for token in tokens)


def parse_key(value: str | None) -> int:
    if value is None:
        return secrets.randbelow(256)

    key = int(value, 0)
    if not 0 <= key <= 0xFF:
        raise argparse.ArgumentTypeError("XOR key must be one byte: 0..255.")
    return key


def xor_bytes(data: bytes, key: int) -> bytes:
    return bytes(byte ^ key for byte in data)


def format_hex_lines(data: bytes, per_line: int = 16) -> str:
    lines = []
    for offset in range(0, len(data), per_line):
        chunk = data[offset : offset + per_line]
        lines.append(" ".join(f"{byte:02X}" for byte in chunk))
    return "\n".join(lines) + "\n"


def format_c_array(data: bytes, name: str = "encrypted_shellcode") -> str:
    lines = [f"unsigned char {name}[] = {{"]
    for offset in range(0, len(data), 12):
        chunk = data[offset : offset + 12]
        lines.append("    " + ", ".join(f"0x{byte:02X}" for byte in chunk) + ",")
    lines.append("};")
    lines.append(f"unsigned int {name}_len = {len(data)};")
    return "\n".join(lines) + "\n"


def build_decoder_template(key: int) -> str:
    # Store two seed bytes instead of the final XOR key byte.
    seed_a = secrets.randbelow(256)
    seed_b = seed_a ^ key

    return textwrap.dedent(
        f"""\
        /*
         * Small XOR decoder template for Bai 9.
         * The final XOR key is derived from two seed bytes, so the key byte is
         * not stored directly as a single source-level constant.
         *
         * This template only decodes a buffer in memory. Insert it into your
         * own lab code where the encrypted payload already exists.
         */
        #include <stddef.h>
        #include <stdint.h>

        static uint8_t derive_xor_key(void) {{
            volatile uint8_t seed_a = 0x{seed_a:02X};
            volatile uint8_t seed_b = 0x{seed_b:02X};
            return (uint8_t)(seed_a ^ seed_b);
        }}

        static void xor_decode_in_place(uint8_t *buffer, size_t length) {{
            uint8_t key = derive_xor_key();

            for (size_t i = 0; i < length; ++i) {{
                buffer[i] ^= key;
            }}
        }}
        """
    )


def read_payload(args: argparse.Namespace) -> bytes:
    sources = [
        args.hex_literal is not None,
        args.in_hex is not None,
        args.in_bin is not None,
    ]
    if sum(sources) > 1:
        raise ValueError("Choose only one input source: --hex, --in-hex, or --in-bin.")

    if args.hex_literal is not None:
        return parse_hex_blob(args.hex_literal)
    if args.in_hex is not None:
        return parse_hex_blob(args.in_hex.read_text(encoding="utf-8"))
    if args.in_bin is not None:
        return args.in_bin.read_bytes()

    return parse_hex_blob(DEFAULT_SHELLCODE_HEX)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")

    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="XOR-encode shellcode bytes for Bai 9 and emit lab artifacts."
    )
    parser.add_argument("--key", help="XOR key byte, e.g. 0x55 or 85. Random if omitted.")
    parser.add_argument("--hex", dest="hex_literal", help="Payload bytes as a hex string.")
    parser.add_argument("--in-hex", type=Path, help="Text file containing payload hex bytes.")
    parser.add_argument("--in-bin", type=Path, help="Raw binary payload file.")
    parser.add_argument("--out-dir", type=Path, default=script_dir, help="Output directory.")
    parser.add_argument("--prefix", default="bai9", help="Output filename prefix.")
    args = parser.parse_args()

    payload = read_payload(args)
    key = parse_key(args.key)
    encrypted = xor_bytes(payload, key)
    decrypted_check = xor_bytes(encrypted, key)

    if decrypted_check != payload:
        raise RuntimeError("Round-trip XOR check failed.")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    encrypted_bin = args.out_dir / f"{args.prefix}_encrypted_shellcode.bin"
    encrypted_hex = args.out_dir / f"{args.prefix}_encrypted_shellcode.hex.txt"
    encrypted_c = args.out_dir / f"{args.prefix}_encrypted_shellcode.c.txt"
    decoder_c = args.out_dir / f"{args.prefix}_decoder_template.c"

    encrypted_bin.write_bytes(encrypted)
    encrypted_hex.write_text(format_hex_lines(encrypted), encoding="utf-8")
    encrypted_c.write_text(format_c_array(encrypted), encoding="utf-8")
    decoder_c.write_text(build_decoder_template(key), encoding="utf-8")

    print(f"Input length : {len(payload)} bytes")
    print(f"XOR key      : 0x{key:02X}")
    print(f"BIN output   : {encrypted_bin}")
    print(f"HEX output   : {encrypted_hex}")
    print(f"C array      : {encrypted_c}")
    print(f"Decoder      : {decoder_c}")
    print("Round-trip   : OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
