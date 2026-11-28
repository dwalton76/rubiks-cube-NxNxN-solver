/*
 * Joint LR t-center + x-center table for the native 5x5 phase 1.
 *
 * A state is the pair of 24-bit masks that mark the L/R stickers on the 24
 * t-center positions and the 24 x-center positions (8 of each). That is
 * C(24,8)^2 = 540,917,591,841 raw states. The 16 symmetries that keep the LR
 * axis (the 8 sign flips of the three axes, with or without swapping U/D and
 * F/B) act on the pair at once, and the 5x5 move set is closed under them.
 *
 * The table is two-coordinate. The t mask is reduced to one of 46,935
 * classes, with the symmetry k that sent it to the class representative. The
 * x mask is then rotated by the same k and ranked in C(24,8). The cell is
 * class * 735,471 + rank. A class representative can have a nontrivial
 * stabilizer; the pair then has several cells that hold the same distance,
 * and every writer must write all of them (see lrj.stab).
 *
 * The packed file stores one nibble per cell: depth + 1, 0 is unseen.
 *
 * The lookup-tables builder (build-555-lr-joint.c) and the searcher both
 * include this file, so geometry and indexing cannot drift apart.
 */
#ifndef LR_JOINT_555_H
#define LR_JOINT_555_H

#include "ida_search_core.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LRJ_POSITIONS 24
#define LRJ_SELECTED 8
#define LRJ_UNIVERSE UINT64_C(735471)
#define LRJ_SYMMETRIES 48
#define LRJ_GROUP 16
#define LRJ_MOVES MOVE_COUNT_555
#define LRJ_CUBE_ARRAY 151
#define LRJ_GOAL_MASK UINT32_C(0x00F0F0)
#define LRJ_MAX_NIBBLE 15

/* Centers of the 5x5, faces U, L, F, R, B, D with 25 squares each. */
static const unsigned int lrj_t_squares[LRJ_POSITIONS] = {
    8, 12, 14, 18, 33, 37, 39, 43, 58, 62, 64, 68,
    83, 87, 89, 93, 108, 112, 114, 118, 133, 137, 139, 143,
};
static const unsigned int lrj_x_squares[LRJ_POSITIONS] = {
    7, 9, 17, 19, 32, 34, 42, 44, 57, 59, 67, 69,
    82, 84, 92, 94, 107, 109, 117, 119, 132, 134, 142, 144,
};

struct lrj_state {
    unsigned char t_dest[LRJ_MOVES][LRJ_POSITIONS];
    unsigned char x_dest[LRJ_MOVES][LRJ_POSITIONS];
    uint32_t t_chunk[LRJ_MOVES][3][256];
    uint32_t x_chunk[LRJ_MOVES][3][256];
    unsigned char sym_t[LRJ_SYMMETRIES][LRJ_POSITIONS];
    unsigned char sym_x[LRJ_SYMMETRIES][LRJ_POSITIONS];
    uint32_t sym_t_chunk[LRJ_SYMMETRIES][3][256];
    uint32_t sym_x_chunk[LRJ_SYMMETRIES][3][256];
    unsigned char keeper[LRJ_GROUP]; /* symmetry index of each LR-axis keeper */
    uint32_t classes;
    uint32_t *class_of;              /* t rank -> class << 4 | keeper index that sends it to the representative */
    uint32_t *rep_mask;              /* class -> representative t mask */
    unsigned char *stab_count;       /* class -> number of keepers that fix the representative */
    unsigned char (*stab)[LRJ_GROUP]; /* class -> those keeper indexes */
    uint32_t *x_sym_rank[LRJ_GROUP]; /* keeper index -> x rank -> rank of the rotated x mask (builder only) */
    int axis_sym[3];                 /* symmetry that carries the L, U, or F axis masks onto the LR goal */
    /* C(24,8) rank split at position 12: low 12 bits, then high 12 bits given how many selected bits remain. */
    uint32_t rank_low[1 << 12];
    uint32_t rank_high[LRJ_SELECTED + 1][1 << 12];
};

static struct lrj_state lrj;

/* FLU state symbols for the L, U, and F axes. Each axis is mapped onto LR before its cell is read. */
static const unsigned char lrj_axis_symbol[3] = {1, 2, 0};

static inline uint64_t lrj_cell_count(void)
{
    return (uint64_t)lrj.classes * LRJ_UNIVERSE;
}

/* Lexicographic C(24,8) rank of an 8-bit mask; lrj_init_rank must run first. */
static inline uint32_t lrj_rank(uint32_t selected)
{
    uint32_t low = selected & 0xfff;

    return lrj.rank_low[low] + lrj.rank_high[LRJ_SELECTED - __builtin_popcount(low)][selected >> 12];
}

/* Rank contribution of 12 positions starting at first, with remaining selected bits still to place. */
static inline uint32_t lrj_rank_span(uint32_t bits, unsigned int first, unsigned int remaining)
{
    uint64_t rank = 0;

    for (unsigned int offset = 0; offset < 12; offset++) {
        if (bits & (UINT32_C(1) << offset)) {
            remaining -= remaining ? 1 : 0;
        } else if (remaining) {
            rank += binom[LRJ_POSITIONS - (first + offset) - 1][remaining - 1];
        }
    }
    return (uint32_t)rank;
}

static inline uint32_t lrj_unrank(uint32_t rank_in)
{
    uint64_t rank = rank_in;
    uint32_t mask = 0;
    unsigned int remaining = LRJ_SELECTED;

    for (unsigned int position = 0; position < LRJ_POSITIONS && remaining; position++) {
        uint64_t selected_prefix = binom[LRJ_POSITIONS - position - 1][remaining - 1];

        if (rank < selected_prefix) {
            mask |= UINT32_C(1) << position;
            remaining--;
        } else {
            rank -= selected_prefix;
        }
    }
    return mask;
}

static inline uint32_t lrj_apply_chunks(uint32_t mask, const uint32_t chunks[3][256])
{
    return chunks[0][mask & 0xff] | chunks[1][(mask >> 8) & 0xff] | chunks[2][(mask >> 16) & 0xff];
}

static inline uint32_t lrj_apply_t(unsigned int move_index, uint32_t mask)
{
    return lrj_apply_chunks(mask, lrj.t_chunk[move_index]);
}

static inline uint32_t lrj_apply_x(unsigned int move_index, uint32_t mask)
{
    return lrj_apply_chunks(mask, lrj.x_chunk[move_index]);
}

static inline uint32_t lrj_keeper_t(unsigned int keeper_index, uint32_t mask)
{
    return lrj_apply_chunks(mask, lrj.sym_t_chunk[lrj.keeper[keeper_index]]);
}

static inline uint32_t lrj_keeper_x(unsigned int keeper_index, uint32_t mask)
{
    return lrj_apply_chunks(mask, lrj.sym_x_chunk[lrj.keeper[keeper_index]]);
}

/* Cell of a (t mask, x mask) pair. Any cell of the pair's stabilizer set is as good as another. */
static inline uint64_t lrj_cell_index(uint32_t t_mask, uint32_t x_mask)
{
    uint32_t entry = lrj.class_of[lrj_rank(t_mask)];

    return (uint64_t)(entry >> 4) * LRJ_UNIVERSE + lrj_rank(lrj_keeper_x(entry & 15, x_mask));
}

/* Packed file: nibble 0 of byte i is cell 2i, nibble 1 is cell 2i+1. Value is depth + 1, 0 is unseen. */
static inline uint64_t lrj_packed_bytes(void)
{
    return (lrj_cell_count() + 1) / 2;
}

/* Parity of a move for orbit-0 OLL: 1 for the wide quarter turns, 0 for every other 5x5 move. */
static inline unsigned char lrj_move_parity(move_type move)
{
    switch (move) {
    case Uw:
    case Uw_PRIME:
    case Lw:
    case Lw_PRIME:
    case Fw:
    case Fw_PRIME:
    case Rw:
    case Rw_PRIME:
    case Bw:
    case Bw_PRIME:
    case Dw:
    case Dw_PRIME:
        return 1;
    default:
        return 0;
    }
}

static inline unsigned int lrj_nibble_get(const unsigned char *packed, uint64_t cell)
{
    unsigned char byte = packed[cell >> 1];

    return (cell & 1) ? (unsigned int)(byte >> 4) : (unsigned int)(byte & 15);
}

static inline void lrj_fail(const char *message)
{
    fprintf(stderr, "ERROR: %s\n", message);
    exit(1);
}

static inline void lrj_square_coordinate(unsigned int square, int8_t position[3])
{
    static const int8_t coordinate[5] = {-4, -2, 0, 2, 4};
    unsigned int face = (square - 1) / 25;
    unsigned int offset = (square - 1) % 25;
    int row = (int)(offset / 5);
    int col = (int)(offset % 5);

    switch (face) {
    case 0: position[0] = coordinate[col]; position[1] = 5; position[2] = coordinate[row]; break;
    case 1: position[0] = -5; position[1] = -coordinate[row]; position[2] = coordinate[col]; break;
    case 2: position[0] = coordinate[col]; position[1] = -coordinate[row]; position[2] = 5; break;
    case 3: position[0] = 5; position[1] = -coordinate[row]; position[2] = -coordinate[col]; break;
    case 4: position[0] = -coordinate[col]; position[1] = -coordinate[row]; position[2] = -5; break;
    default: position[0] = coordinate[col]; position[1] = -5; position[2] = -coordinate[row]; break;
    }
}

static inline int lrj_all_moves(move_type move)
{
    (void)move;
    return 1;
}

/* dest[move][source position] = position that sticker lands on. */
static inline void lrj_init_destinations(
    const unsigned int squares[LRJ_POSITIONS],
    unsigned char dest[LRJ_MOVES][LRJ_POSITIONS]
)
{
    char marker[LRJ_CUBE_ARRAY];
    char scratch[LRJ_CUBE_ARRAY];
    int square_to_position[LRJ_CUBE_ARRAY];

    for (unsigned int square = 0; square < LRJ_CUBE_ARRAY; square++) {
        marker[square] = (char)square;
        square_to_position[square] = -1;
    }
    for (unsigned int position = 0; position < LRJ_POSITIONS; position++) {
        square_to_position[squares[position]] = (int)position;
    }
    for (unsigned int move_index = 0; move_index < LRJ_MOVES; move_index++) {
        char moved[LRJ_CUBE_ARRAY];

        memcpy(moved, marker, sizeof(moved));
        rotate_555_centers(moved, scratch, LRJ_CUBE_ARRAY, moves_555[move_index]);
        for (unsigned int destination = 0; destination < LRJ_POSITIONS; destination++) {
            unsigned int source_square = (unsigned char)moved[squares[destination]];
            int source = source_square < LRJ_CUBE_ARRAY ? square_to_position[source_square] : -1;

            if (source < 0) {
                lrj_fail("a center orbit is not closed under a 5x5 move");
            }
            dest[move_index][source] = (unsigned char)destination;
        }
    }
}

static inline void lrj_init_chunks(
    const unsigned char permutation[][LRJ_POSITIONS],
    unsigned int count,
    uint32_t chunks[][3][256]
)
{
    for (unsigned int index = 0; index < count; index++) {
        for (unsigned int chunk = 0; chunk < 3; chunk++) {
            for (unsigned int value = 0; value < 256; value++) {
                uint32_t transformed = 0;

                for (unsigned int bit = 0; bit < 8; bit++) {
                    if (value & (1U << bit)) {
                        transformed |= UINT32_C(1) << permutation[index][chunk * 8 + bit];
                    }
                }
                chunks[index][chunk][value] = transformed;
            }
        }
    }
}

static inline void lrj_init_symmetries(
    const unsigned int squares[LRJ_POSITIONS],
    unsigned char table[LRJ_SYMMETRIES][LRJ_POSITIONS]
)
{
    static const unsigned char axis_perm[6][3] = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
    int8_t coords[LRJ_POSITIONS][3];
    unsigned int symmetry = 0;

    for (unsigned int position = 0; position < LRJ_POSITIONS; position++) {
        lrj_square_coordinate(squares[position], coords[position]);
    }
    for (unsigned int permutation = 0; permutation < 6; permutation++) {
        const unsigned char *axes = axis_perm[permutation];

        for (unsigned int sign_bits = 0; sign_bits < 8; sign_bits++, symmetry++) {
            for (unsigned int source = 0; source < LRJ_POSITIONS; source++) {
                int8_t image[3] = {0, 0, 0};
                unsigned int destination = LRJ_POSITIONS;

                for (unsigned int axis = 0; axis < 3; axis++) {
                    int sign = (sign_bits & (1u << axis)) ? 1 : -1;

                    image[axes[axis]] = (int8_t)(sign * coords[source][axis]);
                }
                for (unsigned int candidate = 0; candidate < LRJ_POSITIONS; candidate++) {
                    if (coords[candidate][0] == image[0] && coords[candidate][1] == image[1] &&
                        coords[candidate][2] == image[2]) {
                        destination = candidate;
                        break;
                    }
                }
                if (destination == LRJ_POSITIONS) {
                    lrj_fail("a symmetry leaves the center coordinates");
                }
                table[symmetry][source] = (unsigned char)destination;
            }
        }
    }
}

/* Symmetry index = axis permutation * 8 + sign bits; the LR-axis keepers fix axis 0. */
static inline int lrj_symmetry_keeps_lr(unsigned int symmetry)
{
    return symmetry / 8 < 2;
}

/* Every symmetry must conjugate the move set onto itself, for t and x together. */
static inline void lrj_check_conjugation(void)
{
    for (unsigned int symmetry = 0; symmetry < LRJ_SYMMETRIES; symmetry++) {
        for (unsigned int move = 0; move < LRJ_MOVES; move++) {
            int found = 0;

            for (unsigned int candidate = 0; candidate < LRJ_MOVES; candidate++) {
                int matches = 1;

                for (unsigned int source = 0; source < LRJ_POSITIONS && matches; source++) {
                    matches = lrj.sym_t[symmetry][lrj.t_dest[move][source]] ==
                                  lrj.t_dest[candidate][lrj.sym_t[symmetry][source]] &&
                              lrj.sym_x[symmetry][lrj.x_dest[move][source]] ==
                                  lrj.x_dest[candidate][lrj.sym_x[symmetry][source]];
                }
                if (matches) {
                    found = 1;
                    break;
                }
            }
            if (!found) {
                lrj_fail("5x5 center moves do not match the symmetry geometry");
            }
        }
    }
}

static inline void lrj_init_classes(void)
{
    uint32_t *class_by_rank = malloc((size_t)LRJ_UNIVERSE * sizeof(*class_by_rank));
    uint32_t class_total = 0;

    lrj.class_of = malloc((size_t)LRJ_UNIVERSE * sizeof(*lrj.class_of));
    if (!class_by_rank || !lrj.class_of) {
        lrj_fail("out of memory");
    }
    for (uint32_t rank = 0; rank < LRJ_UNIVERSE; rank++) {
        uint32_t mask = lrj_unrank(rank);
        int is_canonical = 1;

        for (unsigned int keeper = 0; keeper < LRJ_GROUP && is_canonical; keeper++) {
            is_canonical = lrj_keeper_t(keeper, mask) >= mask;
        }
        class_by_rank[rank] = is_canonical ? class_total++ : UINT32_MAX;
    }
    lrj.classes = class_total;
    lrj.rep_mask = malloc((size_t)class_total * sizeof(*lrj.rep_mask));
    lrj.stab_count = calloc(class_total, sizeof(*lrj.stab_count));
    lrj.stab = calloc(class_total, sizeof(*lrj.stab));
    if (!lrj.rep_mask || !lrj.stab_count || !lrj.stab) {
        lrj_fail("out of memory");
    }
    for (uint32_t rank = 0; rank < LRJ_UNIVERSE; rank++) {
        uint32_t mask = lrj_unrank(rank);
        uint32_t canonical = mask;
        unsigned int canonical_keeper = 0;

        for (unsigned int keeper = 0; keeper < LRJ_GROUP; keeper++) {
            uint32_t image = lrj_keeper_t(keeper, mask);

            if (image < canonical) {
                canonical = image;
                canonical_keeper = keeper;
            }
        }
        if (canonical == mask) {
            uint32_t class_id = class_by_rank[rank];

            lrj.rep_mask[class_id] = mask;
            for (unsigned int keeper = 0; keeper < LRJ_GROUP; keeper++) {
                if (lrj_keeper_t(keeper, mask) == mask) {
                    lrj.stab[class_id][lrj.stab_count[class_id]++] = (unsigned char)keeper;
                }
            }
            canonical_keeper = lrj.stab[class_id][0];
            lrj.class_of[rank] = (class_id << 4) | canonical_keeper;
        } else {
            lrj.class_of[rank] = (class_by_rank[lrj_rank(canonical)] << 4) | canonical_keeper;
        }
    }
    free(class_by_rank);
}

static inline void lrj_init_rank(void)
{
    for (uint32_t bits = 0; bits < (1 << 12); bits++) {
        lrj.rank_low[bits] = lrj_rank_span(bits, 0, LRJ_SELECTED);
        for (unsigned int remaining = 0; remaining <= LRJ_SELECTED; remaining++) {
            lrj.rank_high[remaining][bits] = lrj_rank_span(bits, 12, remaining);
        }
    }
    for (uint32_t rank = 0; rank < LRJ_UNIVERSE; rank++) {
        if (lrj_rank(lrj_unrank(rank)) != rank) {
            lrj_fail("split C(24,8) rank disagrees with unrank");
        }
    }
}

static inline void lrj_init_x_sym_rank(void)
{
    for (unsigned int keeper = 0; keeper < LRJ_GROUP; keeper++) {
        lrj.x_sym_rank[keeper] = malloc((size_t)LRJ_UNIVERSE * sizeof(uint32_t));
        if (!lrj.x_sym_rank[keeper]) {
            lrj_fail("out of memory");
        }
    }
    for (uint32_t rank = 0; rank < LRJ_UNIVERSE; rank++) {
        uint32_t mask = lrj_unrank(rank);

        for (unsigned int keeper = 0; keeper < LRJ_GROUP; keeper++) {
            lrj.x_sym_rank[keeper][rank] = lrj_rank(lrj_keeper_x(keeper, mask));
        }
    }
}

/* Finds, for each axis, a symmetry that maps the axis's t and x masks onto the LR goal masks.
 * The LR axis itself uses whichever symmetry the search finds first, usually the identity. */
static inline void lrj_init_axis_symmetries(void)
{
    static const uint32_t goal_axis[3] = {0x00F0F0, 0xF0000F, 0x0F0F00};

    for (unsigned int axis = 0; axis < 3; axis++) {
        lrj.axis_sym[axis] = -1;
        for (unsigned int symmetry = 0; symmetry < LRJ_SYMMETRIES && lrj.axis_sym[axis] < 0; symmetry++) {
            if (lrj_apply_chunks(goal_axis[axis], lrj.sym_t_chunk[symmetry]) == LRJ_GOAL_MASK &&
                lrj_apply_chunks(goal_axis[axis], lrj.sym_x_chunk[symmetry]) == LRJ_GOAL_MASK) {
                lrj.axis_sym[axis] = (int)symmetry;
            }
        }
        if (lrj.axis_sym[axis] < 0) {
            lrj_fail("no symmetry maps an axis onto the LR goal");
        }
    }
}

/* masks[symbol] marks the positions of an FLU state (symbols 0, 1, 2) that hold that symbol. */
static inline void lrj_symbol_masks(const unsigned char state[LRJ_POSITIONS], uint32_t masks[3])
{
    masks[0] = masks[1] = masks[2] = 0;
    for (unsigned int bit = 0; bit < LRJ_POSITIONS; bit++) {
        masks[state[bit]] |= UINT32_C(1) << bit;
    }
}

/* Rank of one axis's t mask (0 = L, 1 = U, 2 = F), the class_of index lrj_axis_cell_from_t_rank needs. */
static inline uint32_t lrj_axis_t_rank(unsigned int axis, const uint32_t t_masks[3])
{
    return lrj_rank(lrj_apply_chunks(t_masks[lrj_axis_symbol[axis]], lrj.sym_t_chunk[lrj.axis_sym[axis]]));
}

static inline uint64_t lrj_axis_cell_from_t_rank(unsigned int axis, uint32_t t_rank, const uint32_t x_masks[3])
{
    uint32_t entry = lrj.class_of[t_rank];
    uint32_t x_mask = lrj_apply_chunks(x_masks[lrj_axis_symbol[axis]], lrj.sym_x_chunk[lrj.axis_sym[axis]]);

    return (uint64_t)(entry >> 4) * LRJ_UNIVERSE + lrj_rank(lrj_keeper_x(entry & 15, x_mask));
}

/* Cell for the joint table of one axis (0 = L, 1 = U, 2 = F), from lrj_symbol_masks of the t and x states. */
static inline uint64_t lrj_axis_cell_from_masks(unsigned int axis, const uint32_t t_masks[3], const uint32_t x_masks[3])
{
    return lrj_axis_cell_from_t_rank(axis, lrj_axis_t_rank(axis, t_masks), x_masks);
}

/* Build every table. Aborts if the symmetry geometry and the move tables disagree.
 * x_sym_rank (47 MB) is only built when the caller writes cells, as the builder does. */
static inline void lrj_init(int with_x_sym_rank)
{
    unsigned int keeper_count = 0;

    init_binom();
    lrj_init_rank();
    lrj_init_destinations(lrj_t_squares, lrj.t_dest);
    lrj_init_destinations(lrj_x_squares, lrj.x_dest);
    lrj_init_chunks(lrj.t_dest, LRJ_MOVES, lrj.t_chunk);
    lrj_init_chunks(lrj.x_dest, LRJ_MOVES, lrj.x_chunk);
    lrj_init_symmetries(lrj_t_squares, lrj.sym_t);
    lrj_init_symmetries(lrj_x_squares, lrj.sym_x);
    lrj_init_chunks(lrj.sym_t, LRJ_SYMMETRIES, lrj.sym_t_chunk);
    lrj_init_chunks(lrj.sym_x, LRJ_SYMMETRIES, lrj.sym_x_chunk);
    lrj_check_conjugation();
    for (unsigned int symmetry = 0; symmetry < LRJ_SYMMETRIES; symmetry++) {
        if (lrj_symmetry_keeps_lr(symmetry)) {
            lrj.keeper[keeper_count++] = (unsigned char)symmetry;
        }
    }
    if (keeper_count != LRJ_GROUP) {
        lrj_fail("expected 16 LR-axis symmetries");
    }
    lrj_init_classes();
    if (with_x_sym_rank) {
        lrj_init_x_sym_rank();
    }
    lrj_init_axis_symmetries();
}

#endif
