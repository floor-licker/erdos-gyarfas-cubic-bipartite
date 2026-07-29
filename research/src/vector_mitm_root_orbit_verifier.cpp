#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "transcript_sha256.hpp"

#ifndef SIDE
#define SIDE 30
#endif

namespace exact_verifier_b {
constexpr int v = SIDE;
static_assert(v >= 9, "the three root-orbit representatives require SIDE >= 9");
static_assert(2 * v <= 64, "this implementation stores incidence vertices in one uint64_t");

using Triple = std::array<int, 3>;

struct Counters {
    std::uint64_t states = 0;
    std::uint64_t attempted = 0;
    std::uint64_t pair_reject = 0;
    std::uint64_t c8_reject = 0;
    std::uint64_t c16_reject = 0;
    std::uint64_t completions = 0;

    Counters& operator+=(const Counters& other) {
        states += other.states;
        attempted += other.attempted;
        pair_reject += other.pair_reject;
        c8_reject += other.c8_reject;
        c16_reject += other.c16_reject;
        completions += other.completions;
        return *this;
    }
};

struct HalfPath {
    std::uint8_t endpoint = 0;
    std::uint64_t visited = 0;
};

class Search {
  public:
    Counters run_orbit(int orbit) {
        transcript_.begin(static_cast<std::uint8_t>(v),
                          static_cast<std::uint8_t>(orbit));
        insert({0, 1, 2});
        insert({0, 3, 4});
        insert({0, 5, 6});

        Triple first{};
        if (orbit == 1) {
            first = {1, 3, 5};
        } else if (orbit == 2) {
            first = {1, 3, 7};
            next_label_ = 8;
        } else if (orbit == 3) {
            first = {1, 7, 8};
            next_label_ = 9;
        } else {
            std::abort();
        }
        insert(first);
        extend(1, first[1], first[2]);
        return counters_;
    }

    const transcript_audit::SearchTranscript& transcript() const {
        return transcript_;
    }

    bool transcript_matches_counts() const {
        return transcript_.states() == counters_.states &&
               transcript_.candidates() == counters_.attempted;
    }

  private:
    std::vector<Triple> blocks_;
    std::array<std::vector<int>, v> incident_{};
    std::array<std::uint8_t, v> degree_{};
    std::array<std::uint64_t, v> paired_{};
    int next_label_ = 7;
    Counters counters_{};
    transcript_audit::SearchTranscript transcript_;

    static int one_common_point(const Triple& a, const Triple& b) {
        int common = -1;
        int count = 0;
        for (int x : a) {
            for (int y : b) {
                if (x == y) {
                    common = x;
                    ++count;
                }
            }
        }
        if (count == 0) return -1;
        if (count == 1) return common;
        return -2;
    }

    void insert(const Triple& block) {
        const int id = static_cast<int>(blocks_.size());
        blocks_.push_back(block);
        for (int point : block) {
            ++degree_[point];
            incident_[point].push_back(id);
        }
        for (int i = 0; i < 3; ++i) {
            for (int j = i + 1; j < 3; ++j) {
                paired_[block[i]] |= std::uint64_t{1} << block[j];
                paired_[block[j]] |= std::uint64_t{1} << block[i];
            }
        }
    }

    void erase_last() {
        const Triple block = blocks_.back();
        blocks_.pop_back();
        for (int point : block) {
            --degree_[point];
            incident_[point].pop_back();
        }
        for (int i = 0; i < 3; ++i) {
            for (int j = i + 1; j < 3; ++j) {
                paired_[block[i]] &= ~(std::uint64_t{1} << block[j]);
                paired_[block[j]] &= ~(std::uint64_t{1} << block[i]);
            }
        }
    }

    bool violates_degree_or_linearity(const Triple& block, int old_labels) const {
        for (int point : block) {
            if (point < old_labels && degree_[point] == 3) return true;
        }
        for (int i = 0; i < 3; ++i) {
            for (int j = i + 1; j < 3; ++j) {
                if (block[i] < old_labels && block[j] < old_labels &&
                    ((paired_[block[i]] >> block[j]) & std::uint64_t{1}) != 0) {
                    return true;
                }
            }
        }
        return false;
    }

    // In a linear triple system, an incidence C8 is exactly a Berge quadrilateral.
    bool closes_c8(const Triple& new_block) const {
        const int number = static_cast<int>(blocks_.size());
        for (int a = 0; a < number; ++a) {
            const int p0 = one_common_point(new_block, blocks_[a]);
            if (p0 < 0) continue;
            for (int b = 0; b < number; ++b) {
                if (b == a) continue;
                const int p1 = one_common_point(blocks_[a], blocks_[b]);
                if (p1 < 0 || p1 == p0) continue;
                for (int c = 0; c < number; ++c) {
                    if (c == a || c == b) continue;
                    const int p2 = one_common_point(blocks_[b], blocks_[c]);
                    if (p2 < 0 || p2 == p0 || p2 == p1) continue;
                    const int p3 = one_common_point(blocks_[c], new_block);
                    if (p3 < 0 || p3 == p0 || p3 == p1 || p3 == p2) continue;
                    return true;
                }
            }
        }
        return false;
    }

    void enumerate_seven_edge_halves(int current, int depth, std::uint64_t visited,
                                     std::vector<HalfPath>& output) const {
        if (depth == 7) {
            output.push_back(HalfPath{static_cast<std::uint8_t>(current), visited});
            return;
        }
        if (current < v) {
            for (int block_id : incident_[current]) {
                const int next = v + block_id;
                const std::uint64_t bit = std::uint64_t{1} << next;
                if ((visited & bit) == 0) {
                    enumerate_seven_edge_halves(next, depth + 1, visited | bit, output);
                }
            }
        } else {
            for (int point : blocks_[current - v]) {
                const std::uint64_t bit = std::uint64_t{1} << point;
                if ((visited & bit) == 0) {
                    enumerate_seven_edge_halves(point, depth + 1, visited | bit, output);
                }
            }
        }
    }

    bool has_old_simple_path_14(int start, int finish) const {
        if (degree_[start] == 0 || degree_[finish] == 0) return false;

        std::vector<HalfPath> left;
        std::vector<HalfPath> right;
        left.reserve(192);
        right.reserve(192);
        enumerate_seven_edge_halves(start, 0, std::uint64_t{1} << start,
                                    left);
        enumerate_seven_edge_halves(finish, 0, std::uint64_t{1} << finish,
                                    right);

        // Store every left half-path, grouped by its midpoint.  The vectors
        // deliberately impose no global or per-midpoint capacity.
        std::array<std::vector<std::uint64_t>, 2 * v> masks;
        for (const HalfPath& half : left) {
            masks[half.endpoint].push_back(half.visited);
        }
        for (const HalfPath& half : right) {
            const int endpoint = half.endpoint;
            const std::uint64_t common_endpoint = std::uint64_t{1} << endpoint;
            for (const std::uint64_t left_mask : masks[endpoint]) {
                if ((left_mask & half.visited) == common_endpoint) return true;
            }
        }
        return false;
    }

    bool closes_c16(const Triple& new_block) const {
        for (int i = 0; i < 3; ++i) {
            for (int j = i + 1; j < 3; ++j) {
                if (has_old_simple_path_14(new_block[i], new_block[j])) return true;
            }
        }
        return false;
    }

    void extend(int point, int previous_q, int previous_r) {
        ++counters_.states;
        while (point < next_label_ && degree_[point] == 3) {
            ++point;
            previous_q = -1;
            previous_r = -1;
        }
        transcript_.state(
            static_cast<std::uint8_t>(point),
            static_cast<std::uint8_t>(next_label_),
            previous_q, previous_r,
            static_cast<std::uint8_t>(blocks_.size()));
        for (const Triple& block : blocks_) {
            transcript_.block(
                static_cast<std::uint8_t>(block[0]),
                static_cast<std::uint8_t>(block[1]),
                static_cast<std::uint8_t>(block[2]));
        }
        if (point == v) {
            if (static_cast<int>(blocks_.size()) == v) {
                ++counters_.completions;
                transcript_.terminal(0);
            } else {
                transcript_.terminal(1);
            }
            transcript_.leave();
            return;
        }
        if (point >= next_label_) {
            transcript_.terminal(2);
            transcript_.leave();
            return;
        }
        if (static_cast<int>(blocks_.size()) >= v) {
            transcript_.terminal(3);
            transcript_.leave();
            return;
        }

        const int old_labels = next_label_;
        std::vector<int> choices;
        for (int q = point + 1; q < old_labels; ++q) {
            if (degree_[q] < 3 && ((paired_[point] >> q) & std::uint64_t{1}) == 0) {
                choices.push_back(q);
            }
        }
        if (old_labels < v) choices.push_back(old_labels);
        if (old_labels + 1 < v) choices.push_back(old_labels + 1);

        for (std::size_t i = 0; i < choices.size(); ++i) {
            for (std::size_t j = i + 1; j < choices.size(); ++j) {
                const int q = choices[i];
                const int r = choices[j];
                if (r == old_labels + 1 && q != old_labels) continue;
                if (previous_q >= 0 &&
                    (q < previous_q || (q == previous_q && r <= previous_r))) {
                    continue;
                }

                ++counters_.attempted;
                const Triple block{point, q, r};
                if (violates_degree_or_linearity(block, old_labels)) {
                    ++counters_.pair_reject;
                    transcript_.candidate(
                        static_cast<std::uint8_t>(point),
                        static_cast<std::uint8_t>(q),
                        static_cast<std::uint8_t>(r),
                        transcript_audit::Outcome::degree_or_pair);
                    continue;
                }
                if (closes_c8(block)) {
                    ++counters_.c8_reject;
                    transcript_.candidate(
                        static_cast<std::uint8_t>(point),
                        static_cast<std::uint8_t>(q),
                        static_cast<std::uint8_t>(r),
                        transcript_audit::Outcome::c8);
                    continue;
                }
                if (closes_c16(block)) {
                    ++counters_.c16_reject;
                    transcript_.candidate(
                        static_cast<std::uint8_t>(point),
                        static_cast<std::uint8_t>(q),
                        static_cast<std::uint8_t>(r),
                        transcript_audit::Outcome::c16);
                    continue;
                }

                transcript_.candidate(
                    static_cast<std::uint8_t>(point),
                    static_cast<std::uint8_t>(q),
                    static_cast<std::uint8_t>(r),
                    transcript_audit::Outcome::accepted);
                int new_labels = old_labels;
                if (q == old_labels || r == old_labels) ++new_labels;
                if (r == old_labels + 1) ++new_labels;
                const int saved = next_label_;
                next_label_ = new_labels;
                insert(block);
                extend(point, q, r);
                erase_last();
                next_label_ = saved;
            }
        }
        transcript_.leave();
    }
};
}  // namespace exact_verifier_b

int main(int argc, char** argv) {
    int first = 1;
    int last = 3;
    if (argc == 2) {
        const int orbit = std::atoi(argv[1]);
        if (orbit < 1 || orbit > 3) {
            std::fprintf(stderr, "usage: %s [orbit: 1|2|3]\n", argv[0]);
            return 64;
        }
        first = last = orbit;
    } else if (argc != 1) {
        std::fprintf(stderr, "usage: %s [orbit: 1|2|3]\n", argv[0]);
        return 64;
    }

    const auto start = std::chrono::steady_clock::now();
    exact_verifier_b::Counters total;
    for (int orbit = first; orbit <= last; ++orbit) {
        exact_verifier_b::Search search;
        const auto result = search.run_orbit(orbit);
        if (!search.transcript_matches_counts()) {
            std::fprintf(stderr,
                         "transcript counter mismatch in orbit %d\n", orbit);
            return 70;
        }
        total += result;
        std::printf(
            "ORBIT %d states=%llu attempted=%llu pair=%llu c8=%llu c16=%llu completions=%llu\n",
            orbit,
            static_cast<unsigned long long>(result.states),
            static_cast<unsigned long long>(result.attempted),
            static_cast<unsigned long long>(result.pair_reject),
            static_cast<unsigned long long>(result.c8_reject),
            static_cast<unsigned long long>(result.c16_reject),
            static_cast<unsigned long long>(result.completions));
        std::printf(
            "TRANSCRIPT orbit=%d states=%llu candidates=%llu sha256=%s\n",
            orbit,
            static_cast<unsigned long long>(search.transcript().states()),
            static_cast<unsigned long long>(search.transcript().candidates()),
            search.transcript().hex_digest().c_str());
        std::fflush(stdout);
    }
    const double seconds = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - start).count();
    std::printf(
        "TOTAL V=%d states=%llu attempted=%llu pair=%llu c8=%llu c16=%llu completions=%llu seconds=%.6f\n",
        exact_verifier_b::v,
        static_cast<unsigned long long>(total.states),
        static_cast<unsigned long long>(total.attempted),
        static_cast<unsigned long long>(total.pair_reject),
        static_cast<unsigned long long>(total.c8_reject),
        static_cast<unsigned long long>(total.c16_reject),
        static_cast<unsigned long long>(total.completions),
        seconds);
    return total.completions == 0 ? 0 : 2;
}
