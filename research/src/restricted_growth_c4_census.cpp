#include <array>
#include <cstdint>
#include <cstdio>
#include <vector>

#ifndef SIDE
#define SIDE 12
#endif

namespace restricted_growth_census {

constexpr int V = SIDE;
constexpr int N = 2 * V;
static_assert(N <= 62, "the graph6 encoder supports orders at most 62");

using Block = std::array<int, 3>;

struct Search {
    std::vector<Block> blocks;
    std::array<int, V> degree{};
    std::array<std::array<bool, V>, V> paired{};
    int introduced = 7;
    std::uint64_t labelled_completions = 0;

    void add(const Block& block) {
        blocks.push_back(block);
        for (const int point : block) {
            ++degree[point];
        }
        for (int i = 0; i < 3; ++i) {
            for (int j = i + 1; j < 3; ++j) {
                paired[block[i]][block[j]] = true;
                paired[block[j]][block[i]] = true;
            }
        }
    }

    void remove() {
        const Block block = blocks.back();
        blocks.pop_back();
        for (const int point : block) {
            --degree[point];
        }
        for (int i = 0; i < 3; ++i) {
            for (int j = i + 1; j < 3; ++j) {
                paired[block[i]][block[j]] = false;
                paired[block[j]][block[i]] = false;
            }
        }
    }

    bool invalid(const Block& block, int old_introduced) const {
        for (const int point : block) {
            if (point < old_introduced && degree[point] >= 3) {
                return true;
            }
        }
        for (int i = 0; i < 3; ++i) {
            for (int j = i + 1; j < 3; ++j) {
                if (block[i] < old_introduced &&
                    block[j] < old_introduced &&
                    paired[block[i]][block[j]]) {
                    return true;
                }
            }
        }
        return false;
    }

    void emit_graph6() const {
        std::array<std::array<bool, N>, N> adjacent{};
        for (std::size_t id = 0; id < blocks.size(); ++id) {
            const int block_vertex = V + static_cast<int>(id);
            for (const int point : blocks[id]) {
                adjacent[point][block_vertex] = true;
                adjacent[block_vertex][point] = true;
            }
        }

        std::putchar(N + 63);
        int value = 0;
        int used = 0;
        for (int high = 1; high < N; ++high) {
            for (int low = 0; low < high; ++low) {
                value = (value << 1) | (adjacent[low][high] ? 1 : 0);
                ++used;
                if (used == 6) {
                    std::putchar(value + 63);
                    value = 0;
                    used = 0;
                }
            }
        }
        if (used != 0) {
            value <<= 6 - used;
            std::putchar(value + 63);
        }
        std::putchar('\n');
    }

    void recurse(int point, int last_q, int last_r) {
        while (point < introduced && degree[point] == 3) {
            ++point;
            last_q = -1;
            last_r = -1;
        }
        if (point == V) {
            if (static_cast<int>(blocks.size()) == V) {
                ++labelled_completions;
                emit_graph6();
            }
            return;
        }
        if (point >= introduced || static_cast<int>(blocks.size()) >= V) {
            return;
        }

        const int old_introduced = introduced;
        std::vector<int> possible;
        for (int q = point + 1; q < old_introduced; ++q) {
            if (degree[q] < 3 && !paired[point][q]) {
                possible.push_back(q);
            }
        }
        if (old_introduced < V) {
            possible.push_back(old_introduced);
        }
        if (old_introduced + 1 < V) {
            possible.push_back(old_introduced + 1);
        }

        for (std::size_t i = 0; i < possible.size(); ++i) {
            for (std::size_t j = i + 1; j < possible.size(); ++j) {
                const int q = possible[i];
                const int r = possible[j];
                if (r == old_introduced + 1 && q != old_introduced) {
                    continue;
                }
                if (last_q >= 0 &&
                    (q < last_q || (q == last_q && r <= last_r))) {
                    continue;
                }

                const Block block{point, q, r};
                if (invalid(block, old_introduced)) {
                    continue;
                }

                int next_introduced = old_introduced;
                if (q == old_introduced || r == old_introduced) {
                    ++next_introduced;
                }
                if (r == old_introduced + 1) {
                    ++next_introduced;
                }
                const int saved_introduced = introduced;
                introduced = next_introduced;
                add(block);
                recurse(point, q, r);
                remove();
                introduced = saved_introduced;
            }
        }
    }

    void run_orbit(int orbit) {
        add({0, 1, 2});
        add({0, 3, 4});
        add({0, 5, 6});

        Block first{};
        if (orbit == 1) {
            first = {1, 3, 5};
        } else if (orbit == 2) {
            if (V < 8) {
                return;
            }
            first = {1, 3, 7};
            introduced = 8;
        } else {
            if (V < 9) {
                return;
            }
            first = {1, 7, 8};
            introduced = 9;
        }
        add(first);
        recurse(1, first[1], first[2]);
    }
};

}  // namespace restricted_growth_census

int main() {
    std::uint64_t total = 0;
    for (int orbit = 1; orbit <= 3; ++orbit) {
        restricted_growth_census::Search search;
        search.run_orbit(orbit);
        total += search.labelled_completions;
    }
    std::fprintf(
        stderr,
        "C4_CENSUS V=%d labelled_completions=%llu\n",
        restricted_growth_census::V,
        static_cast<unsigned long long>(total));
    return 0;
}
