#ifndef CENTER_SYMMETRY_777_H
#define CENTER_SYMMETRY_777_H

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

/*
 * Symmetry for the 7x7x7 daisy and native-solve center tables.
 *
 * Each axis tracks five (4,4) orbits of eight stickers, four on the axis's
 * primary face and four on its opposite face, for a 70^5 = 1,680,700,000 raw
 * coordinate.  Two facts let one table cover all six of the old files:
 *
 *   1. The cube symmetries that map an axis onto itself form a 16 element
 *      subgroup, 8 rotations and 8 mirrors.  The move set (outer turns plus
 *      wide half turns) and both daisy goals are closed under all 16, so the
 *      cost is constant on each orbit.  1,680,700,000 raw ranks collapse to
 *      105,356,972 orbits.
 *   2. Any cube rotation carrying one axis onto another carries that axis's
 *      tracked stickers onto the other's, so the three axes are one cost
 *      function under three different indexings.
 *
 * So we normalise every axis onto the UD coordinate and canonicalise there.
 * The 16 maps that carry axis A's stickers onto UD's are exactly the 16
 * UD-preserving symmetries composed with any one such map, which is why the
 * canonical rank does not depend on which normalising rotation we pick.
 *
 * Normalising can permute the rank groups: mirrors exchange the left and right
 * obliques, because those two orbits are reflections of each other.  The
 * per-symmetry group permutation below records that.
 */

#define DAISY_AXIS_COUNT_777 3
#define DAISY_ORBIT_COUNT_777 5
#define DAISY_GROUP_SIZE_777 8
#define DAISY_GROUP_COLOR_COUNT_777 4
#define DAISY_GROUP_UNIVERSE_777 UINT64_C(70)
#define DAISY_SYMMETRY_COUNT_777 16
#define DAISY_PERFECT_UNIVERSE_777 UINT64_C(1680700000)
#define DAISY_PERFECT_ORBIT_COUNT_777 UINT64_C(105356972)

#define DAISY_CUBE_SIZE_777 7
#define DAISY_CUBE_ARRAY_SIZE_777 295

/*
 * Exact 8-sticker (4,4) orbits from builder777.py DAISY_CENTER_ORBITS_777.
 * Outer-x and the fixed middles are untracked. Rank order per axis is
 * left-oblique, middle-oblique (outer t), right-oblique, inner-t, inner-x.
 */
static const unsigned int daisy_orbit_squares_777
    [DAISY_AXIS_COUNT_777][DAISY_ORBIT_COUNT_777][DAISY_GROUP_SIZE_777] = {
    {
        {10, 20, 30, 40, 255, 265, 275, 285},
        {11, 23, 27, 39, 256, 268, 272, 284},
        {12, 16, 34, 38, 257, 261, 279, 283},
        {18, 24, 26, 32, 263, 269, 271, 277},
        {17, 19, 31, 33, 262, 264, 276, 278},
    },
    {
        {59, 69, 79, 89, 157, 167, 177, 187},
        {60, 72, 76, 88, 158, 170, 174, 186},
        {61, 65, 83, 87, 159, 163, 181, 185},
        {67, 73, 75, 81, 165, 171, 173, 179},
        {66, 68, 80, 82, 164, 166, 178, 180},
    },
    {
        {108, 118, 128, 138, 206, 216, 226, 236},
        {109, 121, 125, 137, 207, 219, 223, 235},
        {110, 114, 132, 136, 208, 212, 230, 234},
        {116, 122, 124, 130, 214, 220, 222, 228},
        {115, 117, 129, 131, 213, 215, 227, 229},
    },
};

/* Alphabetically sorted pair used by the builder's multiset rank. */
static const char daisy_axis_small_777[DAISY_AXIS_COUNT_777] = {'D', 'L', 'B'};
static const char daisy_axis_large_777[DAISY_AXIS_COUNT_777] = {'U', 'R', 'F'};

/*
 * Where axis A's orbit G lands in the UD coordinate under symmetry S, and the
 * UD group rank that axis A's group rank becomes.  16.8 KB total, so
 * canonicalising a state is 80 cache-resident lookups rather than 80 ranks.
 */
static unsigned char daisy_symmetry_group_777
    [DAISY_AXIS_COUNT_777][DAISY_SYMMETRY_COUNT_777][DAISY_ORBIT_COUNT_777];
static unsigned char daisy_symmetry_rank_777
    [DAISY_AXIS_COUNT_777][DAISY_SYMMETRY_COUNT_777][DAISY_ORBIT_COUNT_777]
    [DAISY_GROUP_UNIVERSE_777];
/* The inverse of daisy_symmetry_group_777, so a UD place can be filled without
 * searching for the source orbit that lands there. */
static unsigned char daisy_symmetry_source_777
    [DAISY_AXIS_COUNT_777][DAISY_SYMMETRY_COUNT_777][DAISY_ORBIT_COUNT_777];
static int daisy_symmetry_initialized_777;

static const uint64_t daisy_group_place_777[DAISY_ORBIT_COUNT_777] = {
    UINT64_C(24010000), UINT64_C(343000), UINT64_C(4900), UINT64_C(70), UINT64_C(1),
};

/*
 * Rank four copies of `small` and four copies of `large` in lexicographic
 * order, matching buildercore.multiset_rank.
 */
static uint64_t
daisy_group_rank_777(const char colors[DAISY_GROUP_SIZE_777], char small, char large)
{
    unsigned int remaining[2] = {DAISY_GROUP_COLOR_COUNT_777, DAISY_GROUP_COLOR_COUNT_777};
    uint64_t permutations = DAISY_GROUP_UNIVERSE_777;
    uint64_t rank = 0;
    unsigned int slots = DAISY_GROUP_SIZE_777;

    for (unsigned int position = 0; position < DAISY_GROUP_SIZE_777; position++) {
        unsigned int symbol_index;

        if (colors[position] == small) {
            symbol_index = 0;
        } else if (colors[position] == large) {
            symbol_index = 1;
        } else {
            return UINT64_MAX;
        }
        if (!remaining[symbol_index]) {
            return UINT64_MAX;
        }
        if (symbol_index) {
            rank += permutations * remaining[0] / slots;
        }
        permutations = permutations * remaining[symbol_index] / slots;
        remaining[symbol_index]--;
        slots--;
    }
    return rank;
}

static void
daisy_group_unrank_777(uint64_t rank, char small, char large, char colors[DAISY_GROUP_SIZE_777])
{
    unsigned int remaining[2] = {DAISY_GROUP_COLOR_COUNT_777, DAISY_GROUP_COLOR_COUNT_777};
    uint64_t permutations = DAISY_GROUP_UNIVERSE_777;
    unsigned int slots = DAISY_GROUP_SIZE_777;

    for (unsigned int position = 0; position < DAISY_GROUP_SIZE_777; position++) {
        uint64_t block = remaining[0] ? permutations * remaining[0] / slots : 0;
        unsigned int symbol_index;

        if (remaining[0] && rank < block) {
            symbol_index = 0;
            permutations = block;
        } else {
            symbol_index = 1;
            rank -= block;
            permutations = permutations * remaining[1] / slots;
        }
        colors[position] = symbol_index ? large : small;
        remaining[symbol_index]--;
        slots--;
    }
}

/*
 * A sticker's 3D position, coordinates in -3..3.  Face order is ULFRBD, x is
 * +R, y is +U and z is +F.  Only center stickers get a unique position, which
 * is all the tracked orbits contain.
 */
static void
daisy_square_position_777(unsigned int square, int8_t position[3])
{
    unsigned int face = (square - 1) / (DAISY_CUBE_SIZE_777 * DAISY_CUBE_SIZE_777);
    unsigned int offset = (square - 1) % (DAISY_CUBE_SIZE_777 * DAISY_CUBE_SIZE_777);
    int row = (int) (offset / DAISY_CUBE_SIZE_777);
    int col = (int) (offset % DAISY_CUBE_SIZE_777);

    switch (face) {
        case 0: position[0] = (int8_t) (col - 3); position[1] = 3; position[2] = (int8_t) (row - 3); break;
        case 1: position[0] = -3; position[1] = (int8_t) (3 - row); position[2] = (int8_t) (col - 3); break;
        case 2: position[0] = (int8_t) (col - 3); position[1] = (int8_t) (3 - row); position[2] = 3; break;
        case 3: position[0] = 3; position[1] = (int8_t) (3 - row); position[2] = (int8_t) (3 - col); break;
        case 4: position[0] = (int8_t) (3 - col); position[1] = (int8_t) (3 - row); position[2] = -3; break;
        default: position[0] = (int8_t) (col - 3); position[1] = -3; position[2] = (int8_t) (3 - row); break;
    }
}

static int
daisy_square_is_center_777(unsigned int square)
{
    unsigned int offset = (square - 1) % (DAISY_CUBE_SIZE_777 * DAISY_CUBE_SIZE_777);
    unsigned int row = offset / DAISY_CUBE_SIZE_777;
    unsigned int col = offset % DAISY_CUBE_SIZE_777;

    return row && col && row < DAISY_CUBE_SIZE_777 - 1 && col < DAISY_CUBE_SIZE_777 - 1;
}

static char
daisy_face_color_777(const int8_t normal[3])
{
    if (normal[1] == 3) return 'U';
    if (normal[1] == -3) return 'D';
    if (normal[0] == -3) return 'L';
    if (normal[0] == 3) return 'R';
    if (normal[2] == 3) return 'F';
    if (normal[2] == -3) return 'B';
    abort();
}

static void
init_center_symmetry_777(void)
{
    /* Signed permutation matrices: out[row] = sum(matrix[row][col] * in[col]). */
    static const unsigned char axis_permutations[6][3] = {
        {0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0},
    };
    int8_t maps[48][3][3];
    int position_to_square[7][7][7];
    unsigned int map_count = 0;

    if (daisy_symmetry_initialized_777) {
        return;
    }
    for (unsigned int permutation = 0; permutation < 6; permutation++) {
        for (unsigned int sign_bits = 0; sign_bits < 8; sign_bits++, map_count++) {
            for (unsigned int row = 0; row < 3; row++) {
                for (unsigned int col = 0; col < 3; col++) {
                    maps[map_count][row][col] = 0;
                }
            }
            for (unsigned int col = 0; col < 3; col++) {
                maps[map_count][axis_permutations[permutation][col]][col] =
                    (sign_bits & (1U << col)) ? 1 : -1;
            }
        }
    }

    for (unsigned int x = 0; x < 7; x++) {
        for (unsigned int y = 0; y < 7; y++) {
            for (unsigned int z = 0; z < 7; z++) {
                position_to_square[x][y][z] = -1;
            }
        }
    }
    for (unsigned int square = 1; square < DAISY_CUBE_ARRAY_SIZE_777; square++) {
        int8_t position[3];

        if (!daisy_square_is_center_777(square)) {
            continue;
        }
        daisy_square_position_777(square, position);
        position_to_square[position[0] + 3][position[1] + 3][position[2] + 3] = (int) square;
    }

    /* Which UD orbit a tracked UD square belongs to, -1 for everything else. */
    int ud_orbit_of[DAISY_CUBE_ARRAY_SIZE_777];
    for (unsigned int square = 0; square < DAISY_CUBE_ARRAY_SIZE_777; square++) {
        ud_orbit_of[square] = -1;
    }
    for (unsigned int orbit = 0; orbit < DAISY_ORBIT_COUNT_777; orbit++) {
        for (unsigned int slot = 0; slot < DAISY_GROUP_SIZE_777; slot++) {
            ud_orbit_of[daisy_orbit_squares_777[0][orbit][slot]] = (int) orbit;
        }
    }

    for (unsigned int axis = 0; axis < DAISY_AXIS_COUNT_777; axis++) {
        unsigned int found = 0;

        for (unsigned int map = 0; map < 48; map++) {
            unsigned int images[DAISY_ORBIT_COUNT_777][DAISY_GROUP_SIZE_777];
            int target_orbit[DAISY_ORBIT_COUNT_777];
            int carries_axis = 1;

            for (unsigned int orbit = 0; orbit < DAISY_ORBIT_COUNT_777 && carries_axis; orbit++) {
                target_orbit[orbit] = -1;
                for (unsigned int slot = 0; slot < DAISY_GROUP_SIZE_777; slot++) {
                    unsigned int square = daisy_orbit_squares_777[axis][orbit][slot];
                    int8_t source[3];
                    int8_t image[3];
                    int landed;

                    daisy_square_position_777(square, source);
                    for (unsigned int row = 0; row < 3; row++) {
                        image[row] = (int8_t) (maps[map][row][0] * source[0] +
                                               maps[map][row][1] * source[1] +
                                               maps[map][row][2] * source[2]);
                    }
                    landed = position_to_square[image[0] + 3][image[1] + 3][image[2] + 3];
                    if (landed < 0 || ud_orbit_of[landed] < 0 ||
                            (target_orbit[orbit] >= 0 && target_orbit[orbit] != ud_orbit_of[landed])) {
                        carries_axis = 0;
                        break;
                    }
                    target_orbit[orbit] = ud_orbit_of[landed];
                    images[orbit][slot] = (unsigned int) landed;
                }
            }
            if (!carries_axis) {
                continue;
            }
            if (found >= DAISY_SYMMETRY_COUNT_777) {
                abort();
            }

            for (unsigned int orbit = 0; orbit < DAISY_ORBIT_COUNT_777; orbit++) {
                const unsigned int *ud_squares = daisy_orbit_squares_777[0][target_orbit[orbit]];
                unsigned char slot_of_image[DAISY_GROUP_SIZE_777];
                int8_t primary_normal[3] = {0, 0, 0};
                int8_t opposite_normal[3] = {0, 0, 0};
                char primary_image;
                char opposite_image;

                daisy_symmetry_group_777[axis][found][orbit] = (unsigned char) target_orbit[orbit];
                for (unsigned int slot = 0; slot < DAISY_GROUP_SIZE_777; slot++) {
                    unsigned int landed = DAISY_GROUP_SIZE_777;

                    for (unsigned int candidate = 0; candidate < DAISY_GROUP_SIZE_777; candidate++) {
                        if (ud_squares[candidate] == images[orbit][slot]) {
                            landed = candidate;
                            break;
                        }
                    }
                    if (landed == DAISY_GROUP_SIZE_777) {
                        abort();
                    }
                    slot_of_image[slot] = (unsigned char) landed;
                }

                /* The transform relabels this axis's two colours by moving their faces. */
                switch (daisy_axis_small_777[axis]) {
                    case 'D': opposite_normal[1] = -3; primary_normal[1] = 3; break;
                    case 'L': opposite_normal[0] = -3; primary_normal[0] = 3; break;
                    default: opposite_normal[2] = -3; primary_normal[2] = 3; break;
                }
                {
                    int8_t moved_small[3];
                    int8_t moved_large[3];

                    for (unsigned int row = 0; row < 3; row++) {
                        moved_small[row] = (int8_t) (maps[map][row][0] * opposite_normal[0] +
                                                     maps[map][row][1] * opposite_normal[1] +
                                                     maps[map][row][2] * opposite_normal[2]);
                        moved_large[row] = (int8_t) (maps[map][row][0] * primary_normal[0] +
                                                     maps[map][row][1] * primary_normal[1] +
                                                     maps[map][row][2] * primary_normal[2]);
                    }
                    opposite_image = daisy_face_color_777(moved_small);
                    primary_image = daisy_face_color_777(moved_large);
                }

                for (uint64_t rank = 0; rank < DAISY_GROUP_UNIVERSE_777; rank++) {
                    char source_colors[DAISY_GROUP_SIZE_777];
                    char ud_colors[DAISY_GROUP_SIZE_777];
                    uint64_t mapped;

                    daisy_group_unrank_777(
                        rank, daisy_axis_small_777[axis], daisy_axis_large_777[axis], source_colors);
                    for (unsigned int slot = 0; slot < DAISY_GROUP_SIZE_777; slot++) {
                        ud_colors[slot_of_image[slot]] =
                            source_colors[slot] == daisy_axis_small_777[axis] ?
                            opposite_image : primary_image;
                    }
                    mapped = daisy_group_rank_777(ud_colors, 'D', 'U');
                    if (mapped >= DAISY_GROUP_UNIVERSE_777) {
                        abort();
                    }
                    daisy_symmetry_rank_777[axis][found][orbit][rank] = (unsigned char) mapped;
                }
            }
            for (unsigned int orbit = 0; orbit < DAISY_ORBIT_COUNT_777; orbit++) {
                daisy_symmetry_source_777[axis][found]
                    [daisy_symmetry_group_777[axis][found][orbit]] = (unsigned char) orbit;
            }
            found++;
        }
        if (found != DAISY_SYMMETRY_COUNT_777) {
            abort();
        }
    }
    daisy_symmetry_initialized_777 = 1;
}

/*
 * The smallest UD raw rank any of the 16 normalising symmetries produces. Two
 * states share a value exactly when they share a cost.
 *
 * Since every group rank is below 70 and the places are powers of 70, the
 * smallest rank is the lexicographically smallest digit tuple. So we settle one
 * place at a time and keep only the symmetries still tied for the lead, which
 * usually leaves a single candidate after the first place. That costs about 20
 * lookups per axis rather than the 80 a full 16 way minimum would take, and the
 * search calls this three times for every node it touches.
 */
static uint64_t
daisy_canonical_rank_777(unsigned int axis, const uint64_t orbit_rank[DAISY_ORBIT_COUNT_777])
{
    unsigned char survivors[DAISY_SYMMETRY_COUNT_777];
    unsigned int count = DAISY_SYMMETRY_COUNT_777;
    uint64_t canonical = 0;

    for (unsigned int orbit = 0; orbit < DAISY_ORBIT_COUNT_777; orbit++) {
        if (orbit_rank[orbit] >= DAISY_GROUP_UNIVERSE_777) {
            return UINT64_MAX;
        }
    }
    for (unsigned int symmetry = 0; symmetry < DAISY_SYMMETRY_COUNT_777; symmetry++) {
        survivors[symmetry] = (unsigned char) symmetry;
    }

    for (unsigned int place = 0; place < DAISY_ORBIT_COUNT_777; place++) {
        unsigned char best = (unsigned char) DAISY_GROUP_UNIVERSE_777;
        unsigned int kept = 0;

        for (unsigned int index = 0; index < count; index++) {
            unsigned int symmetry = survivors[index];
            unsigned int source = daisy_symmetry_source_777[axis][symmetry][place];
            unsigned char digit =
                daisy_symmetry_rank_777[axis][symmetry][source][orbit_rank[source]];

            if (digit < best) {
                best = digit;
                kept = 0;
            }
            if (digit == best) {
                survivors[kept++] = (unsigned char) symmetry;
            }
        }
        canonical += (uint64_t) best * daisy_group_place_777[place];
        count = kept;

        if (count == 1) {
            unsigned int symmetry = survivors[0];

            while (++place < DAISY_ORBIT_COUNT_777) {
                unsigned int source = daisy_symmetry_source_777[axis][symmetry][place];

                canonical += (uint64_t) daisy_symmetry_rank_777[axis][symmetry][source]
                             [orbit_rank[source]] * daisy_group_place_777[place];
            }
            break;
        }
    }
    return canonical;
}

/*
 * Index mapping a canonical raw rank to its position in the compacted cost
 * file, written by compact-center-symmetry-777.
 *
 * One bit per raw rank, set where that rank is the smallest in its symmetry
 * orbit, plus a running count of set bits before each 512 bit block. A lookup
 * is then the block's count plus the set bits below the rank inside the block,
 * which is one 64 byte line of popcounts and one counter.
 *
 * This replaced an Elias-Fano index, which was half the size but read about
 * three times slower: Elias-Fano has to walk every orbit sharing a rank's high
 * bits, and that bucket grows with the split. See compact-center-symmetry-777.c.
 */

#define DAISY_RANK_INDEX_MAGIC_777 "CS777RS1"
#define DAISY_RANK_BLOCK_BITS_777 512
#define DAISY_RANK_BLOCK_WORDS_777 (DAISY_RANK_BLOCK_BITS_777 / 64)

/* Exactly 64 bytes, so the bitmap that follows starts on a cache line. */
struct daisy_symmetry_index_header_777 {
    char magic[8];
    uint64_t raw_universe;
    uint64_t orbit_count;
    uint64_t word_count;
    uint64_t block_count;
    uint64_t unused[3];
};

struct daisy_symmetry_index_777 {
    int fd;
    size_t size;
    unsigned char *mapping;
    const struct daisy_symmetry_index_header_777 *header;
    const uint64_t *bitmap;
    const uint32_t *block_rank;
};

static uint64_t
daisy_symmetry_index_size_777(uint64_t block_count)
{
    return sizeof(struct daisy_symmetry_index_header_777) +
        block_count * DAISY_RANK_BLOCK_WORDS_777 * sizeof(uint64_t) +
        block_count * sizeof(uint32_t);
}

static uint64_t
daisy_symmetry_block_count_777(uint64_t raw_universe)
{
    return (raw_universe + DAISY_RANK_BLOCK_BITS_777 - 1) / DAISY_RANK_BLOCK_BITS_777;
}

/* Reports what went wrong through `problem` rather than exiting, so callers can
 * phrase the failure their own way. */
static int
daisy_symmetry_index_open_777(
    struct daisy_symmetry_index_777 *index,
    const char *filename,
    const char **problem)
{
    struct stat file_stat;

    index->fd = open(filename, O_RDONLY);
    if (index->fd < 0) {
        *problem = "could not open";
        return 0;
    }
    if (fstat(index->fd, &file_stat) != 0) {
        *problem = "could not stat";
        return 0;
    }
    index->size = (size_t) file_stat.st_size;
    index->mapping = mmap(NULL, index->size, PROT_READ, MAP_SHARED, index->fd, 0);
    if (index->mapping == MAP_FAILED) {
        *problem = "could not mmap";
        return 0;
    }
    index->header = (const struct daisy_symmetry_index_header_777 *) index->mapping;
    errno = 0;
    if (index->size < sizeof(*index->header) ||
            memcmp(index->header->magic, DAISY_RANK_INDEX_MAGIC_777, 8) ||
            index->header->raw_universe != DAISY_PERFECT_UNIVERSE_777 ||
            index->header->orbit_count != DAISY_PERFECT_ORBIT_COUNT_777) {
        *problem = "is not a 7x7x7 center symmetry index";
        return 0;
    }
    if (index->header->block_count != daisy_symmetry_block_count_777(DAISY_PERFECT_UNIVERSE_777) ||
            index->header->word_count !=
                index->header->block_count * DAISY_RANK_BLOCK_WORDS_777 ||
            index->size != daisy_symmetry_index_size_777(index->header->block_count)) {
        *problem = "has an inconsistent symmetry index size";
        return 0;
    }
    index->bitmap = (const uint64_t *) (index->mapping + sizeof(*index->header));
    index->block_rank = (const uint32_t *) (index->bitmap + index->header->word_count);
    return 1;
}

static void
daisy_symmetry_index_close_777(struct daisy_symmetry_index_777 *index)
{
    if (index->mapping && index->mapping != MAP_FAILED) {
        munmap(index->mapping, index->size);
    }
    if (index->fd >= 0) {
        close(index->fd);
    }
    index->fd = -1;
    index->mapping = NULL;
    index->header = NULL;
}

/*
 * The compacted position of a canonical raw rank, or UINT64_MAX if the rank is
 * not canonical, which only happens if the index does not match the table.
 */
static uint64_t
daisy_symmetry_dense_rank_777(const struct daisy_symmetry_index_777 *index, uint64_t raw)
{
    uint64_t word = raw >> 6;
    uint64_t block = raw / DAISY_RANK_BLOCK_BITS_777;
    uint64_t below = UINT64_C(1) << (raw & 63);
    uint64_t dense;

    if (!(index->bitmap[word] & below)) {
        return UINT64_MAX;
    }
    dense = index->block_rank[block];
    for (uint64_t scan = block * DAISY_RANK_BLOCK_WORDS_777; scan < word; scan++) {
        dense += (unsigned int) __builtin_popcountll(index->bitmap[scan]);
    }
    return dense + (unsigned int) __builtin_popcountll(index->bitmap[word] & (below - 1));
}

#endif
