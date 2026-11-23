/*
 * Goal ball for the native 5x5 phase 1: every center state within D moves of staged, stored once per
 * 48-symmetry orbit, with its exact distance to staged for each orbit-0 OLL parity.
 *
 * A state is the FLU symbol of each of the 24 t-center and 24 x-center positions (8 of each symbol).
 * Each of the 48 cube symmetries maps staged onto staged once the three symbols are relabelled to
 * follow their axes, and it maps the move set onto itself with wide quarter turns onto wide quarter
 * turns (lrj_check_conjugation). So both distances are constant on an orbit.
 *
 * Canonical form: the image with the smallest key over the 48 symmetries. The key ranks the image's
 * L t-mask by its 16-symmetry class (lr_joint_555.h), then its U t-mask among the 16 positions left,
 * its L x-mask in C(24,8), and its U x-mask among the 16 positions left. It is below 2^62.4 and
 * determines the state exactly. Only the symmetries that send some axis's t-mask to the smallest class
 * are scored, usually one or two.
 *
 * The file is a 4096-byte header followed by 2^S open-addressed 8-byte slots. A slot holds the even
 * and odd distances as depth + 1 nibbles (0 is more than D away), the linear-probe offset from the home
 * slot, and the bits of the mixed key above the home slot index. Mixing is a bijection, so a lookup
 * never confuses two keys. An empty slot is 0.
 *
 * The lookup-tables builder (build-555-goal-ball.c) and the searcher both include this file.
 * lrj_init must run before gb_init.
 */
#ifndef GOAL_BALL_555_H
#define GOAL_BALL_555_H

#include "lr_joint_555.h"

#define GB_MAGIC "555BALL1"
#define GB_VERSION 1
#define GB_HEADER_BYTES 4096
#define GB_RANK16 12870
#define GB_MAX_DEPTH 14
#define GB_MAX_PROBE 1023
#define GB_MIN_SLOTS_LOG2 17
#define GB_MAX_SLOTS_LOG2 40
#define GB_UNSEEN 255
#define GB_MASK24 UINT32_C(0xFFFFFF)
#define GB_KEY_BITS 63

struct gb_header {
    char magic[8];
    uint32_t version;
    uint32_t slots_log2;
    uint32_t max_depth;
    uint32_t reserved;
    uint64_t states;
    uint64_t depth_counts[GB_MAX_DEPTH + 1]; /* states whose nearer parity is at each depth */
};

struct gb_tables {
    unsigned char compose[LRJ_SYMMETRIES][LRJ_SYMMETRIES]; /* [h][g] = apply g, then h */
    unsigned char sigma[LRJ_SYMMETRIES][3];                /* symbol s becomes sigma[g][s] under g */
    unsigned char sigma_inverse[LRJ_SYMMETRIES][3];
    uint16_t rank16[1 << 16]; /* 16-bit masks with 8 bits set, in numeric order */
    uint16_t unrank16[GB_RANK16];
};

static struct gb_tables gb;

/* Staged masks for symbols F, L, U; t and x positions follow the same face order. */
static const uint32_t gb_goal_mask[3] = {0x0F0F00, 0x00F0F0, 0xF0000F};

/* Packs the bits of value at the positions set in keep. */
static inline uint32_t gb_compress(uint32_t value, uint32_t keep)
{
    uint32_t packed = 0;

    for (unsigned int out = 0; keep; out++) {
        uint32_t bit = keep & (0u - keep);

        if (value & bit) {
            packed |= UINT32_C(1) << out;
        }
        keep ^= bit;
    }
    return packed;
}

/* Inverse of gb_compress. */
static inline uint32_t gb_expand(uint32_t packed, uint32_t keep)
{
    uint32_t value = 0;

    for (unsigned int in = 0; keep; in++) {
        uint32_t bit = keep & (0u - keep);

        if (packed & (UINT32_C(1) << in)) {
            value |= bit;
        }
        keep ^= bit;
    }
    return value;
}

static inline uint32_t gb_apply(unsigned int symmetry, uint32_t mask, int x_orbit)
{
    return lrj_apply_chunks(mask, x_orbit ? lrj.sym_x_chunk[symmetry] : lrj.sym_t_chunk[symmetry]);
}

/* Image of a state under a symmetry, symbols relabelled so staged stays staged. */
static inline void gb_transform(unsigned int symmetry, const uint32_t t[3], const uint32_t x[3], uint32_t t_out[3], uint32_t x_out[3])
{
    for (unsigned int symbol = 0; symbol < 3; symbol++) {
        t_out[gb.sigma[symmetry][symbol]] = gb_apply(symmetry, t[symbol], 0);
        x_out[gb.sigma[symmetry][symbol]] = gb_apply(symmetry, x[symbol], 1);
    }
}

static inline uint64_t gb_key_under(unsigned int symmetry, uint32_t class_id, const uint32_t t[3], const uint32_t x[3])
{
    unsigned int from_l = gb.sigma_inverse[symmetry][1];
    unsigned int from_u = gb.sigma_inverse[symmetry][2];
    uint32_t t_l = gb_apply(symmetry, t[from_l], 0);
    uint32_t t_u = gb_apply(symmetry, t[from_u], 0);
    uint32_t x_l = gb_apply(symmetry, x[from_l], 1);
    uint32_t x_u = gb_apply(symmetry, x[from_u], 1);
    uint64_t key = class_id;

    key = key * GB_RANK16 + gb.rank16[gb_compress(t_u, ~t_l & GB_MASK24)];
    key = key * LRJ_UNIVERSE + lrj_rank(x_l);
    return key * GB_RANK16 + gb.rank16[gb_compress(x_u, ~x_l & GB_MASK24)];
}

/* Canonical key of a state given as masks per FLU symbol (lrj_symbol_masks). */
static inline uint64_t gb_canonical_key(const uint32_t t[3], const uint32_t x[3])
{
    unsigned char candidates[LRJ_SYMMETRIES];
    unsigned int candidate_count = 0;
    uint32_t best_class = UINT32_MAX;
    uint64_t best_key = UINT64_MAX;

    for (unsigned int axis = 0; axis < 3; axis++) {
        unsigned int to_lr = (unsigned int)lrj.axis_sym[axis];
        uint32_t mask = gb_apply(to_lr, t[lrj_axis_symbol[axis]], 0);
        uint32_t entry = lrj.class_of[lrj_rank(mask)];
        uint32_t class_id = entry >> 4;
        unsigned int onto_rep = gb.compose[lrj.keeper[entry & 15]][to_lr];

        if (class_id > best_class) {
            continue;
        }
        if (class_id < best_class) {
            best_class = class_id;
            candidate_count = 0;
        }
        for (unsigned int index = 0; index < lrj.stab_count[class_id]; index++) {
            candidates[candidate_count++] = gb.compose[lrj.keeper[lrj.stab[class_id][index]]][onto_rep];
        }
    }
    for (unsigned int index = 0; index < candidate_count; index++) {
        uint64_t key = gb_key_under(candidates[index], best_class, t, x);

        best_key = key < best_key ? key : best_key;
    }
    return best_key;
}

/* Masks of the canonical state a key stands for. */
static inline void gb_decode_key(uint64_t key, uint32_t t[3], uint32_t x[3])
{
    uint32_t x_u_rank = (uint32_t)(key % GB_RANK16);
    uint32_t x_l_rank;
    uint32_t t_u_rank;
    uint32_t class_id;

    key /= GB_RANK16;
    x_l_rank = (uint32_t)(key % LRJ_UNIVERSE);
    key /= LRJ_UNIVERSE;
    t_u_rank = (uint32_t)(key % GB_RANK16);
    class_id = (uint32_t)(key / GB_RANK16);
    t[1] = lrj.rep_mask[class_id];
    t[2] = gb_expand(gb.unrank16[t_u_rank], ~t[1] & GB_MASK24);
    t[0] = ~(t[1] | t[2]) & GB_MASK24;
    x[1] = lrj_unrank(x_l_rank);
    x[2] = gb_expand(gb.unrank16[x_u_rank], ~x[1] & GB_MASK24);
    x[0] = ~(x[1] | x[2]) & GB_MASK24;
}

/* Bijection on [0, 2^63): xorshifts and odd multipliers modulo 2^63. */
static inline uint64_t gb_mix(uint64_t key)
{
    const uint64_t low63 = (UINT64_C(1) << GB_KEY_BITS) - 1;

    key ^= key >> 31;
    key = (key * UINT64_C(0x5851F42D4C957F2D)) & low63;
    key ^= key >> 29;
    key = (key * UINT64_C(0x9E3779B97F4A7C15)) & low63;
    key ^= key >> 32;
    return key;
}

static inline uint64_t gb_slot_quotient(uint64_t slot)
{
    return slot >> 18;
}

static inline unsigned int gb_slot_delta(uint64_t slot)
{
    return (unsigned int)((slot >> 8) & GB_MAX_PROBE);
}

/* Even and odd nibbles (depth + 1, 0 unseen) of a key, or 0 when the key is not in the ball. */
static inline unsigned int gb_lookup(const uint64_t *slots, unsigned int slots_log2, uint64_t key)
{
    uint64_t mixed = gb_mix(key);
    uint64_t mask = (UINT64_C(1) << slots_log2) - 1;
    uint64_t home = mixed & mask;
    uint64_t quotient = mixed >> slots_log2;

    for (unsigned int delta = 0; delta <= GB_MAX_PROBE; delta++) {
        uint64_t slot = slots[(home + delta) & mask];

        if (!slot) {
            return 0;
        }
        if (gb_slot_delta(slot) == delta && gb_slot_quotient(slot) == quotient) {
            return (unsigned int)(slot & 0xff);
        }
    }
    return 0;
}

/* Distance for a parity (0 even, 1 odd) from gb_lookup's nibbles, or GB_UNSEEN. */
static inline unsigned int gb_distance(unsigned int nibbles, unsigned int parity)
{
    unsigned int value = (nibbles >> (4 * parity)) & 15;

    return value ? value - 1 : GB_UNSEEN;
}

static inline int gb_is_goal(const uint32_t t[3], const uint32_t x[3])
{
    for (unsigned int symbol = 0; symbol < 3; symbol++) {
        if (t[symbol] != gb_goal_mask[symbol] || x[symbol] != gb_goal_mask[symbol]) {
            return 0;
        }
    }
    return 1;
}

static inline void gb_init(void)
{
    unsigned int rank = 0;

    for (unsigned int symmetry = 0; symmetry < LRJ_SYMMETRIES; symmetry++) {
        for (unsigned int symbol = 0; symbol < 3; symbol++) {
            uint32_t t_image = gb_apply(symmetry, gb_goal_mask[symbol], 0);
            uint32_t x_image = gb_apply(symmetry, gb_goal_mask[symbol], 1);
            int found = -1;

            for (unsigned int target = 0; target < 3; target++) {
                if (t_image == gb_goal_mask[target] && x_image == gb_goal_mask[target]) {
                    found = (int)target;
                }
            }
            if (found < 0) {
                lrj_fail("a symmetry does not map staged onto staged");
            }
            gb.sigma[symmetry][symbol] = (unsigned char)found;
            gb.sigma_inverse[symmetry][found] = (unsigned char)symbol;
        }
        for (unsigned int first = 0; first < LRJ_SYMMETRIES; first++) {
            int found = -1;

            for (unsigned int candidate = 0; candidate < LRJ_SYMMETRIES && found < 0; candidate++) {
                int matches = 1;

                for (unsigned int source = 0; source < LRJ_POSITIONS && matches; source++) {
                    matches = lrj.sym_t[candidate][source] == lrj.sym_t[symmetry][lrj.sym_t[first][source]] &&
                              lrj.sym_x[candidate][source] == lrj.sym_x[symmetry][lrj.sym_x[first][source]];
                }
                found = matches ? (int)candidate : -1;
            }
            if (found < 0) {
                lrj_fail("the 48 symmetries are not closed under composition");
            }
            gb.compose[symmetry][first] = (unsigned char)found;
        }
    }
    for (uint32_t mask = 0; mask < (1 << 16); mask++) {
        if (__builtin_popcount(mask) == 8) {
            gb.rank16[mask] = (uint16_t)rank;
            gb.unrank16[rank++] = (uint16_t)mask;
        }
    }
    if (rank != GB_RANK16) {
        lrj_fail("C(16,8) rank table has the wrong size");
    }
}

#endif
