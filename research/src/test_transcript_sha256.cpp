#include <cstdio>

#include "transcript_sha256.hpp"

int main() {
    if (!transcript_audit::sha256_self_test()) {
        std::fputs("SHA256 SELF-TEST FAILED\n", stderr);
        return 1;
    }
    std::puts("VERIFIED: transcript SHA-256 implementation passes standard vectors.");
    return 0;
}
