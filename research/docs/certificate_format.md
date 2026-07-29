# Certificate format

The authoritative, implementation-independent byte specification is
[`../certificates/FORMAT.md`](../certificates/FORMAT.md).

The compact checker is `research/src/verify_eg_certificate.cpp`. The
certificate generator is `research/src/generate_eg_certificate.cpp`. These
programs are separate implementations; the checker reconstructs the search
schedule and validates positive witnesses rather than invoking a production
cycle oracle.
