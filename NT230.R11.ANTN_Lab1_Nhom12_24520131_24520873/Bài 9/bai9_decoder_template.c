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

static uint8_t derive_xor_key(void) {
    volatile uint8_t seed_a = 0x0A;
    volatile uint8_t seed_b = 0x5F;
    return (uint8_t)(seed_a ^ seed_b);
}

static void xor_decode_in_place(uint8_t *buffer, size_t length) {
    uint8_t key = derive_xor_key();

    for (size_t i = 0; i < length; ++i) {
        buffer[i] ^= key;
    }
}
