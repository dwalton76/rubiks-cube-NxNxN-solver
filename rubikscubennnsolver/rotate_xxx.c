
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "ida_search_core.h"

    
void
rotate_444(char *cube, char *cube_tmp, int array_size, move_type move)
{
    /* This was contructed using utils/rotate-printer.py */
    memcpy(cube_tmp, cube, sizeof(char) * array_size);

    switch (move) {
    case U: {
        cube[1] = cube_tmp[13];
        cube[2] = cube_tmp[9];
        cube[3] = cube_tmp[5];
        cube[4] = cube_tmp[1];
        cube[5] = cube_tmp[14];
        cube[6] = cube_tmp[10];
        cube[7] = cube_tmp[6];
        cube[8] = cube_tmp[2];
        cube[9] = cube_tmp[15];
        cube[10] = cube_tmp[11];
        cube[11] = cube_tmp[7];
        cube[12] = cube_tmp[3];
        cube[13] = cube_tmp[16];
        cube[14] = cube_tmp[12];
        cube[15] = cube_tmp[8];
        cube[16] = cube_tmp[4];
        cube[17] = cube_tmp[33];
        cube[18] = cube_tmp[34];
        cube[19] = cube_tmp[35];
        cube[20] = cube_tmp[36];
        cube[33] = cube_tmp[49];
        cube[34] = cube_tmp[50];
        cube[35] = cube_tmp[51];
        cube[36] = cube_tmp[52];
        cube[49] = cube_tmp[65];
        cube[50] = cube_tmp[66];
        cube[51] = cube_tmp[67];
        cube[52] = cube_tmp[68];
        cube[65] = cube_tmp[17];
        cube[66] = cube_tmp[18];
        cube[67] = cube_tmp[19];
        cube[68] = cube_tmp[20];
        break;
    }

    case U_PRIME: {
        cube[1] = cube_tmp[4];
        cube[2] = cube_tmp[8];
        cube[3] = cube_tmp[12];
        cube[4] = cube_tmp[16];
        cube[5] = cube_tmp[3];
        cube[6] = cube_tmp[7];
        cube[7] = cube_tmp[11];
        cube[8] = cube_tmp[15];
        cube[9] = cube_tmp[2];
        cube[10] = cube_tmp[6];
        cube[11] = cube_tmp[10];
        cube[12] = cube_tmp[14];
        cube[13] = cube_tmp[1];
        cube[14] = cube_tmp[5];
        cube[15] = cube_tmp[9];
        cube[16] = cube_tmp[13];
        cube[17] = cube_tmp[65];
        cube[18] = cube_tmp[66];
        cube[19] = cube_tmp[67];
        cube[20] = cube_tmp[68];
        cube[33] = cube_tmp[17];
        cube[34] = cube_tmp[18];
        cube[35] = cube_tmp[19];
        cube[36] = cube_tmp[20];
        cube[49] = cube_tmp[33];
        cube[50] = cube_tmp[34];
        cube[51] = cube_tmp[35];
        cube[52] = cube_tmp[36];
        cube[65] = cube_tmp[49];
        cube[66] = cube_tmp[50];
        cube[67] = cube_tmp[51];
        cube[68] = cube_tmp[52];
        break;
    }

    case U2: {
        cube[1] = cube_tmp[16];
        cube[2] = cube_tmp[15];
        cube[3] = cube_tmp[14];
        cube[4] = cube_tmp[13];
        cube[5] = cube_tmp[12];
        cube[6] = cube_tmp[11];
        cube[7] = cube_tmp[10];
        cube[8] = cube_tmp[9];
        cube[9] = cube_tmp[8];
        cube[10] = cube_tmp[7];
        cube[11] = cube_tmp[6];
        cube[12] = cube_tmp[5];
        cube[13] = cube_tmp[4];
        cube[14] = cube_tmp[3];
        cube[15] = cube_tmp[2];
        cube[16] = cube_tmp[1];
        cube[17] = cube_tmp[49];
        cube[18] = cube_tmp[50];
        cube[19] = cube_tmp[51];
        cube[20] = cube_tmp[52];
        cube[33] = cube_tmp[65];
        cube[34] = cube_tmp[66];
        cube[35] = cube_tmp[67];
        cube[36] = cube_tmp[68];
        cube[49] = cube_tmp[17];
        cube[50] = cube_tmp[18];
        cube[51] = cube_tmp[19];
        cube[52] = cube_tmp[20];
        cube[65] = cube_tmp[33];
        cube[66] = cube_tmp[34];
        cube[67] = cube_tmp[35];
        cube[68] = cube_tmp[36];
        break;
    }

    case Uw: {
        cube[1] = cube_tmp[13];
        cube[2] = cube_tmp[9];
        cube[3] = cube_tmp[5];
        cube[4] = cube_tmp[1];
        cube[5] = cube_tmp[14];
        cube[6] = cube_tmp[10];
        cube[7] = cube_tmp[6];
        cube[8] = cube_tmp[2];
        cube[9] = cube_tmp[15];
        cube[10] = cube_tmp[11];
        cube[11] = cube_tmp[7];
        cube[12] = cube_tmp[3];
        cube[13] = cube_tmp[16];
        cube[14] = cube_tmp[12];
        cube[15] = cube_tmp[8];
        cube[16] = cube_tmp[4];
        cube[17] = cube_tmp[33];
        cube[18] = cube_tmp[34];
        cube[19] = cube_tmp[35];
        cube[20] = cube_tmp[36];
        cube[21] = cube_tmp[37];
        cube[22] = cube_tmp[38];
        cube[23] = cube_tmp[39];
        cube[24] = cube_tmp[40];
        cube[33] = cube_tmp[49];
        cube[34] = cube_tmp[50];
        cube[35] = cube_tmp[51];
        cube[36] = cube_tmp[52];
        cube[37] = cube_tmp[53];
        cube[38] = cube_tmp[54];
        cube[39] = cube_tmp[55];
        cube[40] = cube_tmp[56];
        cube[49] = cube_tmp[65];
        cube[50] = cube_tmp[66];
        cube[51] = cube_tmp[67];
        cube[52] = cube_tmp[68];
        cube[53] = cube_tmp[69];
        cube[54] = cube_tmp[70];
        cube[55] = cube_tmp[71];
        cube[56] = cube_tmp[72];
        cube[65] = cube_tmp[17];
        cube[66] = cube_tmp[18];
        cube[67] = cube_tmp[19];
        cube[68] = cube_tmp[20];
        cube[69] = cube_tmp[21];
        cube[70] = cube_tmp[22];
        cube[71] = cube_tmp[23];
        cube[72] = cube_tmp[24];
        break;
    }

    case Uw_PRIME: {
        cube[1] = cube_tmp[4];
        cube[2] = cube_tmp[8];
        cube[3] = cube_tmp[12];
        cube[4] = cube_tmp[16];
        cube[5] = cube_tmp[3];
        cube[6] = cube_tmp[7];
        cube[7] = cube_tmp[11];
        cube[8] = cube_tmp[15];
        cube[9] = cube_tmp[2];
        cube[10] = cube_tmp[6];
        cube[11] = cube_tmp[10];
        cube[12] = cube_tmp[14];
        cube[13] = cube_tmp[1];
        cube[14] = cube_tmp[5];
        cube[15] = cube_tmp[9];
        cube[16] = cube_tmp[13];
        cube[17] = cube_tmp[65];
        cube[18] = cube_tmp[66];
        cube[19] = cube_tmp[67];
        cube[20] = cube_tmp[68];
        cube[21] = cube_tmp[69];
        cube[22] = cube_tmp[70];
        cube[23] = cube_tmp[71];
        cube[24] = cube_tmp[72];
        cube[33] = cube_tmp[17];
        cube[34] = cube_tmp[18];
        cube[35] = cube_tmp[19];
        cube[36] = cube_tmp[20];
        cube[37] = cube_tmp[21];
        cube[38] = cube_tmp[22];
        cube[39] = cube_tmp[23];
        cube[40] = cube_tmp[24];
        cube[49] = cube_tmp[33];
        cube[50] = cube_tmp[34];
        cube[51] = cube_tmp[35];
        cube[52] = cube_tmp[36];
        cube[53] = cube_tmp[37];
        cube[54] = cube_tmp[38];
        cube[55] = cube_tmp[39];
        cube[56] = cube_tmp[40];
        cube[65] = cube_tmp[49];
        cube[66] = cube_tmp[50];
        cube[67] = cube_tmp[51];
        cube[68] = cube_tmp[52];
        cube[69] = cube_tmp[53];
        cube[70] = cube_tmp[54];
        cube[71] = cube_tmp[55];
        cube[72] = cube_tmp[56];
        break;
    }

    case Uw2: {
        cube[1] = cube_tmp[16];
        cube[2] = cube_tmp[15];
        cube[3] = cube_tmp[14];
        cube[4] = cube_tmp[13];
        cube[5] = cube_tmp[12];
        cube[6] = cube_tmp[11];
        cube[7] = cube_tmp[10];
        cube[8] = cube_tmp[9];
        cube[9] = cube_tmp[8];
        cube[10] = cube_tmp[7];
        cube[11] = cube_tmp[6];
        cube[12] = cube_tmp[5];
        cube[13] = cube_tmp[4];
        cube[14] = cube_tmp[3];
        cube[15] = cube_tmp[2];
        cube[16] = cube_tmp[1];
        cube[17] = cube_tmp[49];
        cube[18] = cube_tmp[50];
        cube[19] = cube_tmp[51];
        cube[20] = cube_tmp[52];
        cube[21] = cube_tmp[53];
        cube[22] = cube_tmp[54];
        cube[23] = cube_tmp[55];
        cube[24] = cube_tmp[56];
        cube[33] = cube_tmp[65];
        cube[34] = cube_tmp[66];
        cube[35] = cube_tmp[67];
        cube[36] = cube_tmp[68];
        cube[37] = cube_tmp[69];
        cube[38] = cube_tmp[70];
        cube[39] = cube_tmp[71];
        cube[40] = cube_tmp[72];
        cube[49] = cube_tmp[17];
        cube[50] = cube_tmp[18];
        cube[51] = cube_tmp[19];
        cube[52] = cube_tmp[20];
        cube[53] = cube_tmp[21];
        cube[54] = cube_tmp[22];
        cube[55] = cube_tmp[23];
        cube[56] = cube_tmp[24];
        cube[65] = cube_tmp[33];
        cube[66] = cube_tmp[34];
        cube[67] = cube_tmp[35];
        cube[68] = cube_tmp[36];
        cube[69] = cube_tmp[37];
        cube[70] = cube_tmp[38];
        cube[71] = cube_tmp[39];
        cube[72] = cube_tmp[40];
        break;
    }

    case L: {
        cube[1] = cube_tmp[80];
        cube[5] = cube_tmp[76];
        cube[9] = cube_tmp[72];
        cube[13] = cube_tmp[68];
        cube[17] = cube_tmp[29];
        cube[18] = cube_tmp[25];
        cube[19] = cube_tmp[21];
        cube[20] = cube_tmp[17];
        cube[21] = cube_tmp[30];
        cube[22] = cube_tmp[26];
        cube[23] = cube_tmp[22];
        cube[24] = cube_tmp[18];
        cube[25] = cube_tmp[31];
        cube[26] = cube_tmp[27];
        cube[27] = cube_tmp[23];
        cube[28] = cube_tmp[19];
        cube[29] = cube_tmp[32];
        cube[30] = cube_tmp[28];
        cube[31] = cube_tmp[24];
        cube[32] = cube_tmp[20];
        cube[33] = cube_tmp[1];
        cube[37] = cube_tmp[5];
        cube[41] = cube_tmp[9];
        cube[45] = cube_tmp[13];
        cube[68] = cube_tmp[93];
        cube[72] = cube_tmp[89];
        cube[76] = cube_tmp[85];
        cube[80] = cube_tmp[81];
        cube[81] = cube_tmp[33];
        cube[85] = cube_tmp[37];
        cube[89] = cube_tmp[41];
        cube[93] = cube_tmp[45];
        break;
    }

    case L_PRIME: {
        cube[1] = cube_tmp[33];
        cube[5] = cube_tmp[37];
        cube[9] = cube_tmp[41];
        cube[13] = cube_tmp[45];
        cube[17] = cube_tmp[20];
        cube[18] = cube_tmp[24];
        cube[19] = cube_tmp[28];
        cube[20] = cube_tmp[32];
        cube[21] = cube_tmp[19];
        cube[22] = cube_tmp[23];
        cube[23] = cube_tmp[27];
        cube[24] = cube_tmp[31];
        cube[25] = cube_tmp[18];
        cube[26] = cube_tmp[22];
        cube[27] = cube_tmp[26];
        cube[28] = cube_tmp[30];
        cube[29] = cube_tmp[17];
        cube[30] = cube_tmp[21];
        cube[31] = cube_tmp[25];
        cube[32] = cube_tmp[29];
        cube[33] = cube_tmp[81];
        cube[37] = cube_tmp[85];
        cube[41] = cube_tmp[89];
        cube[45] = cube_tmp[93];
        cube[68] = cube_tmp[13];
        cube[72] = cube_tmp[9];
        cube[76] = cube_tmp[5];
        cube[80] = cube_tmp[1];
        cube[81] = cube_tmp[80];
        cube[85] = cube_tmp[76];
        cube[89] = cube_tmp[72];
        cube[93] = cube_tmp[68];
        break;
    }

    case L2: {
        cube[1] = cube_tmp[81];
        cube[5] = cube_tmp[85];
        cube[9] = cube_tmp[89];
        cube[13] = cube_tmp[93];
        cube[17] = cube_tmp[32];
        cube[18] = cube_tmp[31];
        cube[19] = cube_tmp[30];
        cube[20] = cube_tmp[29];
        cube[21] = cube_tmp[28];
        cube[22] = cube_tmp[27];
        cube[23] = cube_tmp[26];
        cube[24] = cube_tmp[25];
        cube[25] = cube_tmp[24];
        cube[26] = cube_tmp[23];
        cube[27] = cube_tmp[22];
        cube[28] = cube_tmp[21];
        cube[29] = cube_tmp[20];
        cube[30] = cube_tmp[19];
        cube[31] = cube_tmp[18];
        cube[32] = cube_tmp[17];
        cube[33] = cube_tmp[80];
        cube[37] = cube_tmp[76];
        cube[41] = cube_tmp[72];
        cube[45] = cube_tmp[68];
        cube[68] = cube_tmp[45];
        cube[72] = cube_tmp[41];
        cube[76] = cube_tmp[37];
        cube[80] = cube_tmp[33];
        cube[81] = cube_tmp[1];
        cube[85] = cube_tmp[5];
        cube[89] = cube_tmp[9];
        cube[93] = cube_tmp[13];
        break;
    }

    case Lw: {
        cube[1] = cube_tmp[80];
        cube[2] = cube_tmp[79];
        cube[5] = cube_tmp[76];
        cube[6] = cube_tmp[75];
        cube[9] = cube_tmp[72];
        cube[10] = cube_tmp[71];
        cube[13] = cube_tmp[68];
        cube[14] = cube_tmp[67];
        cube[17] = cube_tmp[29];
        cube[18] = cube_tmp[25];
        cube[19] = cube_tmp[21];
        cube[20] = cube_tmp[17];
        cube[21] = cube_tmp[30];
        cube[22] = cube_tmp[26];
        cube[23] = cube_tmp[22];
        cube[24] = cube_tmp[18];
        cube[25] = cube_tmp[31];
        cube[26] = cube_tmp[27];
        cube[27] = cube_tmp[23];
        cube[28] = cube_tmp[19];
        cube[29] = cube_tmp[32];
        cube[30] = cube_tmp[28];
        cube[31] = cube_tmp[24];
        cube[32] = cube_tmp[20];
        cube[33] = cube_tmp[1];
        cube[34] = cube_tmp[2];
        cube[37] = cube_tmp[5];
        cube[38] = cube_tmp[6];
        cube[41] = cube_tmp[9];
        cube[42] = cube_tmp[10];
        cube[45] = cube_tmp[13];
        cube[46] = cube_tmp[14];
        cube[67] = cube_tmp[94];
        cube[68] = cube_tmp[93];
        cube[71] = cube_tmp[90];
        cube[72] = cube_tmp[89];
        cube[75] = cube_tmp[86];
        cube[76] = cube_tmp[85];
        cube[79] = cube_tmp[82];
        cube[80] = cube_tmp[81];
        cube[81] = cube_tmp[33];
        cube[82] = cube_tmp[34];
        cube[85] = cube_tmp[37];
        cube[86] = cube_tmp[38];
        cube[89] = cube_tmp[41];
        cube[90] = cube_tmp[42];
        cube[93] = cube_tmp[45];
        cube[94] = cube_tmp[46];
        break;
    }

    case Lw_PRIME: {
        cube[1] = cube_tmp[33];
        cube[2] = cube_tmp[34];
        cube[5] = cube_tmp[37];
        cube[6] = cube_tmp[38];
        cube[9] = cube_tmp[41];
        cube[10] = cube_tmp[42];
        cube[13] = cube_tmp[45];
        cube[14] = cube_tmp[46];
        cube[17] = cube_tmp[20];
        cube[18] = cube_tmp[24];
        cube[19] = cube_tmp[28];
        cube[20] = cube_tmp[32];
        cube[21] = cube_tmp[19];
        cube[22] = cube_tmp[23];
        cube[23] = cube_tmp[27];
        cube[24] = cube_tmp[31];
        cube[25] = cube_tmp[18];
        cube[26] = cube_tmp[22];
        cube[27] = cube_tmp[26];
        cube[28] = cube_tmp[30];
        cube[29] = cube_tmp[17];
        cube[30] = cube_tmp[21];
        cube[31] = cube_tmp[25];
        cube[32] = cube_tmp[29];
        cube[33] = cube_tmp[81];
        cube[34] = cube_tmp[82];
        cube[37] = cube_tmp[85];
        cube[38] = cube_tmp[86];
        cube[41] = cube_tmp[89];
        cube[42] = cube_tmp[90];
        cube[45] = cube_tmp[93];
        cube[46] = cube_tmp[94];
        cube[67] = cube_tmp[14];
        cube[68] = cube_tmp[13];
        cube[71] = cube_tmp[10];
        cube[72] = cube_tmp[9];
        cube[75] = cube_tmp[6];
        cube[76] = cube_tmp[5];
        cube[79] = cube_tmp[2];
        cube[80] = cube_tmp[1];
        cube[81] = cube_tmp[80];
        cube[82] = cube_tmp[79];
        cube[85] = cube_tmp[76];
        cube[86] = cube_tmp[75];
        cube[89] = cube_tmp[72];
        cube[90] = cube_tmp[71];
        cube[93] = cube_tmp[68];
        cube[94] = cube_tmp[67];
        break;
    }

    case Lw2: {
        cube[1] = cube_tmp[81];
        cube[2] = cube_tmp[82];
        cube[5] = cube_tmp[85];
        cube[6] = cube_tmp[86];
        cube[9] = cube_tmp[89];
        cube[10] = cube_tmp[90];
        cube[13] = cube_tmp[93];
        cube[14] = cube_tmp[94];
        cube[17] = cube_tmp[32];
        cube[18] = cube_tmp[31];
        cube[19] = cube_tmp[30];
        cube[20] = cube_tmp[29];
        cube[21] = cube_tmp[28];
        cube[22] = cube_tmp[27];
        cube[23] = cube_tmp[26];
        cube[24] = cube_tmp[25];
        cube[25] = cube_tmp[24];
        cube[26] = cube_tmp[23];
        cube[27] = cube_tmp[22];
        cube[28] = cube_tmp[21];
        cube[29] = cube_tmp[20];
        cube[30] = cube_tmp[19];
        cube[31] = cube_tmp[18];
        cube[32] = cube_tmp[17];
        cube[33] = cube_tmp[80];
        cube[34] = cube_tmp[79];
        cube[37] = cube_tmp[76];
        cube[38] = cube_tmp[75];
        cube[41] = cube_tmp[72];
        cube[42] = cube_tmp[71];
        cube[45] = cube_tmp[68];
        cube[46] = cube_tmp[67];
        cube[67] = cube_tmp[46];
        cube[68] = cube_tmp[45];
        cube[71] = cube_tmp[42];
        cube[72] = cube_tmp[41];
        cube[75] = cube_tmp[38];
        cube[76] = cube_tmp[37];
        cube[79] = cube_tmp[34];
        cube[80] = cube_tmp[33];
        cube[81] = cube_tmp[1];
        cube[82] = cube_tmp[2];
        cube[85] = cube_tmp[5];
        cube[86] = cube_tmp[6];
        cube[89] = cube_tmp[9];
        cube[90] = cube_tmp[10];
        cube[93] = cube_tmp[13];
        cube[94] = cube_tmp[14];
        break;
    }

    case F: {
        cube[13] = cube_tmp[32];
        cube[14] = cube_tmp[28];
        cube[15] = cube_tmp[24];
        cube[16] = cube_tmp[20];
        cube[20] = cube_tmp[81];
        cube[24] = cube_tmp[82];
        cube[28] = cube_tmp[83];
        cube[32] = cube_tmp[84];
        cube[33] = cube_tmp[45];
        cube[34] = cube_tmp[41];
        cube[35] = cube_tmp[37];
        cube[36] = cube_tmp[33];
        cube[37] = cube_tmp[46];
        cube[38] = cube_tmp[42];
        cube[39] = cube_tmp[38];
        cube[40] = cube_tmp[34];
        cube[41] = cube_tmp[47];
        cube[42] = cube_tmp[43];
        cube[43] = cube_tmp[39];
        cube[44] = cube_tmp[35];
        cube[45] = cube_tmp[48];
        cube[46] = cube_tmp[44];
        cube[47] = cube_tmp[40];
        cube[48] = cube_tmp[36];
        cube[49] = cube_tmp[13];
        cube[53] = cube_tmp[14];
        cube[57] = cube_tmp[15];
        cube[61] = cube_tmp[16];
        cube[81] = cube_tmp[61];
        cube[82] = cube_tmp[57];
        cube[83] = cube_tmp[53];
        cube[84] = cube_tmp[49];
        break;
    }

    case F_PRIME: {
        cube[13] = cube_tmp[49];
        cube[14] = cube_tmp[53];
        cube[15] = cube_tmp[57];
        cube[16] = cube_tmp[61];
        cube[20] = cube_tmp[16];
        cube[24] = cube_tmp[15];
        cube[28] = cube_tmp[14];
        cube[32] = cube_tmp[13];
        cube[33] = cube_tmp[36];
        cube[34] = cube_tmp[40];
        cube[35] = cube_tmp[44];
        cube[36] = cube_tmp[48];
        cube[37] = cube_tmp[35];
        cube[38] = cube_tmp[39];
        cube[39] = cube_tmp[43];
        cube[40] = cube_tmp[47];
        cube[41] = cube_tmp[34];
        cube[42] = cube_tmp[38];
        cube[43] = cube_tmp[42];
        cube[44] = cube_tmp[46];
        cube[45] = cube_tmp[33];
        cube[46] = cube_tmp[37];
        cube[47] = cube_tmp[41];
        cube[48] = cube_tmp[45];
        cube[49] = cube_tmp[84];
        cube[53] = cube_tmp[83];
        cube[57] = cube_tmp[82];
        cube[61] = cube_tmp[81];
        cube[81] = cube_tmp[20];
        cube[82] = cube_tmp[24];
        cube[83] = cube_tmp[28];
        cube[84] = cube_tmp[32];
        break;
    }

    case F2: {
        cube[13] = cube_tmp[84];
        cube[14] = cube_tmp[83];
        cube[15] = cube_tmp[82];
        cube[16] = cube_tmp[81];
        cube[20] = cube_tmp[61];
        cube[24] = cube_tmp[57];
        cube[28] = cube_tmp[53];
        cube[32] = cube_tmp[49];
        cube[33] = cube_tmp[48];
        cube[34] = cube_tmp[47];
        cube[35] = cube_tmp[46];
        cube[36] = cube_tmp[45];
        cube[37] = cube_tmp[44];
        cube[38] = cube_tmp[43];
        cube[39] = cube_tmp[42];
        cube[40] = cube_tmp[41];
        cube[41] = cube_tmp[40];
        cube[42] = cube_tmp[39];
        cube[43] = cube_tmp[38];
        cube[44] = cube_tmp[37];
        cube[45] = cube_tmp[36];
        cube[46] = cube_tmp[35];
        cube[47] = cube_tmp[34];
        cube[48] = cube_tmp[33];
        cube[49] = cube_tmp[32];
        cube[53] = cube_tmp[28];
        cube[57] = cube_tmp[24];
        cube[61] = cube_tmp[20];
        cube[81] = cube_tmp[16];
        cube[82] = cube_tmp[15];
        cube[83] = cube_tmp[14];
        cube[84] = cube_tmp[13];
        break;
    }

    case Fw: {
        cube[9] = cube_tmp[31];
        cube[10] = cube_tmp[27];
        cube[11] = cube_tmp[23];
        cube[12] = cube_tmp[19];
        cube[13] = cube_tmp[32];
        cube[14] = cube_tmp[28];
        cube[15] = cube_tmp[24];
        cube[16] = cube_tmp[20];
        cube[19] = cube_tmp[85];
        cube[20] = cube_tmp[81];
        cube[23] = cube_tmp[86];
        cube[24] = cube_tmp[82];
        cube[27] = cube_tmp[87];
        cube[28] = cube_tmp[83];
        cube[31] = cube_tmp[88];
        cube[32] = cube_tmp[84];
        cube[33] = cube_tmp[45];
        cube[34] = cube_tmp[41];
        cube[35] = cube_tmp[37];
        cube[36] = cube_tmp[33];
        cube[37] = cube_tmp[46];
        cube[38] = cube_tmp[42];
        cube[39] = cube_tmp[38];
        cube[40] = cube_tmp[34];
        cube[41] = cube_tmp[47];
        cube[42] = cube_tmp[43];
        cube[43] = cube_tmp[39];
        cube[44] = cube_tmp[35];
        cube[45] = cube_tmp[48];
        cube[46] = cube_tmp[44];
        cube[47] = cube_tmp[40];
        cube[48] = cube_tmp[36];
        cube[49] = cube_tmp[13];
        cube[50] = cube_tmp[9];
        cube[53] = cube_tmp[14];
        cube[54] = cube_tmp[10];
        cube[57] = cube_tmp[15];
        cube[58] = cube_tmp[11];
        cube[61] = cube_tmp[16];
        cube[62] = cube_tmp[12];
        cube[81] = cube_tmp[61];
        cube[82] = cube_tmp[57];
        cube[83] = cube_tmp[53];
        cube[84] = cube_tmp[49];
        cube[85] = cube_tmp[62];
        cube[86] = cube_tmp[58];
        cube[87] = cube_tmp[54];
        cube[88] = cube_tmp[50];
        break;
    }

    case Fw_PRIME: {
        cube[9] = cube_tmp[50];
        cube[10] = cube_tmp[54];
        cube[11] = cube_tmp[58];
        cube[12] = cube_tmp[62];
        cube[13] = cube_tmp[49];
        cube[14] = cube_tmp[53];
        cube[15] = cube_tmp[57];
        cube[16] = cube_tmp[61];
        cube[19] = cube_tmp[12];
        cube[20] = cube_tmp[16];
        cube[23] = cube_tmp[11];
        cube[24] = cube_tmp[15];
        cube[27] = cube_tmp[10];
        cube[28] = cube_tmp[14];
        cube[31] = cube_tmp[9];
        cube[32] = cube_tmp[13];
        cube[33] = cube_tmp[36];
        cube[34] = cube_tmp[40];
        cube[35] = cube_tmp[44];
        cube[36] = cube_tmp[48];
        cube[37] = cube_tmp[35];
        cube[38] = cube_tmp[39];
        cube[39] = cube_tmp[43];
        cube[40] = cube_tmp[47];
        cube[41] = cube_tmp[34];
        cube[42] = cube_tmp[38];
        cube[43] = cube_tmp[42];
        cube[44] = cube_tmp[46];
        cube[45] = cube_tmp[33];
        cube[46] = cube_tmp[37];
        cube[47] = cube_tmp[41];
        cube[48] = cube_tmp[45];
        cube[49] = cube_tmp[84];
        cube[50] = cube_tmp[88];
        cube[53] = cube_tmp[83];
        cube[54] = cube_tmp[87];
        cube[57] = cube_tmp[82];
        cube[58] = cube_tmp[86];
        cube[61] = cube_tmp[81];
        cube[62] = cube_tmp[85];
        cube[81] = cube_tmp[20];
        cube[82] = cube_tmp[24];
        cube[83] = cube_tmp[28];
        cube[84] = cube_tmp[32];
        cube[85] = cube_tmp[19];
        cube[86] = cube_tmp[23];
        cube[87] = cube_tmp[27];
        cube[88] = cube_tmp[31];
        break;
    }

    case Fw2: {
        cube[9] = cube_tmp[88];
        cube[10] = cube_tmp[87];
        cube[11] = cube_tmp[86];
        cube[12] = cube_tmp[85];
        cube[13] = cube_tmp[84];
        cube[14] = cube_tmp[83];
        cube[15] = cube_tmp[82];
        cube[16] = cube_tmp[81];
        cube[19] = cube_tmp[62];
        cube[20] = cube_tmp[61];
        cube[23] = cube_tmp[58];
        cube[24] = cube_tmp[57];
        cube[27] = cube_tmp[54];
        cube[28] = cube_tmp[53];
        cube[31] = cube_tmp[50];
        cube[32] = cube_tmp[49];
        cube[33] = cube_tmp[48];
        cube[34] = cube_tmp[47];
        cube[35] = cube_tmp[46];
        cube[36] = cube_tmp[45];
        cube[37] = cube_tmp[44];
        cube[38] = cube_tmp[43];
        cube[39] = cube_tmp[42];
        cube[40] = cube_tmp[41];
        cube[41] = cube_tmp[40];
        cube[42] = cube_tmp[39];
        cube[43] = cube_tmp[38];
        cube[44] = cube_tmp[37];
        cube[45] = cube_tmp[36];
        cube[46] = cube_tmp[35];
        cube[47] = cube_tmp[34];
        cube[48] = cube_tmp[33];
        cube[49] = cube_tmp[32];
        cube[50] = cube_tmp[31];
        cube[53] = cube_tmp[28];
        cube[54] = cube_tmp[27];
        cube[57] = cube_tmp[24];
        cube[58] = cube_tmp[23];
        cube[61] = cube_tmp[20];
        cube[62] = cube_tmp[19];
        cube[81] = cube_tmp[16];
        cube[82] = cube_tmp[15];
        cube[83] = cube_tmp[14];
        cube[84] = cube_tmp[13];
        cube[85] = cube_tmp[12];
        cube[86] = cube_tmp[11];
        cube[87] = cube_tmp[10];
        cube[88] = cube_tmp[9];
        break;
    }

    case R: {
        cube[4] = cube_tmp[36];
        cube[8] = cube_tmp[40];
        cube[12] = cube_tmp[44];
        cube[16] = cube_tmp[48];
        cube[36] = cube_tmp[84];
        cube[40] = cube_tmp[88];
        cube[44] = cube_tmp[92];
        cube[48] = cube_tmp[96];
        cube[49] = cube_tmp[61];
        cube[50] = cube_tmp[57];
        cube[51] = cube_tmp[53];
        cube[52] = cube_tmp[49];
        cube[53] = cube_tmp[62];
        cube[54] = cube_tmp[58];
        cube[55] = cube_tmp[54];
        cube[56] = cube_tmp[50];
        cube[57] = cube_tmp[63];
        cube[58] = cube_tmp[59];
        cube[59] = cube_tmp[55];
        cube[60] = cube_tmp[51];
        cube[61] = cube_tmp[64];
        cube[62] = cube_tmp[60];
        cube[63] = cube_tmp[56];
        cube[64] = cube_tmp[52];
        cube[65] = cube_tmp[16];
        cube[69] = cube_tmp[12];
        cube[73] = cube_tmp[8];
        cube[77] = cube_tmp[4];
        cube[84] = cube_tmp[77];
        cube[88] = cube_tmp[73];
        cube[92] = cube_tmp[69];
        cube[96] = cube_tmp[65];
        break;
    }

    case R_PRIME: {
        cube[4] = cube_tmp[77];
        cube[8] = cube_tmp[73];
        cube[12] = cube_tmp[69];
        cube[16] = cube_tmp[65];
        cube[36] = cube_tmp[4];
        cube[40] = cube_tmp[8];
        cube[44] = cube_tmp[12];
        cube[48] = cube_tmp[16];
        cube[49] = cube_tmp[52];
        cube[50] = cube_tmp[56];
        cube[51] = cube_tmp[60];
        cube[52] = cube_tmp[64];
        cube[53] = cube_tmp[51];
        cube[54] = cube_tmp[55];
        cube[55] = cube_tmp[59];
        cube[56] = cube_tmp[63];
        cube[57] = cube_tmp[50];
        cube[58] = cube_tmp[54];
        cube[59] = cube_tmp[58];
        cube[60] = cube_tmp[62];
        cube[61] = cube_tmp[49];
        cube[62] = cube_tmp[53];
        cube[63] = cube_tmp[57];
        cube[64] = cube_tmp[61];
        cube[65] = cube_tmp[96];
        cube[69] = cube_tmp[92];
        cube[73] = cube_tmp[88];
        cube[77] = cube_tmp[84];
        cube[84] = cube_tmp[36];
        cube[88] = cube_tmp[40];
        cube[92] = cube_tmp[44];
        cube[96] = cube_tmp[48];
        break;
    }

    case R2: {
        cube[4] = cube_tmp[84];
        cube[8] = cube_tmp[88];
        cube[12] = cube_tmp[92];
        cube[16] = cube_tmp[96];
        cube[36] = cube_tmp[77];
        cube[40] = cube_tmp[73];
        cube[44] = cube_tmp[69];
        cube[48] = cube_tmp[65];
        cube[49] = cube_tmp[64];
        cube[50] = cube_tmp[63];
        cube[51] = cube_tmp[62];
        cube[52] = cube_tmp[61];
        cube[53] = cube_tmp[60];
        cube[54] = cube_tmp[59];
        cube[55] = cube_tmp[58];
        cube[56] = cube_tmp[57];
        cube[57] = cube_tmp[56];
        cube[58] = cube_tmp[55];
        cube[59] = cube_tmp[54];
        cube[60] = cube_tmp[53];
        cube[61] = cube_tmp[52];
        cube[62] = cube_tmp[51];
        cube[63] = cube_tmp[50];
        cube[64] = cube_tmp[49];
        cube[65] = cube_tmp[48];
        cube[69] = cube_tmp[44];
        cube[73] = cube_tmp[40];
        cube[77] = cube_tmp[36];
        cube[84] = cube_tmp[4];
        cube[88] = cube_tmp[8];
        cube[92] = cube_tmp[12];
        cube[96] = cube_tmp[16];
        break;
    }

    case Rw: {
        cube[3] = cube_tmp[35];
        cube[4] = cube_tmp[36];
        cube[7] = cube_tmp[39];
        cube[8] = cube_tmp[40];
        cube[11] = cube_tmp[43];
        cube[12] = cube_tmp[44];
        cube[15] = cube_tmp[47];
        cube[16] = cube_tmp[48];
        cube[35] = cube_tmp[83];
        cube[36] = cube_tmp[84];
        cube[39] = cube_tmp[87];
        cube[40] = cube_tmp[88];
        cube[43] = cube_tmp[91];
        cube[44] = cube_tmp[92];
        cube[47] = cube_tmp[95];
        cube[48] = cube_tmp[96];
        cube[49] = cube_tmp[61];
        cube[50] = cube_tmp[57];
        cube[51] = cube_tmp[53];
        cube[52] = cube_tmp[49];
        cube[53] = cube_tmp[62];
        cube[54] = cube_tmp[58];
        cube[55] = cube_tmp[54];
        cube[56] = cube_tmp[50];
        cube[57] = cube_tmp[63];
        cube[58] = cube_tmp[59];
        cube[59] = cube_tmp[55];
        cube[60] = cube_tmp[51];
        cube[61] = cube_tmp[64];
        cube[62] = cube_tmp[60];
        cube[63] = cube_tmp[56];
        cube[64] = cube_tmp[52];
        cube[65] = cube_tmp[16];
        cube[66] = cube_tmp[15];
        cube[69] = cube_tmp[12];
        cube[70] = cube_tmp[11];
        cube[73] = cube_tmp[8];
        cube[74] = cube_tmp[7];
        cube[77] = cube_tmp[4];
        cube[78] = cube_tmp[3];
        cube[83] = cube_tmp[78];
        cube[84] = cube_tmp[77];
        cube[87] = cube_tmp[74];
        cube[88] = cube_tmp[73];
        cube[91] = cube_tmp[70];
        cube[92] = cube_tmp[69];
        cube[95] = cube_tmp[66];
        cube[96] = cube_tmp[65];
        break;
    }

    case Rw_PRIME: {
        cube[3] = cube_tmp[78];
        cube[4] = cube_tmp[77];
        cube[7] = cube_tmp[74];
        cube[8] = cube_tmp[73];
        cube[11] = cube_tmp[70];
        cube[12] = cube_tmp[69];
        cube[15] = cube_tmp[66];
        cube[16] = cube_tmp[65];
        cube[35] = cube_tmp[3];
        cube[36] = cube_tmp[4];
        cube[39] = cube_tmp[7];
        cube[40] = cube_tmp[8];
        cube[43] = cube_tmp[11];
        cube[44] = cube_tmp[12];
        cube[47] = cube_tmp[15];
        cube[48] = cube_tmp[16];
        cube[49] = cube_tmp[52];
        cube[50] = cube_tmp[56];
        cube[51] = cube_tmp[60];
        cube[52] = cube_tmp[64];
        cube[53] = cube_tmp[51];
        cube[54] = cube_tmp[55];
        cube[55] = cube_tmp[59];
        cube[56] = cube_tmp[63];
        cube[57] = cube_tmp[50];
        cube[58] = cube_tmp[54];
        cube[59] = cube_tmp[58];
        cube[60] = cube_tmp[62];
        cube[61] = cube_tmp[49];
        cube[62] = cube_tmp[53];
        cube[63] = cube_tmp[57];
        cube[64] = cube_tmp[61];
        cube[65] = cube_tmp[96];
        cube[66] = cube_tmp[95];
        cube[69] = cube_tmp[92];
        cube[70] = cube_tmp[91];
        cube[73] = cube_tmp[88];
        cube[74] = cube_tmp[87];
        cube[77] = cube_tmp[84];
        cube[78] = cube_tmp[83];
        cube[83] = cube_tmp[35];
        cube[84] = cube_tmp[36];
        cube[87] = cube_tmp[39];
        cube[88] = cube_tmp[40];
        cube[91] = cube_tmp[43];
        cube[92] = cube_tmp[44];
        cube[95] = cube_tmp[47];
        cube[96] = cube_tmp[48];
        break;
    }

    case Rw2: {
        cube[3] = cube_tmp[83];
        cube[4] = cube_tmp[84];
        cube[7] = cube_tmp[87];
        cube[8] = cube_tmp[88];
        cube[11] = cube_tmp[91];
        cube[12] = cube_tmp[92];
        cube[15] = cube_tmp[95];
        cube[16] = cube_tmp[96];
        cube[35] = cube_tmp[78];
        cube[36] = cube_tmp[77];
        cube[39] = cube_tmp[74];
        cube[40] = cube_tmp[73];
        cube[43] = cube_tmp[70];
        cube[44] = cube_tmp[69];
        cube[47] = cube_tmp[66];
        cube[48] = cube_tmp[65];
        cube[49] = cube_tmp[64];
        cube[50] = cube_tmp[63];
        cube[51] = cube_tmp[62];
        cube[52] = cube_tmp[61];
        cube[53] = cube_tmp[60];
        cube[54] = cube_tmp[59];
        cube[55] = cube_tmp[58];
        cube[56] = cube_tmp[57];
        cube[57] = cube_tmp[56];
        cube[58] = cube_tmp[55];
        cube[59] = cube_tmp[54];
        cube[60] = cube_tmp[53];
        cube[61] = cube_tmp[52];
        cube[62] = cube_tmp[51];
        cube[63] = cube_tmp[50];
        cube[64] = cube_tmp[49];
        cube[65] = cube_tmp[48];
        cube[66] = cube_tmp[47];
        cube[69] = cube_tmp[44];
        cube[70] = cube_tmp[43];
        cube[73] = cube_tmp[40];
        cube[74] = cube_tmp[39];
        cube[77] = cube_tmp[36];
        cube[78] = cube_tmp[35];
        cube[83] = cube_tmp[3];
        cube[84] = cube_tmp[4];
        cube[87] = cube_tmp[7];
        cube[88] = cube_tmp[8];
        cube[91] = cube_tmp[11];
        cube[92] = cube_tmp[12];
        cube[95] = cube_tmp[15];
        cube[96] = cube_tmp[16];
        break;
    }

    case B: {
        cube[1] = cube_tmp[52];
        cube[2] = cube_tmp[56];
        cube[3] = cube_tmp[60];
        cube[4] = cube_tmp[64];
        cube[17] = cube_tmp[4];
        cube[21] = cube_tmp[3];
        cube[25] = cube_tmp[2];
        cube[29] = cube_tmp[1];
        cube[52] = cube_tmp[96];
        cube[56] = cube_tmp[95];
        cube[60] = cube_tmp[94];
        cube[64] = cube_tmp[93];
        cube[65] = cube_tmp[77];
        cube[66] = cube_tmp[73];
        cube[67] = cube_tmp[69];
        cube[68] = cube_tmp[65];
        cube[69] = cube_tmp[78];
        cube[70] = cube_tmp[74];
        cube[71] = cube_tmp[70];
        cube[72] = cube_tmp[66];
        cube[73] = cube_tmp[79];
        cube[74] = cube_tmp[75];
        cube[75] = cube_tmp[71];
        cube[76] = cube_tmp[67];
        cube[77] = cube_tmp[80];
        cube[78] = cube_tmp[76];
        cube[79] = cube_tmp[72];
        cube[80] = cube_tmp[68];
        cube[93] = cube_tmp[17];
        cube[94] = cube_tmp[21];
        cube[95] = cube_tmp[25];
        cube[96] = cube_tmp[29];
        break;
    }

    case B_PRIME: {
        cube[1] = cube_tmp[29];
        cube[2] = cube_tmp[25];
        cube[3] = cube_tmp[21];
        cube[4] = cube_tmp[17];
        cube[17] = cube_tmp[93];
        cube[21] = cube_tmp[94];
        cube[25] = cube_tmp[95];
        cube[29] = cube_tmp[96];
        cube[52] = cube_tmp[1];
        cube[56] = cube_tmp[2];
        cube[60] = cube_tmp[3];
        cube[64] = cube_tmp[4];
        cube[65] = cube_tmp[68];
        cube[66] = cube_tmp[72];
        cube[67] = cube_tmp[76];
        cube[68] = cube_tmp[80];
        cube[69] = cube_tmp[67];
        cube[70] = cube_tmp[71];
        cube[71] = cube_tmp[75];
        cube[72] = cube_tmp[79];
        cube[73] = cube_tmp[66];
        cube[74] = cube_tmp[70];
        cube[75] = cube_tmp[74];
        cube[76] = cube_tmp[78];
        cube[77] = cube_tmp[65];
        cube[78] = cube_tmp[69];
        cube[79] = cube_tmp[73];
        cube[80] = cube_tmp[77];
        cube[93] = cube_tmp[64];
        cube[94] = cube_tmp[60];
        cube[95] = cube_tmp[56];
        cube[96] = cube_tmp[52];
        break;
    }

    case B2: {
        cube[1] = cube_tmp[96];
        cube[2] = cube_tmp[95];
        cube[3] = cube_tmp[94];
        cube[4] = cube_tmp[93];
        cube[17] = cube_tmp[64];
        cube[21] = cube_tmp[60];
        cube[25] = cube_tmp[56];
        cube[29] = cube_tmp[52];
        cube[52] = cube_tmp[29];
        cube[56] = cube_tmp[25];
        cube[60] = cube_tmp[21];
        cube[64] = cube_tmp[17];
        cube[65] = cube_tmp[80];
        cube[66] = cube_tmp[79];
        cube[67] = cube_tmp[78];
        cube[68] = cube_tmp[77];
        cube[69] = cube_tmp[76];
        cube[70] = cube_tmp[75];
        cube[71] = cube_tmp[74];
        cube[72] = cube_tmp[73];
        cube[73] = cube_tmp[72];
        cube[74] = cube_tmp[71];
        cube[75] = cube_tmp[70];
        cube[76] = cube_tmp[69];
        cube[77] = cube_tmp[68];
        cube[78] = cube_tmp[67];
        cube[79] = cube_tmp[66];
        cube[80] = cube_tmp[65];
        cube[93] = cube_tmp[4];
        cube[94] = cube_tmp[3];
        cube[95] = cube_tmp[2];
        cube[96] = cube_tmp[1];
        break;
    }

    case Bw: {
        cube[1] = cube_tmp[52];
        cube[2] = cube_tmp[56];
        cube[3] = cube_tmp[60];
        cube[4] = cube_tmp[64];
        cube[5] = cube_tmp[51];
        cube[6] = cube_tmp[55];
        cube[7] = cube_tmp[59];
        cube[8] = cube_tmp[63];
        cube[17] = cube_tmp[4];
        cube[18] = cube_tmp[8];
        cube[21] = cube_tmp[3];
        cube[22] = cube_tmp[7];
        cube[25] = cube_tmp[2];
        cube[26] = cube_tmp[6];
        cube[29] = cube_tmp[1];
        cube[30] = cube_tmp[5];
        cube[51] = cube_tmp[92];
        cube[52] = cube_tmp[96];
        cube[55] = cube_tmp[91];
        cube[56] = cube_tmp[95];
        cube[59] = cube_tmp[90];
        cube[60] = cube_tmp[94];
        cube[63] = cube_tmp[89];
        cube[64] = cube_tmp[93];
        cube[65] = cube_tmp[77];
        cube[66] = cube_tmp[73];
        cube[67] = cube_tmp[69];
        cube[68] = cube_tmp[65];
        cube[69] = cube_tmp[78];
        cube[70] = cube_tmp[74];
        cube[71] = cube_tmp[70];
        cube[72] = cube_tmp[66];
        cube[73] = cube_tmp[79];
        cube[74] = cube_tmp[75];
        cube[75] = cube_tmp[71];
        cube[76] = cube_tmp[67];
        cube[77] = cube_tmp[80];
        cube[78] = cube_tmp[76];
        cube[79] = cube_tmp[72];
        cube[80] = cube_tmp[68];
        cube[89] = cube_tmp[18];
        cube[90] = cube_tmp[22];
        cube[91] = cube_tmp[26];
        cube[92] = cube_tmp[30];
        cube[93] = cube_tmp[17];
        cube[94] = cube_tmp[21];
        cube[95] = cube_tmp[25];
        cube[96] = cube_tmp[29];
        break;
    }

    case Bw_PRIME: {
        cube[1] = cube_tmp[29];
        cube[2] = cube_tmp[25];
        cube[3] = cube_tmp[21];
        cube[4] = cube_tmp[17];
        cube[5] = cube_tmp[30];
        cube[6] = cube_tmp[26];
        cube[7] = cube_tmp[22];
        cube[8] = cube_tmp[18];
        cube[17] = cube_tmp[93];
        cube[18] = cube_tmp[89];
        cube[21] = cube_tmp[94];
        cube[22] = cube_tmp[90];
        cube[25] = cube_tmp[95];
        cube[26] = cube_tmp[91];
        cube[29] = cube_tmp[96];
        cube[30] = cube_tmp[92];
        cube[51] = cube_tmp[5];
        cube[52] = cube_tmp[1];
        cube[55] = cube_tmp[6];
        cube[56] = cube_tmp[2];
        cube[59] = cube_tmp[7];
        cube[60] = cube_tmp[3];
        cube[63] = cube_tmp[8];
        cube[64] = cube_tmp[4];
        cube[65] = cube_tmp[68];
        cube[66] = cube_tmp[72];
        cube[67] = cube_tmp[76];
        cube[68] = cube_tmp[80];
        cube[69] = cube_tmp[67];
        cube[70] = cube_tmp[71];
        cube[71] = cube_tmp[75];
        cube[72] = cube_tmp[79];
        cube[73] = cube_tmp[66];
        cube[74] = cube_tmp[70];
        cube[75] = cube_tmp[74];
        cube[76] = cube_tmp[78];
        cube[77] = cube_tmp[65];
        cube[78] = cube_tmp[69];
        cube[79] = cube_tmp[73];
        cube[80] = cube_tmp[77];
        cube[89] = cube_tmp[63];
        cube[90] = cube_tmp[59];
        cube[91] = cube_tmp[55];
        cube[92] = cube_tmp[51];
        cube[93] = cube_tmp[64];
        cube[94] = cube_tmp[60];
        cube[95] = cube_tmp[56];
        cube[96] = cube_tmp[52];
        break;
    }

    case Bw2: {
        cube[1] = cube_tmp[96];
        cube[2] = cube_tmp[95];
        cube[3] = cube_tmp[94];
        cube[4] = cube_tmp[93];
        cube[5] = cube_tmp[92];
        cube[6] = cube_tmp[91];
        cube[7] = cube_tmp[90];
        cube[8] = cube_tmp[89];
        cube[17] = cube_tmp[64];
        cube[18] = cube_tmp[63];
        cube[21] = cube_tmp[60];
        cube[22] = cube_tmp[59];
        cube[25] = cube_tmp[56];
        cube[26] = cube_tmp[55];
        cube[29] = cube_tmp[52];
        cube[30] = cube_tmp[51];
        cube[51] = cube_tmp[30];
        cube[52] = cube_tmp[29];
        cube[55] = cube_tmp[26];
        cube[56] = cube_tmp[25];
        cube[59] = cube_tmp[22];
        cube[60] = cube_tmp[21];
        cube[63] = cube_tmp[18];
        cube[64] = cube_tmp[17];
        cube[65] = cube_tmp[80];
        cube[66] = cube_tmp[79];
        cube[67] = cube_tmp[78];
        cube[68] = cube_tmp[77];
        cube[69] = cube_tmp[76];
        cube[70] = cube_tmp[75];
        cube[71] = cube_tmp[74];
        cube[72] = cube_tmp[73];
        cube[73] = cube_tmp[72];
        cube[74] = cube_tmp[71];
        cube[75] = cube_tmp[70];
        cube[76] = cube_tmp[69];
        cube[77] = cube_tmp[68];
        cube[78] = cube_tmp[67];
        cube[79] = cube_tmp[66];
        cube[80] = cube_tmp[65];
        cube[89] = cube_tmp[8];
        cube[90] = cube_tmp[7];
        cube[91] = cube_tmp[6];
        cube[92] = cube_tmp[5];
        cube[93] = cube_tmp[4];
        cube[94] = cube_tmp[3];
        cube[95] = cube_tmp[2];
        cube[96] = cube_tmp[1];
        break;
    }

    case D: {
        cube[29] = cube_tmp[77];
        cube[30] = cube_tmp[78];
        cube[31] = cube_tmp[79];
        cube[32] = cube_tmp[80];
        cube[45] = cube_tmp[29];
        cube[46] = cube_tmp[30];
        cube[47] = cube_tmp[31];
        cube[48] = cube_tmp[32];
        cube[61] = cube_tmp[45];
        cube[62] = cube_tmp[46];
        cube[63] = cube_tmp[47];
        cube[64] = cube_tmp[48];
        cube[77] = cube_tmp[61];
        cube[78] = cube_tmp[62];
        cube[79] = cube_tmp[63];
        cube[80] = cube_tmp[64];
        cube[81] = cube_tmp[93];
        cube[82] = cube_tmp[89];
        cube[83] = cube_tmp[85];
        cube[84] = cube_tmp[81];
        cube[85] = cube_tmp[94];
        cube[86] = cube_tmp[90];
        cube[87] = cube_tmp[86];
        cube[88] = cube_tmp[82];
        cube[89] = cube_tmp[95];
        cube[90] = cube_tmp[91];
        cube[91] = cube_tmp[87];
        cube[92] = cube_tmp[83];
        cube[93] = cube_tmp[96];
        cube[94] = cube_tmp[92];
        cube[95] = cube_tmp[88];
        cube[96] = cube_tmp[84];
        break;
    }

    case D_PRIME: {
        cube[29] = cube_tmp[45];
        cube[30] = cube_tmp[46];
        cube[31] = cube_tmp[47];
        cube[32] = cube_tmp[48];
        cube[45] = cube_tmp[61];
        cube[46] = cube_tmp[62];
        cube[47] = cube_tmp[63];
        cube[48] = cube_tmp[64];
        cube[61] = cube_tmp[77];
        cube[62] = cube_tmp[78];
        cube[63] = cube_tmp[79];
        cube[64] = cube_tmp[80];
        cube[77] = cube_tmp[29];
        cube[78] = cube_tmp[30];
        cube[79] = cube_tmp[31];
        cube[80] = cube_tmp[32];
        cube[81] = cube_tmp[84];
        cube[82] = cube_tmp[88];
        cube[83] = cube_tmp[92];
        cube[84] = cube_tmp[96];
        cube[85] = cube_tmp[83];
        cube[86] = cube_tmp[87];
        cube[87] = cube_tmp[91];
        cube[88] = cube_tmp[95];
        cube[89] = cube_tmp[82];
        cube[90] = cube_tmp[86];
        cube[91] = cube_tmp[90];
        cube[92] = cube_tmp[94];
        cube[93] = cube_tmp[81];
        cube[94] = cube_tmp[85];
        cube[95] = cube_tmp[89];
        cube[96] = cube_tmp[93];
        break;
    }

    case D2: {
        cube[29] = cube_tmp[61];
        cube[30] = cube_tmp[62];
        cube[31] = cube_tmp[63];
        cube[32] = cube_tmp[64];
        cube[45] = cube_tmp[77];
        cube[46] = cube_tmp[78];
        cube[47] = cube_tmp[79];
        cube[48] = cube_tmp[80];
        cube[61] = cube_tmp[29];
        cube[62] = cube_tmp[30];
        cube[63] = cube_tmp[31];
        cube[64] = cube_tmp[32];
        cube[77] = cube_tmp[45];
        cube[78] = cube_tmp[46];
        cube[79] = cube_tmp[47];
        cube[80] = cube_tmp[48];
        cube[81] = cube_tmp[96];
        cube[82] = cube_tmp[95];
        cube[83] = cube_tmp[94];
        cube[84] = cube_tmp[93];
        cube[85] = cube_tmp[92];
        cube[86] = cube_tmp[91];
        cube[87] = cube_tmp[90];
        cube[88] = cube_tmp[89];
        cube[89] = cube_tmp[88];
        cube[90] = cube_tmp[87];
        cube[91] = cube_tmp[86];
        cube[92] = cube_tmp[85];
        cube[93] = cube_tmp[84];
        cube[94] = cube_tmp[83];
        cube[95] = cube_tmp[82];
        cube[96] = cube_tmp[81];
        break;
    }

    case Dw: {
        cube[25] = cube_tmp[73];
        cube[26] = cube_tmp[74];
        cube[27] = cube_tmp[75];
        cube[28] = cube_tmp[76];
        cube[29] = cube_tmp[77];
        cube[30] = cube_tmp[78];
        cube[31] = cube_tmp[79];
        cube[32] = cube_tmp[80];
        cube[41] = cube_tmp[25];
        cube[42] = cube_tmp[26];
        cube[43] = cube_tmp[27];
        cube[44] = cube_tmp[28];
        cube[45] = cube_tmp[29];
        cube[46] = cube_tmp[30];
        cube[47] = cube_tmp[31];
        cube[48] = cube_tmp[32];
        cube[57] = cube_tmp[41];
        cube[58] = cube_tmp[42];
        cube[59] = cube_tmp[43];
        cube[60] = cube_tmp[44];
        cube[61] = cube_tmp[45];
        cube[62] = cube_tmp[46];
        cube[63] = cube_tmp[47];
        cube[64] = cube_tmp[48];
        cube[73] = cube_tmp[57];
        cube[74] = cube_tmp[58];
        cube[75] = cube_tmp[59];
        cube[76] = cube_tmp[60];
        cube[77] = cube_tmp[61];
        cube[78] = cube_tmp[62];
        cube[79] = cube_tmp[63];
        cube[80] = cube_tmp[64];
        cube[81] = cube_tmp[93];
        cube[82] = cube_tmp[89];
        cube[83] = cube_tmp[85];
        cube[84] = cube_tmp[81];
        cube[85] = cube_tmp[94];
        cube[86] = cube_tmp[90];
        cube[87] = cube_tmp[86];
        cube[88] = cube_tmp[82];
        cube[89] = cube_tmp[95];
        cube[90] = cube_tmp[91];
        cube[91] = cube_tmp[87];
        cube[92] = cube_tmp[83];
        cube[93] = cube_tmp[96];
        cube[94] = cube_tmp[92];
        cube[95] = cube_tmp[88];
        cube[96] = cube_tmp[84];
        break;
    }

    case Dw_PRIME: {
        cube[25] = cube_tmp[41];
        cube[26] = cube_tmp[42];
        cube[27] = cube_tmp[43];
        cube[28] = cube_tmp[44];
        cube[29] = cube_tmp[45];
        cube[30] = cube_tmp[46];
        cube[31] = cube_tmp[47];
        cube[32] = cube_tmp[48];
        cube[41] = cube_tmp[57];
        cube[42] = cube_tmp[58];
        cube[43] = cube_tmp[59];
        cube[44] = cube_tmp[60];
        cube[45] = cube_tmp[61];
        cube[46] = cube_tmp[62];
        cube[47] = cube_tmp[63];
        cube[48] = cube_tmp[64];
        cube[57] = cube_tmp[73];
        cube[58] = cube_tmp[74];
        cube[59] = cube_tmp[75];
        cube[60] = cube_tmp[76];
        cube[61] = cube_tmp[77];
        cube[62] = cube_tmp[78];
        cube[63] = cube_tmp[79];
        cube[64] = cube_tmp[80];
        cube[73] = cube_tmp[25];
        cube[74] = cube_tmp[26];
        cube[75] = cube_tmp[27];
        cube[76] = cube_tmp[28];
        cube[77] = cube_tmp[29];
        cube[78] = cube_tmp[30];
        cube[79] = cube_tmp[31];
        cube[80] = cube_tmp[32];
        cube[81] = cube_tmp[84];
        cube[82] = cube_tmp[88];
        cube[83] = cube_tmp[92];
        cube[84] = cube_tmp[96];
        cube[85] = cube_tmp[83];
        cube[86] = cube_tmp[87];
        cube[87] = cube_tmp[91];
        cube[88] = cube_tmp[95];
        cube[89] = cube_tmp[82];
        cube[90] = cube_tmp[86];
        cube[91] = cube_tmp[90];
        cube[92] = cube_tmp[94];
        cube[93] = cube_tmp[81];
        cube[94] = cube_tmp[85];
        cube[95] = cube_tmp[89];
        cube[96] = cube_tmp[93];
        break;
    }

    case Dw2: {
        cube[25] = cube_tmp[57];
        cube[26] = cube_tmp[58];
        cube[27] = cube_tmp[59];
        cube[28] = cube_tmp[60];
        cube[29] = cube_tmp[61];
        cube[30] = cube_tmp[62];
        cube[31] = cube_tmp[63];
        cube[32] = cube_tmp[64];
        cube[41] = cube_tmp[73];
        cube[42] = cube_tmp[74];
        cube[43] = cube_tmp[75];
        cube[44] = cube_tmp[76];
        cube[45] = cube_tmp[77];
        cube[46] = cube_tmp[78];
        cube[47] = cube_tmp[79];
        cube[48] = cube_tmp[80];
        cube[57] = cube_tmp[25];
        cube[58] = cube_tmp[26];
        cube[59] = cube_tmp[27];
        cube[60] = cube_tmp[28];
        cube[61] = cube_tmp[29];
        cube[62] = cube_tmp[30];
        cube[63] = cube_tmp[31];
        cube[64] = cube_tmp[32];
        cube[73] = cube_tmp[41];
        cube[74] = cube_tmp[42];
        cube[75] = cube_tmp[43];
        cube[76] = cube_tmp[44];
        cube[77] = cube_tmp[45];
        cube[78] = cube_tmp[46];
        cube[79] = cube_tmp[47];
        cube[80] = cube_tmp[48];
        cube[81] = cube_tmp[96];
        cube[82] = cube_tmp[95];
        cube[83] = cube_tmp[94];
        cube[84] = cube_tmp[93];
        cube[85] = cube_tmp[92];
        cube[86] = cube_tmp[91];
        cube[87] = cube_tmp[90];
        cube[88] = cube_tmp[89];
        cube[89] = cube_tmp[88];
        cube[90] = cube_tmp[87];
        cube[91] = cube_tmp[86];
        cube[92] = cube_tmp[85];
        cube[93] = cube_tmp[84];
        cube[94] = cube_tmp[83];
        cube[95] = cube_tmp[82];
        cube[96] = cube_tmp[81];
        break;
    }


    default:
        printf("ERROR: invalid move %d\n", move);
        exit(1);
    }
}
            
void
rotate_444_centers(char *cube, char *cube_tmp, int array_size, move_type move)
{
    /* This was contructed using utils/rotate-printer.py */
    (void)cube_tmp;
    (void)array_size;

    switch (move) {
    case U: {
        char c6 = cube[6], c7 = cube[7], c10 = cube[10], c11 = cube[11];
        cube[6] = c10;
        cube[7] = c6;
        cube[10] = c11;
        cube[11] = c7;
        break;
    }

    case U_PRIME: {
        char c6 = cube[6], c7 = cube[7], c10 = cube[10], c11 = cube[11];
        cube[6] = c7;
        cube[7] = c11;
        cube[10] = c6;
        cube[11] = c10;
        break;
    }

    case U2: {
        char c6 = cube[6], c7 = cube[7], c10 = cube[10], c11 = cube[11];
        cube[6] = c11;
        cube[7] = c10;
        cube[10] = c7;
        cube[11] = c6;
        break;
    }

    case Uw: {
        char c6 = cube[6], c7 = cube[7], c10 = cube[10], c11 = cube[11],
             c22 = cube[22], c23 = cube[23], c38 = cube[38], c39 = cube[39],
             c54 = cube[54], c55 = cube[55], c70 = cube[70], c71 = cube[71];
        cube[6] = c10;
        cube[7] = c6;
        cube[10] = c11;
        cube[11] = c7;
        cube[22] = c38;
        cube[23] = c39;
        cube[38] = c54;
        cube[39] = c55;
        cube[54] = c70;
        cube[55] = c71;
        cube[70] = c22;
        cube[71] = c23;
        break;
    }

    case Uw_PRIME: {
        char c6 = cube[6], c7 = cube[7], c10 = cube[10], c11 = cube[11],
             c22 = cube[22], c23 = cube[23], c38 = cube[38], c39 = cube[39],
             c54 = cube[54], c55 = cube[55], c70 = cube[70], c71 = cube[71];
        cube[6] = c7;
        cube[7] = c11;
        cube[10] = c6;
        cube[11] = c10;
        cube[22] = c70;
        cube[23] = c71;
        cube[38] = c22;
        cube[39] = c23;
        cube[54] = c38;
        cube[55] = c39;
        cube[70] = c54;
        cube[71] = c55;
        break;
    }

    case Uw2: {
        char c6 = cube[6], c7 = cube[7], c10 = cube[10], c11 = cube[11],
             c22 = cube[22], c23 = cube[23], c38 = cube[38], c39 = cube[39],
             c54 = cube[54], c55 = cube[55], c70 = cube[70], c71 = cube[71];
        cube[6] = c11;
        cube[7] = c10;
        cube[10] = c7;
        cube[11] = c6;
        cube[22] = c54;
        cube[23] = c55;
        cube[38] = c70;
        cube[39] = c71;
        cube[54] = c22;
        cube[55] = c23;
        cube[70] = c38;
        cube[71] = c39;
        break;
    }

    case L: {
        char c22 = cube[22], c23 = cube[23], c26 = cube[26], c27 = cube[27];
        cube[22] = c26;
        cube[23] = c22;
        cube[26] = c27;
        cube[27] = c23;
        break;
    }

    case L_PRIME: {
        char c22 = cube[22], c23 = cube[23], c26 = cube[26], c27 = cube[27];
        cube[22] = c23;
        cube[23] = c27;
        cube[26] = c22;
        cube[27] = c26;
        break;
    }

    case L2: {
        char c22 = cube[22], c23 = cube[23], c26 = cube[26], c27 = cube[27];
        cube[22] = c27;
        cube[23] = c26;
        cube[26] = c23;
        cube[27] = c22;
        break;
    }

    case Lw: {
        char c6 = cube[6], c10 = cube[10], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c38 = cube[38], c42 = cube[42],
             c71 = cube[71], c75 = cube[75], c86 = cube[86], c90 = cube[90];
        cube[6] = c75;
        cube[10] = c71;
        cube[22] = c26;
        cube[23] = c22;
        cube[26] = c27;
        cube[27] = c23;
        cube[38] = c6;
        cube[42] = c10;
        cube[71] = c90;
        cube[75] = c86;
        cube[86] = c38;
        cube[90] = c42;
        break;
    }

    case Lw_PRIME: {
        char c6 = cube[6], c10 = cube[10], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c38 = cube[38], c42 = cube[42],
             c71 = cube[71], c75 = cube[75], c86 = cube[86], c90 = cube[90];
        cube[6] = c38;
        cube[10] = c42;
        cube[22] = c23;
        cube[23] = c27;
        cube[26] = c22;
        cube[27] = c26;
        cube[38] = c86;
        cube[42] = c90;
        cube[71] = c10;
        cube[75] = c6;
        cube[86] = c75;
        cube[90] = c71;
        break;
    }

    case Lw2: {
        char c6 = cube[6], c10 = cube[10], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c38 = cube[38], c42 = cube[42],
             c71 = cube[71], c75 = cube[75], c86 = cube[86], c90 = cube[90];
        cube[6] = c86;
        cube[10] = c90;
        cube[22] = c27;
        cube[23] = c26;
        cube[26] = c23;
        cube[27] = c22;
        cube[38] = c75;
        cube[42] = c71;
        cube[71] = c42;
        cube[75] = c38;
        cube[86] = c6;
        cube[90] = c10;
        break;
    }

    case F: {
        char c38 = cube[38], c39 = cube[39], c42 = cube[42], c43 = cube[43];
        cube[38] = c42;
        cube[39] = c38;
        cube[42] = c43;
        cube[43] = c39;
        break;
    }

    case F_PRIME: {
        char c38 = cube[38], c39 = cube[39], c42 = cube[42], c43 = cube[43];
        cube[38] = c39;
        cube[39] = c43;
        cube[42] = c38;
        cube[43] = c42;
        break;
    }

    case F2: {
        char c38 = cube[38], c39 = cube[39], c42 = cube[42], c43 = cube[43];
        cube[38] = c43;
        cube[39] = c42;
        cube[42] = c39;
        cube[43] = c38;
        break;
    }

    case Fw: {
        char c10 = cube[10], c11 = cube[11], c23 = cube[23], c27 = cube[27],
             c38 = cube[38], c39 = cube[39], c42 = cube[42], c43 = cube[43],
             c54 = cube[54], c58 = cube[58], c86 = cube[86], c87 = cube[87];
        cube[10] = c27;
        cube[11] = c23;
        cube[23] = c86;
        cube[27] = c87;
        cube[38] = c42;
        cube[39] = c38;
        cube[42] = c43;
        cube[43] = c39;
        cube[54] = c10;
        cube[58] = c11;
        cube[86] = c58;
        cube[87] = c54;
        break;
    }

    case Fw_PRIME: {
        char c10 = cube[10], c11 = cube[11], c23 = cube[23], c27 = cube[27],
             c38 = cube[38], c39 = cube[39], c42 = cube[42], c43 = cube[43],
             c54 = cube[54], c58 = cube[58], c86 = cube[86], c87 = cube[87];
        cube[10] = c54;
        cube[11] = c58;
        cube[23] = c11;
        cube[27] = c10;
        cube[38] = c39;
        cube[39] = c43;
        cube[42] = c38;
        cube[43] = c42;
        cube[54] = c87;
        cube[58] = c86;
        cube[86] = c23;
        cube[87] = c27;
        break;
    }

    case Fw2: {
        char c10 = cube[10], c11 = cube[11], c23 = cube[23], c27 = cube[27],
             c38 = cube[38], c39 = cube[39], c42 = cube[42], c43 = cube[43],
             c54 = cube[54], c58 = cube[58], c86 = cube[86], c87 = cube[87];
        cube[10] = c87;
        cube[11] = c86;
        cube[23] = c58;
        cube[27] = c54;
        cube[38] = c43;
        cube[39] = c42;
        cube[42] = c39;
        cube[43] = c38;
        cube[54] = c27;
        cube[58] = c23;
        cube[86] = c11;
        cube[87] = c10;
        break;
    }

    case R: {
        char c54 = cube[54], c55 = cube[55], c58 = cube[58], c59 = cube[59];
        cube[54] = c58;
        cube[55] = c54;
        cube[58] = c59;
        cube[59] = c55;
        break;
    }

    case R_PRIME: {
        char c54 = cube[54], c55 = cube[55], c58 = cube[58], c59 = cube[59];
        cube[54] = c55;
        cube[55] = c59;
        cube[58] = c54;
        cube[59] = c58;
        break;
    }

    case R2: {
        char c54 = cube[54], c55 = cube[55], c58 = cube[58], c59 = cube[59];
        cube[54] = c59;
        cube[55] = c58;
        cube[58] = c55;
        cube[59] = c54;
        break;
    }

    case Rw: {
        char c7 = cube[7], c11 = cube[11], c39 = cube[39], c43 = cube[43],
             c54 = cube[54], c55 = cube[55], c58 = cube[58], c59 = cube[59],
             c70 = cube[70], c74 = cube[74], c87 = cube[87], c91 = cube[91];
        cube[7] = c39;
        cube[11] = c43;
        cube[39] = c87;
        cube[43] = c91;
        cube[54] = c58;
        cube[55] = c54;
        cube[58] = c59;
        cube[59] = c55;
        cube[70] = c11;
        cube[74] = c7;
        cube[87] = c74;
        cube[91] = c70;
        break;
    }

    case Rw_PRIME: {
        char c7 = cube[7], c11 = cube[11], c39 = cube[39], c43 = cube[43],
             c54 = cube[54], c55 = cube[55], c58 = cube[58], c59 = cube[59],
             c70 = cube[70], c74 = cube[74], c87 = cube[87], c91 = cube[91];
        cube[7] = c74;
        cube[11] = c70;
        cube[39] = c7;
        cube[43] = c11;
        cube[54] = c55;
        cube[55] = c59;
        cube[58] = c54;
        cube[59] = c58;
        cube[70] = c91;
        cube[74] = c87;
        cube[87] = c39;
        cube[91] = c43;
        break;
    }

    case Rw2: {
        char c7 = cube[7], c11 = cube[11], c39 = cube[39], c43 = cube[43],
             c54 = cube[54], c55 = cube[55], c58 = cube[58], c59 = cube[59],
             c70 = cube[70], c74 = cube[74], c87 = cube[87], c91 = cube[91];
        cube[7] = c87;
        cube[11] = c91;
        cube[39] = c74;
        cube[43] = c70;
        cube[54] = c59;
        cube[55] = c58;
        cube[58] = c55;
        cube[59] = c54;
        cube[70] = c43;
        cube[74] = c39;
        cube[87] = c7;
        cube[91] = c11;
        break;
    }

    case B: {
        char c70 = cube[70], c71 = cube[71], c74 = cube[74], c75 = cube[75];
        cube[70] = c74;
        cube[71] = c70;
        cube[74] = c75;
        cube[75] = c71;
        break;
    }

    case B_PRIME: {
        char c70 = cube[70], c71 = cube[71], c74 = cube[74], c75 = cube[75];
        cube[70] = c71;
        cube[71] = c75;
        cube[74] = c70;
        cube[75] = c74;
        break;
    }

    case B2: {
        char c70 = cube[70], c71 = cube[71], c74 = cube[74], c75 = cube[75];
        cube[70] = c75;
        cube[71] = c74;
        cube[74] = c71;
        cube[75] = c70;
        break;
    }

    case Bw: {
        char c6 = cube[6], c7 = cube[7], c22 = cube[22], c26 = cube[26],
             c55 = cube[55], c59 = cube[59], c70 = cube[70], c71 = cube[71],
             c74 = cube[74], c75 = cube[75], c90 = cube[90], c91 = cube[91];
        cube[6] = c55;
        cube[7] = c59;
        cube[22] = c7;
        cube[26] = c6;
        cube[55] = c91;
        cube[59] = c90;
        cube[70] = c74;
        cube[71] = c70;
        cube[74] = c75;
        cube[75] = c71;
        cube[90] = c22;
        cube[91] = c26;
        break;
    }

    case Bw_PRIME: {
        char c6 = cube[6], c7 = cube[7], c22 = cube[22], c26 = cube[26],
             c55 = cube[55], c59 = cube[59], c70 = cube[70], c71 = cube[71],
             c74 = cube[74], c75 = cube[75], c90 = cube[90], c91 = cube[91];
        cube[6] = c26;
        cube[7] = c22;
        cube[22] = c90;
        cube[26] = c91;
        cube[55] = c6;
        cube[59] = c7;
        cube[70] = c71;
        cube[71] = c75;
        cube[74] = c70;
        cube[75] = c74;
        cube[90] = c59;
        cube[91] = c55;
        break;
    }

    case Bw2: {
        char c6 = cube[6], c7 = cube[7], c22 = cube[22], c26 = cube[26],
             c55 = cube[55], c59 = cube[59], c70 = cube[70], c71 = cube[71],
             c74 = cube[74], c75 = cube[75], c90 = cube[90], c91 = cube[91];
        cube[6] = c91;
        cube[7] = c90;
        cube[22] = c59;
        cube[26] = c55;
        cube[55] = c26;
        cube[59] = c22;
        cube[70] = c75;
        cube[71] = c74;
        cube[74] = c71;
        cube[75] = c70;
        cube[90] = c7;
        cube[91] = c6;
        break;
    }

    case D: {
        char c86 = cube[86], c87 = cube[87], c90 = cube[90], c91 = cube[91];
        cube[86] = c90;
        cube[87] = c86;
        cube[90] = c91;
        cube[91] = c87;
        break;
    }

    case D_PRIME: {
        char c86 = cube[86], c87 = cube[87], c90 = cube[90], c91 = cube[91];
        cube[86] = c87;
        cube[87] = c91;
        cube[90] = c86;
        cube[91] = c90;
        break;
    }

    case D2: {
        char c86 = cube[86], c87 = cube[87], c90 = cube[90], c91 = cube[91];
        cube[86] = c91;
        cube[87] = c90;
        cube[90] = c87;
        cube[91] = c86;
        break;
    }

    case Dw: {
        char c26 = cube[26], c27 = cube[27], c42 = cube[42], c43 = cube[43],
             c58 = cube[58], c59 = cube[59], c74 = cube[74], c75 = cube[75],
             c86 = cube[86], c87 = cube[87], c90 = cube[90], c91 = cube[91];
        cube[26] = c74;
        cube[27] = c75;
        cube[42] = c26;
        cube[43] = c27;
        cube[58] = c42;
        cube[59] = c43;
        cube[74] = c58;
        cube[75] = c59;
        cube[86] = c90;
        cube[87] = c86;
        cube[90] = c91;
        cube[91] = c87;
        break;
    }

    case Dw_PRIME: {
        char c26 = cube[26], c27 = cube[27], c42 = cube[42], c43 = cube[43],
             c58 = cube[58], c59 = cube[59], c74 = cube[74], c75 = cube[75],
             c86 = cube[86], c87 = cube[87], c90 = cube[90], c91 = cube[91];
        cube[26] = c42;
        cube[27] = c43;
        cube[42] = c58;
        cube[43] = c59;
        cube[58] = c74;
        cube[59] = c75;
        cube[74] = c26;
        cube[75] = c27;
        cube[86] = c87;
        cube[87] = c91;
        cube[90] = c86;
        cube[91] = c90;
        break;
    }

    case Dw2: {
        char c26 = cube[26], c27 = cube[27], c42 = cube[42], c43 = cube[43],
             c58 = cube[58], c59 = cube[59], c74 = cube[74], c75 = cube[75],
             c86 = cube[86], c87 = cube[87], c90 = cube[90], c91 = cube[91];
        cube[26] = c58;
        cube[27] = c59;
        cube[42] = c74;
        cube[43] = c75;
        cube[58] = c26;
        cube[59] = c27;
        cube[74] = c42;
        cube[75] = c43;
        cube[86] = c91;
        cube[87] = c90;
        cube[90] = c87;
        cube[91] = c86;
        break;
    }


    default:
        printf("ERROR: invalid move %d\n", move);
        exit(1);
    }
}
            
void
rotate_555(char *cube, char *cube_tmp, int array_size, move_type move)
{
    /* This was contructed using utils/rotate-printer.py */
    memcpy(cube_tmp, cube, sizeof(char) * array_size);

    switch (move) {
    case U: {
        cube[1] = cube_tmp[21];
        cube[2] = cube_tmp[16];
        cube[3] = cube_tmp[11];
        cube[4] = cube_tmp[6];
        cube[5] = cube_tmp[1];
        cube[6] = cube_tmp[22];
        cube[7] = cube_tmp[17];
        cube[8] = cube_tmp[12];
        cube[9] = cube_tmp[7];
        cube[10] = cube_tmp[2];
        cube[11] = cube_tmp[23];
        cube[12] = cube_tmp[18];
        cube[14] = cube_tmp[8];
        cube[15] = cube_tmp[3];
        cube[16] = cube_tmp[24];
        cube[17] = cube_tmp[19];
        cube[18] = cube_tmp[14];
        cube[19] = cube_tmp[9];
        cube[20] = cube_tmp[4];
        cube[21] = cube_tmp[25];
        cube[22] = cube_tmp[20];
        cube[23] = cube_tmp[15];
        cube[24] = cube_tmp[10];
        cube[25] = cube_tmp[5];
        cube[26] = cube_tmp[51];
        cube[27] = cube_tmp[52];
        cube[28] = cube_tmp[53];
        cube[29] = cube_tmp[54];
        cube[30] = cube_tmp[55];
        cube[51] = cube_tmp[76];
        cube[52] = cube_tmp[77];
        cube[53] = cube_tmp[78];
        cube[54] = cube_tmp[79];
        cube[55] = cube_tmp[80];
        cube[76] = cube_tmp[101];
        cube[77] = cube_tmp[102];
        cube[78] = cube_tmp[103];
        cube[79] = cube_tmp[104];
        cube[80] = cube_tmp[105];
        cube[101] = cube_tmp[26];
        cube[102] = cube_tmp[27];
        cube[103] = cube_tmp[28];
        cube[104] = cube_tmp[29];
        cube[105] = cube_tmp[30];
        break;
    }

    case U_PRIME: {
        cube[1] = cube_tmp[5];
        cube[2] = cube_tmp[10];
        cube[3] = cube_tmp[15];
        cube[4] = cube_tmp[20];
        cube[5] = cube_tmp[25];
        cube[6] = cube_tmp[4];
        cube[7] = cube_tmp[9];
        cube[8] = cube_tmp[14];
        cube[9] = cube_tmp[19];
        cube[10] = cube_tmp[24];
        cube[11] = cube_tmp[3];
        cube[12] = cube_tmp[8];
        cube[14] = cube_tmp[18];
        cube[15] = cube_tmp[23];
        cube[16] = cube_tmp[2];
        cube[17] = cube_tmp[7];
        cube[18] = cube_tmp[12];
        cube[19] = cube_tmp[17];
        cube[20] = cube_tmp[22];
        cube[21] = cube_tmp[1];
        cube[22] = cube_tmp[6];
        cube[23] = cube_tmp[11];
        cube[24] = cube_tmp[16];
        cube[25] = cube_tmp[21];
        cube[26] = cube_tmp[101];
        cube[27] = cube_tmp[102];
        cube[28] = cube_tmp[103];
        cube[29] = cube_tmp[104];
        cube[30] = cube_tmp[105];
        cube[51] = cube_tmp[26];
        cube[52] = cube_tmp[27];
        cube[53] = cube_tmp[28];
        cube[54] = cube_tmp[29];
        cube[55] = cube_tmp[30];
        cube[76] = cube_tmp[51];
        cube[77] = cube_tmp[52];
        cube[78] = cube_tmp[53];
        cube[79] = cube_tmp[54];
        cube[80] = cube_tmp[55];
        cube[101] = cube_tmp[76];
        cube[102] = cube_tmp[77];
        cube[103] = cube_tmp[78];
        cube[104] = cube_tmp[79];
        cube[105] = cube_tmp[80];
        break;
    }

    case U2: {
        cube[1] = cube_tmp[25];
        cube[2] = cube_tmp[24];
        cube[3] = cube_tmp[23];
        cube[4] = cube_tmp[22];
        cube[5] = cube_tmp[21];
        cube[6] = cube_tmp[20];
        cube[7] = cube_tmp[19];
        cube[8] = cube_tmp[18];
        cube[9] = cube_tmp[17];
        cube[10] = cube_tmp[16];
        cube[11] = cube_tmp[15];
        cube[12] = cube_tmp[14];
        cube[14] = cube_tmp[12];
        cube[15] = cube_tmp[11];
        cube[16] = cube_tmp[10];
        cube[17] = cube_tmp[9];
        cube[18] = cube_tmp[8];
        cube[19] = cube_tmp[7];
        cube[20] = cube_tmp[6];
        cube[21] = cube_tmp[5];
        cube[22] = cube_tmp[4];
        cube[23] = cube_tmp[3];
        cube[24] = cube_tmp[2];
        cube[25] = cube_tmp[1];
        cube[26] = cube_tmp[76];
        cube[27] = cube_tmp[77];
        cube[28] = cube_tmp[78];
        cube[29] = cube_tmp[79];
        cube[30] = cube_tmp[80];
        cube[51] = cube_tmp[101];
        cube[52] = cube_tmp[102];
        cube[53] = cube_tmp[103];
        cube[54] = cube_tmp[104];
        cube[55] = cube_tmp[105];
        cube[76] = cube_tmp[26];
        cube[77] = cube_tmp[27];
        cube[78] = cube_tmp[28];
        cube[79] = cube_tmp[29];
        cube[80] = cube_tmp[30];
        cube[101] = cube_tmp[51];
        cube[102] = cube_tmp[52];
        cube[103] = cube_tmp[53];
        cube[104] = cube_tmp[54];
        cube[105] = cube_tmp[55];
        break;
    }

    case Uw: {
        cube[1] = cube_tmp[21];
        cube[2] = cube_tmp[16];
        cube[3] = cube_tmp[11];
        cube[4] = cube_tmp[6];
        cube[5] = cube_tmp[1];
        cube[6] = cube_tmp[22];
        cube[7] = cube_tmp[17];
        cube[8] = cube_tmp[12];
        cube[9] = cube_tmp[7];
        cube[10] = cube_tmp[2];
        cube[11] = cube_tmp[23];
        cube[12] = cube_tmp[18];
        cube[14] = cube_tmp[8];
        cube[15] = cube_tmp[3];
        cube[16] = cube_tmp[24];
        cube[17] = cube_tmp[19];
        cube[18] = cube_tmp[14];
        cube[19] = cube_tmp[9];
        cube[20] = cube_tmp[4];
        cube[21] = cube_tmp[25];
        cube[22] = cube_tmp[20];
        cube[23] = cube_tmp[15];
        cube[24] = cube_tmp[10];
        cube[25] = cube_tmp[5];
        cube[26] = cube_tmp[51];
        cube[27] = cube_tmp[52];
        cube[28] = cube_tmp[53];
        cube[29] = cube_tmp[54];
        cube[30] = cube_tmp[55];
        cube[31] = cube_tmp[56];
        cube[32] = cube_tmp[57];
        cube[33] = cube_tmp[58];
        cube[34] = cube_tmp[59];
        cube[35] = cube_tmp[60];
        cube[51] = cube_tmp[76];
        cube[52] = cube_tmp[77];
        cube[53] = cube_tmp[78];
        cube[54] = cube_tmp[79];
        cube[55] = cube_tmp[80];
        cube[56] = cube_tmp[81];
        cube[57] = cube_tmp[82];
        cube[58] = cube_tmp[83];
        cube[59] = cube_tmp[84];
        cube[60] = cube_tmp[85];
        cube[76] = cube_tmp[101];
        cube[77] = cube_tmp[102];
        cube[78] = cube_tmp[103];
        cube[79] = cube_tmp[104];
        cube[80] = cube_tmp[105];
        cube[81] = cube_tmp[106];
        cube[82] = cube_tmp[107];
        cube[83] = cube_tmp[108];
        cube[84] = cube_tmp[109];
        cube[85] = cube_tmp[110];
        cube[101] = cube_tmp[26];
        cube[102] = cube_tmp[27];
        cube[103] = cube_tmp[28];
        cube[104] = cube_tmp[29];
        cube[105] = cube_tmp[30];
        cube[106] = cube_tmp[31];
        cube[107] = cube_tmp[32];
        cube[108] = cube_tmp[33];
        cube[109] = cube_tmp[34];
        cube[110] = cube_tmp[35];
        break;
    }

    case Uw_PRIME: {
        cube[1] = cube_tmp[5];
        cube[2] = cube_tmp[10];
        cube[3] = cube_tmp[15];
        cube[4] = cube_tmp[20];
        cube[5] = cube_tmp[25];
        cube[6] = cube_tmp[4];
        cube[7] = cube_tmp[9];
        cube[8] = cube_tmp[14];
        cube[9] = cube_tmp[19];
        cube[10] = cube_tmp[24];
        cube[11] = cube_tmp[3];
        cube[12] = cube_tmp[8];
        cube[14] = cube_tmp[18];
        cube[15] = cube_tmp[23];
        cube[16] = cube_tmp[2];
        cube[17] = cube_tmp[7];
        cube[18] = cube_tmp[12];
        cube[19] = cube_tmp[17];
        cube[20] = cube_tmp[22];
        cube[21] = cube_tmp[1];
        cube[22] = cube_tmp[6];
        cube[23] = cube_tmp[11];
        cube[24] = cube_tmp[16];
        cube[25] = cube_tmp[21];
        cube[26] = cube_tmp[101];
        cube[27] = cube_tmp[102];
        cube[28] = cube_tmp[103];
        cube[29] = cube_tmp[104];
        cube[30] = cube_tmp[105];
        cube[31] = cube_tmp[106];
        cube[32] = cube_tmp[107];
        cube[33] = cube_tmp[108];
        cube[34] = cube_tmp[109];
        cube[35] = cube_tmp[110];
        cube[51] = cube_tmp[26];
        cube[52] = cube_tmp[27];
        cube[53] = cube_tmp[28];
        cube[54] = cube_tmp[29];
        cube[55] = cube_tmp[30];
        cube[56] = cube_tmp[31];
        cube[57] = cube_tmp[32];
        cube[58] = cube_tmp[33];
        cube[59] = cube_tmp[34];
        cube[60] = cube_tmp[35];
        cube[76] = cube_tmp[51];
        cube[77] = cube_tmp[52];
        cube[78] = cube_tmp[53];
        cube[79] = cube_tmp[54];
        cube[80] = cube_tmp[55];
        cube[81] = cube_tmp[56];
        cube[82] = cube_tmp[57];
        cube[83] = cube_tmp[58];
        cube[84] = cube_tmp[59];
        cube[85] = cube_tmp[60];
        cube[101] = cube_tmp[76];
        cube[102] = cube_tmp[77];
        cube[103] = cube_tmp[78];
        cube[104] = cube_tmp[79];
        cube[105] = cube_tmp[80];
        cube[106] = cube_tmp[81];
        cube[107] = cube_tmp[82];
        cube[108] = cube_tmp[83];
        cube[109] = cube_tmp[84];
        cube[110] = cube_tmp[85];
        break;
    }

    case Uw2: {
        cube[1] = cube_tmp[25];
        cube[2] = cube_tmp[24];
        cube[3] = cube_tmp[23];
        cube[4] = cube_tmp[22];
        cube[5] = cube_tmp[21];
        cube[6] = cube_tmp[20];
        cube[7] = cube_tmp[19];
        cube[8] = cube_tmp[18];
        cube[9] = cube_tmp[17];
        cube[10] = cube_tmp[16];
        cube[11] = cube_tmp[15];
        cube[12] = cube_tmp[14];
        cube[14] = cube_tmp[12];
        cube[15] = cube_tmp[11];
        cube[16] = cube_tmp[10];
        cube[17] = cube_tmp[9];
        cube[18] = cube_tmp[8];
        cube[19] = cube_tmp[7];
        cube[20] = cube_tmp[6];
        cube[21] = cube_tmp[5];
        cube[22] = cube_tmp[4];
        cube[23] = cube_tmp[3];
        cube[24] = cube_tmp[2];
        cube[25] = cube_tmp[1];
        cube[26] = cube_tmp[76];
        cube[27] = cube_tmp[77];
        cube[28] = cube_tmp[78];
        cube[29] = cube_tmp[79];
        cube[30] = cube_tmp[80];
        cube[31] = cube_tmp[81];
        cube[32] = cube_tmp[82];
        cube[33] = cube_tmp[83];
        cube[34] = cube_tmp[84];
        cube[35] = cube_tmp[85];
        cube[51] = cube_tmp[101];
        cube[52] = cube_tmp[102];
        cube[53] = cube_tmp[103];
        cube[54] = cube_tmp[104];
        cube[55] = cube_tmp[105];
        cube[56] = cube_tmp[106];
        cube[57] = cube_tmp[107];
        cube[58] = cube_tmp[108];
        cube[59] = cube_tmp[109];
        cube[60] = cube_tmp[110];
        cube[76] = cube_tmp[26];
        cube[77] = cube_tmp[27];
        cube[78] = cube_tmp[28];
        cube[79] = cube_tmp[29];
        cube[80] = cube_tmp[30];
        cube[81] = cube_tmp[31];
        cube[82] = cube_tmp[32];
        cube[83] = cube_tmp[33];
        cube[84] = cube_tmp[34];
        cube[85] = cube_tmp[35];
        cube[101] = cube_tmp[51];
        cube[102] = cube_tmp[52];
        cube[103] = cube_tmp[53];
        cube[104] = cube_tmp[54];
        cube[105] = cube_tmp[55];
        cube[106] = cube_tmp[56];
        cube[107] = cube_tmp[57];
        cube[108] = cube_tmp[58];
        cube[109] = cube_tmp[59];
        cube[110] = cube_tmp[60];
        break;
    }

    case L: {
        cube[1] = cube_tmp[125];
        cube[6] = cube_tmp[120];
        cube[11] = cube_tmp[115];
        cube[16] = cube_tmp[110];
        cube[21] = cube_tmp[105];
        cube[26] = cube_tmp[46];
        cube[27] = cube_tmp[41];
        cube[28] = cube_tmp[36];
        cube[29] = cube_tmp[31];
        cube[30] = cube_tmp[26];
        cube[31] = cube_tmp[47];
        cube[32] = cube_tmp[42];
        cube[33] = cube_tmp[37];
        cube[34] = cube_tmp[32];
        cube[35] = cube_tmp[27];
        cube[36] = cube_tmp[48];
        cube[37] = cube_tmp[43];
        cube[39] = cube_tmp[33];
        cube[40] = cube_tmp[28];
        cube[41] = cube_tmp[49];
        cube[42] = cube_tmp[44];
        cube[43] = cube_tmp[39];
        cube[44] = cube_tmp[34];
        cube[45] = cube_tmp[29];
        cube[46] = cube_tmp[50];
        cube[47] = cube_tmp[45];
        cube[48] = cube_tmp[40];
        cube[49] = cube_tmp[35];
        cube[50] = cube_tmp[30];
        cube[51] = cube_tmp[1];
        cube[56] = cube_tmp[6];
        cube[61] = cube_tmp[11];
        cube[66] = cube_tmp[16];
        cube[71] = cube_tmp[21];
        cube[105] = cube_tmp[146];
        cube[110] = cube_tmp[141];
        cube[115] = cube_tmp[136];
        cube[120] = cube_tmp[131];
        cube[125] = cube_tmp[126];
        cube[126] = cube_tmp[51];
        cube[131] = cube_tmp[56];
        cube[136] = cube_tmp[61];
        cube[141] = cube_tmp[66];
        cube[146] = cube_tmp[71];
        break;
    }

    case L_PRIME: {
        cube[1] = cube_tmp[51];
        cube[6] = cube_tmp[56];
        cube[11] = cube_tmp[61];
        cube[16] = cube_tmp[66];
        cube[21] = cube_tmp[71];
        cube[26] = cube_tmp[30];
        cube[27] = cube_tmp[35];
        cube[28] = cube_tmp[40];
        cube[29] = cube_tmp[45];
        cube[30] = cube_tmp[50];
        cube[31] = cube_tmp[29];
        cube[32] = cube_tmp[34];
        cube[33] = cube_tmp[39];
        cube[34] = cube_tmp[44];
        cube[35] = cube_tmp[49];
        cube[36] = cube_tmp[28];
        cube[37] = cube_tmp[33];
        cube[39] = cube_tmp[43];
        cube[40] = cube_tmp[48];
        cube[41] = cube_tmp[27];
        cube[42] = cube_tmp[32];
        cube[43] = cube_tmp[37];
        cube[44] = cube_tmp[42];
        cube[45] = cube_tmp[47];
        cube[46] = cube_tmp[26];
        cube[47] = cube_tmp[31];
        cube[48] = cube_tmp[36];
        cube[49] = cube_tmp[41];
        cube[50] = cube_tmp[46];
        cube[51] = cube_tmp[126];
        cube[56] = cube_tmp[131];
        cube[61] = cube_tmp[136];
        cube[66] = cube_tmp[141];
        cube[71] = cube_tmp[146];
        cube[105] = cube_tmp[21];
        cube[110] = cube_tmp[16];
        cube[115] = cube_tmp[11];
        cube[120] = cube_tmp[6];
        cube[125] = cube_tmp[1];
        cube[126] = cube_tmp[125];
        cube[131] = cube_tmp[120];
        cube[136] = cube_tmp[115];
        cube[141] = cube_tmp[110];
        cube[146] = cube_tmp[105];
        break;
    }

    case L2: {
        cube[1] = cube_tmp[126];
        cube[6] = cube_tmp[131];
        cube[11] = cube_tmp[136];
        cube[16] = cube_tmp[141];
        cube[21] = cube_tmp[146];
        cube[26] = cube_tmp[50];
        cube[27] = cube_tmp[49];
        cube[28] = cube_tmp[48];
        cube[29] = cube_tmp[47];
        cube[30] = cube_tmp[46];
        cube[31] = cube_tmp[45];
        cube[32] = cube_tmp[44];
        cube[33] = cube_tmp[43];
        cube[34] = cube_tmp[42];
        cube[35] = cube_tmp[41];
        cube[36] = cube_tmp[40];
        cube[37] = cube_tmp[39];
        cube[39] = cube_tmp[37];
        cube[40] = cube_tmp[36];
        cube[41] = cube_tmp[35];
        cube[42] = cube_tmp[34];
        cube[43] = cube_tmp[33];
        cube[44] = cube_tmp[32];
        cube[45] = cube_tmp[31];
        cube[46] = cube_tmp[30];
        cube[47] = cube_tmp[29];
        cube[48] = cube_tmp[28];
        cube[49] = cube_tmp[27];
        cube[50] = cube_tmp[26];
        cube[51] = cube_tmp[125];
        cube[56] = cube_tmp[120];
        cube[61] = cube_tmp[115];
        cube[66] = cube_tmp[110];
        cube[71] = cube_tmp[105];
        cube[105] = cube_tmp[71];
        cube[110] = cube_tmp[66];
        cube[115] = cube_tmp[61];
        cube[120] = cube_tmp[56];
        cube[125] = cube_tmp[51];
        cube[126] = cube_tmp[1];
        cube[131] = cube_tmp[6];
        cube[136] = cube_tmp[11];
        cube[141] = cube_tmp[16];
        cube[146] = cube_tmp[21];
        break;
    }

    case Lw: {
        cube[1] = cube_tmp[125];
        cube[2] = cube_tmp[124];
        cube[6] = cube_tmp[120];
        cube[7] = cube_tmp[119];
        cube[11] = cube_tmp[115];
        cube[12] = cube_tmp[114];
        cube[16] = cube_tmp[110];
        cube[17] = cube_tmp[109];
        cube[21] = cube_tmp[105];
        cube[22] = cube_tmp[104];
        cube[26] = cube_tmp[46];
        cube[27] = cube_tmp[41];
        cube[28] = cube_tmp[36];
        cube[29] = cube_tmp[31];
        cube[30] = cube_tmp[26];
        cube[31] = cube_tmp[47];
        cube[32] = cube_tmp[42];
        cube[33] = cube_tmp[37];
        cube[34] = cube_tmp[32];
        cube[35] = cube_tmp[27];
        cube[36] = cube_tmp[48];
        cube[37] = cube_tmp[43];
        cube[39] = cube_tmp[33];
        cube[40] = cube_tmp[28];
        cube[41] = cube_tmp[49];
        cube[42] = cube_tmp[44];
        cube[43] = cube_tmp[39];
        cube[44] = cube_tmp[34];
        cube[45] = cube_tmp[29];
        cube[46] = cube_tmp[50];
        cube[47] = cube_tmp[45];
        cube[48] = cube_tmp[40];
        cube[49] = cube_tmp[35];
        cube[50] = cube_tmp[30];
        cube[51] = cube_tmp[1];
        cube[52] = cube_tmp[2];
        cube[56] = cube_tmp[6];
        cube[57] = cube_tmp[7];
        cube[61] = cube_tmp[11];
        cube[62] = cube_tmp[12];
        cube[66] = cube_tmp[16];
        cube[67] = cube_tmp[17];
        cube[71] = cube_tmp[21];
        cube[72] = cube_tmp[22];
        cube[104] = cube_tmp[147];
        cube[105] = cube_tmp[146];
        cube[109] = cube_tmp[142];
        cube[110] = cube_tmp[141];
        cube[114] = cube_tmp[137];
        cube[115] = cube_tmp[136];
        cube[119] = cube_tmp[132];
        cube[120] = cube_tmp[131];
        cube[124] = cube_tmp[127];
        cube[125] = cube_tmp[126];
        cube[126] = cube_tmp[51];
        cube[127] = cube_tmp[52];
        cube[131] = cube_tmp[56];
        cube[132] = cube_tmp[57];
        cube[136] = cube_tmp[61];
        cube[137] = cube_tmp[62];
        cube[141] = cube_tmp[66];
        cube[142] = cube_tmp[67];
        cube[146] = cube_tmp[71];
        cube[147] = cube_tmp[72];
        break;
    }

    case Lw_PRIME: {
        cube[1] = cube_tmp[51];
        cube[2] = cube_tmp[52];
        cube[6] = cube_tmp[56];
        cube[7] = cube_tmp[57];
        cube[11] = cube_tmp[61];
        cube[12] = cube_tmp[62];
        cube[16] = cube_tmp[66];
        cube[17] = cube_tmp[67];
        cube[21] = cube_tmp[71];
        cube[22] = cube_tmp[72];
        cube[26] = cube_tmp[30];
        cube[27] = cube_tmp[35];
        cube[28] = cube_tmp[40];
        cube[29] = cube_tmp[45];
        cube[30] = cube_tmp[50];
        cube[31] = cube_tmp[29];
        cube[32] = cube_tmp[34];
        cube[33] = cube_tmp[39];
        cube[34] = cube_tmp[44];
        cube[35] = cube_tmp[49];
        cube[36] = cube_tmp[28];
        cube[37] = cube_tmp[33];
        cube[39] = cube_tmp[43];
        cube[40] = cube_tmp[48];
        cube[41] = cube_tmp[27];
        cube[42] = cube_tmp[32];
        cube[43] = cube_tmp[37];
        cube[44] = cube_tmp[42];
        cube[45] = cube_tmp[47];
        cube[46] = cube_tmp[26];
        cube[47] = cube_tmp[31];
        cube[48] = cube_tmp[36];
        cube[49] = cube_tmp[41];
        cube[50] = cube_tmp[46];
        cube[51] = cube_tmp[126];
        cube[52] = cube_tmp[127];
        cube[56] = cube_tmp[131];
        cube[57] = cube_tmp[132];
        cube[61] = cube_tmp[136];
        cube[62] = cube_tmp[137];
        cube[66] = cube_tmp[141];
        cube[67] = cube_tmp[142];
        cube[71] = cube_tmp[146];
        cube[72] = cube_tmp[147];
        cube[104] = cube_tmp[22];
        cube[105] = cube_tmp[21];
        cube[109] = cube_tmp[17];
        cube[110] = cube_tmp[16];
        cube[114] = cube_tmp[12];
        cube[115] = cube_tmp[11];
        cube[119] = cube_tmp[7];
        cube[120] = cube_tmp[6];
        cube[124] = cube_tmp[2];
        cube[125] = cube_tmp[1];
        cube[126] = cube_tmp[125];
        cube[127] = cube_tmp[124];
        cube[131] = cube_tmp[120];
        cube[132] = cube_tmp[119];
        cube[136] = cube_tmp[115];
        cube[137] = cube_tmp[114];
        cube[141] = cube_tmp[110];
        cube[142] = cube_tmp[109];
        cube[146] = cube_tmp[105];
        cube[147] = cube_tmp[104];
        break;
    }

    case Lw2: {
        cube[1] = cube_tmp[126];
        cube[2] = cube_tmp[127];
        cube[6] = cube_tmp[131];
        cube[7] = cube_tmp[132];
        cube[11] = cube_tmp[136];
        cube[12] = cube_tmp[137];
        cube[16] = cube_tmp[141];
        cube[17] = cube_tmp[142];
        cube[21] = cube_tmp[146];
        cube[22] = cube_tmp[147];
        cube[26] = cube_tmp[50];
        cube[27] = cube_tmp[49];
        cube[28] = cube_tmp[48];
        cube[29] = cube_tmp[47];
        cube[30] = cube_tmp[46];
        cube[31] = cube_tmp[45];
        cube[32] = cube_tmp[44];
        cube[33] = cube_tmp[43];
        cube[34] = cube_tmp[42];
        cube[35] = cube_tmp[41];
        cube[36] = cube_tmp[40];
        cube[37] = cube_tmp[39];
        cube[39] = cube_tmp[37];
        cube[40] = cube_tmp[36];
        cube[41] = cube_tmp[35];
        cube[42] = cube_tmp[34];
        cube[43] = cube_tmp[33];
        cube[44] = cube_tmp[32];
        cube[45] = cube_tmp[31];
        cube[46] = cube_tmp[30];
        cube[47] = cube_tmp[29];
        cube[48] = cube_tmp[28];
        cube[49] = cube_tmp[27];
        cube[50] = cube_tmp[26];
        cube[51] = cube_tmp[125];
        cube[52] = cube_tmp[124];
        cube[56] = cube_tmp[120];
        cube[57] = cube_tmp[119];
        cube[61] = cube_tmp[115];
        cube[62] = cube_tmp[114];
        cube[66] = cube_tmp[110];
        cube[67] = cube_tmp[109];
        cube[71] = cube_tmp[105];
        cube[72] = cube_tmp[104];
        cube[104] = cube_tmp[72];
        cube[105] = cube_tmp[71];
        cube[109] = cube_tmp[67];
        cube[110] = cube_tmp[66];
        cube[114] = cube_tmp[62];
        cube[115] = cube_tmp[61];
        cube[119] = cube_tmp[57];
        cube[120] = cube_tmp[56];
        cube[124] = cube_tmp[52];
        cube[125] = cube_tmp[51];
        cube[126] = cube_tmp[1];
        cube[127] = cube_tmp[2];
        cube[131] = cube_tmp[6];
        cube[132] = cube_tmp[7];
        cube[136] = cube_tmp[11];
        cube[137] = cube_tmp[12];
        cube[141] = cube_tmp[16];
        cube[142] = cube_tmp[17];
        cube[146] = cube_tmp[21];
        cube[147] = cube_tmp[22];
        break;
    }

    case F: {
        cube[21] = cube_tmp[50];
        cube[22] = cube_tmp[45];
        cube[23] = cube_tmp[40];
        cube[24] = cube_tmp[35];
        cube[25] = cube_tmp[30];
        cube[30] = cube_tmp[126];
        cube[35] = cube_tmp[127];
        cube[40] = cube_tmp[128];
        cube[45] = cube_tmp[129];
        cube[50] = cube_tmp[130];
        cube[51] = cube_tmp[71];
        cube[52] = cube_tmp[66];
        cube[53] = cube_tmp[61];
        cube[54] = cube_tmp[56];
        cube[55] = cube_tmp[51];
        cube[56] = cube_tmp[72];
        cube[57] = cube_tmp[67];
        cube[58] = cube_tmp[62];
        cube[59] = cube_tmp[57];
        cube[60] = cube_tmp[52];
        cube[61] = cube_tmp[73];
        cube[62] = cube_tmp[68];
        cube[64] = cube_tmp[58];
        cube[65] = cube_tmp[53];
        cube[66] = cube_tmp[74];
        cube[67] = cube_tmp[69];
        cube[68] = cube_tmp[64];
        cube[69] = cube_tmp[59];
        cube[70] = cube_tmp[54];
        cube[71] = cube_tmp[75];
        cube[72] = cube_tmp[70];
        cube[73] = cube_tmp[65];
        cube[74] = cube_tmp[60];
        cube[75] = cube_tmp[55];
        cube[76] = cube_tmp[21];
        cube[81] = cube_tmp[22];
        cube[86] = cube_tmp[23];
        cube[91] = cube_tmp[24];
        cube[96] = cube_tmp[25];
        cube[126] = cube_tmp[96];
        cube[127] = cube_tmp[91];
        cube[128] = cube_tmp[86];
        cube[129] = cube_tmp[81];
        cube[130] = cube_tmp[76];
        break;
    }

    case F_PRIME: {
        cube[21] = cube_tmp[76];
        cube[22] = cube_tmp[81];
        cube[23] = cube_tmp[86];
        cube[24] = cube_tmp[91];
        cube[25] = cube_tmp[96];
        cube[30] = cube_tmp[25];
        cube[35] = cube_tmp[24];
        cube[40] = cube_tmp[23];
        cube[45] = cube_tmp[22];
        cube[50] = cube_tmp[21];
        cube[51] = cube_tmp[55];
        cube[52] = cube_tmp[60];
        cube[53] = cube_tmp[65];
        cube[54] = cube_tmp[70];
        cube[55] = cube_tmp[75];
        cube[56] = cube_tmp[54];
        cube[57] = cube_tmp[59];
        cube[58] = cube_tmp[64];
        cube[59] = cube_tmp[69];
        cube[60] = cube_tmp[74];
        cube[61] = cube_tmp[53];
        cube[62] = cube_tmp[58];
        cube[64] = cube_tmp[68];
        cube[65] = cube_tmp[73];
        cube[66] = cube_tmp[52];
        cube[67] = cube_tmp[57];
        cube[68] = cube_tmp[62];
        cube[69] = cube_tmp[67];
        cube[70] = cube_tmp[72];
        cube[71] = cube_tmp[51];
        cube[72] = cube_tmp[56];
        cube[73] = cube_tmp[61];
        cube[74] = cube_tmp[66];
        cube[75] = cube_tmp[71];
        cube[76] = cube_tmp[130];
        cube[81] = cube_tmp[129];
        cube[86] = cube_tmp[128];
        cube[91] = cube_tmp[127];
        cube[96] = cube_tmp[126];
        cube[126] = cube_tmp[30];
        cube[127] = cube_tmp[35];
        cube[128] = cube_tmp[40];
        cube[129] = cube_tmp[45];
        cube[130] = cube_tmp[50];
        break;
    }

    case F2: {
        cube[21] = cube_tmp[130];
        cube[22] = cube_tmp[129];
        cube[23] = cube_tmp[128];
        cube[24] = cube_tmp[127];
        cube[25] = cube_tmp[126];
        cube[30] = cube_tmp[96];
        cube[35] = cube_tmp[91];
        cube[40] = cube_tmp[86];
        cube[45] = cube_tmp[81];
        cube[50] = cube_tmp[76];
        cube[51] = cube_tmp[75];
        cube[52] = cube_tmp[74];
        cube[53] = cube_tmp[73];
        cube[54] = cube_tmp[72];
        cube[55] = cube_tmp[71];
        cube[56] = cube_tmp[70];
        cube[57] = cube_tmp[69];
        cube[58] = cube_tmp[68];
        cube[59] = cube_tmp[67];
        cube[60] = cube_tmp[66];
        cube[61] = cube_tmp[65];
        cube[62] = cube_tmp[64];
        cube[64] = cube_tmp[62];
        cube[65] = cube_tmp[61];
        cube[66] = cube_tmp[60];
        cube[67] = cube_tmp[59];
        cube[68] = cube_tmp[58];
        cube[69] = cube_tmp[57];
        cube[70] = cube_tmp[56];
        cube[71] = cube_tmp[55];
        cube[72] = cube_tmp[54];
        cube[73] = cube_tmp[53];
        cube[74] = cube_tmp[52];
        cube[75] = cube_tmp[51];
        cube[76] = cube_tmp[50];
        cube[81] = cube_tmp[45];
        cube[86] = cube_tmp[40];
        cube[91] = cube_tmp[35];
        cube[96] = cube_tmp[30];
        cube[126] = cube_tmp[25];
        cube[127] = cube_tmp[24];
        cube[128] = cube_tmp[23];
        cube[129] = cube_tmp[22];
        cube[130] = cube_tmp[21];
        break;
    }

    case Fw: {
        cube[16] = cube_tmp[49];
        cube[17] = cube_tmp[44];
        cube[18] = cube_tmp[39];
        cube[19] = cube_tmp[34];
        cube[20] = cube_tmp[29];
        cube[21] = cube_tmp[50];
        cube[22] = cube_tmp[45];
        cube[23] = cube_tmp[40];
        cube[24] = cube_tmp[35];
        cube[25] = cube_tmp[30];
        cube[29] = cube_tmp[131];
        cube[30] = cube_tmp[126];
        cube[34] = cube_tmp[132];
        cube[35] = cube_tmp[127];
        cube[39] = cube_tmp[133];
        cube[40] = cube_tmp[128];
        cube[44] = cube_tmp[134];
        cube[45] = cube_tmp[129];
        cube[49] = cube_tmp[135];
        cube[50] = cube_tmp[130];
        cube[51] = cube_tmp[71];
        cube[52] = cube_tmp[66];
        cube[53] = cube_tmp[61];
        cube[54] = cube_tmp[56];
        cube[55] = cube_tmp[51];
        cube[56] = cube_tmp[72];
        cube[57] = cube_tmp[67];
        cube[58] = cube_tmp[62];
        cube[59] = cube_tmp[57];
        cube[60] = cube_tmp[52];
        cube[61] = cube_tmp[73];
        cube[62] = cube_tmp[68];
        cube[64] = cube_tmp[58];
        cube[65] = cube_tmp[53];
        cube[66] = cube_tmp[74];
        cube[67] = cube_tmp[69];
        cube[68] = cube_tmp[64];
        cube[69] = cube_tmp[59];
        cube[70] = cube_tmp[54];
        cube[71] = cube_tmp[75];
        cube[72] = cube_tmp[70];
        cube[73] = cube_tmp[65];
        cube[74] = cube_tmp[60];
        cube[75] = cube_tmp[55];
        cube[76] = cube_tmp[21];
        cube[77] = cube_tmp[16];
        cube[81] = cube_tmp[22];
        cube[82] = cube_tmp[17];
        cube[86] = cube_tmp[23];
        cube[87] = cube_tmp[18];
        cube[91] = cube_tmp[24];
        cube[92] = cube_tmp[19];
        cube[96] = cube_tmp[25];
        cube[97] = cube_tmp[20];
        cube[126] = cube_tmp[96];
        cube[127] = cube_tmp[91];
        cube[128] = cube_tmp[86];
        cube[129] = cube_tmp[81];
        cube[130] = cube_tmp[76];
        cube[131] = cube_tmp[97];
        cube[132] = cube_tmp[92];
        cube[133] = cube_tmp[87];
        cube[134] = cube_tmp[82];
        cube[135] = cube_tmp[77];
        break;
    }

    case Fw_PRIME: {
        cube[16] = cube_tmp[77];
        cube[17] = cube_tmp[82];
        cube[18] = cube_tmp[87];
        cube[19] = cube_tmp[92];
        cube[20] = cube_tmp[97];
        cube[21] = cube_tmp[76];
        cube[22] = cube_tmp[81];
        cube[23] = cube_tmp[86];
        cube[24] = cube_tmp[91];
        cube[25] = cube_tmp[96];
        cube[29] = cube_tmp[20];
        cube[30] = cube_tmp[25];
        cube[34] = cube_tmp[19];
        cube[35] = cube_tmp[24];
        cube[39] = cube_tmp[18];
        cube[40] = cube_tmp[23];
        cube[44] = cube_tmp[17];
        cube[45] = cube_tmp[22];
        cube[49] = cube_tmp[16];
        cube[50] = cube_tmp[21];
        cube[51] = cube_tmp[55];
        cube[52] = cube_tmp[60];
        cube[53] = cube_tmp[65];
        cube[54] = cube_tmp[70];
        cube[55] = cube_tmp[75];
        cube[56] = cube_tmp[54];
        cube[57] = cube_tmp[59];
        cube[58] = cube_tmp[64];
        cube[59] = cube_tmp[69];
        cube[60] = cube_tmp[74];
        cube[61] = cube_tmp[53];
        cube[62] = cube_tmp[58];
        cube[64] = cube_tmp[68];
        cube[65] = cube_tmp[73];
        cube[66] = cube_tmp[52];
        cube[67] = cube_tmp[57];
        cube[68] = cube_tmp[62];
        cube[69] = cube_tmp[67];
        cube[70] = cube_tmp[72];
        cube[71] = cube_tmp[51];
        cube[72] = cube_tmp[56];
        cube[73] = cube_tmp[61];
        cube[74] = cube_tmp[66];
        cube[75] = cube_tmp[71];
        cube[76] = cube_tmp[130];
        cube[77] = cube_tmp[135];
        cube[81] = cube_tmp[129];
        cube[82] = cube_tmp[134];
        cube[86] = cube_tmp[128];
        cube[87] = cube_tmp[133];
        cube[91] = cube_tmp[127];
        cube[92] = cube_tmp[132];
        cube[96] = cube_tmp[126];
        cube[97] = cube_tmp[131];
        cube[126] = cube_tmp[30];
        cube[127] = cube_tmp[35];
        cube[128] = cube_tmp[40];
        cube[129] = cube_tmp[45];
        cube[130] = cube_tmp[50];
        cube[131] = cube_tmp[29];
        cube[132] = cube_tmp[34];
        cube[133] = cube_tmp[39];
        cube[134] = cube_tmp[44];
        cube[135] = cube_tmp[49];
        break;
    }

    case Fw2: {
        cube[16] = cube_tmp[135];
        cube[17] = cube_tmp[134];
        cube[18] = cube_tmp[133];
        cube[19] = cube_tmp[132];
        cube[20] = cube_tmp[131];
        cube[21] = cube_tmp[130];
        cube[22] = cube_tmp[129];
        cube[23] = cube_tmp[128];
        cube[24] = cube_tmp[127];
        cube[25] = cube_tmp[126];
        cube[29] = cube_tmp[97];
        cube[30] = cube_tmp[96];
        cube[34] = cube_tmp[92];
        cube[35] = cube_tmp[91];
        cube[39] = cube_tmp[87];
        cube[40] = cube_tmp[86];
        cube[44] = cube_tmp[82];
        cube[45] = cube_tmp[81];
        cube[49] = cube_tmp[77];
        cube[50] = cube_tmp[76];
        cube[51] = cube_tmp[75];
        cube[52] = cube_tmp[74];
        cube[53] = cube_tmp[73];
        cube[54] = cube_tmp[72];
        cube[55] = cube_tmp[71];
        cube[56] = cube_tmp[70];
        cube[57] = cube_tmp[69];
        cube[58] = cube_tmp[68];
        cube[59] = cube_tmp[67];
        cube[60] = cube_tmp[66];
        cube[61] = cube_tmp[65];
        cube[62] = cube_tmp[64];
        cube[64] = cube_tmp[62];
        cube[65] = cube_tmp[61];
        cube[66] = cube_tmp[60];
        cube[67] = cube_tmp[59];
        cube[68] = cube_tmp[58];
        cube[69] = cube_tmp[57];
        cube[70] = cube_tmp[56];
        cube[71] = cube_tmp[55];
        cube[72] = cube_tmp[54];
        cube[73] = cube_tmp[53];
        cube[74] = cube_tmp[52];
        cube[75] = cube_tmp[51];
        cube[76] = cube_tmp[50];
        cube[77] = cube_tmp[49];
        cube[81] = cube_tmp[45];
        cube[82] = cube_tmp[44];
        cube[86] = cube_tmp[40];
        cube[87] = cube_tmp[39];
        cube[91] = cube_tmp[35];
        cube[92] = cube_tmp[34];
        cube[96] = cube_tmp[30];
        cube[97] = cube_tmp[29];
        cube[126] = cube_tmp[25];
        cube[127] = cube_tmp[24];
        cube[128] = cube_tmp[23];
        cube[129] = cube_tmp[22];
        cube[130] = cube_tmp[21];
        cube[131] = cube_tmp[20];
        cube[132] = cube_tmp[19];
        cube[133] = cube_tmp[18];
        cube[134] = cube_tmp[17];
        cube[135] = cube_tmp[16];
        break;
    }

    case R: {
        cube[5] = cube_tmp[55];
        cube[10] = cube_tmp[60];
        cube[15] = cube_tmp[65];
        cube[20] = cube_tmp[70];
        cube[25] = cube_tmp[75];
        cube[55] = cube_tmp[130];
        cube[60] = cube_tmp[135];
        cube[65] = cube_tmp[140];
        cube[70] = cube_tmp[145];
        cube[75] = cube_tmp[150];
        cube[76] = cube_tmp[96];
        cube[77] = cube_tmp[91];
        cube[78] = cube_tmp[86];
        cube[79] = cube_tmp[81];
        cube[80] = cube_tmp[76];
        cube[81] = cube_tmp[97];
        cube[82] = cube_tmp[92];
        cube[83] = cube_tmp[87];
        cube[84] = cube_tmp[82];
        cube[85] = cube_tmp[77];
        cube[86] = cube_tmp[98];
        cube[87] = cube_tmp[93];
        cube[89] = cube_tmp[83];
        cube[90] = cube_tmp[78];
        cube[91] = cube_tmp[99];
        cube[92] = cube_tmp[94];
        cube[93] = cube_tmp[89];
        cube[94] = cube_tmp[84];
        cube[95] = cube_tmp[79];
        cube[96] = cube_tmp[100];
        cube[97] = cube_tmp[95];
        cube[98] = cube_tmp[90];
        cube[99] = cube_tmp[85];
        cube[100] = cube_tmp[80];
        cube[101] = cube_tmp[25];
        cube[106] = cube_tmp[20];
        cube[111] = cube_tmp[15];
        cube[116] = cube_tmp[10];
        cube[121] = cube_tmp[5];
        cube[130] = cube_tmp[121];
        cube[135] = cube_tmp[116];
        cube[140] = cube_tmp[111];
        cube[145] = cube_tmp[106];
        cube[150] = cube_tmp[101];
        break;
    }

    case R_PRIME: {
        cube[5] = cube_tmp[121];
        cube[10] = cube_tmp[116];
        cube[15] = cube_tmp[111];
        cube[20] = cube_tmp[106];
        cube[25] = cube_tmp[101];
        cube[55] = cube_tmp[5];
        cube[60] = cube_tmp[10];
        cube[65] = cube_tmp[15];
        cube[70] = cube_tmp[20];
        cube[75] = cube_tmp[25];
        cube[76] = cube_tmp[80];
        cube[77] = cube_tmp[85];
        cube[78] = cube_tmp[90];
        cube[79] = cube_tmp[95];
        cube[80] = cube_tmp[100];
        cube[81] = cube_tmp[79];
        cube[82] = cube_tmp[84];
        cube[83] = cube_tmp[89];
        cube[84] = cube_tmp[94];
        cube[85] = cube_tmp[99];
        cube[86] = cube_tmp[78];
        cube[87] = cube_tmp[83];
        cube[89] = cube_tmp[93];
        cube[90] = cube_tmp[98];
        cube[91] = cube_tmp[77];
        cube[92] = cube_tmp[82];
        cube[93] = cube_tmp[87];
        cube[94] = cube_tmp[92];
        cube[95] = cube_tmp[97];
        cube[96] = cube_tmp[76];
        cube[97] = cube_tmp[81];
        cube[98] = cube_tmp[86];
        cube[99] = cube_tmp[91];
        cube[100] = cube_tmp[96];
        cube[101] = cube_tmp[150];
        cube[106] = cube_tmp[145];
        cube[111] = cube_tmp[140];
        cube[116] = cube_tmp[135];
        cube[121] = cube_tmp[130];
        cube[130] = cube_tmp[55];
        cube[135] = cube_tmp[60];
        cube[140] = cube_tmp[65];
        cube[145] = cube_tmp[70];
        cube[150] = cube_tmp[75];
        break;
    }

    case R2: {
        cube[5] = cube_tmp[130];
        cube[10] = cube_tmp[135];
        cube[15] = cube_tmp[140];
        cube[20] = cube_tmp[145];
        cube[25] = cube_tmp[150];
        cube[55] = cube_tmp[121];
        cube[60] = cube_tmp[116];
        cube[65] = cube_tmp[111];
        cube[70] = cube_tmp[106];
        cube[75] = cube_tmp[101];
        cube[76] = cube_tmp[100];
        cube[77] = cube_tmp[99];
        cube[78] = cube_tmp[98];
        cube[79] = cube_tmp[97];
        cube[80] = cube_tmp[96];
        cube[81] = cube_tmp[95];
        cube[82] = cube_tmp[94];
        cube[83] = cube_tmp[93];
        cube[84] = cube_tmp[92];
        cube[85] = cube_tmp[91];
        cube[86] = cube_tmp[90];
        cube[87] = cube_tmp[89];
        cube[89] = cube_tmp[87];
        cube[90] = cube_tmp[86];
        cube[91] = cube_tmp[85];
        cube[92] = cube_tmp[84];
        cube[93] = cube_tmp[83];
        cube[94] = cube_tmp[82];
        cube[95] = cube_tmp[81];
        cube[96] = cube_tmp[80];
        cube[97] = cube_tmp[79];
        cube[98] = cube_tmp[78];
        cube[99] = cube_tmp[77];
        cube[100] = cube_tmp[76];
        cube[101] = cube_tmp[75];
        cube[106] = cube_tmp[70];
        cube[111] = cube_tmp[65];
        cube[116] = cube_tmp[60];
        cube[121] = cube_tmp[55];
        cube[130] = cube_tmp[5];
        cube[135] = cube_tmp[10];
        cube[140] = cube_tmp[15];
        cube[145] = cube_tmp[20];
        cube[150] = cube_tmp[25];
        break;
    }

    case Rw: {
        cube[4] = cube_tmp[54];
        cube[5] = cube_tmp[55];
        cube[9] = cube_tmp[59];
        cube[10] = cube_tmp[60];
        cube[14] = cube_tmp[64];
        cube[15] = cube_tmp[65];
        cube[19] = cube_tmp[69];
        cube[20] = cube_tmp[70];
        cube[24] = cube_tmp[74];
        cube[25] = cube_tmp[75];
        cube[54] = cube_tmp[129];
        cube[55] = cube_tmp[130];
        cube[59] = cube_tmp[134];
        cube[60] = cube_tmp[135];
        cube[64] = cube_tmp[139];
        cube[65] = cube_tmp[140];
        cube[69] = cube_tmp[144];
        cube[70] = cube_tmp[145];
        cube[74] = cube_tmp[149];
        cube[75] = cube_tmp[150];
        cube[76] = cube_tmp[96];
        cube[77] = cube_tmp[91];
        cube[78] = cube_tmp[86];
        cube[79] = cube_tmp[81];
        cube[80] = cube_tmp[76];
        cube[81] = cube_tmp[97];
        cube[82] = cube_tmp[92];
        cube[83] = cube_tmp[87];
        cube[84] = cube_tmp[82];
        cube[85] = cube_tmp[77];
        cube[86] = cube_tmp[98];
        cube[87] = cube_tmp[93];
        cube[89] = cube_tmp[83];
        cube[90] = cube_tmp[78];
        cube[91] = cube_tmp[99];
        cube[92] = cube_tmp[94];
        cube[93] = cube_tmp[89];
        cube[94] = cube_tmp[84];
        cube[95] = cube_tmp[79];
        cube[96] = cube_tmp[100];
        cube[97] = cube_tmp[95];
        cube[98] = cube_tmp[90];
        cube[99] = cube_tmp[85];
        cube[100] = cube_tmp[80];
        cube[101] = cube_tmp[25];
        cube[102] = cube_tmp[24];
        cube[106] = cube_tmp[20];
        cube[107] = cube_tmp[19];
        cube[111] = cube_tmp[15];
        cube[112] = cube_tmp[14];
        cube[116] = cube_tmp[10];
        cube[117] = cube_tmp[9];
        cube[121] = cube_tmp[5];
        cube[122] = cube_tmp[4];
        cube[129] = cube_tmp[122];
        cube[130] = cube_tmp[121];
        cube[134] = cube_tmp[117];
        cube[135] = cube_tmp[116];
        cube[139] = cube_tmp[112];
        cube[140] = cube_tmp[111];
        cube[144] = cube_tmp[107];
        cube[145] = cube_tmp[106];
        cube[149] = cube_tmp[102];
        cube[150] = cube_tmp[101];
        break;
    }

    case Rw_PRIME: {
        cube[4] = cube_tmp[122];
        cube[5] = cube_tmp[121];
        cube[9] = cube_tmp[117];
        cube[10] = cube_tmp[116];
        cube[14] = cube_tmp[112];
        cube[15] = cube_tmp[111];
        cube[19] = cube_tmp[107];
        cube[20] = cube_tmp[106];
        cube[24] = cube_tmp[102];
        cube[25] = cube_tmp[101];
        cube[54] = cube_tmp[4];
        cube[55] = cube_tmp[5];
        cube[59] = cube_tmp[9];
        cube[60] = cube_tmp[10];
        cube[64] = cube_tmp[14];
        cube[65] = cube_tmp[15];
        cube[69] = cube_tmp[19];
        cube[70] = cube_tmp[20];
        cube[74] = cube_tmp[24];
        cube[75] = cube_tmp[25];
        cube[76] = cube_tmp[80];
        cube[77] = cube_tmp[85];
        cube[78] = cube_tmp[90];
        cube[79] = cube_tmp[95];
        cube[80] = cube_tmp[100];
        cube[81] = cube_tmp[79];
        cube[82] = cube_tmp[84];
        cube[83] = cube_tmp[89];
        cube[84] = cube_tmp[94];
        cube[85] = cube_tmp[99];
        cube[86] = cube_tmp[78];
        cube[87] = cube_tmp[83];
        cube[89] = cube_tmp[93];
        cube[90] = cube_tmp[98];
        cube[91] = cube_tmp[77];
        cube[92] = cube_tmp[82];
        cube[93] = cube_tmp[87];
        cube[94] = cube_tmp[92];
        cube[95] = cube_tmp[97];
        cube[96] = cube_tmp[76];
        cube[97] = cube_tmp[81];
        cube[98] = cube_tmp[86];
        cube[99] = cube_tmp[91];
        cube[100] = cube_tmp[96];
        cube[101] = cube_tmp[150];
        cube[102] = cube_tmp[149];
        cube[106] = cube_tmp[145];
        cube[107] = cube_tmp[144];
        cube[111] = cube_tmp[140];
        cube[112] = cube_tmp[139];
        cube[116] = cube_tmp[135];
        cube[117] = cube_tmp[134];
        cube[121] = cube_tmp[130];
        cube[122] = cube_tmp[129];
        cube[129] = cube_tmp[54];
        cube[130] = cube_tmp[55];
        cube[134] = cube_tmp[59];
        cube[135] = cube_tmp[60];
        cube[139] = cube_tmp[64];
        cube[140] = cube_tmp[65];
        cube[144] = cube_tmp[69];
        cube[145] = cube_tmp[70];
        cube[149] = cube_tmp[74];
        cube[150] = cube_tmp[75];
        break;
    }

    case Rw2: {
        cube[4] = cube_tmp[129];
        cube[5] = cube_tmp[130];
        cube[9] = cube_tmp[134];
        cube[10] = cube_tmp[135];
        cube[14] = cube_tmp[139];
        cube[15] = cube_tmp[140];
        cube[19] = cube_tmp[144];
        cube[20] = cube_tmp[145];
        cube[24] = cube_tmp[149];
        cube[25] = cube_tmp[150];
        cube[54] = cube_tmp[122];
        cube[55] = cube_tmp[121];
        cube[59] = cube_tmp[117];
        cube[60] = cube_tmp[116];
        cube[64] = cube_tmp[112];
        cube[65] = cube_tmp[111];
        cube[69] = cube_tmp[107];
        cube[70] = cube_tmp[106];
        cube[74] = cube_tmp[102];
        cube[75] = cube_tmp[101];
        cube[76] = cube_tmp[100];
        cube[77] = cube_tmp[99];
        cube[78] = cube_tmp[98];
        cube[79] = cube_tmp[97];
        cube[80] = cube_tmp[96];
        cube[81] = cube_tmp[95];
        cube[82] = cube_tmp[94];
        cube[83] = cube_tmp[93];
        cube[84] = cube_tmp[92];
        cube[85] = cube_tmp[91];
        cube[86] = cube_tmp[90];
        cube[87] = cube_tmp[89];
        cube[89] = cube_tmp[87];
        cube[90] = cube_tmp[86];
        cube[91] = cube_tmp[85];
        cube[92] = cube_tmp[84];
        cube[93] = cube_tmp[83];
        cube[94] = cube_tmp[82];
        cube[95] = cube_tmp[81];
        cube[96] = cube_tmp[80];
        cube[97] = cube_tmp[79];
        cube[98] = cube_tmp[78];
        cube[99] = cube_tmp[77];
        cube[100] = cube_tmp[76];
        cube[101] = cube_tmp[75];
        cube[102] = cube_tmp[74];
        cube[106] = cube_tmp[70];
        cube[107] = cube_tmp[69];
        cube[111] = cube_tmp[65];
        cube[112] = cube_tmp[64];
        cube[116] = cube_tmp[60];
        cube[117] = cube_tmp[59];
        cube[121] = cube_tmp[55];
        cube[122] = cube_tmp[54];
        cube[129] = cube_tmp[4];
        cube[130] = cube_tmp[5];
        cube[134] = cube_tmp[9];
        cube[135] = cube_tmp[10];
        cube[139] = cube_tmp[14];
        cube[140] = cube_tmp[15];
        cube[144] = cube_tmp[19];
        cube[145] = cube_tmp[20];
        cube[149] = cube_tmp[24];
        cube[150] = cube_tmp[25];
        break;
    }

    case B: {
        cube[1] = cube_tmp[80];
        cube[2] = cube_tmp[85];
        cube[3] = cube_tmp[90];
        cube[4] = cube_tmp[95];
        cube[5] = cube_tmp[100];
        cube[26] = cube_tmp[5];
        cube[31] = cube_tmp[4];
        cube[36] = cube_tmp[3];
        cube[41] = cube_tmp[2];
        cube[46] = cube_tmp[1];
        cube[80] = cube_tmp[150];
        cube[85] = cube_tmp[149];
        cube[90] = cube_tmp[148];
        cube[95] = cube_tmp[147];
        cube[100] = cube_tmp[146];
        cube[101] = cube_tmp[121];
        cube[102] = cube_tmp[116];
        cube[103] = cube_tmp[111];
        cube[104] = cube_tmp[106];
        cube[105] = cube_tmp[101];
        cube[106] = cube_tmp[122];
        cube[107] = cube_tmp[117];
        cube[108] = cube_tmp[112];
        cube[109] = cube_tmp[107];
        cube[110] = cube_tmp[102];
        cube[111] = cube_tmp[123];
        cube[112] = cube_tmp[118];
        cube[114] = cube_tmp[108];
        cube[115] = cube_tmp[103];
        cube[116] = cube_tmp[124];
        cube[117] = cube_tmp[119];
        cube[118] = cube_tmp[114];
        cube[119] = cube_tmp[109];
        cube[120] = cube_tmp[104];
        cube[121] = cube_tmp[125];
        cube[122] = cube_tmp[120];
        cube[123] = cube_tmp[115];
        cube[124] = cube_tmp[110];
        cube[125] = cube_tmp[105];
        cube[146] = cube_tmp[26];
        cube[147] = cube_tmp[31];
        cube[148] = cube_tmp[36];
        cube[149] = cube_tmp[41];
        cube[150] = cube_tmp[46];
        break;
    }

    case B_PRIME: {
        cube[1] = cube_tmp[46];
        cube[2] = cube_tmp[41];
        cube[3] = cube_tmp[36];
        cube[4] = cube_tmp[31];
        cube[5] = cube_tmp[26];
        cube[26] = cube_tmp[146];
        cube[31] = cube_tmp[147];
        cube[36] = cube_tmp[148];
        cube[41] = cube_tmp[149];
        cube[46] = cube_tmp[150];
        cube[80] = cube_tmp[1];
        cube[85] = cube_tmp[2];
        cube[90] = cube_tmp[3];
        cube[95] = cube_tmp[4];
        cube[100] = cube_tmp[5];
        cube[101] = cube_tmp[105];
        cube[102] = cube_tmp[110];
        cube[103] = cube_tmp[115];
        cube[104] = cube_tmp[120];
        cube[105] = cube_tmp[125];
        cube[106] = cube_tmp[104];
        cube[107] = cube_tmp[109];
        cube[108] = cube_tmp[114];
        cube[109] = cube_tmp[119];
        cube[110] = cube_tmp[124];
        cube[111] = cube_tmp[103];
        cube[112] = cube_tmp[108];
        cube[114] = cube_tmp[118];
        cube[115] = cube_tmp[123];
        cube[116] = cube_tmp[102];
        cube[117] = cube_tmp[107];
        cube[118] = cube_tmp[112];
        cube[119] = cube_tmp[117];
        cube[120] = cube_tmp[122];
        cube[121] = cube_tmp[101];
        cube[122] = cube_tmp[106];
        cube[123] = cube_tmp[111];
        cube[124] = cube_tmp[116];
        cube[125] = cube_tmp[121];
        cube[146] = cube_tmp[100];
        cube[147] = cube_tmp[95];
        cube[148] = cube_tmp[90];
        cube[149] = cube_tmp[85];
        cube[150] = cube_tmp[80];
        break;
    }

    case B2: {
        cube[1] = cube_tmp[150];
        cube[2] = cube_tmp[149];
        cube[3] = cube_tmp[148];
        cube[4] = cube_tmp[147];
        cube[5] = cube_tmp[146];
        cube[26] = cube_tmp[100];
        cube[31] = cube_tmp[95];
        cube[36] = cube_tmp[90];
        cube[41] = cube_tmp[85];
        cube[46] = cube_tmp[80];
        cube[80] = cube_tmp[46];
        cube[85] = cube_tmp[41];
        cube[90] = cube_tmp[36];
        cube[95] = cube_tmp[31];
        cube[100] = cube_tmp[26];
        cube[101] = cube_tmp[125];
        cube[102] = cube_tmp[124];
        cube[103] = cube_tmp[123];
        cube[104] = cube_tmp[122];
        cube[105] = cube_tmp[121];
        cube[106] = cube_tmp[120];
        cube[107] = cube_tmp[119];
        cube[108] = cube_tmp[118];
        cube[109] = cube_tmp[117];
        cube[110] = cube_tmp[116];
        cube[111] = cube_tmp[115];
        cube[112] = cube_tmp[114];
        cube[114] = cube_tmp[112];
        cube[115] = cube_tmp[111];
        cube[116] = cube_tmp[110];
        cube[117] = cube_tmp[109];
        cube[118] = cube_tmp[108];
        cube[119] = cube_tmp[107];
        cube[120] = cube_tmp[106];
        cube[121] = cube_tmp[105];
        cube[122] = cube_tmp[104];
        cube[123] = cube_tmp[103];
        cube[124] = cube_tmp[102];
        cube[125] = cube_tmp[101];
        cube[146] = cube_tmp[5];
        cube[147] = cube_tmp[4];
        cube[148] = cube_tmp[3];
        cube[149] = cube_tmp[2];
        cube[150] = cube_tmp[1];
        break;
    }

    case Bw: {
        cube[1] = cube_tmp[80];
        cube[2] = cube_tmp[85];
        cube[3] = cube_tmp[90];
        cube[4] = cube_tmp[95];
        cube[5] = cube_tmp[100];
        cube[6] = cube_tmp[79];
        cube[7] = cube_tmp[84];
        cube[8] = cube_tmp[89];
        cube[9] = cube_tmp[94];
        cube[10] = cube_tmp[99];
        cube[26] = cube_tmp[5];
        cube[27] = cube_tmp[10];
        cube[31] = cube_tmp[4];
        cube[32] = cube_tmp[9];
        cube[36] = cube_tmp[3];
        cube[37] = cube_tmp[8];
        cube[41] = cube_tmp[2];
        cube[42] = cube_tmp[7];
        cube[46] = cube_tmp[1];
        cube[47] = cube_tmp[6];
        cube[79] = cube_tmp[145];
        cube[80] = cube_tmp[150];
        cube[84] = cube_tmp[144];
        cube[85] = cube_tmp[149];
        cube[89] = cube_tmp[143];
        cube[90] = cube_tmp[148];
        cube[94] = cube_tmp[142];
        cube[95] = cube_tmp[147];
        cube[99] = cube_tmp[141];
        cube[100] = cube_tmp[146];
        cube[101] = cube_tmp[121];
        cube[102] = cube_tmp[116];
        cube[103] = cube_tmp[111];
        cube[104] = cube_tmp[106];
        cube[105] = cube_tmp[101];
        cube[106] = cube_tmp[122];
        cube[107] = cube_tmp[117];
        cube[108] = cube_tmp[112];
        cube[109] = cube_tmp[107];
        cube[110] = cube_tmp[102];
        cube[111] = cube_tmp[123];
        cube[112] = cube_tmp[118];
        cube[114] = cube_tmp[108];
        cube[115] = cube_tmp[103];
        cube[116] = cube_tmp[124];
        cube[117] = cube_tmp[119];
        cube[118] = cube_tmp[114];
        cube[119] = cube_tmp[109];
        cube[120] = cube_tmp[104];
        cube[121] = cube_tmp[125];
        cube[122] = cube_tmp[120];
        cube[123] = cube_tmp[115];
        cube[124] = cube_tmp[110];
        cube[125] = cube_tmp[105];
        cube[141] = cube_tmp[27];
        cube[142] = cube_tmp[32];
        cube[143] = cube_tmp[37];
        cube[144] = cube_tmp[42];
        cube[145] = cube_tmp[47];
        cube[146] = cube_tmp[26];
        cube[147] = cube_tmp[31];
        cube[148] = cube_tmp[36];
        cube[149] = cube_tmp[41];
        cube[150] = cube_tmp[46];
        break;
    }

    case Bw_PRIME: {
        cube[1] = cube_tmp[46];
        cube[2] = cube_tmp[41];
        cube[3] = cube_tmp[36];
        cube[4] = cube_tmp[31];
        cube[5] = cube_tmp[26];
        cube[6] = cube_tmp[47];
        cube[7] = cube_tmp[42];
        cube[8] = cube_tmp[37];
        cube[9] = cube_tmp[32];
        cube[10] = cube_tmp[27];
        cube[26] = cube_tmp[146];
        cube[27] = cube_tmp[141];
        cube[31] = cube_tmp[147];
        cube[32] = cube_tmp[142];
        cube[36] = cube_tmp[148];
        cube[37] = cube_tmp[143];
        cube[41] = cube_tmp[149];
        cube[42] = cube_tmp[144];
        cube[46] = cube_tmp[150];
        cube[47] = cube_tmp[145];
        cube[79] = cube_tmp[6];
        cube[80] = cube_tmp[1];
        cube[84] = cube_tmp[7];
        cube[85] = cube_tmp[2];
        cube[89] = cube_tmp[8];
        cube[90] = cube_tmp[3];
        cube[94] = cube_tmp[9];
        cube[95] = cube_tmp[4];
        cube[99] = cube_tmp[10];
        cube[100] = cube_tmp[5];
        cube[101] = cube_tmp[105];
        cube[102] = cube_tmp[110];
        cube[103] = cube_tmp[115];
        cube[104] = cube_tmp[120];
        cube[105] = cube_tmp[125];
        cube[106] = cube_tmp[104];
        cube[107] = cube_tmp[109];
        cube[108] = cube_tmp[114];
        cube[109] = cube_tmp[119];
        cube[110] = cube_tmp[124];
        cube[111] = cube_tmp[103];
        cube[112] = cube_tmp[108];
        cube[114] = cube_tmp[118];
        cube[115] = cube_tmp[123];
        cube[116] = cube_tmp[102];
        cube[117] = cube_tmp[107];
        cube[118] = cube_tmp[112];
        cube[119] = cube_tmp[117];
        cube[120] = cube_tmp[122];
        cube[121] = cube_tmp[101];
        cube[122] = cube_tmp[106];
        cube[123] = cube_tmp[111];
        cube[124] = cube_tmp[116];
        cube[125] = cube_tmp[121];
        cube[141] = cube_tmp[99];
        cube[142] = cube_tmp[94];
        cube[143] = cube_tmp[89];
        cube[144] = cube_tmp[84];
        cube[145] = cube_tmp[79];
        cube[146] = cube_tmp[100];
        cube[147] = cube_tmp[95];
        cube[148] = cube_tmp[90];
        cube[149] = cube_tmp[85];
        cube[150] = cube_tmp[80];
        break;
    }

    case Bw2: {
        cube[1] = cube_tmp[150];
        cube[2] = cube_tmp[149];
        cube[3] = cube_tmp[148];
        cube[4] = cube_tmp[147];
        cube[5] = cube_tmp[146];
        cube[6] = cube_tmp[145];
        cube[7] = cube_tmp[144];
        cube[8] = cube_tmp[143];
        cube[9] = cube_tmp[142];
        cube[10] = cube_tmp[141];
        cube[26] = cube_tmp[100];
        cube[27] = cube_tmp[99];
        cube[31] = cube_tmp[95];
        cube[32] = cube_tmp[94];
        cube[36] = cube_tmp[90];
        cube[37] = cube_tmp[89];
        cube[41] = cube_tmp[85];
        cube[42] = cube_tmp[84];
        cube[46] = cube_tmp[80];
        cube[47] = cube_tmp[79];
        cube[79] = cube_tmp[47];
        cube[80] = cube_tmp[46];
        cube[84] = cube_tmp[42];
        cube[85] = cube_tmp[41];
        cube[89] = cube_tmp[37];
        cube[90] = cube_tmp[36];
        cube[94] = cube_tmp[32];
        cube[95] = cube_tmp[31];
        cube[99] = cube_tmp[27];
        cube[100] = cube_tmp[26];
        cube[101] = cube_tmp[125];
        cube[102] = cube_tmp[124];
        cube[103] = cube_tmp[123];
        cube[104] = cube_tmp[122];
        cube[105] = cube_tmp[121];
        cube[106] = cube_tmp[120];
        cube[107] = cube_tmp[119];
        cube[108] = cube_tmp[118];
        cube[109] = cube_tmp[117];
        cube[110] = cube_tmp[116];
        cube[111] = cube_tmp[115];
        cube[112] = cube_tmp[114];
        cube[114] = cube_tmp[112];
        cube[115] = cube_tmp[111];
        cube[116] = cube_tmp[110];
        cube[117] = cube_tmp[109];
        cube[118] = cube_tmp[108];
        cube[119] = cube_tmp[107];
        cube[120] = cube_tmp[106];
        cube[121] = cube_tmp[105];
        cube[122] = cube_tmp[104];
        cube[123] = cube_tmp[103];
        cube[124] = cube_tmp[102];
        cube[125] = cube_tmp[101];
        cube[141] = cube_tmp[10];
        cube[142] = cube_tmp[9];
        cube[143] = cube_tmp[8];
        cube[144] = cube_tmp[7];
        cube[145] = cube_tmp[6];
        cube[146] = cube_tmp[5];
        cube[147] = cube_tmp[4];
        cube[148] = cube_tmp[3];
        cube[149] = cube_tmp[2];
        cube[150] = cube_tmp[1];
        break;
    }

    case D: {
        cube[46] = cube_tmp[121];
        cube[47] = cube_tmp[122];
        cube[48] = cube_tmp[123];
        cube[49] = cube_tmp[124];
        cube[50] = cube_tmp[125];
        cube[71] = cube_tmp[46];
        cube[72] = cube_tmp[47];
        cube[73] = cube_tmp[48];
        cube[74] = cube_tmp[49];
        cube[75] = cube_tmp[50];
        cube[96] = cube_tmp[71];
        cube[97] = cube_tmp[72];
        cube[98] = cube_tmp[73];
        cube[99] = cube_tmp[74];
        cube[100] = cube_tmp[75];
        cube[121] = cube_tmp[96];
        cube[122] = cube_tmp[97];
        cube[123] = cube_tmp[98];
        cube[124] = cube_tmp[99];
        cube[125] = cube_tmp[100];
        cube[126] = cube_tmp[146];
        cube[127] = cube_tmp[141];
        cube[128] = cube_tmp[136];
        cube[129] = cube_tmp[131];
        cube[130] = cube_tmp[126];
        cube[131] = cube_tmp[147];
        cube[132] = cube_tmp[142];
        cube[133] = cube_tmp[137];
        cube[134] = cube_tmp[132];
        cube[135] = cube_tmp[127];
        cube[136] = cube_tmp[148];
        cube[137] = cube_tmp[143];
        cube[139] = cube_tmp[133];
        cube[140] = cube_tmp[128];
        cube[141] = cube_tmp[149];
        cube[142] = cube_tmp[144];
        cube[143] = cube_tmp[139];
        cube[144] = cube_tmp[134];
        cube[145] = cube_tmp[129];
        cube[146] = cube_tmp[150];
        cube[147] = cube_tmp[145];
        cube[148] = cube_tmp[140];
        cube[149] = cube_tmp[135];
        cube[150] = cube_tmp[130];
        break;
    }

    case D_PRIME: {
        cube[46] = cube_tmp[71];
        cube[47] = cube_tmp[72];
        cube[48] = cube_tmp[73];
        cube[49] = cube_tmp[74];
        cube[50] = cube_tmp[75];
        cube[71] = cube_tmp[96];
        cube[72] = cube_tmp[97];
        cube[73] = cube_tmp[98];
        cube[74] = cube_tmp[99];
        cube[75] = cube_tmp[100];
        cube[96] = cube_tmp[121];
        cube[97] = cube_tmp[122];
        cube[98] = cube_tmp[123];
        cube[99] = cube_tmp[124];
        cube[100] = cube_tmp[125];
        cube[121] = cube_tmp[46];
        cube[122] = cube_tmp[47];
        cube[123] = cube_tmp[48];
        cube[124] = cube_tmp[49];
        cube[125] = cube_tmp[50];
        cube[126] = cube_tmp[130];
        cube[127] = cube_tmp[135];
        cube[128] = cube_tmp[140];
        cube[129] = cube_tmp[145];
        cube[130] = cube_tmp[150];
        cube[131] = cube_tmp[129];
        cube[132] = cube_tmp[134];
        cube[133] = cube_tmp[139];
        cube[134] = cube_tmp[144];
        cube[135] = cube_tmp[149];
        cube[136] = cube_tmp[128];
        cube[137] = cube_tmp[133];
        cube[139] = cube_tmp[143];
        cube[140] = cube_tmp[148];
        cube[141] = cube_tmp[127];
        cube[142] = cube_tmp[132];
        cube[143] = cube_tmp[137];
        cube[144] = cube_tmp[142];
        cube[145] = cube_tmp[147];
        cube[146] = cube_tmp[126];
        cube[147] = cube_tmp[131];
        cube[148] = cube_tmp[136];
        cube[149] = cube_tmp[141];
        cube[150] = cube_tmp[146];
        break;
    }

    case D2: {
        cube[46] = cube_tmp[96];
        cube[47] = cube_tmp[97];
        cube[48] = cube_tmp[98];
        cube[49] = cube_tmp[99];
        cube[50] = cube_tmp[100];
        cube[71] = cube_tmp[121];
        cube[72] = cube_tmp[122];
        cube[73] = cube_tmp[123];
        cube[74] = cube_tmp[124];
        cube[75] = cube_tmp[125];
        cube[96] = cube_tmp[46];
        cube[97] = cube_tmp[47];
        cube[98] = cube_tmp[48];
        cube[99] = cube_tmp[49];
        cube[100] = cube_tmp[50];
        cube[121] = cube_tmp[71];
        cube[122] = cube_tmp[72];
        cube[123] = cube_tmp[73];
        cube[124] = cube_tmp[74];
        cube[125] = cube_tmp[75];
        cube[126] = cube_tmp[150];
        cube[127] = cube_tmp[149];
        cube[128] = cube_tmp[148];
        cube[129] = cube_tmp[147];
        cube[130] = cube_tmp[146];
        cube[131] = cube_tmp[145];
        cube[132] = cube_tmp[144];
        cube[133] = cube_tmp[143];
        cube[134] = cube_tmp[142];
        cube[135] = cube_tmp[141];
        cube[136] = cube_tmp[140];
        cube[137] = cube_tmp[139];
        cube[139] = cube_tmp[137];
        cube[140] = cube_tmp[136];
        cube[141] = cube_tmp[135];
        cube[142] = cube_tmp[134];
        cube[143] = cube_tmp[133];
        cube[144] = cube_tmp[132];
        cube[145] = cube_tmp[131];
        cube[146] = cube_tmp[130];
        cube[147] = cube_tmp[129];
        cube[148] = cube_tmp[128];
        cube[149] = cube_tmp[127];
        cube[150] = cube_tmp[126];
        break;
    }

    case Dw: {
        cube[41] = cube_tmp[116];
        cube[42] = cube_tmp[117];
        cube[43] = cube_tmp[118];
        cube[44] = cube_tmp[119];
        cube[45] = cube_tmp[120];
        cube[46] = cube_tmp[121];
        cube[47] = cube_tmp[122];
        cube[48] = cube_tmp[123];
        cube[49] = cube_tmp[124];
        cube[50] = cube_tmp[125];
        cube[66] = cube_tmp[41];
        cube[67] = cube_tmp[42];
        cube[68] = cube_tmp[43];
        cube[69] = cube_tmp[44];
        cube[70] = cube_tmp[45];
        cube[71] = cube_tmp[46];
        cube[72] = cube_tmp[47];
        cube[73] = cube_tmp[48];
        cube[74] = cube_tmp[49];
        cube[75] = cube_tmp[50];
        cube[91] = cube_tmp[66];
        cube[92] = cube_tmp[67];
        cube[93] = cube_tmp[68];
        cube[94] = cube_tmp[69];
        cube[95] = cube_tmp[70];
        cube[96] = cube_tmp[71];
        cube[97] = cube_tmp[72];
        cube[98] = cube_tmp[73];
        cube[99] = cube_tmp[74];
        cube[100] = cube_tmp[75];
        cube[116] = cube_tmp[91];
        cube[117] = cube_tmp[92];
        cube[118] = cube_tmp[93];
        cube[119] = cube_tmp[94];
        cube[120] = cube_tmp[95];
        cube[121] = cube_tmp[96];
        cube[122] = cube_tmp[97];
        cube[123] = cube_tmp[98];
        cube[124] = cube_tmp[99];
        cube[125] = cube_tmp[100];
        cube[126] = cube_tmp[146];
        cube[127] = cube_tmp[141];
        cube[128] = cube_tmp[136];
        cube[129] = cube_tmp[131];
        cube[130] = cube_tmp[126];
        cube[131] = cube_tmp[147];
        cube[132] = cube_tmp[142];
        cube[133] = cube_tmp[137];
        cube[134] = cube_tmp[132];
        cube[135] = cube_tmp[127];
        cube[136] = cube_tmp[148];
        cube[137] = cube_tmp[143];
        cube[139] = cube_tmp[133];
        cube[140] = cube_tmp[128];
        cube[141] = cube_tmp[149];
        cube[142] = cube_tmp[144];
        cube[143] = cube_tmp[139];
        cube[144] = cube_tmp[134];
        cube[145] = cube_tmp[129];
        cube[146] = cube_tmp[150];
        cube[147] = cube_tmp[145];
        cube[148] = cube_tmp[140];
        cube[149] = cube_tmp[135];
        cube[150] = cube_tmp[130];
        break;
    }

    case Dw_PRIME: {
        cube[41] = cube_tmp[66];
        cube[42] = cube_tmp[67];
        cube[43] = cube_tmp[68];
        cube[44] = cube_tmp[69];
        cube[45] = cube_tmp[70];
        cube[46] = cube_tmp[71];
        cube[47] = cube_tmp[72];
        cube[48] = cube_tmp[73];
        cube[49] = cube_tmp[74];
        cube[50] = cube_tmp[75];
        cube[66] = cube_tmp[91];
        cube[67] = cube_tmp[92];
        cube[68] = cube_tmp[93];
        cube[69] = cube_tmp[94];
        cube[70] = cube_tmp[95];
        cube[71] = cube_tmp[96];
        cube[72] = cube_tmp[97];
        cube[73] = cube_tmp[98];
        cube[74] = cube_tmp[99];
        cube[75] = cube_tmp[100];
        cube[91] = cube_tmp[116];
        cube[92] = cube_tmp[117];
        cube[93] = cube_tmp[118];
        cube[94] = cube_tmp[119];
        cube[95] = cube_tmp[120];
        cube[96] = cube_tmp[121];
        cube[97] = cube_tmp[122];
        cube[98] = cube_tmp[123];
        cube[99] = cube_tmp[124];
        cube[100] = cube_tmp[125];
        cube[116] = cube_tmp[41];
        cube[117] = cube_tmp[42];
        cube[118] = cube_tmp[43];
        cube[119] = cube_tmp[44];
        cube[120] = cube_tmp[45];
        cube[121] = cube_tmp[46];
        cube[122] = cube_tmp[47];
        cube[123] = cube_tmp[48];
        cube[124] = cube_tmp[49];
        cube[125] = cube_tmp[50];
        cube[126] = cube_tmp[130];
        cube[127] = cube_tmp[135];
        cube[128] = cube_tmp[140];
        cube[129] = cube_tmp[145];
        cube[130] = cube_tmp[150];
        cube[131] = cube_tmp[129];
        cube[132] = cube_tmp[134];
        cube[133] = cube_tmp[139];
        cube[134] = cube_tmp[144];
        cube[135] = cube_tmp[149];
        cube[136] = cube_tmp[128];
        cube[137] = cube_tmp[133];
        cube[139] = cube_tmp[143];
        cube[140] = cube_tmp[148];
        cube[141] = cube_tmp[127];
        cube[142] = cube_tmp[132];
        cube[143] = cube_tmp[137];
        cube[144] = cube_tmp[142];
        cube[145] = cube_tmp[147];
        cube[146] = cube_tmp[126];
        cube[147] = cube_tmp[131];
        cube[148] = cube_tmp[136];
        cube[149] = cube_tmp[141];
        cube[150] = cube_tmp[146];
        break;
    }

    case Dw2: {
        cube[41] = cube_tmp[91];
        cube[42] = cube_tmp[92];
        cube[43] = cube_tmp[93];
        cube[44] = cube_tmp[94];
        cube[45] = cube_tmp[95];
        cube[46] = cube_tmp[96];
        cube[47] = cube_tmp[97];
        cube[48] = cube_tmp[98];
        cube[49] = cube_tmp[99];
        cube[50] = cube_tmp[100];
        cube[66] = cube_tmp[116];
        cube[67] = cube_tmp[117];
        cube[68] = cube_tmp[118];
        cube[69] = cube_tmp[119];
        cube[70] = cube_tmp[120];
        cube[71] = cube_tmp[121];
        cube[72] = cube_tmp[122];
        cube[73] = cube_tmp[123];
        cube[74] = cube_tmp[124];
        cube[75] = cube_tmp[125];
        cube[91] = cube_tmp[41];
        cube[92] = cube_tmp[42];
        cube[93] = cube_tmp[43];
        cube[94] = cube_tmp[44];
        cube[95] = cube_tmp[45];
        cube[96] = cube_tmp[46];
        cube[97] = cube_tmp[47];
        cube[98] = cube_tmp[48];
        cube[99] = cube_tmp[49];
        cube[100] = cube_tmp[50];
        cube[116] = cube_tmp[66];
        cube[117] = cube_tmp[67];
        cube[118] = cube_tmp[68];
        cube[119] = cube_tmp[69];
        cube[120] = cube_tmp[70];
        cube[121] = cube_tmp[71];
        cube[122] = cube_tmp[72];
        cube[123] = cube_tmp[73];
        cube[124] = cube_tmp[74];
        cube[125] = cube_tmp[75];
        cube[126] = cube_tmp[150];
        cube[127] = cube_tmp[149];
        cube[128] = cube_tmp[148];
        cube[129] = cube_tmp[147];
        cube[130] = cube_tmp[146];
        cube[131] = cube_tmp[145];
        cube[132] = cube_tmp[144];
        cube[133] = cube_tmp[143];
        cube[134] = cube_tmp[142];
        cube[135] = cube_tmp[141];
        cube[136] = cube_tmp[140];
        cube[137] = cube_tmp[139];
        cube[139] = cube_tmp[137];
        cube[140] = cube_tmp[136];
        cube[141] = cube_tmp[135];
        cube[142] = cube_tmp[134];
        cube[143] = cube_tmp[133];
        cube[144] = cube_tmp[132];
        cube[145] = cube_tmp[131];
        cube[146] = cube_tmp[130];
        cube[147] = cube_tmp[129];
        cube[148] = cube_tmp[128];
        cube[149] = cube_tmp[127];
        cube[150] = cube_tmp[126];
        break;
    }


    default:
        printf("ERROR: invalid move %d\n", move);
        exit(1);
    }
}
            
void
rotate_555_centers(char *cube, char *cube_tmp, int array_size, move_type move)
{
    /* This was contructed using utils/rotate-printer.py */
    (void)cube_tmp;
    (void)array_size;

    switch (move) {
    case U: {
        char c7 = cube[7], c8 = cube[8], c9 = cube[9], c12 = cube[12],
             c14 = cube[14], c17 = cube[17], c18 = cube[18], c19 = cube[19];
        cube[7] = c17;
        cube[8] = c12;
        cube[9] = c7;
        cube[12] = c18;
        cube[14] = c8;
        cube[17] = c19;
        cube[18] = c14;
        cube[19] = c9;
        break;
    }

    case U_PRIME: {
        char c7 = cube[7], c8 = cube[8], c9 = cube[9], c12 = cube[12],
             c14 = cube[14], c17 = cube[17], c18 = cube[18], c19 = cube[19];
        cube[7] = c9;
        cube[8] = c14;
        cube[9] = c19;
        cube[12] = c8;
        cube[14] = c18;
        cube[17] = c7;
        cube[18] = c12;
        cube[19] = c17;
        break;
    }

    case U2: {
        char c7 = cube[7], c8 = cube[8], c9 = cube[9], c12 = cube[12],
             c14 = cube[14], c17 = cube[17], c18 = cube[18], c19 = cube[19];
        cube[7] = c19;
        cube[8] = c18;
        cube[9] = c17;
        cube[12] = c14;
        cube[14] = c12;
        cube[17] = c9;
        cube[18] = c8;
        cube[19] = c7;
        break;
    }

    case Uw: {
        char c7 = cube[7], c8 = cube[8], c9 = cube[9], c12 = cube[12],
             c14 = cube[14], c17 = cube[17], c18 = cube[18], c19 = cube[19],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c57 = cube[57],
             c58 = cube[58], c59 = cube[59], c82 = cube[82], c83 = cube[83],
             c84 = cube[84], c107 = cube[107], c108 = cube[108], c109 = cube[109];
        cube[7] = c17;
        cube[8] = c12;
        cube[9] = c7;
        cube[12] = c18;
        cube[14] = c8;
        cube[17] = c19;
        cube[18] = c14;
        cube[19] = c9;
        cube[32] = c57;
        cube[33] = c58;
        cube[34] = c59;
        cube[57] = c82;
        cube[58] = c83;
        cube[59] = c84;
        cube[82] = c107;
        cube[83] = c108;
        cube[84] = c109;
        cube[107] = c32;
        cube[108] = c33;
        cube[109] = c34;
        break;
    }

    case Uw_PRIME: {
        char c7 = cube[7], c8 = cube[8], c9 = cube[9], c12 = cube[12],
             c14 = cube[14], c17 = cube[17], c18 = cube[18], c19 = cube[19],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c57 = cube[57],
             c58 = cube[58], c59 = cube[59], c82 = cube[82], c83 = cube[83],
             c84 = cube[84], c107 = cube[107], c108 = cube[108], c109 = cube[109];
        cube[7] = c9;
        cube[8] = c14;
        cube[9] = c19;
        cube[12] = c8;
        cube[14] = c18;
        cube[17] = c7;
        cube[18] = c12;
        cube[19] = c17;
        cube[32] = c107;
        cube[33] = c108;
        cube[34] = c109;
        cube[57] = c32;
        cube[58] = c33;
        cube[59] = c34;
        cube[82] = c57;
        cube[83] = c58;
        cube[84] = c59;
        cube[107] = c82;
        cube[108] = c83;
        cube[109] = c84;
        break;
    }

    case Uw2: {
        char c7 = cube[7], c8 = cube[8], c9 = cube[9], c12 = cube[12],
             c14 = cube[14], c17 = cube[17], c18 = cube[18], c19 = cube[19],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c57 = cube[57],
             c58 = cube[58], c59 = cube[59], c82 = cube[82], c83 = cube[83],
             c84 = cube[84], c107 = cube[107], c108 = cube[108], c109 = cube[109];
        cube[7] = c19;
        cube[8] = c18;
        cube[9] = c17;
        cube[12] = c14;
        cube[14] = c12;
        cube[17] = c9;
        cube[18] = c8;
        cube[19] = c7;
        cube[32] = c82;
        cube[33] = c83;
        cube[34] = c84;
        cube[57] = c107;
        cube[58] = c108;
        cube[59] = c109;
        cube[82] = c32;
        cube[83] = c33;
        cube[84] = c34;
        cube[107] = c57;
        cube[108] = c58;
        cube[109] = c59;
        break;
    }

    case L: {
        char c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c39 = cube[39], c42 = cube[42], c43 = cube[43], c44 = cube[44];
        cube[32] = c42;
        cube[33] = c37;
        cube[34] = c32;
        cube[37] = c43;
        cube[39] = c33;
        cube[42] = c44;
        cube[43] = c39;
        cube[44] = c34;
        break;
    }

    case L_PRIME: {
        char c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c39 = cube[39], c42 = cube[42], c43 = cube[43], c44 = cube[44];
        cube[32] = c34;
        cube[33] = c39;
        cube[34] = c44;
        cube[37] = c33;
        cube[39] = c43;
        cube[42] = c32;
        cube[43] = c37;
        cube[44] = c42;
        break;
    }

    case L2: {
        char c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c39 = cube[39], c42 = cube[42], c43 = cube[43], c44 = cube[44];
        cube[32] = c44;
        cube[33] = c43;
        cube[34] = c42;
        cube[37] = c39;
        cube[39] = c37;
        cube[42] = c34;
        cube[43] = c33;
        cube[44] = c32;
        break;
    }

    case Lw: {
        char c7 = cube[7], c12 = cube[12], c17 = cube[17], c32 = cube[32],
             c33 = cube[33], c34 = cube[34], c37 = cube[37], c39 = cube[39],
             c42 = cube[42], c43 = cube[43], c44 = cube[44], c57 = cube[57],
             c62 = cube[62], c67 = cube[67], c109 = cube[109], c114 = cube[114],
             c119 = cube[119], c132 = cube[132], c137 = cube[137], c142 = cube[142];
        cube[7] = c119;
        cube[12] = c114;
        cube[17] = c109;
        cube[32] = c42;
        cube[33] = c37;
        cube[34] = c32;
        cube[37] = c43;
        cube[39] = c33;
        cube[42] = c44;
        cube[43] = c39;
        cube[44] = c34;
        cube[57] = c7;
        cube[62] = c12;
        cube[67] = c17;
        cube[109] = c142;
        cube[114] = c137;
        cube[119] = c132;
        cube[132] = c57;
        cube[137] = c62;
        cube[142] = c67;
        break;
    }

    case Lw_PRIME: {
        char c7 = cube[7], c12 = cube[12], c17 = cube[17], c32 = cube[32],
             c33 = cube[33], c34 = cube[34], c37 = cube[37], c39 = cube[39],
             c42 = cube[42], c43 = cube[43], c44 = cube[44], c57 = cube[57],
             c62 = cube[62], c67 = cube[67], c109 = cube[109], c114 = cube[114],
             c119 = cube[119], c132 = cube[132], c137 = cube[137], c142 = cube[142];
        cube[7] = c57;
        cube[12] = c62;
        cube[17] = c67;
        cube[32] = c34;
        cube[33] = c39;
        cube[34] = c44;
        cube[37] = c33;
        cube[39] = c43;
        cube[42] = c32;
        cube[43] = c37;
        cube[44] = c42;
        cube[57] = c132;
        cube[62] = c137;
        cube[67] = c142;
        cube[109] = c17;
        cube[114] = c12;
        cube[119] = c7;
        cube[132] = c119;
        cube[137] = c114;
        cube[142] = c109;
        break;
    }

    case Lw2: {
        char c7 = cube[7], c12 = cube[12], c17 = cube[17], c32 = cube[32],
             c33 = cube[33], c34 = cube[34], c37 = cube[37], c39 = cube[39],
             c42 = cube[42], c43 = cube[43], c44 = cube[44], c57 = cube[57],
             c62 = cube[62], c67 = cube[67], c109 = cube[109], c114 = cube[114],
             c119 = cube[119], c132 = cube[132], c137 = cube[137], c142 = cube[142];
        cube[7] = c132;
        cube[12] = c137;
        cube[17] = c142;
        cube[32] = c44;
        cube[33] = c43;
        cube[34] = c42;
        cube[37] = c39;
        cube[39] = c37;
        cube[42] = c34;
        cube[43] = c33;
        cube[44] = c32;
        cube[57] = c119;
        cube[62] = c114;
        cube[67] = c109;
        cube[109] = c67;
        cube[114] = c62;
        cube[119] = c57;
        cube[132] = c7;
        cube[137] = c12;
        cube[142] = c17;
        break;
    }

    case F: {
        char c57 = cube[57], c58 = cube[58], c59 = cube[59], c62 = cube[62],
             c64 = cube[64], c67 = cube[67], c68 = cube[68], c69 = cube[69];
        cube[57] = c67;
        cube[58] = c62;
        cube[59] = c57;
        cube[62] = c68;
        cube[64] = c58;
        cube[67] = c69;
        cube[68] = c64;
        cube[69] = c59;
        break;
    }

    case F_PRIME: {
        char c57 = cube[57], c58 = cube[58], c59 = cube[59], c62 = cube[62],
             c64 = cube[64], c67 = cube[67], c68 = cube[68], c69 = cube[69];
        cube[57] = c59;
        cube[58] = c64;
        cube[59] = c69;
        cube[62] = c58;
        cube[64] = c68;
        cube[67] = c57;
        cube[68] = c62;
        cube[69] = c67;
        break;
    }

    case F2: {
        char c57 = cube[57], c58 = cube[58], c59 = cube[59], c62 = cube[62],
             c64 = cube[64], c67 = cube[67], c68 = cube[68], c69 = cube[69];
        cube[57] = c69;
        cube[58] = c68;
        cube[59] = c67;
        cube[62] = c64;
        cube[64] = c62;
        cube[67] = c59;
        cube[68] = c58;
        cube[69] = c57;
        break;
    }

    case Fw: {
        char c17 = cube[17], c18 = cube[18], c19 = cube[19], c34 = cube[34],
             c39 = cube[39], c44 = cube[44], c57 = cube[57], c58 = cube[58],
             c59 = cube[59], c62 = cube[62], c64 = cube[64], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c82 = cube[82], c87 = cube[87],
             c92 = cube[92], c132 = cube[132], c133 = cube[133], c134 = cube[134];
        cube[17] = c44;
        cube[18] = c39;
        cube[19] = c34;
        cube[34] = c132;
        cube[39] = c133;
        cube[44] = c134;
        cube[57] = c67;
        cube[58] = c62;
        cube[59] = c57;
        cube[62] = c68;
        cube[64] = c58;
        cube[67] = c69;
        cube[68] = c64;
        cube[69] = c59;
        cube[82] = c17;
        cube[87] = c18;
        cube[92] = c19;
        cube[132] = c92;
        cube[133] = c87;
        cube[134] = c82;
        break;
    }

    case Fw_PRIME: {
        char c17 = cube[17], c18 = cube[18], c19 = cube[19], c34 = cube[34],
             c39 = cube[39], c44 = cube[44], c57 = cube[57], c58 = cube[58],
             c59 = cube[59], c62 = cube[62], c64 = cube[64], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c82 = cube[82], c87 = cube[87],
             c92 = cube[92], c132 = cube[132], c133 = cube[133], c134 = cube[134];
        cube[17] = c82;
        cube[18] = c87;
        cube[19] = c92;
        cube[34] = c19;
        cube[39] = c18;
        cube[44] = c17;
        cube[57] = c59;
        cube[58] = c64;
        cube[59] = c69;
        cube[62] = c58;
        cube[64] = c68;
        cube[67] = c57;
        cube[68] = c62;
        cube[69] = c67;
        cube[82] = c134;
        cube[87] = c133;
        cube[92] = c132;
        cube[132] = c34;
        cube[133] = c39;
        cube[134] = c44;
        break;
    }

    case Fw2: {
        char c17 = cube[17], c18 = cube[18], c19 = cube[19], c34 = cube[34],
             c39 = cube[39], c44 = cube[44], c57 = cube[57], c58 = cube[58],
             c59 = cube[59], c62 = cube[62], c64 = cube[64], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c82 = cube[82], c87 = cube[87],
             c92 = cube[92], c132 = cube[132], c133 = cube[133], c134 = cube[134];
        cube[17] = c134;
        cube[18] = c133;
        cube[19] = c132;
        cube[34] = c92;
        cube[39] = c87;
        cube[44] = c82;
        cube[57] = c69;
        cube[58] = c68;
        cube[59] = c67;
        cube[62] = c64;
        cube[64] = c62;
        cube[67] = c59;
        cube[68] = c58;
        cube[69] = c57;
        cube[82] = c44;
        cube[87] = c39;
        cube[92] = c34;
        cube[132] = c19;
        cube[133] = c18;
        cube[134] = c17;
        break;
    }

    case R: {
        char c82 = cube[82], c83 = cube[83], c84 = cube[84], c87 = cube[87],
             c89 = cube[89], c92 = cube[92], c93 = cube[93], c94 = cube[94];
        cube[82] = c92;
        cube[83] = c87;
        cube[84] = c82;
        cube[87] = c93;
        cube[89] = c83;
        cube[92] = c94;
        cube[93] = c89;
        cube[94] = c84;
        break;
    }

    case R_PRIME: {
        char c82 = cube[82], c83 = cube[83], c84 = cube[84], c87 = cube[87],
             c89 = cube[89], c92 = cube[92], c93 = cube[93], c94 = cube[94];
        cube[82] = c84;
        cube[83] = c89;
        cube[84] = c94;
        cube[87] = c83;
        cube[89] = c93;
        cube[92] = c82;
        cube[93] = c87;
        cube[94] = c92;
        break;
    }

    case R2: {
        char c82 = cube[82], c83 = cube[83], c84 = cube[84], c87 = cube[87],
             c89 = cube[89], c92 = cube[92], c93 = cube[93], c94 = cube[94];
        cube[82] = c94;
        cube[83] = c93;
        cube[84] = c92;
        cube[87] = c89;
        cube[89] = c87;
        cube[92] = c84;
        cube[93] = c83;
        cube[94] = c82;
        break;
    }

    case Rw: {
        char c9 = cube[9], c14 = cube[14], c19 = cube[19], c59 = cube[59],
             c64 = cube[64], c69 = cube[69], c82 = cube[82], c83 = cube[83],
             c84 = cube[84], c87 = cube[87], c89 = cube[89], c92 = cube[92],
             c93 = cube[93], c94 = cube[94], c107 = cube[107], c112 = cube[112],
             c117 = cube[117], c134 = cube[134], c139 = cube[139], c144 = cube[144];
        cube[9] = c59;
        cube[14] = c64;
        cube[19] = c69;
        cube[59] = c134;
        cube[64] = c139;
        cube[69] = c144;
        cube[82] = c92;
        cube[83] = c87;
        cube[84] = c82;
        cube[87] = c93;
        cube[89] = c83;
        cube[92] = c94;
        cube[93] = c89;
        cube[94] = c84;
        cube[107] = c19;
        cube[112] = c14;
        cube[117] = c9;
        cube[134] = c117;
        cube[139] = c112;
        cube[144] = c107;
        break;
    }

    case Rw_PRIME: {
        char c9 = cube[9], c14 = cube[14], c19 = cube[19], c59 = cube[59],
             c64 = cube[64], c69 = cube[69], c82 = cube[82], c83 = cube[83],
             c84 = cube[84], c87 = cube[87], c89 = cube[89], c92 = cube[92],
             c93 = cube[93], c94 = cube[94], c107 = cube[107], c112 = cube[112],
             c117 = cube[117], c134 = cube[134], c139 = cube[139], c144 = cube[144];
        cube[9] = c117;
        cube[14] = c112;
        cube[19] = c107;
        cube[59] = c9;
        cube[64] = c14;
        cube[69] = c19;
        cube[82] = c84;
        cube[83] = c89;
        cube[84] = c94;
        cube[87] = c83;
        cube[89] = c93;
        cube[92] = c82;
        cube[93] = c87;
        cube[94] = c92;
        cube[107] = c144;
        cube[112] = c139;
        cube[117] = c134;
        cube[134] = c59;
        cube[139] = c64;
        cube[144] = c69;
        break;
    }

    case Rw2: {
        char c9 = cube[9], c14 = cube[14], c19 = cube[19], c59 = cube[59],
             c64 = cube[64], c69 = cube[69], c82 = cube[82], c83 = cube[83],
             c84 = cube[84], c87 = cube[87], c89 = cube[89], c92 = cube[92],
             c93 = cube[93], c94 = cube[94], c107 = cube[107], c112 = cube[112],
             c117 = cube[117], c134 = cube[134], c139 = cube[139], c144 = cube[144];
        cube[9] = c134;
        cube[14] = c139;
        cube[19] = c144;
        cube[59] = c117;
        cube[64] = c112;
        cube[69] = c107;
        cube[82] = c94;
        cube[83] = c93;
        cube[84] = c92;
        cube[87] = c89;
        cube[89] = c87;
        cube[92] = c84;
        cube[93] = c83;
        cube[94] = c82;
        cube[107] = c69;
        cube[112] = c64;
        cube[117] = c59;
        cube[134] = c9;
        cube[139] = c14;
        cube[144] = c19;
        break;
    }

    case B: {
        char c107 = cube[107], c108 = cube[108], c109 = cube[109], c112 = cube[112],
             c114 = cube[114], c117 = cube[117], c118 = cube[118], c119 = cube[119];
        cube[107] = c117;
        cube[108] = c112;
        cube[109] = c107;
        cube[112] = c118;
        cube[114] = c108;
        cube[117] = c119;
        cube[118] = c114;
        cube[119] = c109;
        break;
    }

    case B_PRIME: {
        char c107 = cube[107], c108 = cube[108], c109 = cube[109], c112 = cube[112],
             c114 = cube[114], c117 = cube[117], c118 = cube[118], c119 = cube[119];
        cube[107] = c109;
        cube[108] = c114;
        cube[109] = c119;
        cube[112] = c108;
        cube[114] = c118;
        cube[117] = c107;
        cube[118] = c112;
        cube[119] = c117;
        break;
    }

    case B2: {
        char c107 = cube[107], c108 = cube[108], c109 = cube[109], c112 = cube[112],
             c114 = cube[114], c117 = cube[117], c118 = cube[118], c119 = cube[119];
        cube[107] = c119;
        cube[108] = c118;
        cube[109] = c117;
        cube[112] = c114;
        cube[114] = c112;
        cube[117] = c109;
        cube[118] = c108;
        cube[119] = c107;
        break;
    }

    case Bw: {
        char c7 = cube[7], c8 = cube[8], c9 = cube[9], c32 = cube[32],
             c37 = cube[37], c42 = cube[42], c84 = cube[84], c89 = cube[89],
             c94 = cube[94], c107 = cube[107], c108 = cube[108], c109 = cube[109],
             c112 = cube[112], c114 = cube[114], c117 = cube[117], c118 = cube[118],
             c119 = cube[119], c142 = cube[142], c143 = cube[143], c144 = cube[144];
        cube[7] = c84;
        cube[8] = c89;
        cube[9] = c94;
        cube[32] = c9;
        cube[37] = c8;
        cube[42] = c7;
        cube[84] = c144;
        cube[89] = c143;
        cube[94] = c142;
        cube[107] = c117;
        cube[108] = c112;
        cube[109] = c107;
        cube[112] = c118;
        cube[114] = c108;
        cube[117] = c119;
        cube[118] = c114;
        cube[119] = c109;
        cube[142] = c32;
        cube[143] = c37;
        cube[144] = c42;
        break;
    }

    case Bw_PRIME: {
        char c7 = cube[7], c8 = cube[8], c9 = cube[9], c32 = cube[32],
             c37 = cube[37], c42 = cube[42], c84 = cube[84], c89 = cube[89],
             c94 = cube[94], c107 = cube[107], c108 = cube[108], c109 = cube[109],
             c112 = cube[112], c114 = cube[114], c117 = cube[117], c118 = cube[118],
             c119 = cube[119], c142 = cube[142], c143 = cube[143], c144 = cube[144];
        cube[7] = c42;
        cube[8] = c37;
        cube[9] = c32;
        cube[32] = c142;
        cube[37] = c143;
        cube[42] = c144;
        cube[84] = c7;
        cube[89] = c8;
        cube[94] = c9;
        cube[107] = c109;
        cube[108] = c114;
        cube[109] = c119;
        cube[112] = c108;
        cube[114] = c118;
        cube[117] = c107;
        cube[118] = c112;
        cube[119] = c117;
        cube[142] = c94;
        cube[143] = c89;
        cube[144] = c84;
        break;
    }

    case Bw2: {
        char c7 = cube[7], c8 = cube[8], c9 = cube[9], c32 = cube[32],
             c37 = cube[37], c42 = cube[42], c84 = cube[84], c89 = cube[89],
             c94 = cube[94], c107 = cube[107], c108 = cube[108], c109 = cube[109],
             c112 = cube[112], c114 = cube[114], c117 = cube[117], c118 = cube[118],
             c119 = cube[119], c142 = cube[142], c143 = cube[143], c144 = cube[144];
        cube[7] = c144;
        cube[8] = c143;
        cube[9] = c142;
        cube[32] = c94;
        cube[37] = c89;
        cube[42] = c84;
        cube[84] = c42;
        cube[89] = c37;
        cube[94] = c32;
        cube[107] = c119;
        cube[108] = c118;
        cube[109] = c117;
        cube[112] = c114;
        cube[114] = c112;
        cube[117] = c109;
        cube[118] = c108;
        cube[119] = c107;
        cube[142] = c9;
        cube[143] = c8;
        cube[144] = c7;
        break;
    }

    case D: {
        char c132 = cube[132], c133 = cube[133], c134 = cube[134], c137 = cube[137],
             c139 = cube[139], c142 = cube[142], c143 = cube[143], c144 = cube[144];
        cube[132] = c142;
        cube[133] = c137;
        cube[134] = c132;
        cube[137] = c143;
        cube[139] = c133;
        cube[142] = c144;
        cube[143] = c139;
        cube[144] = c134;
        break;
    }

    case D_PRIME: {
        char c132 = cube[132], c133 = cube[133], c134 = cube[134], c137 = cube[137],
             c139 = cube[139], c142 = cube[142], c143 = cube[143], c144 = cube[144];
        cube[132] = c134;
        cube[133] = c139;
        cube[134] = c144;
        cube[137] = c133;
        cube[139] = c143;
        cube[142] = c132;
        cube[143] = c137;
        cube[144] = c142;
        break;
    }

    case D2: {
        char c132 = cube[132], c133 = cube[133], c134 = cube[134], c137 = cube[137],
             c139 = cube[139], c142 = cube[142], c143 = cube[143], c144 = cube[144];
        cube[132] = c144;
        cube[133] = c143;
        cube[134] = c142;
        cube[137] = c139;
        cube[139] = c137;
        cube[142] = c134;
        cube[143] = c133;
        cube[144] = c132;
        break;
    }

    case Dw: {
        char c42 = cube[42], c43 = cube[43], c44 = cube[44], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c92 = cube[92], c93 = cube[93],
             c94 = cube[94], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c132 = cube[132], c133 = cube[133], c134 = cube[134], c137 = cube[137],
             c139 = cube[139], c142 = cube[142], c143 = cube[143], c144 = cube[144];
        cube[42] = c117;
        cube[43] = c118;
        cube[44] = c119;
        cube[67] = c42;
        cube[68] = c43;
        cube[69] = c44;
        cube[92] = c67;
        cube[93] = c68;
        cube[94] = c69;
        cube[117] = c92;
        cube[118] = c93;
        cube[119] = c94;
        cube[132] = c142;
        cube[133] = c137;
        cube[134] = c132;
        cube[137] = c143;
        cube[139] = c133;
        cube[142] = c144;
        cube[143] = c139;
        cube[144] = c134;
        break;
    }

    case Dw_PRIME: {
        char c42 = cube[42], c43 = cube[43], c44 = cube[44], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c92 = cube[92], c93 = cube[93],
             c94 = cube[94], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c132 = cube[132], c133 = cube[133], c134 = cube[134], c137 = cube[137],
             c139 = cube[139], c142 = cube[142], c143 = cube[143], c144 = cube[144];
        cube[42] = c67;
        cube[43] = c68;
        cube[44] = c69;
        cube[67] = c92;
        cube[68] = c93;
        cube[69] = c94;
        cube[92] = c117;
        cube[93] = c118;
        cube[94] = c119;
        cube[117] = c42;
        cube[118] = c43;
        cube[119] = c44;
        cube[132] = c134;
        cube[133] = c139;
        cube[134] = c144;
        cube[137] = c133;
        cube[139] = c143;
        cube[142] = c132;
        cube[143] = c137;
        cube[144] = c142;
        break;
    }

    case Dw2: {
        char c42 = cube[42], c43 = cube[43], c44 = cube[44], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c92 = cube[92], c93 = cube[93],
             c94 = cube[94], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c132 = cube[132], c133 = cube[133], c134 = cube[134], c137 = cube[137],
             c139 = cube[139], c142 = cube[142], c143 = cube[143], c144 = cube[144];
        cube[42] = c92;
        cube[43] = c93;
        cube[44] = c94;
        cube[67] = c117;
        cube[68] = c118;
        cube[69] = c119;
        cube[92] = c42;
        cube[93] = c43;
        cube[94] = c44;
        cube[117] = c67;
        cube[118] = c68;
        cube[119] = c69;
        cube[132] = c144;
        cube[133] = c143;
        cube[134] = c142;
        cube[137] = c139;
        cube[139] = c137;
        cube[142] = c134;
        cube[143] = c133;
        cube[144] = c132;
        break;
    }


    default:
        printf("ERROR: invalid move %d\n", move);
        exit(1);
    }
}
            
void
rotate_666(char *cube, char *cube_tmp, int array_size, move_type move)
{
    /* This was contructed using utils/rotate-printer.py */
    memcpy(cube_tmp, cube, sizeof(char) * array_size);

    switch (move) {
    case U: {
        cube[1] = cube_tmp[31];
        cube[2] = cube_tmp[25];
        cube[3] = cube_tmp[19];
        cube[4] = cube_tmp[13];
        cube[5] = cube_tmp[7];
        cube[6] = cube_tmp[1];
        cube[7] = cube_tmp[32];
        cube[8] = cube_tmp[26];
        cube[9] = cube_tmp[20];
        cube[10] = cube_tmp[14];
        cube[11] = cube_tmp[8];
        cube[12] = cube_tmp[2];
        cube[13] = cube_tmp[33];
        cube[14] = cube_tmp[27];
        cube[15] = cube_tmp[21];
        cube[16] = cube_tmp[15];
        cube[17] = cube_tmp[9];
        cube[18] = cube_tmp[3];
        cube[19] = cube_tmp[34];
        cube[20] = cube_tmp[28];
        cube[21] = cube_tmp[22];
        cube[22] = cube_tmp[16];
        cube[23] = cube_tmp[10];
        cube[24] = cube_tmp[4];
        cube[25] = cube_tmp[35];
        cube[26] = cube_tmp[29];
        cube[27] = cube_tmp[23];
        cube[28] = cube_tmp[17];
        cube[29] = cube_tmp[11];
        cube[30] = cube_tmp[5];
        cube[31] = cube_tmp[36];
        cube[32] = cube_tmp[30];
        cube[33] = cube_tmp[24];
        cube[34] = cube_tmp[18];
        cube[35] = cube_tmp[12];
        cube[36] = cube_tmp[6];
        cube[37] = cube_tmp[73];
        cube[38] = cube_tmp[74];
        cube[39] = cube_tmp[75];
        cube[40] = cube_tmp[76];
        cube[41] = cube_tmp[77];
        cube[42] = cube_tmp[78];
        cube[73] = cube_tmp[109];
        cube[74] = cube_tmp[110];
        cube[75] = cube_tmp[111];
        cube[76] = cube_tmp[112];
        cube[77] = cube_tmp[113];
        cube[78] = cube_tmp[114];
        cube[109] = cube_tmp[145];
        cube[110] = cube_tmp[146];
        cube[111] = cube_tmp[147];
        cube[112] = cube_tmp[148];
        cube[113] = cube_tmp[149];
        cube[114] = cube_tmp[150];
        cube[145] = cube_tmp[37];
        cube[146] = cube_tmp[38];
        cube[147] = cube_tmp[39];
        cube[148] = cube_tmp[40];
        cube[149] = cube_tmp[41];
        cube[150] = cube_tmp[42];
        break;
    }

    case U_PRIME: {
        cube[1] = cube_tmp[6];
        cube[2] = cube_tmp[12];
        cube[3] = cube_tmp[18];
        cube[4] = cube_tmp[24];
        cube[5] = cube_tmp[30];
        cube[6] = cube_tmp[36];
        cube[7] = cube_tmp[5];
        cube[8] = cube_tmp[11];
        cube[9] = cube_tmp[17];
        cube[10] = cube_tmp[23];
        cube[11] = cube_tmp[29];
        cube[12] = cube_tmp[35];
        cube[13] = cube_tmp[4];
        cube[14] = cube_tmp[10];
        cube[15] = cube_tmp[16];
        cube[16] = cube_tmp[22];
        cube[17] = cube_tmp[28];
        cube[18] = cube_tmp[34];
        cube[19] = cube_tmp[3];
        cube[20] = cube_tmp[9];
        cube[21] = cube_tmp[15];
        cube[22] = cube_tmp[21];
        cube[23] = cube_tmp[27];
        cube[24] = cube_tmp[33];
        cube[25] = cube_tmp[2];
        cube[26] = cube_tmp[8];
        cube[27] = cube_tmp[14];
        cube[28] = cube_tmp[20];
        cube[29] = cube_tmp[26];
        cube[30] = cube_tmp[32];
        cube[31] = cube_tmp[1];
        cube[32] = cube_tmp[7];
        cube[33] = cube_tmp[13];
        cube[34] = cube_tmp[19];
        cube[35] = cube_tmp[25];
        cube[36] = cube_tmp[31];
        cube[37] = cube_tmp[145];
        cube[38] = cube_tmp[146];
        cube[39] = cube_tmp[147];
        cube[40] = cube_tmp[148];
        cube[41] = cube_tmp[149];
        cube[42] = cube_tmp[150];
        cube[73] = cube_tmp[37];
        cube[74] = cube_tmp[38];
        cube[75] = cube_tmp[39];
        cube[76] = cube_tmp[40];
        cube[77] = cube_tmp[41];
        cube[78] = cube_tmp[42];
        cube[109] = cube_tmp[73];
        cube[110] = cube_tmp[74];
        cube[111] = cube_tmp[75];
        cube[112] = cube_tmp[76];
        cube[113] = cube_tmp[77];
        cube[114] = cube_tmp[78];
        cube[145] = cube_tmp[109];
        cube[146] = cube_tmp[110];
        cube[147] = cube_tmp[111];
        cube[148] = cube_tmp[112];
        cube[149] = cube_tmp[113];
        cube[150] = cube_tmp[114];
        break;
    }

    case U2: {
        cube[1] = cube_tmp[36];
        cube[2] = cube_tmp[35];
        cube[3] = cube_tmp[34];
        cube[4] = cube_tmp[33];
        cube[5] = cube_tmp[32];
        cube[6] = cube_tmp[31];
        cube[7] = cube_tmp[30];
        cube[8] = cube_tmp[29];
        cube[9] = cube_tmp[28];
        cube[10] = cube_tmp[27];
        cube[11] = cube_tmp[26];
        cube[12] = cube_tmp[25];
        cube[13] = cube_tmp[24];
        cube[14] = cube_tmp[23];
        cube[15] = cube_tmp[22];
        cube[16] = cube_tmp[21];
        cube[17] = cube_tmp[20];
        cube[18] = cube_tmp[19];
        cube[19] = cube_tmp[18];
        cube[20] = cube_tmp[17];
        cube[21] = cube_tmp[16];
        cube[22] = cube_tmp[15];
        cube[23] = cube_tmp[14];
        cube[24] = cube_tmp[13];
        cube[25] = cube_tmp[12];
        cube[26] = cube_tmp[11];
        cube[27] = cube_tmp[10];
        cube[28] = cube_tmp[9];
        cube[29] = cube_tmp[8];
        cube[30] = cube_tmp[7];
        cube[31] = cube_tmp[6];
        cube[32] = cube_tmp[5];
        cube[33] = cube_tmp[4];
        cube[34] = cube_tmp[3];
        cube[35] = cube_tmp[2];
        cube[36] = cube_tmp[1];
        cube[37] = cube_tmp[109];
        cube[38] = cube_tmp[110];
        cube[39] = cube_tmp[111];
        cube[40] = cube_tmp[112];
        cube[41] = cube_tmp[113];
        cube[42] = cube_tmp[114];
        cube[73] = cube_tmp[145];
        cube[74] = cube_tmp[146];
        cube[75] = cube_tmp[147];
        cube[76] = cube_tmp[148];
        cube[77] = cube_tmp[149];
        cube[78] = cube_tmp[150];
        cube[109] = cube_tmp[37];
        cube[110] = cube_tmp[38];
        cube[111] = cube_tmp[39];
        cube[112] = cube_tmp[40];
        cube[113] = cube_tmp[41];
        cube[114] = cube_tmp[42];
        cube[145] = cube_tmp[73];
        cube[146] = cube_tmp[74];
        cube[147] = cube_tmp[75];
        cube[148] = cube_tmp[76];
        cube[149] = cube_tmp[77];
        cube[150] = cube_tmp[78];
        break;
    }

    case Uw: {
        cube[1] = cube_tmp[31];
        cube[2] = cube_tmp[25];
        cube[3] = cube_tmp[19];
        cube[4] = cube_tmp[13];
        cube[5] = cube_tmp[7];
        cube[6] = cube_tmp[1];
        cube[7] = cube_tmp[32];
        cube[8] = cube_tmp[26];
        cube[9] = cube_tmp[20];
        cube[10] = cube_tmp[14];
        cube[11] = cube_tmp[8];
        cube[12] = cube_tmp[2];
        cube[13] = cube_tmp[33];
        cube[14] = cube_tmp[27];
        cube[15] = cube_tmp[21];
        cube[16] = cube_tmp[15];
        cube[17] = cube_tmp[9];
        cube[18] = cube_tmp[3];
        cube[19] = cube_tmp[34];
        cube[20] = cube_tmp[28];
        cube[21] = cube_tmp[22];
        cube[22] = cube_tmp[16];
        cube[23] = cube_tmp[10];
        cube[24] = cube_tmp[4];
        cube[25] = cube_tmp[35];
        cube[26] = cube_tmp[29];
        cube[27] = cube_tmp[23];
        cube[28] = cube_tmp[17];
        cube[29] = cube_tmp[11];
        cube[30] = cube_tmp[5];
        cube[31] = cube_tmp[36];
        cube[32] = cube_tmp[30];
        cube[33] = cube_tmp[24];
        cube[34] = cube_tmp[18];
        cube[35] = cube_tmp[12];
        cube[36] = cube_tmp[6];
        cube[37] = cube_tmp[73];
        cube[38] = cube_tmp[74];
        cube[39] = cube_tmp[75];
        cube[40] = cube_tmp[76];
        cube[41] = cube_tmp[77];
        cube[42] = cube_tmp[78];
        cube[43] = cube_tmp[79];
        cube[44] = cube_tmp[80];
        cube[45] = cube_tmp[81];
        cube[46] = cube_tmp[82];
        cube[47] = cube_tmp[83];
        cube[48] = cube_tmp[84];
        cube[73] = cube_tmp[109];
        cube[74] = cube_tmp[110];
        cube[75] = cube_tmp[111];
        cube[76] = cube_tmp[112];
        cube[77] = cube_tmp[113];
        cube[78] = cube_tmp[114];
        cube[79] = cube_tmp[115];
        cube[80] = cube_tmp[116];
        cube[81] = cube_tmp[117];
        cube[82] = cube_tmp[118];
        cube[83] = cube_tmp[119];
        cube[84] = cube_tmp[120];
        cube[109] = cube_tmp[145];
        cube[110] = cube_tmp[146];
        cube[111] = cube_tmp[147];
        cube[112] = cube_tmp[148];
        cube[113] = cube_tmp[149];
        cube[114] = cube_tmp[150];
        cube[115] = cube_tmp[151];
        cube[116] = cube_tmp[152];
        cube[117] = cube_tmp[153];
        cube[118] = cube_tmp[154];
        cube[119] = cube_tmp[155];
        cube[120] = cube_tmp[156];
        cube[145] = cube_tmp[37];
        cube[146] = cube_tmp[38];
        cube[147] = cube_tmp[39];
        cube[148] = cube_tmp[40];
        cube[149] = cube_tmp[41];
        cube[150] = cube_tmp[42];
        cube[151] = cube_tmp[43];
        cube[152] = cube_tmp[44];
        cube[153] = cube_tmp[45];
        cube[154] = cube_tmp[46];
        cube[155] = cube_tmp[47];
        cube[156] = cube_tmp[48];
        break;
    }

    case Uw_PRIME: {
        cube[1] = cube_tmp[6];
        cube[2] = cube_tmp[12];
        cube[3] = cube_tmp[18];
        cube[4] = cube_tmp[24];
        cube[5] = cube_tmp[30];
        cube[6] = cube_tmp[36];
        cube[7] = cube_tmp[5];
        cube[8] = cube_tmp[11];
        cube[9] = cube_tmp[17];
        cube[10] = cube_tmp[23];
        cube[11] = cube_tmp[29];
        cube[12] = cube_tmp[35];
        cube[13] = cube_tmp[4];
        cube[14] = cube_tmp[10];
        cube[15] = cube_tmp[16];
        cube[16] = cube_tmp[22];
        cube[17] = cube_tmp[28];
        cube[18] = cube_tmp[34];
        cube[19] = cube_tmp[3];
        cube[20] = cube_tmp[9];
        cube[21] = cube_tmp[15];
        cube[22] = cube_tmp[21];
        cube[23] = cube_tmp[27];
        cube[24] = cube_tmp[33];
        cube[25] = cube_tmp[2];
        cube[26] = cube_tmp[8];
        cube[27] = cube_tmp[14];
        cube[28] = cube_tmp[20];
        cube[29] = cube_tmp[26];
        cube[30] = cube_tmp[32];
        cube[31] = cube_tmp[1];
        cube[32] = cube_tmp[7];
        cube[33] = cube_tmp[13];
        cube[34] = cube_tmp[19];
        cube[35] = cube_tmp[25];
        cube[36] = cube_tmp[31];
        cube[37] = cube_tmp[145];
        cube[38] = cube_tmp[146];
        cube[39] = cube_tmp[147];
        cube[40] = cube_tmp[148];
        cube[41] = cube_tmp[149];
        cube[42] = cube_tmp[150];
        cube[43] = cube_tmp[151];
        cube[44] = cube_tmp[152];
        cube[45] = cube_tmp[153];
        cube[46] = cube_tmp[154];
        cube[47] = cube_tmp[155];
        cube[48] = cube_tmp[156];
        cube[73] = cube_tmp[37];
        cube[74] = cube_tmp[38];
        cube[75] = cube_tmp[39];
        cube[76] = cube_tmp[40];
        cube[77] = cube_tmp[41];
        cube[78] = cube_tmp[42];
        cube[79] = cube_tmp[43];
        cube[80] = cube_tmp[44];
        cube[81] = cube_tmp[45];
        cube[82] = cube_tmp[46];
        cube[83] = cube_tmp[47];
        cube[84] = cube_tmp[48];
        cube[109] = cube_tmp[73];
        cube[110] = cube_tmp[74];
        cube[111] = cube_tmp[75];
        cube[112] = cube_tmp[76];
        cube[113] = cube_tmp[77];
        cube[114] = cube_tmp[78];
        cube[115] = cube_tmp[79];
        cube[116] = cube_tmp[80];
        cube[117] = cube_tmp[81];
        cube[118] = cube_tmp[82];
        cube[119] = cube_tmp[83];
        cube[120] = cube_tmp[84];
        cube[145] = cube_tmp[109];
        cube[146] = cube_tmp[110];
        cube[147] = cube_tmp[111];
        cube[148] = cube_tmp[112];
        cube[149] = cube_tmp[113];
        cube[150] = cube_tmp[114];
        cube[151] = cube_tmp[115];
        cube[152] = cube_tmp[116];
        cube[153] = cube_tmp[117];
        cube[154] = cube_tmp[118];
        cube[155] = cube_tmp[119];
        cube[156] = cube_tmp[120];
        break;
    }

    case Uw2: {
        cube[1] = cube_tmp[36];
        cube[2] = cube_tmp[35];
        cube[3] = cube_tmp[34];
        cube[4] = cube_tmp[33];
        cube[5] = cube_tmp[32];
        cube[6] = cube_tmp[31];
        cube[7] = cube_tmp[30];
        cube[8] = cube_tmp[29];
        cube[9] = cube_tmp[28];
        cube[10] = cube_tmp[27];
        cube[11] = cube_tmp[26];
        cube[12] = cube_tmp[25];
        cube[13] = cube_tmp[24];
        cube[14] = cube_tmp[23];
        cube[15] = cube_tmp[22];
        cube[16] = cube_tmp[21];
        cube[17] = cube_tmp[20];
        cube[18] = cube_tmp[19];
        cube[19] = cube_tmp[18];
        cube[20] = cube_tmp[17];
        cube[21] = cube_tmp[16];
        cube[22] = cube_tmp[15];
        cube[23] = cube_tmp[14];
        cube[24] = cube_tmp[13];
        cube[25] = cube_tmp[12];
        cube[26] = cube_tmp[11];
        cube[27] = cube_tmp[10];
        cube[28] = cube_tmp[9];
        cube[29] = cube_tmp[8];
        cube[30] = cube_tmp[7];
        cube[31] = cube_tmp[6];
        cube[32] = cube_tmp[5];
        cube[33] = cube_tmp[4];
        cube[34] = cube_tmp[3];
        cube[35] = cube_tmp[2];
        cube[36] = cube_tmp[1];
        cube[37] = cube_tmp[109];
        cube[38] = cube_tmp[110];
        cube[39] = cube_tmp[111];
        cube[40] = cube_tmp[112];
        cube[41] = cube_tmp[113];
        cube[42] = cube_tmp[114];
        cube[43] = cube_tmp[115];
        cube[44] = cube_tmp[116];
        cube[45] = cube_tmp[117];
        cube[46] = cube_tmp[118];
        cube[47] = cube_tmp[119];
        cube[48] = cube_tmp[120];
        cube[73] = cube_tmp[145];
        cube[74] = cube_tmp[146];
        cube[75] = cube_tmp[147];
        cube[76] = cube_tmp[148];
        cube[77] = cube_tmp[149];
        cube[78] = cube_tmp[150];
        cube[79] = cube_tmp[151];
        cube[80] = cube_tmp[152];
        cube[81] = cube_tmp[153];
        cube[82] = cube_tmp[154];
        cube[83] = cube_tmp[155];
        cube[84] = cube_tmp[156];
        cube[109] = cube_tmp[37];
        cube[110] = cube_tmp[38];
        cube[111] = cube_tmp[39];
        cube[112] = cube_tmp[40];
        cube[113] = cube_tmp[41];
        cube[114] = cube_tmp[42];
        cube[115] = cube_tmp[43];
        cube[116] = cube_tmp[44];
        cube[117] = cube_tmp[45];
        cube[118] = cube_tmp[46];
        cube[119] = cube_tmp[47];
        cube[120] = cube_tmp[48];
        cube[145] = cube_tmp[73];
        cube[146] = cube_tmp[74];
        cube[147] = cube_tmp[75];
        cube[148] = cube_tmp[76];
        cube[149] = cube_tmp[77];
        cube[150] = cube_tmp[78];
        cube[151] = cube_tmp[79];
        cube[152] = cube_tmp[80];
        cube[153] = cube_tmp[81];
        cube[154] = cube_tmp[82];
        cube[155] = cube_tmp[83];
        cube[156] = cube_tmp[84];
        break;
    }

    case threeUw: {
        cube[1] = cube_tmp[31];
        cube[2] = cube_tmp[25];
        cube[3] = cube_tmp[19];
        cube[4] = cube_tmp[13];
        cube[5] = cube_tmp[7];
        cube[6] = cube_tmp[1];
        cube[7] = cube_tmp[32];
        cube[8] = cube_tmp[26];
        cube[9] = cube_tmp[20];
        cube[10] = cube_tmp[14];
        cube[11] = cube_tmp[8];
        cube[12] = cube_tmp[2];
        cube[13] = cube_tmp[33];
        cube[14] = cube_tmp[27];
        cube[15] = cube_tmp[21];
        cube[16] = cube_tmp[15];
        cube[17] = cube_tmp[9];
        cube[18] = cube_tmp[3];
        cube[19] = cube_tmp[34];
        cube[20] = cube_tmp[28];
        cube[21] = cube_tmp[22];
        cube[22] = cube_tmp[16];
        cube[23] = cube_tmp[10];
        cube[24] = cube_tmp[4];
        cube[25] = cube_tmp[35];
        cube[26] = cube_tmp[29];
        cube[27] = cube_tmp[23];
        cube[28] = cube_tmp[17];
        cube[29] = cube_tmp[11];
        cube[30] = cube_tmp[5];
        cube[31] = cube_tmp[36];
        cube[32] = cube_tmp[30];
        cube[33] = cube_tmp[24];
        cube[34] = cube_tmp[18];
        cube[35] = cube_tmp[12];
        cube[36] = cube_tmp[6];
        cube[37] = cube_tmp[73];
        cube[38] = cube_tmp[74];
        cube[39] = cube_tmp[75];
        cube[40] = cube_tmp[76];
        cube[41] = cube_tmp[77];
        cube[42] = cube_tmp[78];
        cube[43] = cube_tmp[79];
        cube[44] = cube_tmp[80];
        cube[45] = cube_tmp[81];
        cube[46] = cube_tmp[82];
        cube[47] = cube_tmp[83];
        cube[48] = cube_tmp[84];
        cube[49] = cube_tmp[85];
        cube[50] = cube_tmp[86];
        cube[51] = cube_tmp[87];
        cube[52] = cube_tmp[88];
        cube[53] = cube_tmp[89];
        cube[54] = cube_tmp[90];
        cube[73] = cube_tmp[109];
        cube[74] = cube_tmp[110];
        cube[75] = cube_tmp[111];
        cube[76] = cube_tmp[112];
        cube[77] = cube_tmp[113];
        cube[78] = cube_tmp[114];
        cube[79] = cube_tmp[115];
        cube[80] = cube_tmp[116];
        cube[81] = cube_tmp[117];
        cube[82] = cube_tmp[118];
        cube[83] = cube_tmp[119];
        cube[84] = cube_tmp[120];
        cube[85] = cube_tmp[121];
        cube[86] = cube_tmp[122];
        cube[87] = cube_tmp[123];
        cube[88] = cube_tmp[124];
        cube[89] = cube_tmp[125];
        cube[90] = cube_tmp[126];
        cube[109] = cube_tmp[145];
        cube[110] = cube_tmp[146];
        cube[111] = cube_tmp[147];
        cube[112] = cube_tmp[148];
        cube[113] = cube_tmp[149];
        cube[114] = cube_tmp[150];
        cube[115] = cube_tmp[151];
        cube[116] = cube_tmp[152];
        cube[117] = cube_tmp[153];
        cube[118] = cube_tmp[154];
        cube[119] = cube_tmp[155];
        cube[120] = cube_tmp[156];
        cube[121] = cube_tmp[157];
        cube[122] = cube_tmp[158];
        cube[123] = cube_tmp[159];
        cube[124] = cube_tmp[160];
        cube[125] = cube_tmp[161];
        cube[126] = cube_tmp[162];
        cube[145] = cube_tmp[37];
        cube[146] = cube_tmp[38];
        cube[147] = cube_tmp[39];
        cube[148] = cube_tmp[40];
        cube[149] = cube_tmp[41];
        cube[150] = cube_tmp[42];
        cube[151] = cube_tmp[43];
        cube[152] = cube_tmp[44];
        cube[153] = cube_tmp[45];
        cube[154] = cube_tmp[46];
        cube[155] = cube_tmp[47];
        cube[156] = cube_tmp[48];
        cube[157] = cube_tmp[49];
        cube[158] = cube_tmp[50];
        cube[159] = cube_tmp[51];
        cube[160] = cube_tmp[52];
        cube[161] = cube_tmp[53];
        cube[162] = cube_tmp[54];
        break;
    }

    case threeUw_PRIME: {
        cube[1] = cube_tmp[6];
        cube[2] = cube_tmp[12];
        cube[3] = cube_tmp[18];
        cube[4] = cube_tmp[24];
        cube[5] = cube_tmp[30];
        cube[6] = cube_tmp[36];
        cube[7] = cube_tmp[5];
        cube[8] = cube_tmp[11];
        cube[9] = cube_tmp[17];
        cube[10] = cube_tmp[23];
        cube[11] = cube_tmp[29];
        cube[12] = cube_tmp[35];
        cube[13] = cube_tmp[4];
        cube[14] = cube_tmp[10];
        cube[15] = cube_tmp[16];
        cube[16] = cube_tmp[22];
        cube[17] = cube_tmp[28];
        cube[18] = cube_tmp[34];
        cube[19] = cube_tmp[3];
        cube[20] = cube_tmp[9];
        cube[21] = cube_tmp[15];
        cube[22] = cube_tmp[21];
        cube[23] = cube_tmp[27];
        cube[24] = cube_tmp[33];
        cube[25] = cube_tmp[2];
        cube[26] = cube_tmp[8];
        cube[27] = cube_tmp[14];
        cube[28] = cube_tmp[20];
        cube[29] = cube_tmp[26];
        cube[30] = cube_tmp[32];
        cube[31] = cube_tmp[1];
        cube[32] = cube_tmp[7];
        cube[33] = cube_tmp[13];
        cube[34] = cube_tmp[19];
        cube[35] = cube_tmp[25];
        cube[36] = cube_tmp[31];
        cube[37] = cube_tmp[145];
        cube[38] = cube_tmp[146];
        cube[39] = cube_tmp[147];
        cube[40] = cube_tmp[148];
        cube[41] = cube_tmp[149];
        cube[42] = cube_tmp[150];
        cube[43] = cube_tmp[151];
        cube[44] = cube_tmp[152];
        cube[45] = cube_tmp[153];
        cube[46] = cube_tmp[154];
        cube[47] = cube_tmp[155];
        cube[48] = cube_tmp[156];
        cube[49] = cube_tmp[157];
        cube[50] = cube_tmp[158];
        cube[51] = cube_tmp[159];
        cube[52] = cube_tmp[160];
        cube[53] = cube_tmp[161];
        cube[54] = cube_tmp[162];
        cube[73] = cube_tmp[37];
        cube[74] = cube_tmp[38];
        cube[75] = cube_tmp[39];
        cube[76] = cube_tmp[40];
        cube[77] = cube_tmp[41];
        cube[78] = cube_tmp[42];
        cube[79] = cube_tmp[43];
        cube[80] = cube_tmp[44];
        cube[81] = cube_tmp[45];
        cube[82] = cube_tmp[46];
        cube[83] = cube_tmp[47];
        cube[84] = cube_tmp[48];
        cube[85] = cube_tmp[49];
        cube[86] = cube_tmp[50];
        cube[87] = cube_tmp[51];
        cube[88] = cube_tmp[52];
        cube[89] = cube_tmp[53];
        cube[90] = cube_tmp[54];
        cube[109] = cube_tmp[73];
        cube[110] = cube_tmp[74];
        cube[111] = cube_tmp[75];
        cube[112] = cube_tmp[76];
        cube[113] = cube_tmp[77];
        cube[114] = cube_tmp[78];
        cube[115] = cube_tmp[79];
        cube[116] = cube_tmp[80];
        cube[117] = cube_tmp[81];
        cube[118] = cube_tmp[82];
        cube[119] = cube_tmp[83];
        cube[120] = cube_tmp[84];
        cube[121] = cube_tmp[85];
        cube[122] = cube_tmp[86];
        cube[123] = cube_tmp[87];
        cube[124] = cube_tmp[88];
        cube[125] = cube_tmp[89];
        cube[126] = cube_tmp[90];
        cube[145] = cube_tmp[109];
        cube[146] = cube_tmp[110];
        cube[147] = cube_tmp[111];
        cube[148] = cube_tmp[112];
        cube[149] = cube_tmp[113];
        cube[150] = cube_tmp[114];
        cube[151] = cube_tmp[115];
        cube[152] = cube_tmp[116];
        cube[153] = cube_tmp[117];
        cube[154] = cube_tmp[118];
        cube[155] = cube_tmp[119];
        cube[156] = cube_tmp[120];
        cube[157] = cube_tmp[121];
        cube[158] = cube_tmp[122];
        cube[159] = cube_tmp[123];
        cube[160] = cube_tmp[124];
        cube[161] = cube_tmp[125];
        cube[162] = cube_tmp[126];
        break;
    }

    case threeUw2: {
        cube[1] = cube_tmp[36];
        cube[2] = cube_tmp[35];
        cube[3] = cube_tmp[34];
        cube[4] = cube_tmp[33];
        cube[5] = cube_tmp[32];
        cube[6] = cube_tmp[31];
        cube[7] = cube_tmp[30];
        cube[8] = cube_tmp[29];
        cube[9] = cube_tmp[28];
        cube[10] = cube_tmp[27];
        cube[11] = cube_tmp[26];
        cube[12] = cube_tmp[25];
        cube[13] = cube_tmp[24];
        cube[14] = cube_tmp[23];
        cube[15] = cube_tmp[22];
        cube[16] = cube_tmp[21];
        cube[17] = cube_tmp[20];
        cube[18] = cube_tmp[19];
        cube[19] = cube_tmp[18];
        cube[20] = cube_tmp[17];
        cube[21] = cube_tmp[16];
        cube[22] = cube_tmp[15];
        cube[23] = cube_tmp[14];
        cube[24] = cube_tmp[13];
        cube[25] = cube_tmp[12];
        cube[26] = cube_tmp[11];
        cube[27] = cube_tmp[10];
        cube[28] = cube_tmp[9];
        cube[29] = cube_tmp[8];
        cube[30] = cube_tmp[7];
        cube[31] = cube_tmp[6];
        cube[32] = cube_tmp[5];
        cube[33] = cube_tmp[4];
        cube[34] = cube_tmp[3];
        cube[35] = cube_tmp[2];
        cube[36] = cube_tmp[1];
        cube[37] = cube_tmp[109];
        cube[38] = cube_tmp[110];
        cube[39] = cube_tmp[111];
        cube[40] = cube_tmp[112];
        cube[41] = cube_tmp[113];
        cube[42] = cube_tmp[114];
        cube[43] = cube_tmp[115];
        cube[44] = cube_tmp[116];
        cube[45] = cube_tmp[117];
        cube[46] = cube_tmp[118];
        cube[47] = cube_tmp[119];
        cube[48] = cube_tmp[120];
        cube[49] = cube_tmp[121];
        cube[50] = cube_tmp[122];
        cube[51] = cube_tmp[123];
        cube[52] = cube_tmp[124];
        cube[53] = cube_tmp[125];
        cube[54] = cube_tmp[126];
        cube[73] = cube_tmp[145];
        cube[74] = cube_tmp[146];
        cube[75] = cube_tmp[147];
        cube[76] = cube_tmp[148];
        cube[77] = cube_tmp[149];
        cube[78] = cube_tmp[150];
        cube[79] = cube_tmp[151];
        cube[80] = cube_tmp[152];
        cube[81] = cube_tmp[153];
        cube[82] = cube_tmp[154];
        cube[83] = cube_tmp[155];
        cube[84] = cube_tmp[156];
        cube[85] = cube_tmp[157];
        cube[86] = cube_tmp[158];
        cube[87] = cube_tmp[159];
        cube[88] = cube_tmp[160];
        cube[89] = cube_tmp[161];
        cube[90] = cube_tmp[162];
        cube[109] = cube_tmp[37];
        cube[110] = cube_tmp[38];
        cube[111] = cube_tmp[39];
        cube[112] = cube_tmp[40];
        cube[113] = cube_tmp[41];
        cube[114] = cube_tmp[42];
        cube[115] = cube_tmp[43];
        cube[116] = cube_tmp[44];
        cube[117] = cube_tmp[45];
        cube[118] = cube_tmp[46];
        cube[119] = cube_tmp[47];
        cube[120] = cube_tmp[48];
        cube[121] = cube_tmp[49];
        cube[122] = cube_tmp[50];
        cube[123] = cube_tmp[51];
        cube[124] = cube_tmp[52];
        cube[125] = cube_tmp[53];
        cube[126] = cube_tmp[54];
        cube[145] = cube_tmp[73];
        cube[146] = cube_tmp[74];
        cube[147] = cube_tmp[75];
        cube[148] = cube_tmp[76];
        cube[149] = cube_tmp[77];
        cube[150] = cube_tmp[78];
        cube[151] = cube_tmp[79];
        cube[152] = cube_tmp[80];
        cube[153] = cube_tmp[81];
        cube[154] = cube_tmp[82];
        cube[155] = cube_tmp[83];
        cube[156] = cube_tmp[84];
        cube[157] = cube_tmp[85];
        cube[158] = cube_tmp[86];
        cube[159] = cube_tmp[87];
        cube[160] = cube_tmp[88];
        cube[161] = cube_tmp[89];
        cube[162] = cube_tmp[90];
        break;
    }

    case L: {
        cube[1] = cube_tmp[180];
        cube[7] = cube_tmp[174];
        cube[13] = cube_tmp[168];
        cube[19] = cube_tmp[162];
        cube[25] = cube_tmp[156];
        cube[31] = cube_tmp[150];
        cube[37] = cube_tmp[67];
        cube[38] = cube_tmp[61];
        cube[39] = cube_tmp[55];
        cube[40] = cube_tmp[49];
        cube[41] = cube_tmp[43];
        cube[42] = cube_tmp[37];
        cube[43] = cube_tmp[68];
        cube[44] = cube_tmp[62];
        cube[45] = cube_tmp[56];
        cube[46] = cube_tmp[50];
        cube[47] = cube_tmp[44];
        cube[48] = cube_tmp[38];
        cube[49] = cube_tmp[69];
        cube[50] = cube_tmp[63];
        cube[51] = cube_tmp[57];
        cube[52] = cube_tmp[51];
        cube[53] = cube_tmp[45];
        cube[54] = cube_tmp[39];
        cube[55] = cube_tmp[70];
        cube[56] = cube_tmp[64];
        cube[57] = cube_tmp[58];
        cube[58] = cube_tmp[52];
        cube[59] = cube_tmp[46];
        cube[60] = cube_tmp[40];
        cube[61] = cube_tmp[71];
        cube[62] = cube_tmp[65];
        cube[63] = cube_tmp[59];
        cube[64] = cube_tmp[53];
        cube[65] = cube_tmp[47];
        cube[66] = cube_tmp[41];
        cube[67] = cube_tmp[72];
        cube[68] = cube_tmp[66];
        cube[69] = cube_tmp[60];
        cube[70] = cube_tmp[54];
        cube[71] = cube_tmp[48];
        cube[72] = cube_tmp[42];
        cube[73] = cube_tmp[1];
        cube[79] = cube_tmp[7];
        cube[85] = cube_tmp[13];
        cube[91] = cube_tmp[19];
        cube[97] = cube_tmp[25];
        cube[103] = cube_tmp[31];
        cube[150] = cube_tmp[211];
        cube[156] = cube_tmp[205];
        cube[162] = cube_tmp[199];
        cube[168] = cube_tmp[193];
        cube[174] = cube_tmp[187];
        cube[180] = cube_tmp[181];
        cube[181] = cube_tmp[73];
        cube[187] = cube_tmp[79];
        cube[193] = cube_tmp[85];
        cube[199] = cube_tmp[91];
        cube[205] = cube_tmp[97];
        cube[211] = cube_tmp[103];
        break;
    }

    case L_PRIME: {
        cube[1] = cube_tmp[73];
        cube[7] = cube_tmp[79];
        cube[13] = cube_tmp[85];
        cube[19] = cube_tmp[91];
        cube[25] = cube_tmp[97];
        cube[31] = cube_tmp[103];
        cube[37] = cube_tmp[42];
        cube[38] = cube_tmp[48];
        cube[39] = cube_tmp[54];
        cube[40] = cube_tmp[60];
        cube[41] = cube_tmp[66];
        cube[42] = cube_tmp[72];
        cube[43] = cube_tmp[41];
        cube[44] = cube_tmp[47];
        cube[45] = cube_tmp[53];
        cube[46] = cube_tmp[59];
        cube[47] = cube_tmp[65];
        cube[48] = cube_tmp[71];
        cube[49] = cube_tmp[40];
        cube[50] = cube_tmp[46];
        cube[51] = cube_tmp[52];
        cube[52] = cube_tmp[58];
        cube[53] = cube_tmp[64];
        cube[54] = cube_tmp[70];
        cube[55] = cube_tmp[39];
        cube[56] = cube_tmp[45];
        cube[57] = cube_tmp[51];
        cube[58] = cube_tmp[57];
        cube[59] = cube_tmp[63];
        cube[60] = cube_tmp[69];
        cube[61] = cube_tmp[38];
        cube[62] = cube_tmp[44];
        cube[63] = cube_tmp[50];
        cube[64] = cube_tmp[56];
        cube[65] = cube_tmp[62];
        cube[66] = cube_tmp[68];
        cube[67] = cube_tmp[37];
        cube[68] = cube_tmp[43];
        cube[69] = cube_tmp[49];
        cube[70] = cube_tmp[55];
        cube[71] = cube_tmp[61];
        cube[72] = cube_tmp[67];
        cube[73] = cube_tmp[181];
        cube[79] = cube_tmp[187];
        cube[85] = cube_tmp[193];
        cube[91] = cube_tmp[199];
        cube[97] = cube_tmp[205];
        cube[103] = cube_tmp[211];
        cube[150] = cube_tmp[31];
        cube[156] = cube_tmp[25];
        cube[162] = cube_tmp[19];
        cube[168] = cube_tmp[13];
        cube[174] = cube_tmp[7];
        cube[180] = cube_tmp[1];
        cube[181] = cube_tmp[180];
        cube[187] = cube_tmp[174];
        cube[193] = cube_tmp[168];
        cube[199] = cube_tmp[162];
        cube[205] = cube_tmp[156];
        cube[211] = cube_tmp[150];
        break;
    }

    case L2: {
        cube[1] = cube_tmp[181];
        cube[7] = cube_tmp[187];
        cube[13] = cube_tmp[193];
        cube[19] = cube_tmp[199];
        cube[25] = cube_tmp[205];
        cube[31] = cube_tmp[211];
        cube[37] = cube_tmp[72];
        cube[38] = cube_tmp[71];
        cube[39] = cube_tmp[70];
        cube[40] = cube_tmp[69];
        cube[41] = cube_tmp[68];
        cube[42] = cube_tmp[67];
        cube[43] = cube_tmp[66];
        cube[44] = cube_tmp[65];
        cube[45] = cube_tmp[64];
        cube[46] = cube_tmp[63];
        cube[47] = cube_tmp[62];
        cube[48] = cube_tmp[61];
        cube[49] = cube_tmp[60];
        cube[50] = cube_tmp[59];
        cube[51] = cube_tmp[58];
        cube[52] = cube_tmp[57];
        cube[53] = cube_tmp[56];
        cube[54] = cube_tmp[55];
        cube[55] = cube_tmp[54];
        cube[56] = cube_tmp[53];
        cube[57] = cube_tmp[52];
        cube[58] = cube_tmp[51];
        cube[59] = cube_tmp[50];
        cube[60] = cube_tmp[49];
        cube[61] = cube_tmp[48];
        cube[62] = cube_tmp[47];
        cube[63] = cube_tmp[46];
        cube[64] = cube_tmp[45];
        cube[65] = cube_tmp[44];
        cube[66] = cube_tmp[43];
        cube[67] = cube_tmp[42];
        cube[68] = cube_tmp[41];
        cube[69] = cube_tmp[40];
        cube[70] = cube_tmp[39];
        cube[71] = cube_tmp[38];
        cube[72] = cube_tmp[37];
        cube[73] = cube_tmp[180];
        cube[79] = cube_tmp[174];
        cube[85] = cube_tmp[168];
        cube[91] = cube_tmp[162];
        cube[97] = cube_tmp[156];
        cube[103] = cube_tmp[150];
        cube[150] = cube_tmp[103];
        cube[156] = cube_tmp[97];
        cube[162] = cube_tmp[91];
        cube[168] = cube_tmp[85];
        cube[174] = cube_tmp[79];
        cube[180] = cube_tmp[73];
        cube[181] = cube_tmp[1];
        cube[187] = cube_tmp[7];
        cube[193] = cube_tmp[13];
        cube[199] = cube_tmp[19];
        cube[205] = cube_tmp[25];
        cube[211] = cube_tmp[31];
        break;
    }

    case Lw: {
        cube[1] = cube_tmp[180];
        cube[2] = cube_tmp[179];
        cube[7] = cube_tmp[174];
        cube[8] = cube_tmp[173];
        cube[13] = cube_tmp[168];
        cube[14] = cube_tmp[167];
        cube[19] = cube_tmp[162];
        cube[20] = cube_tmp[161];
        cube[25] = cube_tmp[156];
        cube[26] = cube_tmp[155];
        cube[31] = cube_tmp[150];
        cube[32] = cube_tmp[149];
        cube[37] = cube_tmp[67];
        cube[38] = cube_tmp[61];
        cube[39] = cube_tmp[55];
        cube[40] = cube_tmp[49];
        cube[41] = cube_tmp[43];
        cube[42] = cube_tmp[37];
        cube[43] = cube_tmp[68];
        cube[44] = cube_tmp[62];
        cube[45] = cube_tmp[56];
        cube[46] = cube_tmp[50];
        cube[47] = cube_tmp[44];
        cube[48] = cube_tmp[38];
        cube[49] = cube_tmp[69];
        cube[50] = cube_tmp[63];
        cube[51] = cube_tmp[57];
        cube[52] = cube_tmp[51];
        cube[53] = cube_tmp[45];
        cube[54] = cube_tmp[39];
        cube[55] = cube_tmp[70];
        cube[56] = cube_tmp[64];
        cube[57] = cube_tmp[58];
        cube[58] = cube_tmp[52];
        cube[59] = cube_tmp[46];
        cube[60] = cube_tmp[40];
        cube[61] = cube_tmp[71];
        cube[62] = cube_tmp[65];
        cube[63] = cube_tmp[59];
        cube[64] = cube_tmp[53];
        cube[65] = cube_tmp[47];
        cube[66] = cube_tmp[41];
        cube[67] = cube_tmp[72];
        cube[68] = cube_tmp[66];
        cube[69] = cube_tmp[60];
        cube[70] = cube_tmp[54];
        cube[71] = cube_tmp[48];
        cube[72] = cube_tmp[42];
        cube[73] = cube_tmp[1];
        cube[74] = cube_tmp[2];
        cube[79] = cube_tmp[7];
        cube[80] = cube_tmp[8];
        cube[85] = cube_tmp[13];
        cube[86] = cube_tmp[14];
        cube[91] = cube_tmp[19];
        cube[92] = cube_tmp[20];
        cube[97] = cube_tmp[25];
        cube[98] = cube_tmp[26];
        cube[103] = cube_tmp[31];
        cube[104] = cube_tmp[32];
        cube[149] = cube_tmp[212];
        cube[150] = cube_tmp[211];
        cube[155] = cube_tmp[206];
        cube[156] = cube_tmp[205];
        cube[161] = cube_tmp[200];
        cube[162] = cube_tmp[199];
        cube[167] = cube_tmp[194];
        cube[168] = cube_tmp[193];
        cube[173] = cube_tmp[188];
        cube[174] = cube_tmp[187];
        cube[179] = cube_tmp[182];
        cube[180] = cube_tmp[181];
        cube[181] = cube_tmp[73];
        cube[182] = cube_tmp[74];
        cube[187] = cube_tmp[79];
        cube[188] = cube_tmp[80];
        cube[193] = cube_tmp[85];
        cube[194] = cube_tmp[86];
        cube[199] = cube_tmp[91];
        cube[200] = cube_tmp[92];
        cube[205] = cube_tmp[97];
        cube[206] = cube_tmp[98];
        cube[211] = cube_tmp[103];
        cube[212] = cube_tmp[104];
        break;
    }

    case Lw_PRIME: {
        cube[1] = cube_tmp[73];
        cube[2] = cube_tmp[74];
        cube[7] = cube_tmp[79];
        cube[8] = cube_tmp[80];
        cube[13] = cube_tmp[85];
        cube[14] = cube_tmp[86];
        cube[19] = cube_tmp[91];
        cube[20] = cube_tmp[92];
        cube[25] = cube_tmp[97];
        cube[26] = cube_tmp[98];
        cube[31] = cube_tmp[103];
        cube[32] = cube_tmp[104];
        cube[37] = cube_tmp[42];
        cube[38] = cube_tmp[48];
        cube[39] = cube_tmp[54];
        cube[40] = cube_tmp[60];
        cube[41] = cube_tmp[66];
        cube[42] = cube_tmp[72];
        cube[43] = cube_tmp[41];
        cube[44] = cube_tmp[47];
        cube[45] = cube_tmp[53];
        cube[46] = cube_tmp[59];
        cube[47] = cube_tmp[65];
        cube[48] = cube_tmp[71];
        cube[49] = cube_tmp[40];
        cube[50] = cube_tmp[46];
        cube[51] = cube_tmp[52];
        cube[52] = cube_tmp[58];
        cube[53] = cube_tmp[64];
        cube[54] = cube_tmp[70];
        cube[55] = cube_tmp[39];
        cube[56] = cube_tmp[45];
        cube[57] = cube_tmp[51];
        cube[58] = cube_tmp[57];
        cube[59] = cube_tmp[63];
        cube[60] = cube_tmp[69];
        cube[61] = cube_tmp[38];
        cube[62] = cube_tmp[44];
        cube[63] = cube_tmp[50];
        cube[64] = cube_tmp[56];
        cube[65] = cube_tmp[62];
        cube[66] = cube_tmp[68];
        cube[67] = cube_tmp[37];
        cube[68] = cube_tmp[43];
        cube[69] = cube_tmp[49];
        cube[70] = cube_tmp[55];
        cube[71] = cube_tmp[61];
        cube[72] = cube_tmp[67];
        cube[73] = cube_tmp[181];
        cube[74] = cube_tmp[182];
        cube[79] = cube_tmp[187];
        cube[80] = cube_tmp[188];
        cube[85] = cube_tmp[193];
        cube[86] = cube_tmp[194];
        cube[91] = cube_tmp[199];
        cube[92] = cube_tmp[200];
        cube[97] = cube_tmp[205];
        cube[98] = cube_tmp[206];
        cube[103] = cube_tmp[211];
        cube[104] = cube_tmp[212];
        cube[149] = cube_tmp[32];
        cube[150] = cube_tmp[31];
        cube[155] = cube_tmp[26];
        cube[156] = cube_tmp[25];
        cube[161] = cube_tmp[20];
        cube[162] = cube_tmp[19];
        cube[167] = cube_tmp[14];
        cube[168] = cube_tmp[13];
        cube[173] = cube_tmp[8];
        cube[174] = cube_tmp[7];
        cube[179] = cube_tmp[2];
        cube[180] = cube_tmp[1];
        cube[181] = cube_tmp[180];
        cube[182] = cube_tmp[179];
        cube[187] = cube_tmp[174];
        cube[188] = cube_tmp[173];
        cube[193] = cube_tmp[168];
        cube[194] = cube_tmp[167];
        cube[199] = cube_tmp[162];
        cube[200] = cube_tmp[161];
        cube[205] = cube_tmp[156];
        cube[206] = cube_tmp[155];
        cube[211] = cube_tmp[150];
        cube[212] = cube_tmp[149];
        break;
    }

    case Lw2: {
        cube[1] = cube_tmp[181];
        cube[2] = cube_tmp[182];
        cube[7] = cube_tmp[187];
        cube[8] = cube_tmp[188];
        cube[13] = cube_tmp[193];
        cube[14] = cube_tmp[194];
        cube[19] = cube_tmp[199];
        cube[20] = cube_tmp[200];
        cube[25] = cube_tmp[205];
        cube[26] = cube_tmp[206];
        cube[31] = cube_tmp[211];
        cube[32] = cube_tmp[212];
        cube[37] = cube_tmp[72];
        cube[38] = cube_tmp[71];
        cube[39] = cube_tmp[70];
        cube[40] = cube_tmp[69];
        cube[41] = cube_tmp[68];
        cube[42] = cube_tmp[67];
        cube[43] = cube_tmp[66];
        cube[44] = cube_tmp[65];
        cube[45] = cube_tmp[64];
        cube[46] = cube_tmp[63];
        cube[47] = cube_tmp[62];
        cube[48] = cube_tmp[61];
        cube[49] = cube_tmp[60];
        cube[50] = cube_tmp[59];
        cube[51] = cube_tmp[58];
        cube[52] = cube_tmp[57];
        cube[53] = cube_tmp[56];
        cube[54] = cube_tmp[55];
        cube[55] = cube_tmp[54];
        cube[56] = cube_tmp[53];
        cube[57] = cube_tmp[52];
        cube[58] = cube_tmp[51];
        cube[59] = cube_tmp[50];
        cube[60] = cube_tmp[49];
        cube[61] = cube_tmp[48];
        cube[62] = cube_tmp[47];
        cube[63] = cube_tmp[46];
        cube[64] = cube_tmp[45];
        cube[65] = cube_tmp[44];
        cube[66] = cube_tmp[43];
        cube[67] = cube_tmp[42];
        cube[68] = cube_tmp[41];
        cube[69] = cube_tmp[40];
        cube[70] = cube_tmp[39];
        cube[71] = cube_tmp[38];
        cube[72] = cube_tmp[37];
        cube[73] = cube_tmp[180];
        cube[74] = cube_tmp[179];
        cube[79] = cube_tmp[174];
        cube[80] = cube_tmp[173];
        cube[85] = cube_tmp[168];
        cube[86] = cube_tmp[167];
        cube[91] = cube_tmp[162];
        cube[92] = cube_tmp[161];
        cube[97] = cube_tmp[156];
        cube[98] = cube_tmp[155];
        cube[103] = cube_tmp[150];
        cube[104] = cube_tmp[149];
        cube[149] = cube_tmp[104];
        cube[150] = cube_tmp[103];
        cube[155] = cube_tmp[98];
        cube[156] = cube_tmp[97];
        cube[161] = cube_tmp[92];
        cube[162] = cube_tmp[91];
        cube[167] = cube_tmp[86];
        cube[168] = cube_tmp[85];
        cube[173] = cube_tmp[80];
        cube[174] = cube_tmp[79];
        cube[179] = cube_tmp[74];
        cube[180] = cube_tmp[73];
        cube[181] = cube_tmp[1];
        cube[182] = cube_tmp[2];
        cube[187] = cube_tmp[7];
        cube[188] = cube_tmp[8];
        cube[193] = cube_tmp[13];
        cube[194] = cube_tmp[14];
        cube[199] = cube_tmp[19];
        cube[200] = cube_tmp[20];
        cube[205] = cube_tmp[25];
        cube[206] = cube_tmp[26];
        cube[211] = cube_tmp[31];
        cube[212] = cube_tmp[32];
        break;
    }

    case threeLw: {
        cube[1] = cube_tmp[180];
        cube[2] = cube_tmp[179];
        cube[3] = cube_tmp[178];
        cube[7] = cube_tmp[174];
        cube[8] = cube_tmp[173];
        cube[9] = cube_tmp[172];
        cube[13] = cube_tmp[168];
        cube[14] = cube_tmp[167];
        cube[15] = cube_tmp[166];
        cube[19] = cube_tmp[162];
        cube[20] = cube_tmp[161];
        cube[21] = cube_tmp[160];
        cube[25] = cube_tmp[156];
        cube[26] = cube_tmp[155];
        cube[27] = cube_tmp[154];
        cube[31] = cube_tmp[150];
        cube[32] = cube_tmp[149];
        cube[33] = cube_tmp[148];
        cube[37] = cube_tmp[67];
        cube[38] = cube_tmp[61];
        cube[39] = cube_tmp[55];
        cube[40] = cube_tmp[49];
        cube[41] = cube_tmp[43];
        cube[42] = cube_tmp[37];
        cube[43] = cube_tmp[68];
        cube[44] = cube_tmp[62];
        cube[45] = cube_tmp[56];
        cube[46] = cube_tmp[50];
        cube[47] = cube_tmp[44];
        cube[48] = cube_tmp[38];
        cube[49] = cube_tmp[69];
        cube[50] = cube_tmp[63];
        cube[51] = cube_tmp[57];
        cube[52] = cube_tmp[51];
        cube[53] = cube_tmp[45];
        cube[54] = cube_tmp[39];
        cube[55] = cube_tmp[70];
        cube[56] = cube_tmp[64];
        cube[57] = cube_tmp[58];
        cube[58] = cube_tmp[52];
        cube[59] = cube_tmp[46];
        cube[60] = cube_tmp[40];
        cube[61] = cube_tmp[71];
        cube[62] = cube_tmp[65];
        cube[63] = cube_tmp[59];
        cube[64] = cube_tmp[53];
        cube[65] = cube_tmp[47];
        cube[66] = cube_tmp[41];
        cube[67] = cube_tmp[72];
        cube[68] = cube_tmp[66];
        cube[69] = cube_tmp[60];
        cube[70] = cube_tmp[54];
        cube[71] = cube_tmp[48];
        cube[72] = cube_tmp[42];
        cube[73] = cube_tmp[1];
        cube[74] = cube_tmp[2];
        cube[75] = cube_tmp[3];
        cube[79] = cube_tmp[7];
        cube[80] = cube_tmp[8];
        cube[81] = cube_tmp[9];
        cube[85] = cube_tmp[13];
        cube[86] = cube_tmp[14];
        cube[87] = cube_tmp[15];
        cube[91] = cube_tmp[19];
        cube[92] = cube_tmp[20];
        cube[93] = cube_tmp[21];
        cube[97] = cube_tmp[25];
        cube[98] = cube_tmp[26];
        cube[99] = cube_tmp[27];
        cube[103] = cube_tmp[31];
        cube[104] = cube_tmp[32];
        cube[105] = cube_tmp[33];
        cube[148] = cube_tmp[213];
        cube[149] = cube_tmp[212];
        cube[150] = cube_tmp[211];
        cube[154] = cube_tmp[207];
        cube[155] = cube_tmp[206];
        cube[156] = cube_tmp[205];
        cube[160] = cube_tmp[201];
        cube[161] = cube_tmp[200];
        cube[162] = cube_tmp[199];
        cube[166] = cube_tmp[195];
        cube[167] = cube_tmp[194];
        cube[168] = cube_tmp[193];
        cube[172] = cube_tmp[189];
        cube[173] = cube_tmp[188];
        cube[174] = cube_tmp[187];
        cube[178] = cube_tmp[183];
        cube[179] = cube_tmp[182];
        cube[180] = cube_tmp[181];
        cube[181] = cube_tmp[73];
        cube[182] = cube_tmp[74];
        cube[183] = cube_tmp[75];
        cube[187] = cube_tmp[79];
        cube[188] = cube_tmp[80];
        cube[189] = cube_tmp[81];
        cube[193] = cube_tmp[85];
        cube[194] = cube_tmp[86];
        cube[195] = cube_tmp[87];
        cube[199] = cube_tmp[91];
        cube[200] = cube_tmp[92];
        cube[201] = cube_tmp[93];
        cube[205] = cube_tmp[97];
        cube[206] = cube_tmp[98];
        cube[207] = cube_tmp[99];
        cube[211] = cube_tmp[103];
        cube[212] = cube_tmp[104];
        cube[213] = cube_tmp[105];
        break;
    }

    case threeLw_PRIME: {
        cube[1] = cube_tmp[73];
        cube[2] = cube_tmp[74];
        cube[3] = cube_tmp[75];
        cube[7] = cube_tmp[79];
        cube[8] = cube_tmp[80];
        cube[9] = cube_tmp[81];
        cube[13] = cube_tmp[85];
        cube[14] = cube_tmp[86];
        cube[15] = cube_tmp[87];
        cube[19] = cube_tmp[91];
        cube[20] = cube_tmp[92];
        cube[21] = cube_tmp[93];
        cube[25] = cube_tmp[97];
        cube[26] = cube_tmp[98];
        cube[27] = cube_tmp[99];
        cube[31] = cube_tmp[103];
        cube[32] = cube_tmp[104];
        cube[33] = cube_tmp[105];
        cube[37] = cube_tmp[42];
        cube[38] = cube_tmp[48];
        cube[39] = cube_tmp[54];
        cube[40] = cube_tmp[60];
        cube[41] = cube_tmp[66];
        cube[42] = cube_tmp[72];
        cube[43] = cube_tmp[41];
        cube[44] = cube_tmp[47];
        cube[45] = cube_tmp[53];
        cube[46] = cube_tmp[59];
        cube[47] = cube_tmp[65];
        cube[48] = cube_tmp[71];
        cube[49] = cube_tmp[40];
        cube[50] = cube_tmp[46];
        cube[51] = cube_tmp[52];
        cube[52] = cube_tmp[58];
        cube[53] = cube_tmp[64];
        cube[54] = cube_tmp[70];
        cube[55] = cube_tmp[39];
        cube[56] = cube_tmp[45];
        cube[57] = cube_tmp[51];
        cube[58] = cube_tmp[57];
        cube[59] = cube_tmp[63];
        cube[60] = cube_tmp[69];
        cube[61] = cube_tmp[38];
        cube[62] = cube_tmp[44];
        cube[63] = cube_tmp[50];
        cube[64] = cube_tmp[56];
        cube[65] = cube_tmp[62];
        cube[66] = cube_tmp[68];
        cube[67] = cube_tmp[37];
        cube[68] = cube_tmp[43];
        cube[69] = cube_tmp[49];
        cube[70] = cube_tmp[55];
        cube[71] = cube_tmp[61];
        cube[72] = cube_tmp[67];
        cube[73] = cube_tmp[181];
        cube[74] = cube_tmp[182];
        cube[75] = cube_tmp[183];
        cube[79] = cube_tmp[187];
        cube[80] = cube_tmp[188];
        cube[81] = cube_tmp[189];
        cube[85] = cube_tmp[193];
        cube[86] = cube_tmp[194];
        cube[87] = cube_tmp[195];
        cube[91] = cube_tmp[199];
        cube[92] = cube_tmp[200];
        cube[93] = cube_tmp[201];
        cube[97] = cube_tmp[205];
        cube[98] = cube_tmp[206];
        cube[99] = cube_tmp[207];
        cube[103] = cube_tmp[211];
        cube[104] = cube_tmp[212];
        cube[105] = cube_tmp[213];
        cube[148] = cube_tmp[33];
        cube[149] = cube_tmp[32];
        cube[150] = cube_tmp[31];
        cube[154] = cube_tmp[27];
        cube[155] = cube_tmp[26];
        cube[156] = cube_tmp[25];
        cube[160] = cube_tmp[21];
        cube[161] = cube_tmp[20];
        cube[162] = cube_tmp[19];
        cube[166] = cube_tmp[15];
        cube[167] = cube_tmp[14];
        cube[168] = cube_tmp[13];
        cube[172] = cube_tmp[9];
        cube[173] = cube_tmp[8];
        cube[174] = cube_tmp[7];
        cube[178] = cube_tmp[3];
        cube[179] = cube_tmp[2];
        cube[180] = cube_tmp[1];
        cube[181] = cube_tmp[180];
        cube[182] = cube_tmp[179];
        cube[183] = cube_tmp[178];
        cube[187] = cube_tmp[174];
        cube[188] = cube_tmp[173];
        cube[189] = cube_tmp[172];
        cube[193] = cube_tmp[168];
        cube[194] = cube_tmp[167];
        cube[195] = cube_tmp[166];
        cube[199] = cube_tmp[162];
        cube[200] = cube_tmp[161];
        cube[201] = cube_tmp[160];
        cube[205] = cube_tmp[156];
        cube[206] = cube_tmp[155];
        cube[207] = cube_tmp[154];
        cube[211] = cube_tmp[150];
        cube[212] = cube_tmp[149];
        cube[213] = cube_tmp[148];
        break;
    }

    case threeLw2: {
        cube[1] = cube_tmp[181];
        cube[2] = cube_tmp[182];
        cube[3] = cube_tmp[183];
        cube[7] = cube_tmp[187];
        cube[8] = cube_tmp[188];
        cube[9] = cube_tmp[189];
        cube[13] = cube_tmp[193];
        cube[14] = cube_tmp[194];
        cube[15] = cube_tmp[195];
        cube[19] = cube_tmp[199];
        cube[20] = cube_tmp[200];
        cube[21] = cube_tmp[201];
        cube[25] = cube_tmp[205];
        cube[26] = cube_tmp[206];
        cube[27] = cube_tmp[207];
        cube[31] = cube_tmp[211];
        cube[32] = cube_tmp[212];
        cube[33] = cube_tmp[213];
        cube[37] = cube_tmp[72];
        cube[38] = cube_tmp[71];
        cube[39] = cube_tmp[70];
        cube[40] = cube_tmp[69];
        cube[41] = cube_tmp[68];
        cube[42] = cube_tmp[67];
        cube[43] = cube_tmp[66];
        cube[44] = cube_tmp[65];
        cube[45] = cube_tmp[64];
        cube[46] = cube_tmp[63];
        cube[47] = cube_tmp[62];
        cube[48] = cube_tmp[61];
        cube[49] = cube_tmp[60];
        cube[50] = cube_tmp[59];
        cube[51] = cube_tmp[58];
        cube[52] = cube_tmp[57];
        cube[53] = cube_tmp[56];
        cube[54] = cube_tmp[55];
        cube[55] = cube_tmp[54];
        cube[56] = cube_tmp[53];
        cube[57] = cube_tmp[52];
        cube[58] = cube_tmp[51];
        cube[59] = cube_tmp[50];
        cube[60] = cube_tmp[49];
        cube[61] = cube_tmp[48];
        cube[62] = cube_tmp[47];
        cube[63] = cube_tmp[46];
        cube[64] = cube_tmp[45];
        cube[65] = cube_tmp[44];
        cube[66] = cube_tmp[43];
        cube[67] = cube_tmp[42];
        cube[68] = cube_tmp[41];
        cube[69] = cube_tmp[40];
        cube[70] = cube_tmp[39];
        cube[71] = cube_tmp[38];
        cube[72] = cube_tmp[37];
        cube[73] = cube_tmp[180];
        cube[74] = cube_tmp[179];
        cube[75] = cube_tmp[178];
        cube[79] = cube_tmp[174];
        cube[80] = cube_tmp[173];
        cube[81] = cube_tmp[172];
        cube[85] = cube_tmp[168];
        cube[86] = cube_tmp[167];
        cube[87] = cube_tmp[166];
        cube[91] = cube_tmp[162];
        cube[92] = cube_tmp[161];
        cube[93] = cube_tmp[160];
        cube[97] = cube_tmp[156];
        cube[98] = cube_tmp[155];
        cube[99] = cube_tmp[154];
        cube[103] = cube_tmp[150];
        cube[104] = cube_tmp[149];
        cube[105] = cube_tmp[148];
        cube[148] = cube_tmp[105];
        cube[149] = cube_tmp[104];
        cube[150] = cube_tmp[103];
        cube[154] = cube_tmp[99];
        cube[155] = cube_tmp[98];
        cube[156] = cube_tmp[97];
        cube[160] = cube_tmp[93];
        cube[161] = cube_tmp[92];
        cube[162] = cube_tmp[91];
        cube[166] = cube_tmp[87];
        cube[167] = cube_tmp[86];
        cube[168] = cube_tmp[85];
        cube[172] = cube_tmp[81];
        cube[173] = cube_tmp[80];
        cube[174] = cube_tmp[79];
        cube[178] = cube_tmp[75];
        cube[179] = cube_tmp[74];
        cube[180] = cube_tmp[73];
        cube[181] = cube_tmp[1];
        cube[182] = cube_tmp[2];
        cube[183] = cube_tmp[3];
        cube[187] = cube_tmp[7];
        cube[188] = cube_tmp[8];
        cube[189] = cube_tmp[9];
        cube[193] = cube_tmp[13];
        cube[194] = cube_tmp[14];
        cube[195] = cube_tmp[15];
        cube[199] = cube_tmp[19];
        cube[200] = cube_tmp[20];
        cube[201] = cube_tmp[21];
        cube[205] = cube_tmp[25];
        cube[206] = cube_tmp[26];
        cube[207] = cube_tmp[27];
        cube[211] = cube_tmp[31];
        cube[212] = cube_tmp[32];
        cube[213] = cube_tmp[33];
        break;
    }

    case F: {
        cube[31] = cube_tmp[72];
        cube[32] = cube_tmp[66];
        cube[33] = cube_tmp[60];
        cube[34] = cube_tmp[54];
        cube[35] = cube_tmp[48];
        cube[36] = cube_tmp[42];
        cube[42] = cube_tmp[181];
        cube[48] = cube_tmp[182];
        cube[54] = cube_tmp[183];
        cube[60] = cube_tmp[184];
        cube[66] = cube_tmp[185];
        cube[72] = cube_tmp[186];
        cube[73] = cube_tmp[103];
        cube[74] = cube_tmp[97];
        cube[75] = cube_tmp[91];
        cube[76] = cube_tmp[85];
        cube[77] = cube_tmp[79];
        cube[78] = cube_tmp[73];
        cube[79] = cube_tmp[104];
        cube[80] = cube_tmp[98];
        cube[81] = cube_tmp[92];
        cube[82] = cube_tmp[86];
        cube[83] = cube_tmp[80];
        cube[84] = cube_tmp[74];
        cube[85] = cube_tmp[105];
        cube[86] = cube_tmp[99];
        cube[87] = cube_tmp[93];
        cube[88] = cube_tmp[87];
        cube[89] = cube_tmp[81];
        cube[90] = cube_tmp[75];
        cube[91] = cube_tmp[106];
        cube[92] = cube_tmp[100];
        cube[93] = cube_tmp[94];
        cube[94] = cube_tmp[88];
        cube[95] = cube_tmp[82];
        cube[96] = cube_tmp[76];
        cube[97] = cube_tmp[107];
        cube[98] = cube_tmp[101];
        cube[99] = cube_tmp[95];
        cube[100] = cube_tmp[89];
        cube[101] = cube_tmp[83];
        cube[102] = cube_tmp[77];
        cube[103] = cube_tmp[108];
        cube[104] = cube_tmp[102];
        cube[105] = cube_tmp[96];
        cube[106] = cube_tmp[90];
        cube[107] = cube_tmp[84];
        cube[108] = cube_tmp[78];
        cube[109] = cube_tmp[31];
        cube[115] = cube_tmp[32];
        cube[121] = cube_tmp[33];
        cube[127] = cube_tmp[34];
        cube[133] = cube_tmp[35];
        cube[139] = cube_tmp[36];
        cube[181] = cube_tmp[139];
        cube[182] = cube_tmp[133];
        cube[183] = cube_tmp[127];
        cube[184] = cube_tmp[121];
        cube[185] = cube_tmp[115];
        cube[186] = cube_tmp[109];
        break;
    }

    case F_PRIME: {
        cube[31] = cube_tmp[109];
        cube[32] = cube_tmp[115];
        cube[33] = cube_tmp[121];
        cube[34] = cube_tmp[127];
        cube[35] = cube_tmp[133];
        cube[36] = cube_tmp[139];
        cube[42] = cube_tmp[36];
        cube[48] = cube_tmp[35];
        cube[54] = cube_tmp[34];
        cube[60] = cube_tmp[33];
        cube[66] = cube_tmp[32];
        cube[72] = cube_tmp[31];
        cube[73] = cube_tmp[78];
        cube[74] = cube_tmp[84];
        cube[75] = cube_tmp[90];
        cube[76] = cube_tmp[96];
        cube[77] = cube_tmp[102];
        cube[78] = cube_tmp[108];
        cube[79] = cube_tmp[77];
        cube[80] = cube_tmp[83];
        cube[81] = cube_tmp[89];
        cube[82] = cube_tmp[95];
        cube[83] = cube_tmp[101];
        cube[84] = cube_tmp[107];
        cube[85] = cube_tmp[76];
        cube[86] = cube_tmp[82];
        cube[87] = cube_tmp[88];
        cube[88] = cube_tmp[94];
        cube[89] = cube_tmp[100];
        cube[90] = cube_tmp[106];
        cube[91] = cube_tmp[75];
        cube[92] = cube_tmp[81];
        cube[93] = cube_tmp[87];
        cube[94] = cube_tmp[93];
        cube[95] = cube_tmp[99];
        cube[96] = cube_tmp[105];
        cube[97] = cube_tmp[74];
        cube[98] = cube_tmp[80];
        cube[99] = cube_tmp[86];
        cube[100] = cube_tmp[92];
        cube[101] = cube_tmp[98];
        cube[102] = cube_tmp[104];
        cube[103] = cube_tmp[73];
        cube[104] = cube_tmp[79];
        cube[105] = cube_tmp[85];
        cube[106] = cube_tmp[91];
        cube[107] = cube_tmp[97];
        cube[108] = cube_tmp[103];
        cube[109] = cube_tmp[186];
        cube[115] = cube_tmp[185];
        cube[121] = cube_tmp[184];
        cube[127] = cube_tmp[183];
        cube[133] = cube_tmp[182];
        cube[139] = cube_tmp[181];
        cube[181] = cube_tmp[42];
        cube[182] = cube_tmp[48];
        cube[183] = cube_tmp[54];
        cube[184] = cube_tmp[60];
        cube[185] = cube_tmp[66];
        cube[186] = cube_tmp[72];
        break;
    }

    case F2: {
        cube[31] = cube_tmp[186];
        cube[32] = cube_tmp[185];
        cube[33] = cube_tmp[184];
        cube[34] = cube_tmp[183];
        cube[35] = cube_tmp[182];
        cube[36] = cube_tmp[181];
        cube[42] = cube_tmp[139];
        cube[48] = cube_tmp[133];
        cube[54] = cube_tmp[127];
        cube[60] = cube_tmp[121];
        cube[66] = cube_tmp[115];
        cube[72] = cube_tmp[109];
        cube[73] = cube_tmp[108];
        cube[74] = cube_tmp[107];
        cube[75] = cube_tmp[106];
        cube[76] = cube_tmp[105];
        cube[77] = cube_tmp[104];
        cube[78] = cube_tmp[103];
        cube[79] = cube_tmp[102];
        cube[80] = cube_tmp[101];
        cube[81] = cube_tmp[100];
        cube[82] = cube_tmp[99];
        cube[83] = cube_tmp[98];
        cube[84] = cube_tmp[97];
        cube[85] = cube_tmp[96];
        cube[86] = cube_tmp[95];
        cube[87] = cube_tmp[94];
        cube[88] = cube_tmp[93];
        cube[89] = cube_tmp[92];
        cube[90] = cube_tmp[91];
        cube[91] = cube_tmp[90];
        cube[92] = cube_tmp[89];
        cube[93] = cube_tmp[88];
        cube[94] = cube_tmp[87];
        cube[95] = cube_tmp[86];
        cube[96] = cube_tmp[85];
        cube[97] = cube_tmp[84];
        cube[98] = cube_tmp[83];
        cube[99] = cube_tmp[82];
        cube[100] = cube_tmp[81];
        cube[101] = cube_tmp[80];
        cube[102] = cube_tmp[79];
        cube[103] = cube_tmp[78];
        cube[104] = cube_tmp[77];
        cube[105] = cube_tmp[76];
        cube[106] = cube_tmp[75];
        cube[107] = cube_tmp[74];
        cube[108] = cube_tmp[73];
        cube[109] = cube_tmp[72];
        cube[115] = cube_tmp[66];
        cube[121] = cube_tmp[60];
        cube[127] = cube_tmp[54];
        cube[133] = cube_tmp[48];
        cube[139] = cube_tmp[42];
        cube[181] = cube_tmp[36];
        cube[182] = cube_tmp[35];
        cube[183] = cube_tmp[34];
        cube[184] = cube_tmp[33];
        cube[185] = cube_tmp[32];
        cube[186] = cube_tmp[31];
        break;
    }

    case Fw: {
        cube[25] = cube_tmp[71];
        cube[26] = cube_tmp[65];
        cube[27] = cube_tmp[59];
        cube[28] = cube_tmp[53];
        cube[29] = cube_tmp[47];
        cube[30] = cube_tmp[41];
        cube[31] = cube_tmp[72];
        cube[32] = cube_tmp[66];
        cube[33] = cube_tmp[60];
        cube[34] = cube_tmp[54];
        cube[35] = cube_tmp[48];
        cube[36] = cube_tmp[42];
        cube[41] = cube_tmp[187];
        cube[42] = cube_tmp[181];
        cube[47] = cube_tmp[188];
        cube[48] = cube_tmp[182];
        cube[53] = cube_tmp[189];
        cube[54] = cube_tmp[183];
        cube[59] = cube_tmp[190];
        cube[60] = cube_tmp[184];
        cube[65] = cube_tmp[191];
        cube[66] = cube_tmp[185];
        cube[71] = cube_tmp[192];
        cube[72] = cube_tmp[186];
        cube[73] = cube_tmp[103];
        cube[74] = cube_tmp[97];
        cube[75] = cube_tmp[91];
        cube[76] = cube_tmp[85];
        cube[77] = cube_tmp[79];
        cube[78] = cube_tmp[73];
        cube[79] = cube_tmp[104];
        cube[80] = cube_tmp[98];
        cube[81] = cube_tmp[92];
        cube[82] = cube_tmp[86];
        cube[83] = cube_tmp[80];
        cube[84] = cube_tmp[74];
        cube[85] = cube_tmp[105];
        cube[86] = cube_tmp[99];
        cube[87] = cube_tmp[93];
        cube[88] = cube_tmp[87];
        cube[89] = cube_tmp[81];
        cube[90] = cube_tmp[75];
        cube[91] = cube_tmp[106];
        cube[92] = cube_tmp[100];
        cube[93] = cube_tmp[94];
        cube[94] = cube_tmp[88];
        cube[95] = cube_tmp[82];
        cube[96] = cube_tmp[76];
        cube[97] = cube_tmp[107];
        cube[98] = cube_tmp[101];
        cube[99] = cube_tmp[95];
        cube[100] = cube_tmp[89];
        cube[101] = cube_tmp[83];
        cube[102] = cube_tmp[77];
        cube[103] = cube_tmp[108];
        cube[104] = cube_tmp[102];
        cube[105] = cube_tmp[96];
        cube[106] = cube_tmp[90];
        cube[107] = cube_tmp[84];
        cube[108] = cube_tmp[78];
        cube[109] = cube_tmp[31];
        cube[110] = cube_tmp[25];
        cube[115] = cube_tmp[32];
        cube[116] = cube_tmp[26];
        cube[121] = cube_tmp[33];
        cube[122] = cube_tmp[27];
        cube[127] = cube_tmp[34];
        cube[128] = cube_tmp[28];
        cube[133] = cube_tmp[35];
        cube[134] = cube_tmp[29];
        cube[139] = cube_tmp[36];
        cube[140] = cube_tmp[30];
        cube[181] = cube_tmp[139];
        cube[182] = cube_tmp[133];
        cube[183] = cube_tmp[127];
        cube[184] = cube_tmp[121];
        cube[185] = cube_tmp[115];
        cube[186] = cube_tmp[109];
        cube[187] = cube_tmp[140];
        cube[188] = cube_tmp[134];
        cube[189] = cube_tmp[128];
        cube[190] = cube_tmp[122];
        cube[191] = cube_tmp[116];
        cube[192] = cube_tmp[110];
        break;
    }

    case Fw_PRIME: {
        cube[25] = cube_tmp[110];
        cube[26] = cube_tmp[116];
        cube[27] = cube_tmp[122];
        cube[28] = cube_tmp[128];
        cube[29] = cube_tmp[134];
        cube[30] = cube_tmp[140];
        cube[31] = cube_tmp[109];
        cube[32] = cube_tmp[115];
        cube[33] = cube_tmp[121];
        cube[34] = cube_tmp[127];
        cube[35] = cube_tmp[133];
        cube[36] = cube_tmp[139];
        cube[41] = cube_tmp[30];
        cube[42] = cube_tmp[36];
        cube[47] = cube_tmp[29];
        cube[48] = cube_tmp[35];
        cube[53] = cube_tmp[28];
        cube[54] = cube_tmp[34];
        cube[59] = cube_tmp[27];
        cube[60] = cube_tmp[33];
        cube[65] = cube_tmp[26];
        cube[66] = cube_tmp[32];
        cube[71] = cube_tmp[25];
        cube[72] = cube_tmp[31];
        cube[73] = cube_tmp[78];
        cube[74] = cube_tmp[84];
        cube[75] = cube_tmp[90];
        cube[76] = cube_tmp[96];
        cube[77] = cube_tmp[102];
        cube[78] = cube_tmp[108];
        cube[79] = cube_tmp[77];
        cube[80] = cube_tmp[83];
        cube[81] = cube_tmp[89];
        cube[82] = cube_tmp[95];
        cube[83] = cube_tmp[101];
        cube[84] = cube_tmp[107];
        cube[85] = cube_tmp[76];
        cube[86] = cube_tmp[82];
        cube[87] = cube_tmp[88];
        cube[88] = cube_tmp[94];
        cube[89] = cube_tmp[100];
        cube[90] = cube_tmp[106];
        cube[91] = cube_tmp[75];
        cube[92] = cube_tmp[81];
        cube[93] = cube_tmp[87];
        cube[94] = cube_tmp[93];
        cube[95] = cube_tmp[99];
        cube[96] = cube_tmp[105];
        cube[97] = cube_tmp[74];
        cube[98] = cube_tmp[80];
        cube[99] = cube_tmp[86];
        cube[100] = cube_tmp[92];
        cube[101] = cube_tmp[98];
        cube[102] = cube_tmp[104];
        cube[103] = cube_tmp[73];
        cube[104] = cube_tmp[79];
        cube[105] = cube_tmp[85];
        cube[106] = cube_tmp[91];
        cube[107] = cube_tmp[97];
        cube[108] = cube_tmp[103];
        cube[109] = cube_tmp[186];
        cube[110] = cube_tmp[192];
        cube[115] = cube_tmp[185];
        cube[116] = cube_tmp[191];
        cube[121] = cube_tmp[184];
        cube[122] = cube_tmp[190];
        cube[127] = cube_tmp[183];
        cube[128] = cube_tmp[189];
        cube[133] = cube_tmp[182];
        cube[134] = cube_tmp[188];
        cube[139] = cube_tmp[181];
        cube[140] = cube_tmp[187];
        cube[181] = cube_tmp[42];
        cube[182] = cube_tmp[48];
        cube[183] = cube_tmp[54];
        cube[184] = cube_tmp[60];
        cube[185] = cube_tmp[66];
        cube[186] = cube_tmp[72];
        cube[187] = cube_tmp[41];
        cube[188] = cube_tmp[47];
        cube[189] = cube_tmp[53];
        cube[190] = cube_tmp[59];
        cube[191] = cube_tmp[65];
        cube[192] = cube_tmp[71];
        break;
    }

    case Fw2: {
        cube[25] = cube_tmp[192];
        cube[26] = cube_tmp[191];
        cube[27] = cube_tmp[190];
        cube[28] = cube_tmp[189];
        cube[29] = cube_tmp[188];
        cube[30] = cube_tmp[187];
        cube[31] = cube_tmp[186];
        cube[32] = cube_tmp[185];
        cube[33] = cube_tmp[184];
        cube[34] = cube_tmp[183];
        cube[35] = cube_tmp[182];
        cube[36] = cube_tmp[181];
        cube[41] = cube_tmp[140];
        cube[42] = cube_tmp[139];
        cube[47] = cube_tmp[134];
        cube[48] = cube_tmp[133];
        cube[53] = cube_tmp[128];
        cube[54] = cube_tmp[127];
        cube[59] = cube_tmp[122];
        cube[60] = cube_tmp[121];
        cube[65] = cube_tmp[116];
        cube[66] = cube_tmp[115];
        cube[71] = cube_tmp[110];
        cube[72] = cube_tmp[109];
        cube[73] = cube_tmp[108];
        cube[74] = cube_tmp[107];
        cube[75] = cube_tmp[106];
        cube[76] = cube_tmp[105];
        cube[77] = cube_tmp[104];
        cube[78] = cube_tmp[103];
        cube[79] = cube_tmp[102];
        cube[80] = cube_tmp[101];
        cube[81] = cube_tmp[100];
        cube[82] = cube_tmp[99];
        cube[83] = cube_tmp[98];
        cube[84] = cube_tmp[97];
        cube[85] = cube_tmp[96];
        cube[86] = cube_tmp[95];
        cube[87] = cube_tmp[94];
        cube[88] = cube_tmp[93];
        cube[89] = cube_tmp[92];
        cube[90] = cube_tmp[91];
        cube[91] = cube_tmp[90];
        cube[92] = cube_tmp[89];
        cube[93] = cube_tmp[88];
        cube[94] = cube_tmp[87];
        cube[95] = cube_tmp[86];
        cube[96] = cube_tmp[85];
        cube[97] = cube_tmp[84];
        cube[98] = cube_tmp[83];
        cube[99] = cube_tmp[82];
        cube[100] = cube_tmp[81];
        cube[101] = cube_tmp[80];
        cube[102] = cube_tmp[79];
        cube[103] = cube_tmp[78];
        cube[104] = cube_tmp[77];
        cube[105] = cube_tmp[76];
        cube[106] = cube_tmp[75];
        cube[107] = cube_tmp[74];
        cube[108] = cube_tmp[73];
        cube[109] = cube_tmp[72];
        cube[110] = cube_tmp[71];
        cube[115] = cube_tmp[66];
        cube[116] = cube_tmp[65];
        cube[121] = cube_tmp[60];
        cube[122] = cube_tmp[59];
        cube[127] = cube_tmp[54];
        cube[128] = cube_tmp[53];
        cube[133] = cube_tmp[48];
        cube[134] = cube_tmp[47];
        cube[139] = cube_tmp[42];
        cube[140] = cube_tmp[41];
        cube[181] = cube_tmp[36];
        cube[182] = cube_tmp[35];
        cube[183] = cube_tmp[34];
        cube[184] = cube_tmp[33];
        cube[185] = cube_tmp[32];
        cube[186] = cube_tmp[31];
        cube[187] = cube_tmp[30];
        cube[188] = cube_tmp[29];
        cube[189] = cube_tmp[28];
        cube[190] = cube_tmp[27];
        cube[191] = cube_tmp[26];
        cube[192] = cube_tmp[25];
        break;
    }

    case threeFw: {
        cube[19] = cube_tmp[70];
        cube[20] = cube_tmp[64];
        cube[21] = cube_tmp[58];
        cube[22] = cube_tmp[52];
        cube[23] = cube_tmp[46];
        cube[24] = cube_tmp[40];
        cube[25] = cube_tmp[71];
        cube[26] = cube_tmp[65];
        cube[27] = cube_tmp[59];
        cube[28] = cube_tmp[53];
        cube[29] = cube_tmp[47];
        cube[30] = cube_tmp[41];
        cube[31] = cube_tmp[72];
        cube[32] = cube_tmp[66];
        cube[33] = cube_tmp[60];
        cube[34] = cube_tmp[54];
        cube[35] = cube_tmp[48];
        cube[36] = cube_tmp[42];
        cube[40] = cube_tmp[193];
        cube[41] = cube_tmp[187];
        cube[42] = cube_tmp[181];
        cube[46] = cube_tmp[194];
        cube[47] = cube_tmp[188];
        cube[48] = cube_tmp[182];
        cube[52] = cube_tmp[195];
        cube[53] = cube_tmp[189];
        cube[54] = cube_tmp[183];
        cube[58] = cube_tmp[196];
        cube[59] = cube_tmp[190];
        cube[60] = cube_tmp[184];
        cube[64] = cube_tmp[197];
        cube[65] = cube_tmp[191];
        cube[66] = cube_tmp[185];
        cube[70] = cube_tmp[198];
        cube[71] = cube_tmp[192];
        cube[72] = cube_tmp[186];
        cube[73] = cube_tmp[103];
        cube[74] = cube_tmp[97];
        cube[75] = cube_tmp[91];
        cube[76] = cube_tmp[85];
        cube[77] = cube_tmp[79];
        cube[78] = cube_tmp[73];
        cube[79] = cube_tmp[104];
        cube[80] = cube_tmp[98];
        cube[81] = cube_tmp[92];
        cube[82] = cube_tmp[86];
        cube[83] = cube_tmp[80];
        cube[84] = cube_tmp[74];
        cube[85] = cube_tmp[105];
        cube[86] = cube_tmp[99];
        cube[87] = cube_tmp[93];
        cube[88] = cube_tmp[87];
        cube[89] = cube_tmp[81];
        cube[90] = cube_tmp[75];
        cube[91] = cube_tmp[106];
        cube[92] = cube_tmp[100];
        cube[93] = cube_tmp[94];
        cube[94] = cube_tmp[88];
        cube[95] = cube_tmp[82];
        cube[96] = cube_tmp[76];
        cube[97] = cube_tmp[107];
        cube[98] = cube_tmp[101];
        cube[99] = cube_tmp[95];
        cube[100] = cube_tmp[89];
        cube[101] = cube_tmp[83];
        cube[102] = cube_tmp[77];
        cube[103] = cube_tmp[108];
        cube[104] = cube_tmp[102];
        cube[105] = cube_tmp[96];
        cube[106] = cube_tmp[90];
        cube[107] = cube_tmp[84];
        cube[108] = cube_tmp[78];
        cube[109] = cube_tmp[31];
        cube[110] = cube_tmp[25];
        cube[111] = cube_tmp[19];
        cube[115] = cube_tmp[32];
        cube[116] = cube_tmp[26];
        cube[117] = cube_tmp[20];
        cube[121] = cube_tmp[33];
        cube[122] = cube_tmp[27];
        cube[123] = cube_tmp[21];
        cube[127] = cube_tmp[34];
        cube[128] = cube_tmp[28];
        cube[129] = cube_tmp[22];
        cube[133] = cube_tmp[35];
        cube[134] = cube_tmp[29];
        cube[135] = cube_tmp[23];
        cube[139] = cube_tmp[36];
        cube[140] = cube_tmp[30];
        cube[141] = cube_tmp[24];
        cube[181] = cube_tmp[139];
        cube[182] = cube_tmp[133];
        cube[183] = cube_tmp[127];
        cube[184] = cube_tmp[121];
        cube[185] = cube_tmp[115];
        cube[186] = cube_tmp[109];
        cube[187] = cube_tmp[140];
        cube[188] = cube_tmp[134];
        cube[189] = cube_tmp[128];
        cube[190] = cube_tmp[122];
        cube[191] = cube_tmp[116];
        cube[192] = cube_tmp[110];
        cube[193] = cube_tmp[141];
        cube[194] = cube_tmp[135];
        cube[195] = cube_tmp[129];
        cube[196] = cube_tmp[123];
        cube[197] = cube_tmp[117];
        cube[198] = cube_tmp[111];
        break;
    }

    case threeFw_PRIME: {
        cube[19] = cube_tmp[111];
        cube[20] = cube_tmp[117];
        cube[21] = cube_tmp[123];
        cube[22] = cube_tmp[129];
        cube[23] = cube_tmp[135];
        cube[24] = cube_tmp[141];
        cube[25] = cube_tmp[110];
        cube[26] = cube_tmp[116];
        cube[27] = cube_tmp[122];
        cube[28] = cube_tmp[128];
        cube[29] = cube_tmp[134];
        cube[30] = cube_tmp[140];
        cube[31] = cube_tmp[109];
        cube[32] = cube_tmp[115];
        cube[33] = cube_tmp[121];
        cube[34] = cube_tmp[127];
        cube[35] = cube_tmp[133];
        cube[36] = cube_tmp[139];
        cube[40] = cube_tmp[24];
        cube[41] = cube_tmp[30];
        cube[42] = cube_tmp[36];
        cube[46] = cube_tmp[23];
        cube[47] = cube_tmp[29];
        cube[48] = cube_tmp[35];
        cube[52] = cube_tmp[22];
        cube[53] = cube_tmp[28];
        cube[54] = cube_tmp[34];
        cube[58] = cube_tmp[21];
        cube[59] = cube_tmp[27];
        cube[60] = cube_tmp[33];
        cube[64] = cube_tmp[20];
        cube[65] = cube_tmp[26];
        cube[66] = cube_tmp[32];
        cube[70] = cube_tmp[19];
        cube[71] = cube_tmp[25];
        cube[72] = cube_tmp[31];
        cube[73] = cube_tmp[78];
        cube[74] = cube_tmp[84];
        cube[75] = cube_tmp[90];
        cube[76] = cube_tmp[96];
        cube[77] = cube_tmp[102];
        cube[78] = cube_tmp[108];
        cube[79] = cube_tmp[77];
        cube[80] = cube_tmp[83];
        cube[81] = cube_tmp[89];
        cube[82] = cube_tmp[95];
        cube[83] = cube_tmp[101];
        cube[84] = cube_tmp[107];
        cube[85] = cube_tmp[76];
        cube[86] = cube_tmp[82];
        cube[87] = cube_tmp[88];
        cube[88] = cube_tmp[94];
        cube[89] = cube_tmp[100];
        cube[90] = cube_tmp[106];
        cube[91] = cube_tmp[75];
        cube[92] = cube_tmp[81];
        cube[93] = cube_tmp[87];
        cube[94] = cube_tmp[93];
        cube[95] = cube_tmp[99];
        cube[96] = cube_tmp[105];
        cube[97] = cube_tmp[74];
        cube[98] = cube_tmp[80];
        cube[99] = cube_tmp[86];
        cube[100] = cube_tmp[92];
        cube[101] = cube_tmp[98];
        cube[102] = cube_tmp[104];
        cube[103] = cube_tmp[73];
        cube[104] = cube_tmp[79];
        cube[105] = cube_tmp[85];
        cube[106] = cube_tmp[91];
        cube[107] = cube_tmp[97];
        cube[108] = cube_tmp[103];
        cube[109] = cube_tmp[186];
        cube[110] = cube_tmp[192];
        cube[111] = cube_tmp[198];
        cube[115] = cube_tmp[185];
        cube[116] = cube_tmp[191];
        cube[117] = cube_tmp[197];
        cube[121] = cube_tmp[184];
        cube[122] = cube_tmp[190];
        cube[123] = cube_tmp[196];
        cube[127] = cube_tmp[183];
        cube[128] = cube_tmp[189];
        cube[129] = cube_tmp[195];
        cube[133] = cube_tmp[182];
        cube[134] = cube_tmp[188];
        cube[135] = cube_tmp[194];
        cube[139] = cube_tmp[181];
        cube[140] = cube_tmp[187];
        cube[141] = cube_tmp[193];
        cube[181] = cube_tmp[42];
        cube[182] = cube_tmp[48];
        cube[183] = cube_tmp[54];
        cube[184] = cube_tmp[60];
        cube[185] = cube_tmp[66];
        cube[186] = cube_tmp[72];
        cube[187] = cube_tmp[41];
        cube[188] = cube_tmp[47];
        cube[189] = cube_tmp[53];
        cube[190] = cube_tmp[59];
        cube[191] = cube_tmp[65];
        cube[192] = cube_tmp[71];
        cube[193] = cube_tmp[40];
        cube[194] = cube_tmp[46];
        cube[195] = cube_tmp[52];
        cube[196] = cube_tmp[58];
        cube[197] = cube_tmp[64];
        cube[198] = cube_tmp[70];
        break;
    }

    case threeFw2: {
        cube[19] = cube_tmp[198];
        cube[20] = cube_tmp[197];
        cube[21] = cube_tmp[196];
        cube[22] = cube_tmp[195];
        cube[23] = cube_tmp[194];
        cube[24] = cube_tmp[193];
        cube[25] = cube_tmp[192];
        cube[26] = cube_tmp[191];
        cube[27] = cube_tmp[190];
        cube[28] = cube_tmp[189];
        cube[29] = cube_tmp[188];
        cube[30] = cube_tmp[187];
        cube[31] = cube_tmp[186];
        cube[32] = cube_tmp[185];
        cube[33] = cube_tmp[184];
        cube[34] = cube_tmp[183];
        cube[35] = cube_tmp[182];
        cube[36] = cube_tmp[181];
        cube[40] = cube_tmp[141];
        cube[41] = cube_tmp[140];
        cube[42] = cube_tmp[139];
        cube[46] = cube_tmp[135];
        cube[47] = cube_tmp[134];
        cube[48] = cube_tmp[133];
        cube[52] = cube_tmp[129];
        cube[53] = cube_tmp[128];
        cube[54] = cube_tmp[127];
        cube[58] = cube_tmp[123];
        cube[59] = cube_tmp[122];
        cube[60] = cube_tmp[121];
        cube[64] = cube_tmp[117];
        cube[65] = cube_tmp[116];
        cube[66] = cube_tmp[115];
        cube[70] = cube_tmp[111];
        cube[71] = cube_tmp[110];
        cube[72] = cube_tmp[109];
        cube[73] = cube_tmp[108];
        cube[74] = cube_tmp[107];
        cube[75] = cube_tmp[106];
        cube[76] = cube_tmp[105];
        cube[77] = cube_tmp[104];
        cube[78] = cube_tmp[103];
        cube[79] = cube_tmp[102];
        cube[80] = cube_tmp[101];
        cube[81] = cube_tmp[100];
        cube[82] = cube_tmp[99];
        cube[83] = cube_tmp[98];
        cube[84] = cube_tmp[97];
        cube[85] = cube_tmp[96];
        cube[86] = cube_tmp[95];
        cube[87] = cube_tmp[94];
        cube[88] = cube_tmp[93];
        cube[89] = cube_tmp[92];
        cube[90] = cube_tmp[91];
        cube[91] = cube_tmp[90];
        cube[92] = cube_tmp[89];
        cube[93] = cube_tmp[88];
        cube[94] = cube_tmp[87];
        cube[95] = cube_tmp[86];
        cube[96] = cube_tmp[85];
        cube[97] = cube_tmp[84];
        cube[98] = cube_tmp[83];
        cube[99] = cube_tmp[82];
        cube[100] = cube_tmp[81];
        cube[101] = cube_tmp[80];
        cube[102] = cube_tmp[79];
        cube[103] = cube_tmp[78];
        cube[104] = cube_tmp[77];
        cube[105] = cube_tmp[76];
        cube[106] = cube_tmp[75];
        cube[107] = cube_tmp[74];
        cube[108] = cube_tmp[73];
        cube[109] = cube_tmp[72];
        cube[110] = cube_tmp[71];
        cube[111] = cube_tmp[70];
        cube[115] = cube_tmp[66];
        cube[116] = cube_tmp[65];
        cube[117] = cube_tmp[64];
        cube[121] = cube_tmp[60];
        cube[122] = cube_tmp[59];
        cube[123] = cube_tmp[58];
        cube[127] = cube_tmp[54];
        cube[128] = cube_tmp[53];
        cube[129] = cube_tmp[52];
        cube[133] = cube_tmp[48];
        cube[134] = cube_tmp[47];
        cube[135] = cube_tmp[46];
        cube[139] = cube_tmp[42];
        cube[140] = cube_tmp[41];
        cube[141] = cube_tmp[40];
        cube[181] = cube_tmp[36];
        cube[182] = cube_tmp[35];
        cube[183] = cube_tmp[34];
        cube[184] = cube_tmp[33];
        cube[185] = cube_tmp[32];
        cube[186] = cube_tmp[31];
        cube[187] = cube_tmp[30];
        cube[188] = cube_tmp[29];
        cube[189] = cube_tmp[28];
        cube[190] = cube_tmp[27];
        cube[191] = cube_tmp[26];
        cube[192] = cube_tmp[25];
        cube[193] = cube_tmp[24];
        cube[194] = cube_tmp[23];
        cube[195] = cube_tmp[22];
        cube[196] = cube_tmp[21];
        cube[197] = cube_tmp[20];
        cube[198] = cube_tmp[19];
        break;
    }

    case R: {
        cube[6] = cube_tmp[78];
        cube[12] = cube_tmp[84];
        cube[18] = cube_tmp[90];
        cube[24] = cube_tmp[96];
        cube[30] = cube_tmp[102];
        cube[36] = cube_tmp[108];
        cube[78] = cube_tmp[186];
        cube[84] = cube_tmp[192];
        cube[90] = cube_tmp[198];
        cube[96] = cube_tmp[204];
        cube[102] = cube_tmp[210];
        cube[108] = cube_tmp[216];
        cube[109] = cube_tmp[139];
        cube[110] = cube_tmp[133];
        cube[111] = cube_tmp[127];
        cube[112] = cube_tmp[121];
        cube[113] = cube_tmp[115];
        cube[114] = cube_tmp[109];
        cube[115] = cube_tmp[140];
        cube[116] = cube_tmp[134];
        cube[117] = cube_tmp[128];
        cube[118] = cube_tmp[122];
        cube[119] = cube_tmp[116];
        cube[120] = cube_tmp[110];
        cube[121] = cube_tmp[141];
        cube[122] = cube_tmp[135];
        cube[123] = cube_tmp[129];
        cube[124] = cube_tmp[123];
        cube[125] = cube_tmp[117];
        cube[126] = cube_tmp[111];
        cube[127] = cube_tmp[142];
        cube[128] = cube_tmp[136];
        cube[129] = cube_tmp[130];
        cube[130] = cube_tmp[124];
        cube[131] = cube_tmp[118];
        cube[132] = cube_tmp[112];
        cube[133] = cube_tmp[143];
        cube[134] = cube_tmp[137];
        cube[135] = cube_tmp[131];
        cube[136] = cube_tmp[125];
        cube[137] = cube_tmp[119];
        cube[138] = cube_tmp[113];
        cube[139] = cube_tmp[144];
        cube[140] = cube_tmp[138];
        cube[141] = cube_tmp[132];
        cube[142] = cube_tmp[126];
        cube[143] = cube_tmp[120];
        cube[144] = cube_tmp[114];
        cube[145] = cube_tmp[36];
        cube[151] = cube_tmp[30];
        cube[157] = cube_tmp[24];
        cube[163] = cube_tmp[18];
        cube[169] = cube_tmp[12];
        cube[175] = cube_tmp[6];
        cube[186] = cube_tmp[175];
        cube[192] = cube_tmp[169];
        cube[198] = cube_tmp[163];
        cube[204] = cube_tmp[157];
        cube[210] = cube_tmp[151];
        cube[216] = cube_tmp[145];
        break;
    }

    case R_PRIME: {
        cube[6] = cube_tmp[175];
        cube[12] = cube_tmp[169];
        cube[18] = cube_tmp[163];
        cube[24] = cube_tmp[157];
        cube[30] = cube_tmp[151];
        cube[36] = cube_tmp[145];
        cube[78] = cube_tmp[6];
        cube[84] = cube_tmp[12];
        cube[90] = cube_tmp[18];
        cube[96] = cube_tmp[24];
        cube[102] = cube_tmp[30];
        cube[108] = cube_tmp[36];
        cube[109] = cube_tmp[114];
        cube[110] = cube_tmp[120];
        cube[111] = cube_tmp[126];
        cube[112] = cube_tmp[132];
        cube[113] = cube_tmp[138];
        cube[114] = cube_tmp[144];
        cube[115] = cube_tmp[113];
        cube[116] = cube_tmp[119];
        cube[117] = cube_tmp[125];
        cube[118] = cube_tmp[131];
        cube[119] = cube_tmp[137];
        cube[120] = cube_tmp[143];
        cube[121] = cube_tmp[112];
        cube[122] = cube_tmp[118];
        cube[123] = cube_tmp[124];
        cube[124] = cube_tmp[130];
        cube[125] = cube_tmp[136];
        cube[126] = cube_tmp[142];
        cube[127] = cube_tmp[111];
        cube[128] = cube_tmp[117];
        cube[129] = cube_tmp[123];
        cube[130] = cube_tmp[129];
        cube[131] = cube_tmp[135];
        cube[132] = cube_tmp[141];
        cube[133] = cube_tmp[110];
        cube[134] = cube_tmp[116];
        cube[135] = cube_tmp[122];
        cube[136] = cube_tmp[128];
        cube[137] = cube_tmp[134];
        cube[138] = cube_tmp[140];
        cube[139] = cube_tmp[109];
        cube[140] = cube_tmp[115];
        cube[141] = cube_tmp[121];
        cube[142] = cube_tmp[127];
        cube[143] = cube_tmp[133];
        cube[144] = cube_tmp[139];
        cube[145] = cube_tmp[216];
        cube[151] = cube_tmp[210];
        cube[157] = cube_tmp[204];
        cube[163] = cube_tmp[198];
        cube[169] = cube_tmp[192];
        cube[175] = cube_tmp[186];
        cube[186] = cube_tmp[78];
        cube[192] = cube_tmp[84];
        cube[198] = cube_tmp[90];
        cube[204] = cube_tmp[96];
        cube[210] = cube_tmp[102];
        cube[216] = cube_tmp[108];
        break;
    }

    case R2: {
        cube[6] = cube_tmp[186];
        cube[12] = cube_tmp[192];
        cube[18] = cube_tmp[198];
        cube[24] = cube_tmp[204];
        cube[30] = cube_tmp[210];
        cube[36] = cube_tmp[216];
        cube[78] = cube_tmp[175];
        cube[84] = cube_tmp[169];
        cube[90] = cube_tmp[163];
        cube[96] = cube_tmp[157];
        cube[102] = cube_tmp[151];
        cube[108] = cube_tmp[145];
        cube[109] = cube_tmp[144];
        cube[110] = cube_tmp[143];
        cube[111] = cube_tmp[142];
        cube[112] = cube_tmp[141];
        cube[113] = cube_tmp[140];
        cube[114] = cube_tmp[139];
        cube[115] = cube_tmp[138];
        cube[116] = cube_tmp[137];
        cube[117] = cube_tmp[136];
        cube[118] = cube_tmp[135];
        cube[119] = cube_tmp[134];
        cube[120] = cube_tmp[133];
        cube[121] = cube_tmp[132];
        cube[122] = cube_tmp[131];
        cube[123] = cube_tmp[130];
        cube[124] = cube_tmp[129];
        cube[125] = cube_tmp[128];
        cube[126] = cube_tmp[127];
        cube[127] = cube_tmp[126];
        cube[128] = cube_tmp[125];
        cube[129] = cube_tmp[124];
        cube[130] = cube_tmp[123];
        cube[131] = cube_tmp[122];
        cube[132] = cube_tmp[121];
        cube[133] = cube_tmp[120];
        cube[134] = cube_tmp[119];
        cube[135] = cube_tmp[118];
        cube[136] = cube_tmp[117];
        cube[137] = cube_tmp[116];
        cube[138] = cube_tmp[115];
        cube[139] = cube_tmp[114];
        cube[140] = cube_tmp[113];
        cube[141] = cube_tmp[112];
        cube[142] = cube_tmp[111];
        cube[143] = cube_tmp[110];
        cube[144] = cube_tmp[109];
        cube[145] = cube_tmp[108];
        cube[151] = cube_tmp[102];
        cube[157] = cube_tmp[96];
        cube[163] = cube_tmp[90];
        cube[169] = cube_tmp[84];
        cube[175] = cube_tmp[78];
        cube[186] = cube_tmp[6];
        cube[192] = cube_tmp[12];
        cube[198] = cube_tmp[18];
        cube[204] = cube_tmp[24];
        cube[210] = cube_tmp[30];
        cube[216] = cube_tmp[36];
        break;
    }

    case Rw: {
        cube[5] = cube_tmp[77];
        cube[6] = cube_tmp[78];
        cube[11] = cube_tmp[83];
        cube[12] = cube_tmp[84];
        cube[17] = cube_tmp[89];
        cube[18] = cube_tmp[90];
        cube[23] = cube_tmp[95];
        cube[24] = cube_tmp[96];
        cube[29] = cube_tmp[101];
        cube[30] = cube_tmp[102];
        cube[35] = cube_tmp[107];
        cube[36] = cube_tmp[108];
        cube[77] = cube_tmp[185];
        cube[78] = cube_tmp[186];
        cube[83] = cube_tmp[191];
        cube[84] = cube_tmp[192];
        cube[89] = cube_tmp[197];
        cube[90] = cube_tmp[198];
        cube[95] = cube_tmp[203];
        cube[96] = cube_tmp[204];
        cube[101] = cube_tmp[209];
        cube[102] = cube_tmp[210];
        cube[107] = cube_tmp[215];
        cube[108] = cube_tmp[216];
        cube[109] = cube_tmp[139];
        cube[110] = cube_tmp[133];
        cube[111] = cube_tmp[127];
        cube[112] = cube_tmp[121];
        cube[113] = cube_tmp[115];
        cube[114] = cube_tmp[109];
        cube[115] = cube_tmp[140];
        cube[116] = cube_tmp[134];
        cube[117] = cube_tmp[128];
        cube[118] = cube_tmp[122];
        cube[119] = cube_tmp[116];
        cube[120] = cube_tmp[110];
        cube[121] = cube_tmp[141];
        cube[122] = cube_tmp[135];
        cube[123] = cube_tmp[129];
        cube[124] = cube_tmp[123];
        cube[125] = cube_tmp[117];
        cube[126] = cube_tmp[111];
        cube[127] = cube_tmp[142];
        cube[128] = cube_tmp[136];
        cube[129] = cube_tmp[130];
        cube[130] = cube_tmp[124];
        cube[131] = cube_tmp[118];
        cube[132] = cube_tmp[112];
        cube[133] = cube_tmp[143];
        cube[134] = cube_tmp[137];
        cube[135] = cube_tmp[131];
        cube[136] = cube_tmp[125];
        cube[137] = cube_tmp[119];
        cube[138] = cube_tmp[113];
        cube[139] = cube_tmp[144];
        cube[140] = cube_tmp[138];
        cube[141] = cube_tmp[132];
        cube[142] = cube_tmp[126];
        cube[143] = cube_tmp[120];
        cube[144] = cube_tmp[114];
        cube[145] = cube_tmp[36];
        cube[146] = cube_tmp[35];
        cube[151] = cube_tmp[30];
        cube[152] = cube_tmp[29];
        cube[157] = cube_tmp[24];
        cube[158] = cube_tmp[23];
        cube[163] = cube_tmp[18];
        cube[164] = cube_tmp[17];
        cube[169] = cube_tmp[12];
        cube[170] = cube_tmp[11];
        cube[175] = cube_tmp[6];
        cube[176] = cube_tmp[5];
        cube[185] = cube_tmp[176];
        cube[186] = cube_tmp[175];
        cube[191] = cube_tmp[170];
        cube[192] = cube_tmp[169];
        cube[197] = cube_tmp[164];
        cube[198] = cube_tmp[163];
        cube[203] = cube_tmp[158];
        cube[204] = cube_tmp[157];
        cube[209] = cube_tmp[152];
        cube[210] = cube_tmp[151];
        cube[215] = cube_tmp[146];
        cube[216] = cube_tmp[145];
        break;
    }

    case Rw_PRIME: {
        cube[5] = cube_tmp[176];
        cube[6] = cube_tmp[175];
        cube[11] = cube_tmp[170];
        cube[12] = cube_tmp[169];
        cube[17] = cube_tmp[164];
        cube[18] = cube_tmp[163];
        cube[23] = cube_tmp[158];
        cube[24] = cube_tmp[157];
        cube[29] = cube_tmp[152];
        cube[30] = cube_tmp[151];
        cube[35] = cube_tmp[146];
        cube[36] = cube_tmp[145];
        cube[77] = cube_tmp[5];
        cube[78] = cube_tmp[6];
        cube[83] = cube_tmp[11];
        cube[84] = cube_tmp[12];
        cube[89] = cube_tmp[17];
        cube[90] = cube_tmp[18];
        cube[95] = cube_tmp[23];
        cube[96] = cube_tmp[24];
        cube[101] = cube_tmp[29];
        cube[102] = cube_tmp[30];
        cube[107] = cube_tmp[35];
        cube[108] = cube_tmp[36];
        cube[109] = cube_tmp[114];
        cube[110] = cube_tmp[120];
        cube[111] = cube_tmp[126];
        cube[112] = cube_tmp[132];
        cube[113] = cube_tmp[138];
        cube[114] = cube_tmp[144];
        cube[115] = cube_tmp[113];
        cube[116] = cube_tmp[119];
        cube[117] = cube_tmp[125];
        cube[118] = cube_tmp[131];
        cube[119] = cube_tmp[137];
        cube[120] = cube_tmp[143];
        cube[121] = cube_tmp[112];
        cube[122] = cube_tmp[118];
        cube[123] = cube_tmp[124];
        cube[124] = cube_tmp[130];
        cube[125] = cube_tmp[136];
        cube[126] = cube_tmp[142];
        cube[127] = cube_tmp[111];
        cube[128] = cube_tmp[117];
        cube[129] = cube_tmp[123];
        cube[130] = cube_tmp[129];
        cube[131] = cube_tmp[135];
        cube[132] = cube_tmp[141];
        cube[133] = cube_tmp[110];
        cube[134] = cube_tmp[116];
        cube[135] = cube_tmp[122];
        cube[136] = cube_tmp[128];
        cube[137] = cube_tmp[134];
        cube[138] = cube_tmp[140];
        cube[139] = cube_tmp[109];
        cube[140] = cube_tmp[115];
        cube[141] = cube_tmp[121];
        cube[142] = cube_tmp[127];
        cube[143] = cube_tmp[133];
        cube[144] = cube_tmp[139];
        cube[145] = cube_tmp[216];
        cube[146] = cube_tmp[215];
        cube[151] = cube_tmp[210];
        cube[152] = cube_tmp[209];
        cube[157] = cube_tmp[204];
        cube[158] = cube_tmp[203];
        cube[163] = cube_tmp[198];
        cube[164] = cube_tmp[197];
        cube[169] = cube_tmp[192];
        cube[170] = cube_tmp[191];
        cube[175] = cube_tmp[186];
        cube[176] = cube_tmp[185];
        cube[185] = cube_tmp[77];
        cube[186] = cube_tmp[78];
        cube[191] = cube_tmp[83];
        cube[192] = cube_tmp[84];
        cube[197] = cube_tmp[89];
        cube[198] = cube_tmp[90];
        cube[203] = cube_tmp[95];
        cube[204] = cube_tmp[96];
        cube[209] = cube_tmp[101];
        cube[210] = cube_tmp[102];
        cube[215] = cube_tmp[107];
        cube[216] = cube_tmp[108];
        break;
    }

    case Rw2: {
        cube[5] = cube_tmp[185];
        cube[6] = cube_tmp[186];
        cube[11] = cube_tmp[191];
        cube[12] = cube_tmp[192];
        cube[17] = cube_tmp[197];
        cube[18] = cube_tmp[198];
        cube[23] = cube_tmp[203];
        cube[24] = cube_tmp[204];
        cube[29] = cube_tmp[209];
        cube[30] = cube_tmp[210];
        cube[35] = cube_tmp[215];
        cube[36] = cube_tmp[216];
        cube[77] = cube_tmp[176];
        cube[78] = cube_tmp[175];
        cube[83] = cube_tmp[170];
        cube[84] = cube_tmp[169];
        cube[89] = cube_tmp[164];
        cube[90] = cube_tmp[163];
        cube[95] = cube_tmp[158];
        cube[96] = cube_tmp[157];
        cube[101] = cube_tmp[152];
        cube[102] = cube_tmp[151];
        cube[107] = cube_tmp[146];
        cube[108] = cube_tmp[145];
        cube[109] = cube_tmp[144];
        cube[110] = cube_tmp[143];
        cube[111] = cube_tmp[142];
        cube[112] = cube_tmp[141];
        cube[113] = cube_tmp[140];
        cube[114] = cube_tmp[139];
        cube[115] = cube_tmp[138];
        cube[116] = cube_tmp[137];
        cube[117] = cube_tmp[136];
        cube[118] = cube_tmp[135];
        cube[119] = cube_tmp[134];
        cube[120] = cube_tmp[133];
        cube[121] = cube_tmp[132];
        cube[122] = cube_tmp[131];
        cube[123] = cube_tmp[130];
        cube[124] = cube_tmp[129];
        cube[125] = cube_tmp[128];
        cube[126] = cube_tmp[127];
        cube[127] = cube_tmp[126];
        cube[128] = cube_tmp[125];
        cube[129] = cube_tmp[124];
        cube[130] = cube_tmp[123];
        cube[131] = cube_tmp[122];
        cube[132] = cube_tmp[121];
        cube[133] = cube_tmp[120];
        cube[134] = cube_tmp[119];
        cube[135] = cube_tmp[118];
        cube[136] = cube_tmp[117];
        cube[137] = cube_tmp[116];
        cube[138] = cube_tmp[115];
        cube[139] = cube_tmp[114];
        cube[140] = cube_tmp[113];
        cube[141] = cube_tmp[112];
        cube[142] = cube_tmp[111];
        cube[143] = cube_tmp[110];
        cube[144] = cube_tmp[109];
        cube[145] = cube_tmp[108];
        cube[146] = cube_tmp[107];
        cube[151] = cube_tmp[102];
        cube[152] = cube_tmp[101];
        cube[157] = cube_tmp[96];
        cube[158] = cube_tmp[95];
        cube[163] = cube_tmp[90];
        cube[164] = cube_tmp[89];
        cube[169] = cube_tmp[84];
        cube[170] = cube_tmp[83];
        cube[175] = cube_tmp[78];
        cube[176] = cube_tmp[77];
        cube[185] = cube_tmp[5];
        cube[186] = cube_tmp[6];
        cube[191] = cube_tmp[11];
        cube[192] = cube_tmp[12];
        cube[197] = cube_tmp[17];
        cube[198] = cube_tmp[18];
        cube[203] = cube_tmp[23];
        cube[204] = cube_tmp[24];
        cube[209] = cube_tmp[29];
        cube[210] = cube_tmp[30];
        cube[215] = cube_tmp[35];
        cube[216] = cube_tmp[36];
        break;
    }

    case threeRw: {
        cube[4] = cube_tmp[76];
        cube[5] = cube_tmp[77];
        cube[6] = cube_tmp[78];
        cube[10] = cube_tmp[82];
        cube[11] = cube_tmp[83];
        cube[12] = cube_tmp[84];
        cube[16] = cube_tmp[88];
        cube[17] = cube_tmp[89];
        cube[18] = cube_tmp[90];
        cube[22] = cube_tmp[94];
        cube[23] = cube_tmp[95];
        cube[24] = cube_tmp[96];
        cube[28] = cube_tmp[100];
        cube[29] = cube_tmp[101];
        cube[30] = cube_tmp[102];
        cube[34] = cube_tmp[106];
        cube[35] = cube_tmp[107];
        cube[36] = cube_tmp[108];
        cube[76] = cube_tmp[184];
        cube[77] = cube_tmp[185];
        cube[78] = cube_tmp[186];
        cube[82] = cube_tmp[190];
        cube[83] = cube_tmp[191];
        cube[84] = cube_tmp[192];
        cube[88] = cube_tmp[196];
        cube[89] = cube_tmp[197];
        cube[90] = cube_tmp[198];
        cube[94] = cube_tmp[202];
        cube[95] = cube_tmp[203];
        cube[96] = cube_tmp[204];
        cube[100] = cube_tmp[208];
        cube[101] = cube_tmp[209];
        cube[102] = cube_tmp[210];
        cube[106] = cube_tmp[214];
        cube[107] = cube_tmp[215];
        cube[108] = cube_tmp[216];
        cube[109] = cube_tmp[139];
        cube[110] = cube_tmp[133];
        cube[111] = cube_tmp[127];
        cube[112] = cube_tmp[121];
        cube[113] = cube_tmp[115];
        cube[114] = cube_tmp[109];
        cube[115] = cube_tmp[140];
        cube[116] = cube_tmp[134];
        cube[117] = cube_tmp[128];
        cube[118] = cube_tmp[122];
        cube[119] = cube_tmp[116];
        cube[120] = cube_tmp[110];
        cube[121] = cube_tmp[141];
        cube[122] = cube_tmp[135];
        cube[123] = cube_tmp[129];
        cube[124] = cube_tmp[123];
        cube[125] = cube_tmp[117];
        cube[126] = cube_tmp[111];
        cube[127] = cube_tmp[142];
        cube[128] = cube_tmp[136];
        cube[129] = cube_tmp[130];
        cube[130] = cube_tmp[124];
        cube[131] = cube_tmp[118];
        cube[132] = cube_tmp[112];
        cube[133] = cube_tmp[143];
        cube[134] = cube_tmp[137];
        cube[135] = cube_tmp[131];
        cube[136] = cube_tmp[125];
        cube[137] = cube_tmp[119];
        cube[138] = cube_tmp[113];
        cube[139] = cube_tmp[144];
        cube[140] = cube_tmp[138];
        cube[141] = cube_tmp[132];
        cube[142] = cube_tmp[126];
        cube[143] = cube_tmp[120];
        cube[144] = cube_tmp[114];
        cube[145] = cube_tmp[36];
        cube[146] = cube_tmp[35];
        cube[147] = cube_tmp[34];
        cube[151] = cube_tmp[30];
        cube[152] = cube_tmp[29];
        cube[153] = cube_tmp[28];
        cube[157] = cube_tmp[24];
        cube[158] = cube_tmp[23];
        cube[159] = cube_tmp[22];
        cube[163] = cube_tmp[18];
        cube[164] = cube_tmp[17];
        cube[165] = cube_tmp[16];
        cube[169] = cube_tmp[12];
        cube[170] = cube_tmp[11];
        cube[171] = cube_tmp[10];
        cube[175] = cube_tmp[6];
        cube[176] = cube_tmp[5];
        cube[177] = cube_tmp[4];
        cube[184] = cube_tmp[177];
        cube[185] = cube_tmp[176];
        cube[186] = cube_tmp[175];
        cube[190] = cube_tmp[171];
        cube[191] = cube_tmp[170];
        cube[192] = cube_tmp[169];
        cube[196] = cube_tmp[165];
        cube[197] = cube_tmp[164];
        cube[198] = cube_tmp[163];
        cube[202] = cube_tmp[159];
        cube[203] = cube_tmp[158];
        cube[204] = cube_tmp[157];
        cube[208] = cube_tmp[153];
        cube[209] = cube_tmp[152];
        cube[210] = cube_tmp[151];
        cube[214] = cube_tmp[147];
        cube[215] = cube_tmp[146];
        cube[216] = cube_tmp[145];
        break;
    }

    case threeRw_PRIME: {
        cube[4] = cube_tmp[177];
        cube[5] = cube_tmp[176];
        cube[6] = cube_tmp[175];
        cube[10] = cube_tmp[171];
        cube[11] = cube_tmp[170];
        cube[12] = cube_tmp[169];
        cube[16] = cube_tmp[165];
        cube[17] = cube_tmp[164];
        cube[18] = cube_tmp[163];
        cube[22] = cube_tmp[159];
        cube[23] = cube_tmp[158];
        cube[24] = cube_tmp[157];
        cube[28] = cube_tmp[153];
        cube[29] = cube_tmp[152];
        cube[30] = cube_tmp[151];
        cube[34] = cube_tmp[147];
        cube[35] = cube_tmp[146];
        cube[36] = cube_tmp[145];
        cube[76] = cube_tmp[4];
        cube[77] = cube_tmp[5];
        cube[78] = cube_tmp[6];
        cube[82] = cube_tmp[10];
        cube[83] = cube_tmp[11];
        cube[84] = cube_tmp[12];
        cube[88] = cube_tmp[16];
        cube[89] = cube_tmp[17];
        cube[90] = cube_tmp[18];
        cube[94] = cube_tmp[22];
        cube[95] = cube_tmp[23];
        cube[96] = cube_tmp[24];
        cube[100] = cube_tmp[28];
        cube[101] = cube_tmp[29];
        cube[102] = cube_tmp[30];
        cube[106] = cube_tmp[34];
        cube[107] = cube_tmp[35];
        cube[108] = cube_tmp[36];
        cube[109] = cube_tmp[114];
        cube[110] = cube_tmp[120];
        cube[111] = cube_tmp[126];
        cube[112] = cube_tmp[132];
        cube[113] = cube_tmp[138];
        cube[114] = cube_tmp[144];
        cube[115] = cube_tmp[113];
        cube[116] = cube_tmp[119];
        cube[117] = cube_tmp[125];
        cube[118] = cube_tmp[131];
        cube[119] = cube_tmp[137];
        cube[120] = cube_tmp[143];
        cube[121] = cube_tmp[112];
        cube[122] = cube_tmp[118];
        cube[123] = cube_tmp[124];
        cube[124] = cube_tmp[130];
        cube[125] = cube_tmp[136];
        cube[126] = cube_tmp[142];
        cube[127] = cube_tmp[111];
        cube[128] = cube_tmp[117];
        cube[129] = cube_tmp[123];
        cube[130] = cube_tmp[129];
        cube[131] = cube_tmp[135];
        cube[132] = cube_tmp[141];
        cube[133] = cube_tmp[110];
        cube[134] = cube_tmp[116];
        cube[135] = cube_tmp[122];
        cube[136] = cube_tmp[128];
        cube[137] = cube_tmp[134];
        cube[138] = cube_tmp[140];
        cube[139] = cube_tmp[109];
        cube[140] = cube_tmp[115];
        cube[141] = cube_tmp[121];
        cube[142] = cube_tmp[127];
        cube[143] = cube_tmp[133];
        cube[144] = cube_tmp[139];
        cube[145] = cube_tmp[216];
        cube[146] = cube_tmp[215];
        cube[147] = cube_tmp[214];
        cube[151] = cube_tmp[210];
        cube[152] = cube_tmp[209];
        cube[153] = cube_tmp[208];
        cube[157] = cube_tmp[204];
        cube[158] = cube_tmp[203];
        cube[159] = cube_tmp[202];
        cube[163] = cube_tmp[198];
        cube[164] = cube_tmp[197];
        cube[165] = cube_tmp[196];
        cube[169] = cube_tmp[192];
        cube[170] = cube_tmp[191];
        cube[171] = cube_tmp[190];
        cube[175] = cube_tmp[186];
        cube[176] = cube_tmp[185];
        cube[177] = cube_tmp[184];
        cube[184] = cube_tmp[76];
        cube[185] = cube_tmp[77];
        cube[186] = cube_tmp[78];
        cube[190] = cube_tmp[82];
        cube[191] = cube_tmp[83];
        cube[192] = cube_tmp[84];
        cube[196] = cube_tmp[88];
        cube[197] = cube_tmp[89];
        cube[198] = cube_tmp[90];
        cube[202] = cube_tmp[94];
        cube[203] = cube_tmp[95];
        cube[204] = cube_tmp[96];
        cube[208] = cube_tmp[100];
        cube[209] = cube_tmp[101];
        cube[210] = cube_tmp[102];
        cube[214] = cube_tmp[106];
        cube[215] = cube_tmp[107];
        cube[216] = cube_tmp[108];
        break;
    }

    case threeRw2: {
        cube[4] = cube_tmp[184];
        cube[5] = cube_tmp[185];
        cube[6] = cube_tmp[186];
        cube[10] = cube_tmp[190];
        cube[11] = cube_tmp[191];
        cube[12] = cube_tmp[192];
        cube[16] = cube_tmp[196];
        cube[17] = cube_tmp[197];
        cube[18] = cube_tmp[198];
        cube[22] = cube_tmp[202];
        cube[23] = cube_tmp[203];
        cube[24] = cube_tmp[204];
        cube[28] = cube_tmp[208];
        cube[29] = cube_tmp[209];
        cube[30] = cube_tmp[210];
        cube[34] = cube_tmp[214];
        cube[35] = cube_tmp[215];
        cube[36] = cube_tmp[216];
        cube[76] = cube_tmp[177];
        cube[77] = cube_tmp[176];
        cube[78] = cube_tmp[175];
        cube[82] = cube_tmp[171];
        cube[83] = cube_tmp[170];
        cube[84] = cube_tmp[169];
        cube[88] = cube_tmp[165];
        cube[89] = cube_tmp[164];
        cube[90] = cube_tmp[163];
        cube[94] = cube_tmp[159];
        cube[95] = cube_tmp[158];
        cube[96] = cube_tmp[157];
        cube[100] = cube_tmp[153];
        cube[101] = cube_tmp[152];
        cube[102] = cube_tmp[151];
        cube[106] = cube_tmp[147];
        cube[107] = cube_tmp[146];
        cube[108] = cube_tmp[145];
        cube[109] = cube_tmp[144];
        cube[110] = cube_tmp[143];
        cube[111] = cube_tmp[142];
        cube[112] = cube_tmp[141];
        cube[113] = cube_tmp[140];
        cube[114] = cube_tmp[139];
        cube[115] = cube_tmp[138];
        cube[116] = cube_tmp[137];
        cube[117] = cube_tmp[136];
        cube[118] = cube_tmp[135];
        cube[119] = cube_tmp[134];
        cube[120] = cube_tmp[133];
        cube[121] = cube_tmp[132];
        cube[122] = cube_tmp[131];
        cube[123] = cube_tmp[130];
        cube[124] = cube_tmp[129];
        cube[125] = cube_tmp[128];
        cube[126] = cube_tmp[127];
        cube[127] = cube_tmp[126];
        cube[128] = cube_tmp[125];
        cube[129] = cube_tmp[124];
        cube[130] = cube_tmp[123];
        cube[131] = cube_tmp[122];
        cube[132] = cube_tmp[121];
        cube[133] = cube_tmp[120];
        cube[134] = cube_tmp[119];
        cube[135] = cube_tmp[118];
        cube[136] = cube_tmp[117];
        cube[137] = cube_tmp[116];
        cube[138] = cube_tmp[115];
        cube[139] = cube_tmp[114];
        cube[140] = cube_tmp[113];
        cube[141] = cube_tmp[112];
        cube[142] = cube_tmp[111];
        cube[143] = cube_tmp[110];
        cube[144] = cube_tmp[109];
        cube[145] = cube_tmp[108];
        cube[146] = cube_tmp[107];
        cube[147] = cube_tmp[106];
        cube[151] = cube_tmp[102];
        cube[152] = cube_tmp[101];
        cube[153] = cube_tmp[100];
        cube[157] = cube_tmp[96];
        cube[158] = cube_tmp[95];
        cube[159] = cube_tmp[94];
        cube[163] = cube_tmp[90];
        cube[164] = cube_tmp[89];
        cube[165] = cube_tmp[88];
        cube[169] = cube_tmp[84];
        cube[170] = cube_tmp[83];
        cube[171] = cube_tmp[82];
        cube[175] = cube_tmp[78];
        cube[176] = cube_tmp[77];
        cube[177] = cube_tmp[76];
        cube[184] = cube_tmp[4];
        cube[185] = cube_tmp[5];
        cube[186] = cube_tmp[6];
        cube[190] = cube_tmp[10];
        cube[191] = cube_tmp[11];
        cube[192] = cube_tmp[12];
        cube[196] = cube_tmp[16];
        cube[197] = cube_tmp[17];
        cube[198] = cube_tmp[18];
        cube[202] = cube_tmp[22];
        cube[203] = cube_tmp[23];
        cube[204] = cube_tmp[24];
        cube[208] = cube_tmp[28];
        cube[209] = cube_tmp[29];
        cube[210] = cube_tmp[30];
        cube[214] = cube_tmp[34];
        cube[215] = cube_tmp[35];
        cube[216] = cube_tmp[36];
        break;
    }

    case B: {
        cube[1] = cube_tmp[114];
        cube[2] = cube_tmp[120];
        cube[3] = cube_tmp[126];
        cube[4] = cube_tmp[132];
        cube[5] = cube_tmp[138];
        cube[6] = cube_tmp[144];
        cube[37] = cube_tmp[6];
        cube[43] = cube_tmp[5];
        cube[49] = cube_tmp[4];
        cube[55] = cube_tmp[3];
        cube[61] = cube_tmp[2];
        cube[67] = cube_tmp[1];
        cube[114] = cube_tmp[216];
        cube[120] = cube_tmp[215];
        cube[126] = cube_tmp[214];
        cube[132] = cube_tmp[213];
        cube[138] = cube_tmp[212];
        cube[144] = cube_tmp[211];
        cube[145] = cube_tmp[175];
        cube[146] = cube_tmp[169];
        cube[147] = cube_tmp[163];
        cube[148] = cube_tmp[157];
        cube[149] = cube_tmp[151];
        cube[150] = cube_tmp[145];
        cube[151] = cube_tmp[176];
        cube[152] = cube_tmp[170];
        cube[153] = cube_tmp[164];
        cube[154] = cube_tmp[158];
        cube[155] = cube_tmp[152];
        cube[156] = cube_tmp[146];
        cube[157] = cube_tmp[177];
        cube[158] = cube_tmp[171];
        cube[159] = cube_tmp[165];
        cube[160] = cube_tmp[159];
        cube[161] = cube_tmp[153];
        cube[162] = cube_tmp[147];
        cube[163] = cube_tmp[178];
        cube[164] = cube_tmp[172];
        cube[165] = cube_tmp[166];
        cube[166] = cube_tmp[160];
        cube[167] = cube_tmp[154];
        cube[168] = cube_tmp[148];
        cube[169] = cube_tmp[179];
        cube[170] = cube_tmp[173];
        cube[171] = cube_tmp[167];
        cube[172] = cube_tmp[161];
        cube[173] = cube_tmp[155];
        cube[174] = cube_tmp[149];
        cube[175] = cube_tmp[180];
        cube[176] = cube_tmp[174];
        cube[177] = cube_tmp[168];
        cube[178] = cube_tmp[162];
        cube[179] = cube_tmp[156];
        cube[180] = cube_tmp[150];
        cube[211] = cube_tmp[37];
        cube[212] = cube_tmp[43];
        cube[213] = cube_tmp[49];
        cube[214] = cube_tmp[55];
        cube[215] = cube_tmp[61];
        cube[216] = cube_tmp[67];
        break;
    }

    case B_PRIME: {
        cube[1] = cube_tmp[67];
        cube[2] = cube_tmp[61];
        cube[3] = cube_tmp[55];
        cube[4] = cube_tmp[49];
        cube[5] = cube_tmp[43];
        cube[6] = cube_tmp[37];
        cube[37] = cube_tmp[211];
        cube[43] = cube_tmp[212];
        cube[49] = cube_tmp[213];
        cube[55] = cube_tmp[214];
        cube[61] = cube_tmp[215];
        cube[67] = cube_tmp[216];
        cube[114] = cube_tmp[1];
        cube[120] = cube_tmp[2];
        cube[126] = cube_tmp[3];
        cube[132] = cube_tmp[4];
        cube[138] = cube_tmp[5];
        cube[144] = cube_tmp[6];
        cube[145] = cube_tmp[150];
        cube[146] = cube_tmp[156];
        cube[147] = cube_tmp[162];
        cube[148] = cube_tmp[168];
        cube[149] = cube_tmp[174];
        cube[150] = cube_tmp[180];
        cube[151] = cube_tmp[149];
        cube[152] = cube_tmp[155];
        cube[153] = cube_tmp[161];
        cube[154] = cube_tmp[167];
        cube[155] = cube_tmp[173];
        cube[156] = cube_tmp[179];
        cube[157] = cube_tmp[148];
        cube[158] = cube_tmp[154];
        cube[159] = cube_tmp[160];
        cube[160] = cube_tmp[166];
        cube[161] = cube_tmp[172];
        cube[162] = cube_tmp[178];
        cube[163] = cube_tmp[147];
        cube[164] = cube_tmp[153];
        cube[165] = cube_tmp[159];
        cube[166] = cube_tmp[165];
        cube[167] = cube_tmp[171];
        cube[168] = cube_tmp[177];
        cube[169] = cube_tmp[146];
        cube[170] = cube_tmp[152];
        cube[171] = cube_tmp[158];
        cube[172] = cube_tmp[164];
        cube[173] = cube_tmp[170];
        cube[174] = cube_tmp[176];
        cube[175] = cube_tmp[145];
        cube[176] = cube_tmp[151];
        cube[177] = cube_tmp[157];
        cube[178] = cube_tmp[163];
        cube[179] = cube_tmp[169];
        cube[180] = cube_tmp[175];
        cube[211] = cube_tmp[144];
        cube[212] = cube_tmp[138];
        cube[213] = cube_tmp[132];
        cube[214] = cube_tmp[126];
        cube[215] = cube_tmp[120];
        cube[216] = cube_tmp[114];
        break;
    }

    case B2: {
        cube[1] = cube_tmp[216];
        cube[2] = cube_tmp[215];
        cube[3] = cube_tmp[214];
        cube[4] = cube_tmp[213];
        cube[5] = cube_tmp[212];
        cube[6] = cube_tmp[211];
        cube[37] = cube_tmp[144];
        cube[43] = cube_tmp[138];
        cube[49] = cube_tmp[132];
        cube[55] = cube_tmp[126];
        cube[61] = cube_tmp[120];
        cube[67] = cube_tmp[114];
        cube[114] = cube_tmp[67];
        cube[120] = cube_tmp[61];
        cube[126] = cube_tmp[55];
        cube[132] = cube_tmp[49];
        cube[138] = cube_tmp[43];
        cube[144] = cube_tmp[37];
        cube[145] = cube_tmp[180];
        cube[146] = cube_tmp[179];
        cube[147] = cube_tmp[178];
        cube[148] = cube_tmp[177];
        cube[149] = cube_tmp[176];
        cube[150] = cube_tmp[175];
        cube[151] = cube_tmp[174];
        cube[152] = cube_tmp[173];
        cube[153] = cube_tmp[172];
        cube[154] = cube_tmp[171];
        cube[155] = cube_tmp[170];
        cube[156] = cube_tmp[169];
        cube[157] = cube_tmp[168];
        cube[158] = cube_tmp[167];
        cube[159] = cube_tmp[166];
        cube[160] = cube_tmp[165];
        cube[161] = cube_tmp[164];
        cube[162] = cube_tmp[163];
        cube[163] = cube_tmp[162];
        cube[164] = cube_tmp[161];
        cube[165] = cube_tmp[160];
        cube[166] = cube_tmp[159];
        cube[167] = cube_tmp[158];
        cube[168] = cube_tmp[157];
        cube[169] = cube_tmp[156];
        cube[170] = cube_tmp[155];
        cube[171] = cube_tmp[154];
        cube[172] = cube_tmp[153];
        cube[173] = cube_tmp[152];
        cube[174] = cube_tmp[151];
        cube[175] = cube_tmp[150];
        cube[176] = cube_tmp[149];
        cube[177] = cube_tmp[148];
        cube[178] = cube_tmp[147];
        cube[179] = cube_tmp[146];
        cube[180] = cube_tmp[145];
        cube[211] = cube_tmp[6];
        cube[212] = cube_tmp[5];
        cube[213] = cube_tmp[4];
        cube[214] = cube_tmp[3];
        cube[215] = cube_tmp[2];
        cube[216] = cube_tmp[1];
        break;
    }

    case Bw: {
        cube[1] = cube_tmp[114];
        cube[2] = cube_tmp[120];
        cube[3] = cube_tmp[126];
        cube[4] = cube_tmp[132];
        cube[5] = cube_tmp[138];
        cube[6] = cube_tmp[144];
        cube[7] = cube_tmp[113];
        cube[8] = cube_tmp[119];
        cube[9] = cube_tmp[125];
        cube[10] = cube_tmp[131];
        cube[11] = cube_tmp[137];
        cube[12] = cube_tmp[143];
        cube[37] = cube_tmp[6];
        cube[38] = cube_tmp[12];
        cube[43] = cube_tmp[5];
        cube[44] = cube_tmp[11];
        cube[49] = cube_tmp[4];
        cube[50] = cube_tmp[10];
        cube[55] = cube_tmp[3];
        cube[56] = cube_tmp[9];
        cube[61] = cube_tmp[2];
        cube[62] = cube_tmp[8];
        cube[67] = cube_tmp[1];
        cube[68] = cube_tmp[7];
        cube[113] = cube_tmp[210];
        cube[114] = cube_tmp[216];
        cube[119] = cube_tmp[209];
        cube[120] = cube_tmp[215];
        cube[125] = cube_tmp[208];
        cube[126] = cube_tmp[214];
        cube[131] = cube_tmp[207];
        cube[132] = cube_tmp[213];
        cube[137] = cube_tmp[206];
        cube[138] = cube_tmp[212];
        cube[143] = cube_tmp[205];
        cube[144] = cube_tmp[211];
        cube[145] = cube_tmp[175];
        cube[146] = cube_tmp[169];
        cube[147] = cube_tmp[163];
        cube[148] = cube_tmp[157];
        cube[149] = cube_tmp[151];
        cube[150] = cube_tmp[145];
        cube[151] = cube_tmp[176];
        cube[152] = cube_tmp[170];
        cube[153] = cube_tmp[164];
        cube[154] = cube_tmp[158];
        cube[155] = cube_tmp[152];
        cube[156] = cube_tmp[146];
        cube[157] = cube_tmp[177];
        cube[158] = cube_tmp[171];
        cube[159] = cube_tmp[165];
        cube[160] = cube_tmp[159];
        cube[161] = cube_tmp[153];
        cube[162] = cube_tmp[147];
        cube[163] = cube_tmp[178];
        cube[164] = cube_tmp[172];
        cube[165] = cube_tmp[166];
        cube[166] = cube_tmp[160];
        cube[167] = cube_tmp[154];
        cube[168] = cube_tmp[148];
        cube[169] = cube_tmp[179];
        cube[170] = cube_tmp[173];
        cube[171] = cube_tmp[167];
        cube[172] = cube_tmp[161];
        cube[173] = cube_tmp[155];
        cube[174] = cube_tmp[149];
        cube[175] = cube_tmp[180];
        cube[176] = cube_tmp[174];
        cube[177] = cube_tmp[168];
        cube[178] = cube_tmp[162];
        cube[179] = cube_tmp[156];
        cube[180] = cube_tmp[150];
        cube[205] = cube_tmp[38];
        cube[206] = cube_tmp[44];
        cube[207] = cube_tmp[50];
        cube[208] = cube_tmp[56];
        cube[209] = cube_tmp[62];
        cube[210] = cube_tmp[68];
        cube[211] = cube_tmp[37];
        cube[212] = cube_tmp[43];
        cube[213] = cube_tmp[49];
        cube[214] = cube_tmp[55];
        cube[215] = cube_tmp[61];
        cube[216] = cube_tmp[67];
        break;
    }

    case Bw_PRIME: {
        cube[1] = cube_tmp[67];
        cube[2] = cube_tmp[61];
        cube[3] = cube_tmp[55];
        cube[4] = cube_tmp[49];
        cube[5] = cube_tmp[43];
        cube[6] = cube_tmp[37];
        cube[7] = cube_tmp[68];
        cube[8] = cube_tmp[62];
        cube[9] = cube_tmp[56];
        cube[10] = cube_tmp[50];
        cube[11] = cube_tmp[44];
        cube[12] = cube_tmp[38];
        cube[37] = cube_tmp[211];
        cube[38] = cube_tmp[205];
        cube[43] = cube_tmp[212];
        cube[44] = cube_tmp[206];
        cube[49] = cube_tmp[213];
        cube[50] = cube_tmp[207];
        cube[55] = cube_tmp[214];
        cube[56] = cube_tmp[208];
        cube[61] = cube_tmp[215];
        cube[62] = cube_tmp[209];
        cube[67] = cube_tmp[216];
        cube[68] = cube_tmp[210];
        cube[113] = cube_tmp[7];
        cube[114] = cube_tmp[1];
        cube[119] = cube_tmp[8];
        cube[120] = cube_tmp[2];
        cube[125] = cube_tmp[9];
        cube[126] = cube_tmp[3];
        cube[131] = cube_tmp[10];
        cube[132] = cube_tmp[4];
        cube[137] = cube_tmp[11];
        cube[138] = cube_tmp[5];
        cube[143] = cube_tmp[12];
        cube[144] = cube_tmp[6];
        cube[145] = cube_tmp[150];
        cube[146] = cube_tmp[156];
        cube[147] = cube_tmp[162];
        cube[148] = cube_tmp[168];
        cube[149] = cube_tmp[174];
        cube[150] = cube_tmp[180];
        cube[151] = cube_tmp[149];
        cube[152] = cube_tmp[155];
        cube[153] = cube_tmp[161];
        cube[154] = cube_tmp[167];
        cube[155] = cube_tmp[173];
        cube[156] = cube_tmp[179];
        cube[157] = cube_tmp[148];
        cube[158] = cube_tmp[154];
        cube[159] = cube_tmp[160];
        cube[160] = cube_tmp[166];
        cube[161] = cube_tmp[172];
        cube[162] = cube_tmp[178];
        cube[163] = cube_tmp[147];
        cube[164] = cube_tmp[153];
        cube[165] = cube_tmp[159];
        cube[166] = cube_tmp[165];
        cube[167] = cube_tmp[171];
        cube[168] = cube_tmp[177];
        cube[169] = cube_tmp[146];
        cube[170] = cube_tmp[152];
        cube[171] = cube_tmp[158];
        cube[172] = cube_tmp[164];
        cube[173] = cube_tmp[170];
        cube[174] = cube_tmp[176];
        cube[175] = cube_tmp[145];
        cube[176] = cube_tmp[151];
        cube[177] = cube_tmp[157];
        cube[178] = cube_tmp[163];
        cube[179] = cube_tmp[169];
        cube[180] = cube_tmp[175];
        cube[205] = cube_tmp[143];
        cube[206] = cube_tmp[137];
        cube[207] = cube_tmp[131];
        cube[208] = cube_tmp[125];
        cube[209] = cube_tmp[119];
        cube[210] = cube_tmp[113];
        cube[211] = cube_tmp[144];
        cube[212] = cube_tmp[138];
        cube[213] = cube_tmp[132];
        cube[214] = cube_tmp[126];
        cube[215] = cube_tmp[120];
        cube[216] = cube_tmp[114];
        break;
    }

    case Bw2: {
        cube[1] = cube_tmp[216];
        cube[2] = cube_tmp[215];
        cube[3] = cube_tmp[214];
        cube[4] = cube_tmp[213];
        cube[5] = cube_tmp[212];
        cube[6] = cube_tmp[211];
        cube[7] = cube_tmp[210];
        cube[8] = cube_tmp[209];
        cube[9] = cube_tmp[208];
        cube[10] = cube_tmp[207];
        cube[11] = cube_tmp[206];
        cube[12] = cube_tmp[205];
        cube[37] = cube_tmp[144];
        cube[38] = cube_tmp[143];
        cube[43] = cube_tmp[138];
        cube[44] = cube_tmp[137];
        cube[49] = cube_tmp[132];
        cube[50] = cube_tmp[131];
        cube[55] = cube_tmp[126];
        cube[56] = cube_tmp[125];
        cube[61] = cube_tmp[120];
        cube[62] = cube_tmp[119];
        cube[67] = cube_tmp[114];
        cube[68] = cube_tmp[113];
        cube[113] = cube_tmp[68];
        cube[114] = cube_tmp[67];
        cube[119] = cube_tmp[62];
        cube[120] = cube_tmp[61];
        cube[125] = cube_tmp[56];
        cube[126] = cube_tmp[55];
        cube[131] = cube_tmp[50];
        cube[132] = cube_tmp[49];
        cube[137] = cube_tmp[44];
        cube[138] = cube_tmp[43];
        cube[143] = cube_tmp[38];
        cube[144] = cube_tmp[37];
        cube[145] = cube_tmp[180];
        cube[146] = cube_tmp[179];
        cube[147] = cube_tmp[178];
        cube[148] = cube_tmp[177];
        cube[149] = cube_tmp[176];
        cube[150] = cube_tmp[175];
        cube[151] = cube_tmp[174];
        cube[152] = cube_tmp[173];
        cube[153] = cube_tmp[172];
        cube[154] = cube_tmp[171];
        cube[155] = cube_tmp[170];
        cube[156] = cube_tmp[169];
        cube[157] = cube_tmp[168];
        cube[158] = cube_tmp[167];
        cube[159] = cube_tmp[166];
        cube[160] = cube_tmp[165];
        cube[161] = cube_tmp[164];
        cube[162] = cube_tmp[163];
        cube[163] = cube_tmp[162];
        cube[164] = cube_tmp[161];
        cube[165] = cube_tmp[160];
        cube[166] = cube_tmp[159];
        cube[167] = cube_tmp[158];
        cube[168] = cube_tmp[157];
        cube[169] = cube_tmp[156];
        cube[170] = cube_tmp[155];
        cube[171] = cube_tmp[154];
        cube[172] = cube_tmp[153];
        cube[173] = cube_tmp[152];
        cube[174] = cube_tmp[151];
        cube[175] = cube_tmp[150];
        cube[176] = cube_tmp[149];
        cube[177] = cube_tmp[148];
        cube[178] = cube_tmp[147];
        cube[179] = cube_tmp[146];
        cube[180] = cube_tmp[145];
        cube[205] = cube_tmp[12];
        cube[206] = cube_tmp[11];
        cube[207] = cube_tmp[10];
        cube[208] = cube_tmp[9];
        cube[209] = cube_tmp[8];
        cube[210] = cube_tmp[7];
        cube[211] = cube_tmp[6];
        cube[212] = cube_tmp[5];
        cube[213] = cube_tmp[4];
        cube[214] = cube_tmp[3];
        cube[215] = cube_tmp[2];
        cube[216] = cube_tmp[1];
        break;
    }

    case threeBw: {
        cube[1] = cube_tmp[114];
        cube[2] = cube_tmp[120];
        cube[3] = cube_tmp[126];
        cube[4] = cube_tmp[132];
        cube[5] = cube_tmp[138];
        cube[6] = cube_tmp[144];
        cube[7] = cube_tmp[113];
        cube[8] = cube_tmp[119];
        cube[9] = cube_tmp[125];
        cube[10] = cube_tmp[131];
        cube[11] = cube_tmp[137];
        cube[12] = cube_tmp[143];
        cube[13] = cube_tmp[112];
        cube[14] = cube_tmp[118];
        cube[15] = cube_tmp[124];
        cube[16] = cube_tmp[130];
        cube[17] = cube_tmp[136];
        cube[18] = cube_tmp[142];
        cube[37] = cube_tmp[6];
        cube[38] = cube_tmp[12];
        cube[39] = cube_tmp[18];
        cube[43] = cube_tmp[5];
        cube[44] = cube_tmp[11];
        cube[45] = cube_tmp[17];
        cube[49] = cube_tmp[4];
        cube[50] = cube_tmp[10];
        cube[51] = cube_tmp[16];
        cube[55] = cube_tmp[3];
        cube[56] = cube_tmp[9];
        cube[57] = cube_tmp[15];
        cube[61] = cube_tmp[2];
        cube[62] = cube_tmp[8];
        cube[63] = cube_tmp[14];
        cube[67] = cube_tmp[1];
        cube[68] = cube_tmp[7];
        cube[69] = cube_tmp[13];
        cube[112] = cube_tmp[204];
        cube[113] = cube_tmp[210];
        cube[114] = cube_tmp[216];
        cube[118] = cube_tmp[203];
        cube[119] = cube_tmp[209];
        cube[120] = cube_tmp[215];
        cube[124] = cube_tmp[202];
        cube[125] = cube_tmp[208];
        cube[126] = cube_tmp[214];
        cube[130] = cube_tmp[201];
        cube[131] = cube_tmp[207];
        cube[132] = cube_tmp[213];
        cube[136] = cube_tmp[200];
        cube[137] = cube_tmp[206];
        cube[138] = cube_tmp[212];
        cube[142] = cube_tmp[199];
        cube[143] = cube_tmp[205];
        cube[144] = cube_tmp[211];
        cube[145] = cube_tmp[175];
        cube[146] = cube_tmp[169];
        cube[147] = cube_tmp[163];
        cube[148] = cube_tmp[157];
        cube[149] = cube_tmp[151];
        cube[150] = cube_tmp[145];
        cube[151] = cube_tmp[176];
        cube[152] = cube_tmp[170];
        cube[153] = cube_tmp[164];
        cube[154] = cube_tmp[158];
        cube[155] = cube_tmp[152];
        cube[156] = cube_tmp[146];
        cube[157] = cube_tmp[177];
        cube[158] = cube_tmp[171];
        cube[159] = cube_tmp[165];
        cube[160] = cube_tmp[159];
        cube[161] = cube_tmp[153];
        cube[162] = cube_tmp[147];
        cube[163] = cube_tmp[178];
        cube[164] = cube_tmp[172];
        cube[165] = cube_tmp[166];
        cube[166] = cube_tmp[160];
        cube[167] = cube_tmp[154];
        cube[168] = cube_tmp[148];
        cube[169] = cube_tmp[179];
        cube[170] = cube_tmp[173];
        cube[171] = cube_tmp[167];
        cube[172] = cube_tmp[161];
        cube[173] = cube_tmp[155];
        cube[174] = cube_tmp[149];
        cube[175] = cube_tmp[180];
        cube[176] = cube_tmp[174];
        cube[177] = cube_tmp[168];
        cube[178] = cube_tmp[162];
        cube[179] = cube_tmp[156];
        cube[180] = cube_tmp[150];
        cube[199] = cube_tmp[39];
        cube[200] = cube_tmp[45];
        cube[201] = cube_tmp[51];
        cube[202] = cube_tmp[57];
        cube[203] = cube_tmp[63];
        cube[204] = cube_tmp[69];
        cube[205] = cube_tmp[38];
        cube[206] = cube_tmp[44];
        cube[207] = cube_tmp[50];
        cube[208] = cube_tmp[56];
        cube[209] = cube_tmp[62];
        cube[210] = cube_tmp[68];
        cube[211] = cube_tmp[37];
        cube[212] = cube_tmp[43];
        cube[213] = cube_tmp[49];
        cube[214] = cube_tmp[55];
        cube[215] = cube_tmp[61];
        cube[216] = cube_tmp[67];
        break;
    }

    case threeBw_PRIME: {
        cube[1] = cube_tmp[67];
        cube[2] = cube_tmp[61];
        cube[3] = cube_tmp[55];
        cube[4] = cube_tmp[49];
        cube[5] = cube_tmp[43];
        cube[6] = cube_tmp[37];
        cube[7] = cube_tmp[68];
        cube[8] = cube_tmp[62];
        cube[9] = cube_tmp[56];
        cube[10] = cube_tmp[50];
        cube[11] = cube_tmp[44];
        cube[12] = cube_tmp[38];
        cube[13] = cube_tmp[69];
        cube[14] = cube_tmp[63];
        cube[15] = cube_tmp[57];
        cube[16] = cube_tmp[51];
        cube[17] = cube_tmp[45];
        cube[18] = cube_tmp[39];
        cube[37] = cube_tmp[211];
        cube[38] = cube_tmp[205];
        cube[39] = cube_tmp[199];
        cube[43] = cube_tmp[212];
        cube[44] = cube_tmp[206];
        cube[45] = cube_tmp[200];
        cube[49] = cube_tmp[213];
        cube[50] = cube_tmp[207];
        cube[51] = cube_tmp[201];
        cube[55] = cube_tmp[214];
        cube[56] = cube_tmp[208];
        cube[57] = cube_tmp[202];
        cube[61] = cube_tmp[215];
        cube[62] = cube_tmp[209];
        cube[63] = cube_tmp[203];
        cube[67] = cube_tmp[216];
        cube[68] = cube_tmp[210];
        cube[69] = cube_tmp[204];
        cube[112] = cube_tmp[13];
        cube[113] = cube_tmp[7];
        cube[114] = cube_tmp[1];
        cube[118] = cube_tmp[14];
        cube[119] = cube_tmp[8];
        cube[120] = cube_tmp[2];
        cube[124] = cube_tmp[15];
        cube[125] = cube_tmp[9];
        cube[126] = cube_tmp[3];
        cube[130] = cube_tmp[16];
        cube[131] = cube_tmp[10];
        cube[132] = cube_tmp[4];
        cube[136] = cube_tmp[17];
        cube[137] = cube_tmp[11];
        cube[138] = cube_tmp[5];
        cube[142] = cube_tmp[18];
        cube[143] = cube_tmp[12];
        cube[144] = cube_tmp[6];
        cube[145] = cube_tmp[150];
        cube[146] = cube_tmp[156];
        cube[147] = cube_tmp[162];
        cube[148] = cube_tmp[168];
        cube[149] = cube_tmp[174];
        cube[150] = cube_tmp[180];
        cube[151] = cube_tmp[149];
        cube[152] = cube_tmp[155];
        cube[153] = cube_tmp[161];
        cube[154] = cube_tmp[167];
        cube[155] = cube_tmp[173];
        cube[156] = cube_tmp[179];
        cube[157] = cube_tmp[148];
        cube[158] = cube_tmp[154];
        cube[159] = cube_tmp[160];
        cube[160] = cube_tmp[166];
        cube[161] = cube_tmp[172];
        cube[162] = cube_tmp[178];
        cube[163] = cube_tmp[147];
        cube[164] = cube_tmp[153];
        cube[165] = cube_tmp[159];
        cube[166] = cube_tmp[165];
        cube[167] = cube_tmp[171];
        cube[168] = cube_tmp[177];
        cube[169] = cube_tmp[146];
        cube[170] = cube_tmp[152];
        cube[171] = cube_tmp[158];
        cube[172] = cube_tmp[164];
        cube[173] = cube_tmp[170];
        cube[174] = cube_tmp[176];
        cube[175] = cube_tmp[145];
        cube[176] = cube_tmp[151];
        cube[177] = cube_tmp[157];
        cube[178] = cube_tmp[163];
        cube[179] = cube_tmp[169];
        cube[180] = cube_tmp[175];
        cube[199] = cube_tmp[142];
        cube[200] = cube_tmp[136];
        cube[201] = cube_tmp[130];
        cube[202] = cube_tmp[124];
        cube[203] = cube_tmp[118];
        cube[204] = cube_tmp[112];
        cube[205] = cube_tmp[143];
        cube[206] = cube_tmp[137];
        cube[207] = cube_tmp[131];
        cube[208] = cube_tmp[125];
        cube[209] = cube_tmp[119];
        cube[210] = cube_tmp[113];
        cube[211] = cube_tmp[144];
        cube[212] = cube_tmp[138];
        cube[213] = cube_tmp[132];
        cube[214] = cube_tmp[126];
        cube[215] = cube_tmp[120];
        cube[216] = cube_tmp[114];
        break;
    }

    case threeBw2: {
        cube[1] = cube_tmp[216];
        cube[2] = cube_tmp[215];
        cube[3] = cube_tmp[214];
        cube[4] = cube_tmp[213];
        cube[5] = cube_tmp[212];
        cube[6] = cube_tmp[211];
        cube[7] = cube_tmp[210];
        cube[8] = cube_tmp[209];
        cube[9] = cube_tmp[208];
        cube[10] = cube_tmp[207];
        cube[11] = cube_tmp[206];
        cube[12] = cube_tmp[205];
        cube[13] = cube_tmp[204];
        cube[14] = cube_tmp[203];
        cube[15] = cube_tmp[202];
        cube[16] = cube_tmp[201];
        cube[17] = cube_tmp[200];
        cube[18] = cube_tmp[199];
        cube[37] = cube_tmp[144];
        cube[38] = cube_tmp[143];
        cube[39] = cube_tmp[142];
        cube[43] = cube_tmp[138];
        cube[44] = cube_tmp[137];
        cube[45] = cube_tmp[136];
        cube[49] = cube_tmp[132];
        cube[50] = cube_tmp[131];
        cube[51] = cube_tmp[130];
        cube[55] = cube_tmp[126];
        cube[56] = cube_tmp[125];
        cube[57] = cube_tmp[124];
        cube[61] = cube_tmp[120];
        cube[62] = cube_tmp[119];
        cube[63] = cube_tmp[118];
        cube[67] = cube_tmp[114];
        cube[68] = cube_tmp[113];
        cube[69] = cube_tmp[112];
        cube[112] = cube_tmp[69];
        cube[113] = cube_tmp[68];
        cube[114] = cube_tmp[67];
        cube[118] = cube_tmp[63];
        cube[119] = cube_tmp[62];
        cube[120] = cube_tmp[61];
        cube[124] = cube_tmp[57];
        cube[125] = cube_tmp[56];
        cube[126] = cube_tmp[55];
        cube[130] = cube_tmp[51];
        cube[131] = cube_tmp[50];
        cube[132] = cube_tmp[49];
        cube[136] = cube_tmp[45];
        cube[137] = cube_tmp[44];
        cube[138] = cube_tmp[43];
        cube[142] = cube_tmp[39];
        cube[143] = cube_tmp[38];
        cube[144] = cube_tmp[37];
        cube[145] = cube_tmp[180];
        cube[146] = cube_tmp[179];
        cube[147] = cube_tmp[178];
        cube[148] = cube_tmp[177];
        cube[149] = cube_tmp[176];
        cube[150] = cube_tmp[175];
        cube[151] = cube_tmp[174];
        cube[152] = cube_tmp[173];
        cube[153] = cube_tmp[172];
        cube[154] = cube_tmp[171];
        cube[155] = cube_tmp[170];
        cube[156] = cube_tmp[169];
        cube[157] = cube_tmp[168];
        cube[158] = cube_tmp[167];
        cube[159] = cube_tmp[166];
        cube[160] = cube_tmp[165];
        cube[161] = cube_tmp[164];
        cube[162] = cube_tmp[163];
        cube[163] = cube_tmp[162];
        cube[164] = cube_tmp[161];
        cube[165] = cube_tmp[160];
        cube[166] = cube_tmp[159];
        cube[167] = cube_tmp[158];
        cube[168] = cube_tmp[157];
        cube[169] = cube_tmp[156];
        cube[170] = cube_tmp[155];
        cube[171] = cube_tmp[154];
        cube[172] = cube_tmp[153];
        cube[173] = cube_tmp[152];
        cube[174] = cube_tmp[151];
        cube[175] = cube_tmp[150];
        cube[176] = cube_tmp[149];
        cube[177] = cube_tmp[148];
        cube[178] = cube_tmp[147];
        cube[179] = cube_tmp[146];
        cube[180] = cube_tmp[145];
        cube[199] = cube_tmp[18];
        cube[200] = cube_tmp[17];
        cube[201] = cube_tmp[16];
        cube[202] = cube_tmp[15];
        cube[203] = cube_tmp[14];
        cube[204] = cube_tmp[13];
        cube[205] = cube_tmp[12];
        cube[206] = cube_tmp[11];
        cube[207] = cube_tmp[10];
        cube[208] = cube_tmp[9];
        cube[209] = cube_tmp[8];
        cube[210] = cube_tmp[7];
        cube[211] = cube_tmp[6];
        cube[212] = cube_tmp[5];
        cube[213] = cube_tmp[4];
        cube[214] = cube_tmp[3];
        cube[215] = cube_tmp[2];
        cube[216] = cube_tmp[1];
        break;
    }

    case D: {
        cube[67] = cube_tmp[175];
        cube[68] = cube_tmp[176];
        cube[69] = cube_tmp[177];
        cube[70] = cube_tmp[178];
        cube[71] = cube_tmp[179];
        cube[72] = cube_tmp[180];
        cube[103] = cube_tmp[67];
        cube[104] = cube_tmp[68];
        cube[105] = cube_tmp[69];
        cube[106] = cube_tmp[70];
        cube[107] = cube_tmp[71];
        cube[108] = cube_tmp[72];
        cube[139] = cube_tmp[103];
        cube[140] = cube_tmp[104];
        cube[141] = cube_tmp[105];
        cube[142] = cube_tmp[106];
        cube[143] = cube_tmp[107];
        cube[144] = cube_tmp[108];
        cube[175] = cube_tmp[139];
        cube[176] = cube_tmp[140];
        cube[177] = cube_tmp[141];
        cube[178] = cube_tmp[142];
        cube[179] = cube_tmp[143];
        cube[180] = cube_tmp[144];
        cube[181] = cube_tmp[211];
        cube[182] = cube_tmp[205];
        cube[183] = cube_tmp[199];
        cube[184] = cube_tmp[193];
        cube[185] = cube_tmp[187];
        cube[186] = cube_tmp[181];
        cube[187] = cube_tmp[212];
        cube[188] = cube_tmp[206];
        cube[189] = cube_tmp[200];
        cube[190] = cube_tmp[194];
        cube[191] = cube_tmp[188];
        cube[192] = cube_tmp[182];
        cube[193] = cube_tmp[213];
        cube[194] = cube_tmp[207];
        cube[195] = cube_tmp[201];
        cube[196] = cube_tmp[195];
        cube[197] = cube_tmp[189];
        cube[198] = cube_tmp[183];
        cube[199] = cube_tmp[214];
        cube[200] = cube_tmp[208];
        cube[201] = cube_tmp[202];
        cube[202] = cube_tmp[196];
        cube[203] = cube_tmp[190];
        cube[204] = cube_tmp[184];
        cube[205] = cube_tmp[215];
        cube[206] = cube_tmp[209];
        cube[207] = cube_tmp[203];
        cube[208] = cube_tmp[197];
        cube[209] = cube_tmp[191];
        cube[210] = cube_tmp[185];
        cube[211] = cube_tmp[216];
        cube[212] = cube_tmp[210];
        cube[213] = cube_tmp[204];
        cube[214] = cube_tmp[198];
        cube[215] = cube_tmp[192];
        cube[216] = cube_tmp[186];
        break;
    }

    case D_PRIME: {
        cube[67] = cube_tmp[103];
        cube[68] = cube_tmp[104];
        cube[69] = cube_tmp[105];
        cube[70] = cube_tmp[106];
        cube[71] = cube_tmp[107];
        cube[72] = cube_tmp[108];
        cube[103] = cube_tmp[139];
        cube[104] = cube_tmp[140];
        cube[105] = cube_tmp[141];
        cube[106] = cube_tmp[142];
        cube[107] = cube_tmp[143];
        cube[108] = cube_tmp[144];
        cube[139] = cube_tmp[175];
        cube[140] = cube_tmp[176];
        cube[141] = cube_tmp[177];
        cube[142] = cube_tmp[178];
        cube[143] = cube_tmp[179];
        cube[144] = cube_tmp[180];
        cube[175] = cube_tmp[67];
        cube[176] = cube_tmp[68];
        cube[177] = cube_tmp[69];
        cube[178] = cube_tmp[70];
        cube[179] = cube_tmp[71];
        cube[180] = cube_tmp[72];
        cube[181] = cube_tmp[186];
        cube[182] = cube_tmp[192];
        cube[183] = cube_tmp[198];
        cube[184] = cube_tmp[204];
        cube[185] = cube_tmp[210];
        cube[186] = cube_tmp[216];
        cube[187] = cube_tmp[185];
        cube[188] = cube_tmp[191];
        cube[189] = cube_tmp[197];
        cube[190] = cube_tmp[203];
        cube[191] = cube_tmp[209];
        cube[192] = cube_tmp[215];
        cube[193] = cube_tmp[184];
        cube[194] = cube_tmp[190];
        cube[195] = cube_tmp[196];
        cube[196] = cube_tmp[202];
        cube[197] = cube_tmp[208];
        cube[198] = cube_tmp[214];
        cube[199] = cube_tmp[183];
        cube[200] = cube_tmp[189];
        cube[201] = cube_tmp[195];
        cube[202] = cube_tmp[201];
        cube[203] = cube_tmp[207];
        cube[204] = cube_tmp[213];
        cube[205] = cube_tmp[182];
        cube[206] = cube_tmp[188];
        cube[207] = cube_tmp[194];
        cube[208] = cube_tmp[200];
        cube[209] = cube_tmp[206];
        cube[210] = cube_tmp[212];
        cube[211] = cube_tmp[181];
        cube[212] = cube_tmp[187];
        cube[213] = cube_tmp[193];
        cube[214] = cube_tmp[199];
        cube[215] = cube_tmp[205];
        cube[216] = cube_tmp[211];
        break;
    }

    case D2: {
        cube[67] = cube_tmp[139];
        cube[68] = cube_tmp[140];
        cube[69] = cube_tmp[141];
        cube[70] = cube_tmp[142];
        cube[71] = cube_tmp[143];
        cube[72] = cube_tmp[144];
        cube[103] = cube_tmp[175];
        cube[104] = cube_tmp[176];
        cube[105] = cube_tmp[177];
        cube[106] = cube_tmp[178];
        cube[107] = cube_tmp[179];
        cube[108] = cube_tmp[180];
        cube[139] = cube_tmp[67];
        cube[140] = cube_tmp[68];
        cube[141] = cube_tmp[69];
        cube[142] = cube_tmp[70];
        cube[143] = cube_tmp[71];
        cube[144] = cube_tmp[72];
        cube[175] = cube_tmp[103];
        cube[176] = cube_tmp[104];
        cube[177] = cube_tmp[105];
        cube[178] = cube_tmp[106];
        cube[179] = cube_tmp[107];
        cube[180] = cube_tmp[108];
        cube[181] = cube_tmp[216];
        cube[182] = cube_tmp[215];
        cube[183] = cube_tmp[214];
        cube[184] = cube_tmp[213];
        cube[185] = cube_tmp[212];
        cube[186] = cube_tmp[211];
        cube[187] = cube_tmp[210];
        cube[188] = cube_tmp[209];
        cube[189] = cube_tmp[208];
        cube[190] = cube_tmp[207];
        cube[191] = cube_tmp[206];
        cube[192] = cube_tmp[205];
        cube[193] = cube_tmp[204];
        cube[194] = cube_tmp[203];
        cube[195] = cube_tmp[202];
        cube[196] = cube_tmp[201];
        cube[197] = cube_tmp[200];
        cube[198] = cube_tmp[199];
        cube[199] = cube_tmp[198];
        cube[200] = cube_tmp[197];
        cube[201] = cube_tmp[196];
        cube[202] = cube_tmp[195];
        cube[203] = cube_tmp[194];
        cube[204] = cube_tmp[193];
        cube[205] = cube_tmp[192];
        cube[206] = cube_tmp[191];
        cube[207] = cube_tmp[190];
        cube[208] = cube_tmp[189];
        cube[209] = cube_tmp[188];
        cube[210] = cube_tmp[187];
        cube[211] = cube_tmp[186];
        cube[212] = cube_tmp[185];
        cube[213] = cube_tmp[184];
        cube[214] = cube_tmp[183];
        cube[215] = cube_tmp[182];
        cube[216] = cube_tmp[181];
        break;
    }

    case Dw: {
        cube[61] = cube_tmp[169];
        cube[62] = cube_tmp[170];
        cube[63] = cube_tmp[171];
        cube[64] = cube_tmp[172];
        cube[65] = cube_tmp[173];
        cube[66] = cube_tmp[174];
        cube[67] = cube_tmp[175];
        cube[68] = cube_tmp[176];
        cube[69] = cube_tmp[177];
        cube[70] = cube_tmp[178];
        cube[71] = cube_tmp[179];
        cube[72] = cube_tmp[180];
        cube[97] = cube_tmp[61];
        cube[98] = cube_tmp[62];
        cube[99] = cube_tmp[63];
        cube[100] = cube_tmp[64];
        cube[101] = cube_tmp[65];
        cube[102] = cube_tmp[66];
        cube[103] = cube_tmp[67];
        cube[104] = cube_tmp[68];
        cube[105] = cube_tmp[69];
        cube[106] = cube_tmp[70];
        cube[107] = cube_tmp[71];
        cube[108] = cube_tmp[72];
        cube[133] = cube_tmp[97];
        cube[134] = cube_tmp[98];
        cube[135] = cube_tmp[99];
        cube[136] = cube_tmp[100];
        cube[137] = cube_tmp[101];
        cube[138] = cube_tmp[102];
        cube[139] = cube_tmp[103];
        cube[140] = cube_tmp[104];
        cube[141] = cube_tmp[105];
        cube[142] = cube_tmp[106];
        cube[143] = cube_tmp[107];
        cube[144] = cube_tmp[108];
        cube[169] = cube_tmp[133];
        cube[170] = cube_tmp[134];
        cube[171] = cube_tmp[135];
        cube[172] = cube_tmp[136];
        cube[173] = cube_tmp[137];
        cube[174] = cube_tmp[138];
        cube[175] = cube_tmp[139];
        cube[176] = cube_tmp[140];
        cube[177] = cube_tmp[141];
        cube[178] = cube_tmp[142];
        cube[179] = cube_tmp[143];
        cube[180] = cube_tmp[144];
        cube[181] = cube_tmp[211];
        cube[182] = cube_tmp[205];
        cube[183] = cube_tmp[199];
        cube[184] = cube_tmp[193];
        cube[185] = cube_tmp[187];
        cube[186] = cube_tmp[181];
        cube[187] = cube_tmp[212];
        cube[188] = cube_tmp[206];
        cube[189] = cube_tmp[200];
        cube[190] = cube_tmp[194];
        cube[191] = cube_tmp[188];
        cube[192] = cube_tmp[182];
        cube[193] = cube_tmp[213];
        cube[194] = cube_tmp[207];
        cube[195] = cube_tmp[201];
        cube[196] = cube_tmp[195];
        cube[197] = cube_tmp[189];
        cube[198] = cube_tmp[183];
        cube[199] = cube_tmp[214];
        cube[200] = cube_tmp[208];
        cube[201] = cube_tmp[202];
        cube[202] = cube_tmp[196];
        cube[203] = cube_tmp[190];
        cube[204] = cube_tmp[184];
        cube[205] = cube_tmp[215];
        cube[206] = cube_tmp[209];
        cube[207] = cube_tmp[203];
        cube[208] = cube_tmp[197];
        cube[209] = cube_tmp[191];
        cube[210] = cube_tmp[185];
        cube[211] = cube_tmp[216];
        cube[212] = cube_tmp[210];
        cube[213] = cube_tmp[204];
        cube[214] = cube_tmp[198];
        cube[215] = cube_tmp[192];
        cube[216] = cube_tmp[186];
        break;
    }

    case Dw_PRIME: {
        cube[61] = cube_tmp[97];
        cube[62] = cube_tmp[98];
        cube[63] = cube_tmp[99];
        cube[64] = cube_tmp[100];
        cube[65] = cube_tmp[101];
        cube[66] = cube_tmp[102];
        cube[67] = cube_tmp[103];
        cube[68] = cube_tmp[104];
        cube[69] = cube_tmp[105];
        cube[70] = cube_tmp[106];
        cube[71] = cube_tmp[107];
        cube[72] = cube_tmp[108];
        cube[97] = cube_tmp[133];
        cube[98] = cube_tmp[134];
        cube[99] = cube_tmp[135];
        cube[100] = cube_tmp[136];
        cube[101] = cube_tmp[137];
        cube[102] = cube_tmp[138];
        cube[103] = cube_tmp[139];
        cube[104] = cube_tmp[140];
        cube[105] = cube_tmp[141];
        cube[106] = cube_tmp[142];
        cube[107] = cube_tmp[143];
        cube[108] = cube_tmp[144];
        cube[133] = cube_tmp[169];
        cube[134] = cube_tmp[170];
        cube[135] = cube_tmp[171];
        cube[136] = cube_tmp[172];
        cube[137] = cube_tmp[173];
        cube[138] = cube_tmp[174];
        cube[139] = cube_tmp[175];
        cube[140] = cube_tmp[176];
        cube[141] = cube_tmp[177];
        cube[142] = cube_tmp[178];
        cube[143] = cube_tmp[179];
        cube[144] = cube_tmp[180];
        cube[169] = cube_tmp[61];
        cube[170] = cube_tmp[62];
        cube[171] = cube_tmp[63];
        cube[172] = cube_tmp[64];
        cube[173] = cube_tmp[65];
        cube[174] = cube_tmp[66];
        cube[175] = cube_tmp[67];
        cube[176] = cube_tmp[68];
        cube[177] = cube_tmp[69];
        cube[178] = cube_tmp[70];
        cube[179] = cube_tmp[71];
        cube[180] = cube_tmp[72];
        cube[181] = cube_tmp[186];
        cube[182] = cube_tmp[192];
        cube[183] = cube_tmp[198];
        cube[184] = cube_tmp[204];
        cube[185] = cube_tmp[210];
        cube[186] = cube_tmp[216];
        cube[187] = cube_tmp[185];
        cube[188] = cube_tmp[191];
        cube[189] = cube_tmp[197];
        cube[190] = cube_tmp[203];
        cube[191] = cube_tmp[209];
        cube[192] = cube_tmp[215];
        cube[193] = cube_tmp[184];
        cube[194] = cube_tmp[190];
        cube[195] = cube_tmp[196];
        cube[196] = cube_tmp[202];
        cube[197] = cube_tmp[208];
        cube[198] = cube_tmp[214];
        cube[199] = cube_tmp[183];
        cube[200] = cube_tmp[189];
        cube[201] = cube_tmp[195];
        cube[202] = cube_tmp[201];
        cube[203] = cube_tmp[207];
        cube[204] = cube_tmp[213];
        cube[205] = cube_tmp[182];
        cube[206] = cube_tmp[188];
        cube[207] = cube_tmp[194];
        cube[208] = cube_tmp[200];
        cube[209] = cube_tmp[206];
        cube[210] = cube_tmp[212];
        cube[211] = cube_tmp[181];
        cube[212] = cube_tmp[187];
        cube[213] = cube_tmp[193];
        cube[214] = cube_tmp[199];
        cube[215] = cube_tmp[205];
        cube[216] = cube_tmp[211];
        break;
    }

    case Dw2: {
        cube[61] = cube_tmp[133];
        cube[62] = cube_tmp[134];
        cube[63] = cube_tmp[135];
        cube[64] = cube_tmp[136];
        cube[65] = cube_tmp[137];
        cube[66] = cube_tmp[138];
        cube[67] = cube_tmp[139];
        cube[68] = cube_tmp[140];
        cube[69] = cube_tmp[141];
        cube[70] = cube_tmp[142];
        cube[71] = cube_tmp[143];
        cube[72] = cube_tmp[144];
        cube[97] = cube_tmp[169];
        cube[98] = cube_tmp[170];
        cube[99] = cube_tmp[171];
        cube[100] = cube_tmp[172];
        cube[101] = cube_tmp[173];
        cube[102] = cube_tmp[174];
        cube[103] = cube_tmp[175];
        cube[104] = cube_tmp[176];
        cube[105] = cube_tmp[177];
        cube[106] = cube_tmp[178];
        cube[107] = cube_tmp[179];
        cube[108] = cube_tmp[180];
        cube[133] = cube_tmp[61];
        cube[134] = cube_tmp[62];
        cube[135] = cube_tmp[63];
        cube[136] = cube_tmp[64];
        cube[137] = cube_tmp[65];
        cube[138] = cube_tmp[66];
        cube[139] = cube_tmp[67];
        cube[140] = cube_tmp[68];
        cube[141] = cube_tmp[69];
        cube[142] = cube_tmp[70];
        cube[143] = cube_tmp[71];
        cube[144] = cube_tmp[72];
        cube[169] = cube_tmp[97];
        cube[170] = cube_tmp[98];
        cube[171] = cube_tmp[99];
        cube[172] = cube_tmp[100];
        cube[173] = cube_tmp[101];
        cube[174] = cube_tmp[102];
        cube[175] = cube_tmp[103];
        cube[176] = cube_tmp[104];
        cube[177] = cube_tmp[105];
        cube[178] = cube_tmp[106];
        cube[179] = cube_tmp[107];
        cube[180] = cube_tmp[108];
        cube[181] = cube_tmp[216];
        cube[182] = cube_tmp[215];
        cube[183] = cube_tmp[214];
        cube[184] = cube_tmp[213];
        cube[185] = cube_tmp[212];
        cube[186] = cube_tmp[211];
        cube[187] = cube_tmp[210];
        cube[188] = cube_tmp[209];
        cube[189] = cube_tmp[208];
        cube[190] = cube_tmp[207];
        cube[191] = cube_tmp[206];
        cube[192] = cube_tmp[205];
        cube[193] = cube_tmp[204];
        cube[194] = cube_tmp[203];
        cube[195] = cube_tmp[202];
        cube[196] = cube_tmp[201];
        cube[197] = cube_tmp[200];
        cube[198] = cube_tmp[199];
        cube[199] = cube_tmp[198];
        cube[200] = cube_tmp[197];
        cube[201] = cube_tmp[196];
        cube[202] = cube_tmp[195];
        cube[203] = cube_tmp[194];
        cube[204] = cube_tmp[193];
        cube[205] = cube_tmp[192];
        cube[206] = cube_tmp[191];
        cube[207] = cube_tmp[190];
        cube[208] = cube_tmp[189];
        cube[209] = cube_tmp[188];
        cube[210] = cube_tmp[187];
        cube[211] = cube_tmp[186];
        cube[212] = cube_tmp[185];
        cube[213] = cube_tmp[184];
        cube[214] = cube_tmp[183];
        cube[215] = cube_tmp[182];
        cube[216] = cube_tmp[181];
        break;
    }

    case threeDw: {
        cube[55] = cube_tmp[163];
        cube[56] = cube_tmp[164];
        cube[57] = cube_tmp[165];
        cube[58] = cube_tmp[166];
        cube[59] = cube_tmp[167];
        cube[60] = cube_tmp[168];
        cube[61] = cube_tmp[169];
        cube[62] = cube_tmp[170];
        cube[63] = cube_tmp[171];
        cube[64] = cube_tmp[172];
        cube[65] = cube_tmp[173];
        cube[66] = cube_tmp[174];
        cube[67] = cube_tmp[175];
        cube[68] = cube_tmp[176];
        cube[69] = cube_tmp[177];
        cube[70] = cube_tmp[178];
        cube[71] = cube_tmp[179];
        cube[72] = cube_tmp[180];
        cube[91] = cube_tmp[55];
        cube[92] = cube_tmp[56];
        cube[93] = cube_tmp[57];
        cube[94] = cube_tmp[58];
        cube[95] = cube_tmp[59];
        cube[96] = cube_tmp[60];
        cube[97] = cube_tmp[61];
        cube[98] = cube_tmp[62];
        cube[99] = cube_tmp[63];
        cube[100] = cube_tmp[64];
        cube[101] = cube_tmp[65];
        cube[102] = cube_tmp[66];
        cube[103] = cube_tmp[67];
        cube[104] = cube_tmp[68];
        cube[105] = cube_tmp[69];
        cube[106] = cube_tmp[70];
        cube[107] = cube_tmp[71];
        cube[108] = cube_tmp[72];
        cube[127] = cube_tmp[91];
        cube[128] = cube_tmp[92];
        cube[129] = cube_tmp[93];
        cube[130] = cube_tmp[94];
        cube[131] = cube_tmp[95];
        cube[132] = cube_tmp[96];
        cube[133] = cube_tmp[97];
        cube[134] = cube_tmp[98];
        cube[135] = cube_tmp[99];
        cube[136] = cube_tmp[100];
        cube[137] = cube_tmp[101];
        cube[138] = cube_tmp[102];
        cube[139] = cube_tmp[103];
        cube[140] = cube_tmp[104];
        cube[141] = cube_tmp[105];
        cube[142] = cube_tmp[106];
        cube[143] = cube_tmp[107];
        cube[144] = cube_tmp[108];
        cube[163] = cube_tmp[127];
        cube[164] = cube_tmp[128];
        cube[165] = cube_tmp[129];
        cube[166] = cube_tmp[130];
        cube[167] = cube_tmp[131];
        cube[168] = cube_tmp[132];
        cube[169] = cube_tmp[133];
        cube[170] = cube_tmp[134];
        cube[171] = cube_tmp[135];
        cube[172] = cube_tmp[136];
        cube[173] = cube_tmp[137];
        cube[174] = cube_tmp[138];
        cube[175] = cube_tmp[139];
        cube[176] = cube_tmp[140];
        cube[177] = cube_tmp[141];
        cube[178] = cube_tmp[142];
        cube[179] = cube_tmp[143];
        cube[180] = cube_tmp[144];
        cube[181] = cube_tmp[211];
        cube[182] = cube_tmp[205];
        cube[183] = cube_tmp[199];
        cube[184] = cube_tmp[193];
        cube[185] = cube_tmp[187];
        cube[186] = cube_tmp[181];
        cube[187] = cube_tmp[212];
        cube[188] = cube_tmp[206];
        cube[189] = cube_tmp[200];
        cube[190] = cube_tmp[194];
        cube[191] = cube_tmp[188];
        cube[192] = cube_tmp[182];
        cube[193] = cube_tmp[213];
        cube[194] = cube_tmp[207];
        cube[195] = cube_tmp[201];
        cube[196] = cube_tmp[195];
        cube[197] = cube_tmp[189];
        cube[198] = cube_tmp[183];
        cube[199] = cube_tmp[214];
        cube[200] = cube_tmp[208];
        cube[201] = cube_tmp[202];
        cube[202] = cube_tmp[196];
        cube[203] = cube_tmp[190];
        cube[204] = cube_tmp[184];
        cube[205] = cube_tmp[215];
        cube[206] = cube_tmp[209];
        cube[207] = cube_tmp[203];
        cube[208] = cube_tmp[197];
        cube[209] = cube_tmp[191];
        cube[210] = cube_tmp[185];
        cube[211] = cube_tmp[216];
        cube[212] = cube_tmp[210];
        cube[213] = cube_tmp[204];
        cube[214] = cube_tmp[198];
        cube[215] = cube_tmp[192];
        cube[216] = cube_tmp[186];
        break;
    }

    case threeDw_PRIME: {
        cube[55] = cube_tmp[91];
        cube[56] = cube_tmp[92];
        cube[57] = cube_tmp[93];
        cube[58] = cube_tmp[94];
        cube[59] = cube_tmp[95];
        cube[60] = cube_tmp[96];
        cube[61] = cube_tmp[97];
        cube[62] = cube_tmp[98];
        cube[63] = cube_tmp[99];
        cube[64] = cube_tmp[100];
        cube[65] = cube_tmp[101];
        cube[66] = cube_tmp[102];
        cube[67] = cube_tmp[103];
        cube[68] = cube_tmp[104];
        cube[69] = cube_tmp[105];
        cube[70] = cube_tmp[106];
        cube[71] = cube_tmp[107];
        cube[72] = cube_tmp[108];
        cube[91] = cube_tmp[127];
        cube[92] = cube_tmp[128];
        cube[93] = cube_tmp[129];
        cube[94] = cube_tmp[130];
        cube[95] = cube_tmp[131];
        cube[96] = cube_tmp[132];
        cube[97] = cube_tmp[133];
        cube[98] = cube_tmp[134];
        cube[99] = cube_tmp[135];
        cube[100] = cube_tmp[136];
        cube[101] = cube_tmp[137];
        cube[102] = cube_tmp[138];
        cube[103] = cube_tmp[139];
        cube[104] = cube_tmp[140];
        cube[105] = cube_tmp[141];
        cube[106] = cube_tmp[142];
        cube[107] = cube_tmp[143];
        cube[108] = cube_tmp[144];
        cube[127] = cube_tmp[163];
        cube[128] = cube_tmp[164];
        cube[129] = cube_tmp[165];
        cube[130] = cube_tmp[166];
        cube[131] = cube_tmp[167];
        cube[132] = cube_tmp[168];
        cube[133] = cube_tmp[169];
        cube[134] = cube_tmp[170];
        cube[135] = cube_tmp[171];
        cube[136] = cube_tmp[172];
        cube[137] = cube_tmp[173];
        cube[138] = cube_tmp[174];
        cube[139] = cube_tmp[175];
        cube[140] = cube_tmp[176];
        cube[141] = cube_tmp[177];
        cube[142] = cube_tmp[178];
        cube[143] = cube_tmp[179];
        cube[144] = cube_tmp[180];
        cube[163] = cube_tmp[55];
        cube[164] = cube_tmp[56];
        cube[165] = cube_tmp[57];
        cube[166] = cube_tmp[58];
        cube[167] = cube_tmp[59];
        cube[168] = cube_tmp[60];
        cube[169] = cube_tmp[61];
        cube[170] = cube_tmp[62];
        cube[171] = cube_tmp[63];
        cube[172] = cube_tmp[64];
        cube[173] = cube_tmp[65];
        cube[174] = cube_tmp[66];
        cube[175] = cube_tmp[67];
        cube[176] = cube_tmp[68];
        cube[177] = cube_tmp[69];
        cube[178] = cube_tmp[70];
        cube[179] = cube_tmp[71];
        cube[180] = cube_tmp[72];
        cube[181] = cube_tmp[186];
        cube[182] = cube_tmp[192];
        cube[183] = cube_tmp[198];
        cube[184] = cube_tmp[204];
        cube[185] = cube_tmp[210];
        cube[186] = cube_tmp[216];
        cube[187] = cube_tmp[185];
        cube[188] = cube_tmp[191];
        cube[189] = cube_tmp[197];
        cube[190] = cube_tmp[203];
        cube[191] = cube_tmp[209];
        cube[192] = cube_tmp[215];
        cube[193] = cube_tmp[184];
        cube[194] = cube_tmp[190];
        cube[195] = cube_tmp[196];
        cube[196] = cube_tmp[202];
        cube[197] = cube_tmp[208];
        cube[198] = cube_tmp[214];
        cube[199] = cube_tmp[183];
        cube[200] = cube_tmp[189];
        cube[201] = cube_tmp[195];
        cube[202] = cube_tmp[201];
        cube[203] = cube_tmp[207];
        cube[204] = cube_tmp[213];
        cube[205] = cube_tmp[182];
        cube[206] = cube_tmp[188];
        cube[207] = cube_tmp[194];
        cube[208] = cube_tmp[200];
        cube[209] = cube_tmp[206];
        cube[210] = cube_tmp[212];
        cube[211] = cube_tmp[181];
        cube[212] = cube_tmp[187];
        cube[213] = cube_tmp[193];
        cube[214] = cube_tmp[199];
        cube[215] = cube_tmp[205];
        cube[216] = cube_tmp[211];
        break;
    }

    case threeDw2: {
        cube[55] = cube_tmp[127];
        cube[56] = cube_tmp[128];
        cube[57] = cube_tmp[129];
        cube[58] = cube_tmp[130];
        cube[59] = cube_tmp[131];
        cube[60] = cube_tmp[132];
        cube[61] = cube_tmp[133];
        cube[62] = cube_tmp[134];
        cube[63] = cube_tmp[135];
        cube[64] = cube_tmp[136];
        cube[65] = cube_tmp[137];
        cube[66] = cube_tmp[138];
        cube[67] = cube_tmp[139];
        cube[68] = cube_tmp[140];
        cube[69] = cube_tmp[141];
        cube[70] = cube_tmp[142];
        cube[71] = cube_tmp[143];
        cube[72] = cube_tmp[144];
        cube[91] = cube_tmp[163];
        cube[92] = cube_tmp[164];
        cube[93] = cube_tmp[165];
        cube[94] = cube_tmp[166];
        cube[95] = cube_tmp[167];
        cube[96] = cube_tmp[168];
        cube[97] = cube_tmp[169];
        cube[98] = cube_tmp[170];
        cube[99] = cube_tmp[171];
        cube[100] = cube_tmp[172];
        cube[101] = cube_tmp[173];
        cube[102] = cube_tmp[174];
        cube[103] = cube_tmp[175];
        cube[104] = cube_tmp[176];
        cube[105] = cube_tmp[177];
        cube[106] = cube_tmp[178];
        cube[107] = cube_tmp[179];
        cube[108] = cube_tmp[180];
        cube[127] = cube_tmp[55];
        cube[128] = cube_tmp[56];
        cube[129] = cube_tmp[57];
        cube[130] = cube_tmp[58];
        cube[131] = cube_tmp[59];
        cube[132] = cube_tmp[60];
        cube[133] = cube_tmp[61];
        cube[134] = cube_tmp[62];
        cube[135] = cube_tmp[63];
        cube[136] = cube_tmp[64];
        cube[137] = cube_tmp[65];
        cube[138] = cube_tmp[66];
        cube[139] = cube_tmp[67];
        cube[140] = cube_tmp[68];
        cube[141] = cube_tmp[69];
        cube[142] = cube_tmp[70];
        cube[143] = cube_tmp[71];
        cube[144] = cube_tmp[72];
        cube[163] = cube_tmp[91];
        cube[164] = cube_tmp[92];
        cube[165] = cube_tmp[93];
        cube[166] = cube_tmp[94];
        cube[167] = cube_tmp[95];
        cube[168] = cube_tmp[96];
        cube[169] = cube_tmp[97];
        cube[170] = cube_tmp[98];
        cube[171] = cube_tmp[99];
        cube[172] = cube_tmp[100];
        cube[173] = cube_tmp[101];
        cube[174] = cube_tmp[102];
        cube[175] = cube_tmp[103];
        cube[176] = cube_tmp[104];
        cube[177] = cube_tmp[105];
        cube[178] = cube_tmp[106];
        cube[179] = cube_tmp[107];
        cube[180] = cube_tmp[108];
        cube[181] = cube_tmp[216];
        cube[182] = cube_tmp[215];
        cube[183] = cube_tmp[214];
        cube[184] = cube_tmp[213];
        cube[185] = cube_tmp[212];
        cube[186] = cube_tmp[211];
        cube[187] = cube_tmp[210];
        cube[188] = cube_tmp[209];
        cube[189] = cube_tmp[208];
        cube[190] = cube_tmp[207];
        cube[191] = cube_tmp[206];
        cube[192] = cube_tmp[205];
        cube[193] = cube_tmp[204];
        cube[194] = cube_tmp[203];
        cube[195] = cube_tmp[202];
        cube[196] = cube_tmp[201];
        cube[197] = cube_tmp[200];
        cube[198] = cube_tmp[199];
        cube[199] = cube_tmp[198];
        cube[200] = cube_tmp[197];
        cube[201] = cube_tmp[196];
        cube[202] = cube_tmp[195];
        cube[203] = cube_tmp[194];
        cube[204] = cube_tmp[193];
        cube[205] = cube_tmp[192];
        cube[206] = cube_tmp[191];
        cube[207] = cube_tmp[190];
        cube[208] = cube_tmp[189];
        cube[209] = cube_tmp[188];
        cube[210] = cube_tmp[187];
        cube[211] = cube_tmp[186];
        cube[212] = cube_tmp[185];
        cube[213] = cube_tmp[184];
        cube[214] = cube_tmp[183];
        cube[215] = cube_tmp[182];
        cube[216] = cube_tmp[181];
        break;
    }


    default:
        printf("ERROR: invalid move %d\n", move);
        exit(1);
    }
}
            
void
rotate_666_centers(char *cube, char *cube_tmp, int array_size, move_type move)
{
    /* This was contructed using utils/rotate-printer.py */
    (void)cube_tmp;
    (void)array_size;

    switch (move) {
    case U: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29];
        cube[8] = c26;
        cube[9] = c20;
        cube[10] = c14;
        cube[11] = c8;
        cube[14] = c27;
        cube[15] = c21;
        cube[16] = c15;
        cube[17] = c9;
        cube[20] = c28;
        cube[21] = c22;
        cube[22] = c16;
        cube[23] = c10;
        cube[26] = c29;
        cube[27] = c23;
        cube[28] = c17;
        cube[29] = c11;
        break;
    }

    case U_PRIME: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29];
        cube[8] = c11;
        cube[9] = c17;
        cube[10] = c23;
        cube[11] = c29;
        cube[14] = c10;
        cube[15] = c16;
        cube[16] = c22;
        cube[17] = c28;
        cube[20] = c9;
        cube[21] = c15;
        cube[22] = c21;
        cube[23] = c27;
        cube[26] = c8;
        cube[27] = c14;
        cube[28] = c20;
        cube[29] = c26;
        break;
    }

    case U2: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29];
        cube[8] = c29;
        cube[9] = c28;
        cube[10] = c27;
        cube[11] = c26;
        cube[14] = c23;
        cube[15] = c22;
        cube[16] = c21;
        cube[17] = c20;
        cube[20] = c17;
        cube[21] = c16;
        cube[22] = c15;
        cube[23] = c14;
        cube[26] = c11;
        cube[27] = c10;
        cube[28] = c9;
        cube[29] = c8;
        break;
    }

    case Uw: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155];
        cube[8] = c26;
        cube[9] = c20;
        cube[10] = c14;
        cube[11] = c8;
        cube[14] = c27;
        cube[15] = c21;
        cube[16] = c15;
        cube[17] = c9;
        cube[20] = c28;
        cube[21] = c22;
        cube[22] = c16;
        cube[23] = c10;
        cube[26] = c29;
        cube[27] = c23;
        cube[28] = c17;
        cube[29] = c11;
        cube[44] = c80;
        cube[45] = c81;
        cube[46] = c82;
        cube[47] = c83;
        cube[80] = c116;
        cube[81] = c117;
        cube[82] = c118;
        cube[83] = c119;
        cube[116] = c152;
        cube[117] = c153;
        cube[118] = c154;
        cube[119] = c155;
        cube[152] = c44;
        cube[153] = c45;
        cube[154] = c46;
        cube[155] = c47;
        break;
    }

    case Uw_PRIME: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155];
        cube[8] = c11;
        cube[9] = c17;
        cube[10] = c23;
        cube[11] = c29;
        cube[14] = c10;
        cube[15] = c16;
        cube[16] = c22;
        cube[17] = c28;
        cube[20] = c9;
        cube[21] = c15;
        cube[22] = c21;
        cube[23] = c27;
        cube[26] = c8;
        cube[27] = c14;
        cube[28] = c20;
        cube[29] = c26;
        cube[44] = c152;
        cube[45] = c153;
        cube[46] = c154;
        cube[47] = c155;
        cube[80] = c44;
        cube[81] = c45;
        cube[82] = c46;
        cube[83] = c47;
        cube[116] = c80;
        cube[117] = c81;
        cube[118] = c82;
        cube[119] = c83;
        cube[152] = c116;
        cube[153] = c117;
        cube[154] = c118;
        cube[155] = c119;
        break;
    }

    case Uw2: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155];
        cube[8] = c29;
        cube[9] = c28;
        cube[10] = c27;
        cube[11] = c26;
        cube[14] = c23;
        cube[15] = c22;
        cube[16] = c21;
        cube[17] = c20;
        cube[20] = c17;
        cube[21] = c16;
        cube[22] = c15;
        cube[23] = c14;
        cube[26] = c11;
        cube[27] = c10;
        cube[28] = c9;
        cube[29] = c8;
        cube[44] = c116;
        cube[45] = c117;
        cube[46] = c118;
        cube[47] = c119;
        cube[80] = c152;
        cube[81] = c153;
        cube[82] = c154;
        cube[83] = c155;
        cube[116] = c44;
        cube[117] = c45;
        cube[118] = c46;
        cube[119] = c47;
        cube[152] = c80;
        cube[153] = c81;
        cube[154] = c82;
        cube[155] = c83;
        break;
    }

    case threeUw: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161];
        cube[8] = c26;
        cube[9] = c20;
        cube[10] = c14;
        cube[11] = c8;
        cube[14] = c27;
        cube[15] = c21;
        cube[16] = c15;
        cube[17] = c9;
        cube[20] = c28;
        cube[21] = c22;
        cube[22] = c16;
        cube[23] = c10;
        cube[26] = c29;
        cube[27] = c23;
        cube[28] = c17;
        cube[29] = c11;
        cube[44] = c80;
        cube[45] = c81;
        cube[46] = c82;
        cube[47] = c83;
        cube[50] = c86;
        cube[51] = c87;
        cube[52] = c88;
        cube[53] = c89;
        cube[80] = c116;
        cube[81] = c117;
        cube[82] = c118;
        cube[83] = c119;
        cube[86] = c122;
        cube[87] = c123;
        cube[88] = c124;
        cube[89] = c125;
        cube[116] = c152;
        cube[117] = c153;
        cube[118] = c154;
        cube[119] = c155;
        cube[122] = c158;
        cube[123] = c159;
        cube[124] = c160;
        cube[125] = c161;
        cube[152] = c44;
        cube[153] = c45;
        cube[154] = c46;
        cube[155] = c47;
        cube[158] = c50;
        cube[159] = c51;
        cube[160] = c52;
        cube[161] = c53;
        break;
    }

    case threeUw_PRIME: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161];
        cube[8] = c11;
        cube[9] = c17;
        cube[10] = c23;
        cube[11] = c29;
        cube[14] = c10;
        cube[15] = c16;
        cube[16] = c22;
        cube[17] = c28;
        cube[20] = c9;
        cube[21] = c15;
        cube[22] = c21;
        cube[23] = c27;
        cube[26] = c8;
        cube[27] = c14;
        cube[28] = c20;
        cube[29] = c26;
        cube[44] = c152;
        cube[45] = c153;
        cube[46] = c154;
        cube[47] = c155;
        cube[50] = c158;
        cube[51] = c159;
        cube[52] = c160;
        cube[53] = c161;
        cube[80] = c44;
        cube[81] = c45;
        cube[82] = c46;
        cube[83] = c47;
        cube[86] = c50;
        cube[87] = c51;
        cube[88] = c52;
        cube[89] = c53;
        cube[116] = c80;
        cube[117] = c81;
        cube[118] = c82;
        cube[119] = c83;
        cube[122] = c86;
        cube[123] = c87;
        cube[124] = c88;
        cube[125] = c89;
        cube[152] = c116;
        cube[153] = c117;
        cube[154] = c118;
        cube[155] = c119;
        cube[158] = c122;
        cube[159] = c123;
        cube[160] = c124;
        cube[161] = c125;
        break;
    }

    case threeUw2: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161];
        cube[8] = c29;
        cube[9] = c28;
        cube[10] = c27;
        cube[11] = c26;
        cube[14] = c23;
        cube[15] = c22;
        cube[16] = c21;
        cube[17] = c20;
        cube[20] = c17;
        cube[21] = c16;
        cube[22] = c15;
        cube[23] = c14;
        cube[26] = c11;
        cube[27] = c10;
        cube[28] = c9;
        cube[29] = c8;
        cube[44] = c116;
        cube[45] = c117;
        cube[46] = c118;
        cube[47] = c119;
        cube[50] = c122;
        cube[51] = c123;
        cube[52] = c124;
        cube[53] = c125;
        cube[80] = c152;
        cube[81] = c153;
        cube[82] = c154;
        cube[83] = c155;
        cube[86] = c158;
        cube[87] = c159;
        cube[88] = c160;
        cube[89] = c161;
        cube[116] = c44;
        cube[117] = c45;
        cube[118] = c46;
        cube[119] = c47;
        cube[122] = c50;
        cube[123] = c51;
        cube[124] = c52;
        cube[125] = c53;
        cube[152] = c80;
        cube[153] = c81;
        cube[154] = c82;
        cube[155] = c83;
        cube[158] = c86;
        cube[159] = c87;
        cube[160] = c88;
        cube[161] = c89;
        break;
    }

    case L: {
        char c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65];
        cube[44] = c62;
        cube[45] = c56;
        cube[46] = c50;
        cube[47] = c44;
        cube[50] = c63;
        cube[51] = c57;
        cube[52] = c51;
        cube[53] = c45;
        cube[56] = c64;
        cube[57] = c58;
        cube[58] = c52;
        cube[59] = c46;
        cube[62] = c65;
        cube[63] = c59;
        cube[64] = c53;
        cube[65] = c47;
        break;
    }

    case L_PRIME: {
        char c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65];
        cube[44] = c47;
        cube[45] = c53;
        cube[46] = c59;
        cube[47] = c65;
        cube[50] = c46;
        cube[51] = c52;
        cube[52] = c58;
        cube[53] = c64;
        cube[56] = c45;
        cube[57] = c51;
        cube[58] = c57;
        cube[59] = c63;
        cube[62] = c44;
        cube[63] = c50;
        cube[64] = c56;
        cube[65] = c62;
        break;
    }

    case L2: {
        char c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65];
        cube[44] = c65;
        cube[45] = c64;
        cube[46] = c63;
        cube[47] = c62;
        cube[50] = c59;
        cube[51] = c58;
        cube[52] = c57;
        cube[53] = c56;
        cube[56] = c53;
        cube[57] = c52;
        cube[58] = c51;
        cube[59] = c50;
        cube[62] = c47;
        cube[63] = c46;
        cube[64] = c45;
        cube[65] = c44;
        break;
    }

    case Lw: {
        char c8 = cube[8], c14 = cube[14], c20 = cube[20], c26 = cube[26],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c80 = cube[80], c86 = cube[86], c92 = cube[92], c98 = cube[98],
             c155 = cube[155], c161 = cube[161], c167 = cube[167], c173 = cube[173],
             c188 = cube[188], c194 = cube[194], c200 = cube[200], c206 = cube[206];
        cube[8] = c173;
        cube[14] = c167;
        cube[20] = c161;
        cube[26] = c155;
        cube[44] = c62;
        cube[45] = c56;
        cube[46] = c50;
        cube[47] = c44;
        cube[50] = c63;
        cube[51] = c57;
        cube[52] = c51;
        cube[53] = c45;
        cube[56] = c64;
        cube[57] = c58;
        cube[58] = c52;
        cube[59] = c46;
        cube[62] = c65;
        cube[63] = c59;
        cube[64] = c53;
        cube[65] = c47;
        cube[80] = c8;
        cube[86] = c14;
        cube[92] = c20;
        cube[98] = c26;
        cube[155] = c206;
        cube[161] = c200;
        cube[167] = c194;
        cube[173] = c188;
        cube[188] = c80;
        cube[194] = c86;
        cube[200] = c92;
        cube[206] = c98;
        break;
    }

    case Lw_PRIME: {
        char c8 = cube[8], c14 = cube[14], c20 = cube[20], c26 = cube[26],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c80 = cube[80], c86 = cube[86], c92 = cube[92], c98 = cube[98],
             c155 = cube[155], c161 = cube[161], c167 = cube[167], c173 = cube[173],
             c188 = cube[188], c194 = cube[194], c200 = cube[200], c206 = cube[206];
        cube[8] = c80;
        cube[14] = c86;
        cube[20] = c92;
        cube[26] = c98;
        cube[44] = c47;
        cube[45] = c53;
        cube[46] = c59;
        cube[47] = c65;
        cube[50] = c46;
        cube[51] = c52;
        cube[52] = c58;
        cube[53] = c64;
        cube[56] = c45;
        cube[57] = c51;
        cube[58] = c57;
        cube[59] = c63;
        cube[62] = c44;
        cube[63] = c50;
        cube[64] = c56;
        cube[65] = c62;
        cube[80] = c188;
        cube[86] = c194;
        cube[92] = c200;
        cube[98] = c206;
        cube[155] = c26;
        cube[161] = c20;
        cube[167] = c14;
        cube[173] = c8;
        cube[188] = c173;
        cube[194] = c167;
        cube[200] = c161;
        cube[206] = c155;
        break;
    }

    case Lw2: {
        char c8 = cube[8], c14 = cube[14], c20 = cube[20], c26 = cube[26],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c80 = cube[80], c86 = cube[86], c92 = cube[92], c98 = cube[98],
             c155 = cube[155], c161 = cube[161], c167 = cube[167], c173 = cube[173],
             c188 = cube[188], c194 = cube[194], c200 = cube[200], c206 = cube[206];
        cube[8] = c188;
        cube[14] = c194;
        cube[20] = c200;
        cube[26] = c206;
        cube[44] = c65;
        cube[45] = c64;
        cube[46] = c63;
        cube[47] = c62;
        cube[50] = c59;
        cube[51] = c58;
        cube[52] = c57;
        cube[53] = c56;
        cube[56] = c53;
        cube[57] = c52;
        cube[58] = c51;
        cube[59] = c50;
        cube[62] = c47;
        cube[63] = c46;
        cube[64] = c45;
        cube[65] = c44;
        cube[80] = c173;
        cube[86] = c167;
        cube[92] = c161;
        cube[98] = c155;
        cube[155] = c98;
        cube[161] = c92;
        cube[167] = c86;
        cube[173] = c80;
        cube[188] = c8;
        cube[194] = c14;
        cube[200] = c20;
        cube[206] = c26;
        break;
    }

    case threeLw: {
        char c8 = cube[8], c9 = cube[9], c14 = cube[14], c15 = cube[15],
             c20 = cube[20], c21 = cube[21], c26 = cube[26], c27 = cube[27],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c80 = cube[80], c81 = cube[81], c86 = cube[86], c87 = cube[87],
             c92 = cube[92], c93 = cube[93], c98 = cube[98], c99 = cube[99],
             c154 = cube[154], c155 = cube[155], c160 = cube[160], c161 = cube[161],
             c166 = cube[166], c167 = cube[167], c172 = cube[172], c173 = cube[173],
             c188 = cube[188], c189 = cube[189], c194 = cube[194], c195 = cube[195],
             c200 = cube[200], c201 = cube[201], c206 = cube[206], c207 = cube[207];
        cube[8] = c173;
        cube[9] = c172;
        cube[14] = c167;
        cube[15] = c166;
        cube[20] = c161;
        cube[21] = c160;
        cube[26] = c155;
        cube[27] = c154;
        cube[44] = c62;
        cube[45] = c56;
        cube[46] = c50;
        cube[47] = c44;
        cube[50] = c63;
        cube[51] = c57;
        cube[52] = c51;
        cube[53] = c45;
        cube[56] = c64;
        cube[57] = c58;
        cube[58] = c52;
        cube[59] = c46;
        cube[62] = c65;
        cube[63] = c59;
        cube[64] = c53;
        cube[65] = c47;
        cube[80] = c8;
        cube[81] = c9;
        cube[86] = c14;
        cube[87] = c15;
        cube[92] = c20;
        cube[93] = c21;
        cube[98] = c26;
        cube[99] = c27;
        cube[154] = c207;
        cube[155] = c206;
        cube[160] = c201;
        cube[161] = c200;
        cube[166] = c195;
        cube[167] = c194;
        cube[172] = c189;
        cube[173] = c188;
        cube[188] = c80;
        cube[189] = c81;
        cube[194] = c86;
        cube[195] = c87;
        cube[200] = c92;
        cube[201] = c93;
        cube[206] = c98;
        cube[207] = c99;
        break;
    }

    case threeLw_PRIME: {
        char c8 = cube[8], c9 = cube[9], c14 = cube[14], c15 = cube[15],
             c20 = cube[20], c21 = cube[21], c26 = cube[26], c27 = cube[27],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c80 = cube[80], c81 = cube[81], c86 = cube[86], c87 = cube[87],
             c92 = cube[92], c93 = cube[93], c98 = cube[98], c99 = cube[99],
             c154 = cube[154], c155 = cube[155], c160 = cube[160], c161 = cube[161],
             c166 = cube[166], c167 = cube[167], c172 = cube[172], c173 = cube[173],
             c188 = cube[188], c189 = cube[189], c194 = cube[194], c195 = cube[195],
             c200 = cube[200], c201 = cube[201], c206 = cube[206], c207 = cube[207];
        cube[8] = c80;
        cube[9] = c81;
        cube[14] = c86;
        cube[15] = c87;
        cube[20] = c92;
        cube[21] = c93;
        cube[26] = c98;
        cube[27] = c99;
        cube[44] = c47;
        cube[45] = c53;
        cube[46] = c59;
        cube[47] = c65;
        cube[50] = c46;
        cube[51] = c52;
        cube[52] = c58;
        cube[53] = c64;
        cube[56] = c45;
        cube[57] = c51;
        cube[58] = c57;
        cube[59] = c63;
        cube[62] = c44;
        cube[63] = c50;
        cube[64] = c56;
        cube[65] = c62;
        cube[80] = c188;
        cube[81] = c189;
        cube[86] = c194;
        cube[87] = c195;
        cube[92] = c200;
        cube[93] = c201;
        cube[98] = c206;
        cube[99] = c207;
        cube[154] = c27;
        cube[155] = c26;
        cube[160] = c21;
        cube[161] = c20;
        cube[166] = c15;
        cube[167] = c14;
        cube[172] = c9;
        cube[173] = c8;
        cube[188] = c173;
        cube[189] = c172;
        cube[194] = c167;
        cube[195] = c166;
        cube[200] = c161;
        cube[201] = c160;
        cube[206] = c155;
        cube[207] = c154;
        break;
    }

    case threeLw2: {
        char c8 = cube[8], c9 = cube[9], c14 = cube[14], c15 = cube[15],
             c20 = cube[20], c21 = cube[21], c26 = cube[26], c27 = cube[27],
             c44 = cube[44], c45 = cube[45], c46 = cube[46], c47 = cube[47],
             c50 = cube[50], c51 = cube[51], c52 = cube[52], c53 = cube[53],
             c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c80 = cube[80], c81 = cube[81], c86 = cube[86], c87 = cube[87],
             c92 = cube[92], c93 = cube[93], c98 = cube[98], c99 = cube[99],
             c154 = cube[154], c155 = cube[155], c160 = cube[160], c161 = cube[161],
             c166 = cube[166], c167 = cube[167], c172 = cube[172], c173 = cube[173],
             c188 = cube[188], c189 = cube[189], c194 = cube[194], c195 = cube[195],
             c200 = cube[200], c201 = cube[201], c206 = cube[206], c207 = cube[207];
        cube[8] = c188;
        cube[9] = c189;
        cube[14] = c194;
        cube[15] = c195;
        cube[20] = c200;
        cube[21] = c201;
        cube[26] = c206;
        cube[27] = c207;
        cube[44] = c65;
        cube[45] = c64;
        cube[46] = c63;
        cube[47] = c62;
        cube[50] = c59;
        cube[51] = c58;
        cube[52] = c57;
        cube[53] = c56;
        cube[56] = c53;
        cube[57] = c52;
        cube[58] = c51;
        cube[59] = c50;
        cube[62] = c47;
        cube[63] = c46;
        cube[64] = c45;
        cube[65] = c44;
        cube[80] = c173;
        cube[81] = c172;
        cube[86] = c167;
        cube[87] = c166;
        cube[92] = c161;
        cube[93] = c160;
        cube[98] = c155;
        cube[99] = c154;
        cube[154] = c99;
        cube[155] = c98;
        cube[160] = c93;
        cube[161] = c92;
        cube[166] = c87;
        cube[167] = c86;
        cube[172] = c81;
        cube[173] = c80;
        cube[188] = c8;
        cube[189] = c9;
        cube[194] = c14;
        cube[195] = c15;
        cube[200] = c20;
        cube[201] = c21;
        cube[206] = c26;
        cube[207] = c27;
        break;
    }

    case F: {
        char c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101];
        cube[80] = c98;
        cube[81] = c92;
        cube[82] = c86;
        cube[83] = c80;
        cube[86] = c99;
        cube[87] = c93;
        cube[88] = c87;
        cube[89] = c81;
        cube[92] = c100;
        cube[93] = c94;
        cube[94] = c88;
        cube[95] = c82;
        cube[98] = c101;
        cube[99] = c95;
        cube[100] = c89;
        cube[101] = c83;
        break;
    }

    case F_PRIME: {
        char c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101];
        cube[80] = c83;
        cube[81] = c89;
        cube[82] = c95;
        cube[83] = c101;
        cube[86] = c82;
        cube[87] = c88;
        cube[88] = c94;
        cube[89] = c100;
        cube[92] = c81;
        cube[93] = c87;
        cube[94] = c93;
        cube[95] = c99;
        cube[98] = c80;
        cube[99] = c86;
        cube[100] = c92;
        cube[101] = c98;
        break;
    }

    case F2: {
        char c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101];
        cube[80] = c101;
        cube[81] = c100;
        cube[82] = c99;
        cube[83] = c98;
        cube[86] = c95;
        cube[87] = c94;
        cube[88] = c93;
        cube[89] = c92;
        cube[92] = c89;
        cube[93] = c88;
        cube[94] = c87;
        cube[95] = c86;
        cube[98] = c83;
        cube[99] = c82;
        cube[100] = c81;
        cube[101] = c80;
        break;
    }

    case Fw: {
        char c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c47 = cube[47], c53 = cube[53], c59 = cube[59], c65 = cube[65],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c116 = cube[116], c122 = cube[122], c128 = cube[128], c134 = cube[134],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191];
        cube[26] = c65;
        cube[27] = c59;
        cube[28] = c53;
        cube[29] = c47;
        cube[47] = c188;
        cube[53] = c189;
        cube[59] = c190;
        cube[65] = c191;
        cube[80] = c98;
        cube[81] = c92;
        cube[82] = c86;
        cube[83] = c80;
        cube[86] = c99;
        cube[87] = c93;
        cube[88] = c87;
        cube[89] = c81;
        cube[92] = c100;
        cube[93] = c94;
        cube[94] = c88;
        cube[95] = c82;
        cube[98] = c101;
        cube[99] = c95;
        cube[100] = c89;
        cube[101] = c83;
        cube[116] = c26;
        cube[122] = c27;
        cube[128] = c28;
        cube[134] = c29;
        cube[188] = c134;
        cube[189] = c128;
        cube[190] = c122;
        cube[191] = c116;
        break;
    }

    case Fw_PRIME: {
        char c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c47 = cube[47], c53 = cube[53], c59 = cube[59], c65 = cube[65],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c116 = cube[116], c122 = cube[122], c128 = cube[128], c134 = cube[134],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191];
        cube[26] = c116;
        cube[27] = c122;
        cube[28] = c128;
        cube[29] = c134;
        cube[47] = c29;
        cube[53] = c28;
        cube[59] = c27;
        cube[65] = c26;
        cube[80] = c83;
        cube[81] = c89;
        cube[82] = c95;
        cube[83] = c101;
        cube[86] = c82;
        cube[87] = c88;
        cube[88] = c94;
        cube[89] = c100;
        cube[92] = c81;
        cube[93] = c87;
        cube[94] = c93;
        cube[95] = c99;
        cube[98] = c80;
        cube[99] = c86;
        cube[100] = c92;
        cube[101] = c98;
        cube[116] = c191;
        cube[122] = c190;
        cube[128] = c189;
        cube[134] = c188;
        cube[188] = c47;
        cube[189] = c53;
        cube[190] = c59;
        cube[191] = c65;
        break;
    }

    case Fw2: {
        char c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c47 = cube[47], c53 = cube[53], c59 = cube[59], c65 = cube[65],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c116 = cube[116], c122 = cube[122], c128 = cube[128], c134 = cube[134],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191];
        cube[26] = c191;
        cube[27] = c190;
        cube[28] = c189;
        cube[29] = c188;
        cube[47] = c134;
        cube[53] = c128;
        cube[59] = c122;
        cube[65] = c116;
        cube[80] = c101;
        cube[81] = c100;
        cube[82] = c99;
        cube[83] = c98;
        cube[86] = c95;
        cube[87] = c94;
        cube[88] = c93;
        cube[89] = c92;
        cube[92] = c89;
        cube[93] = c88;
        cube[94] = c87;
        cube[95] = c86;
        cube[98] = c83;
        cube[99] = c82;
        cube[100] = c81;
        cube[101] = c80;
        cube[116] = c65;
        cube[122] = c59;
        cube[128] = c53;
        cube[134] = c47;
        cube[188] = c29;
        cube[189] = c28;
        cube[190] = c27;
        cube[191] = c26;
        break;
    }

    case threeFw: {
        char c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c46 = cube[46], c47 = cube[47], c52 = cube[52], c53 = cube[53],
             c58 = cube[58], c59 = cube[59], c64 = cube[64], c65 = cube[65],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c116 = cube[116], c117 = cube[117], c122 = cube[122], c123 = cube[123],
             c128 = cube[128], c129 = cube[129], c134 = cube[134], c135 = cube[135],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197];
        cube[20] = c64;
        cube[21] = c58;
        cube[22] = c52;
        cube[23] = c46;
        cube[26] = c65;
        cube[27] = c59;
        cube[28] = c53;
        cube[29] = c47;
        cube[46] = c194;
        cube[47] = c188;
        cube[52] = c195;
        cube[53] = c189;
        cube[58] = c196;
        cube[59] = c190;
        cube[64] = c197;
        cube[65] = c191;
        cube[80] = c98;
        cube[81] = c92;
        cube[82] = c86;
        cube[83] = c80;
        cube[86] = c99;
        cube[87] = c93;
        cube[88] = c87;
        cube[89] = c81;
        cube[92] = c100;
        cube[93] = c94;
        cube[94] = c88;
        cube[95] = c82;
        cube[98] = c101;
        cube[99] = c95;
        cube[100] = c89;
        cube[101] = c83;
        cube[116] = c26;
        cube[117] = c20;
        cube[122] = c27;
        cube[123] = c21;
        cube[128] = c28;
        cube[129] = c22;
        cube[134] = c29;
        cube[135] = c23;
        cube[188] = c134;
        cube[189] = c128;
        cube[190] = c122;
        cube[191] = c116;
        cube[194] = c135;
        cube[195] = c129;
        cube[196] = c123;
        cube[197] = c117;
        break;
    }

    case threeFw_PRIME: {
        char c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c46 = cube[46], c47 = cube[47], c52 = cube[52], c53 = cube[53],
             c58 = cube[58], c59 = cube[59], c64 = cube[64], c65 = cube[65],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c116 = cube[116], c117 = cube[117], c122 = cube[122], c123 = cube[123],
             c128 = cube[128], c129 = cube[129], c134 = cube[134], c135 = cube[135],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197];
        cube[20] = c117;
        cube[21] = c123;
        cube[22] = c129;
        cube[23] = c135;
        cube[26] = c116;
        cube[27] = c122;
        cube[28] = c128;
        cube[29] = c134;
        cube[46] = c23;
        cube[47] = c29;
        cube[52] = c22;
        cube[53] = c28;
        cube[58] = c21;
        cube[59] = c27;
        cube[64] = c20;
        cube[65] = c26;
        cube[80] = c83;
        cube[81] = c89;
        cube[82] = c95;
        cube[83] = c101;
        cube[86] = c82;
        cube[87] = c88;
        cube[88] = c94;
        cube[89] = c100;
        cube[92] = c81;
        cube[93] = c87;
        cube[94] = c93;
        cube[95] = c99;
        cube[98] = c80;
        cube[99] = c86;
        cube[100] = c92;
        cube[101] = c98;
        cube[116] = c191;
        cube[117] = c197;
        cube[122] = c190;
        cube[123] = c196;
        cube[128] = c189;
        cube[129] = c195;
        cube[134] = c188;
        cube[135] = c194;
        cube[188] = c47;
        cube[189] = c53;
        cube[190] = c59;
        cube[191] = c65;
        cube[194] = c46;
        cube[195] = c52;
        cube[196] = c58;
        cube[197] = c64;
        break;
    }

    case threeFw2: {
        char c20 = cube[20], c21 = cube[21], c22 = cube[22], c23 = cube[23],
             c26 = cube[26], c27 = cube[27], c28 = cube[28], c29 = cube[29],
             c46 = cube[46], c47 = cube[47], c52 = cube[52], c53 = cube[53],
             c58 = cube[58], c59 = cube[59], c64 = cube[64], c65 = cube[65],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c116 = cube[116], c117 = cube[117], c122 = cube[122], c123 = cube[123],
             c128 = cube[128], c129 = cube[129], c134 = cube[134], c135 = cube[135],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197];
        cube[20] = c197;
        cube[21] = c196;
        cube[22] = c195;
        cube[23] = c194;
        cube[26] = c191;
        cube[27] = c190;
        cube[28] = c189;
        cube[29] = c188;
        cube[46] = c135;
        cube[47] = c134;
        cube[52] = c129;
        cube[53] = c128;
        cube[58] = c123;
        cube[59] = c122;
        cube[64] = c117;
        cube[65] = c116;
        cube[80] = c101;
        cube[81] = c100;
        cube[82] = c99;
        cube[83] = c98;
        cube[86] = c95;
        cube[87] = c94;
        cube[88] = c93;
        cube[89] = c92;
        cube[92] = c89;
        cube[93] = c88;
        cube[94] = c87;
        cube[95] = c86;
        cube[98] = c83;
        cube[99] = c82;
        cube[100] = c81;
        cube[101] = c80;
        cube[116] = c65;
        cube[117] = c64;
        cube[122] = c59;
        cube[123] = c58;
        cube[128] = c53;
        cube[129] = c52;
        cube[134] = c47;
        cube[135] = c46;
        cube[188] = c29;
        cube[189] = c28;
        cube[190] = c27;
        cube[191] = c26;
        cube[194] = c23;
        cube[195] = c22;
        cube[196] = c21;
        cube[197] = c20;
        break;
    }

    case R: {
        char c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137];
        cube[116] = c134;
        cube[117] = c128;
        cube[118] = c122;
        cube[119] = c116;
        cube[122] = c135;
        cube[123] = c129;
        cube[124] = c123;
        cube[125] = c117;
        cube[128] = c136;
        cube[129] = c130;
        cube[130] = c124;
        cube[131] = c118;
        cube[134] = c137;
        cube[135] = c131;
        cube[136] = c125;
        cube[137] = c119;
        break;
    }

    case R_PRIME: {
        char c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137];
        cube[116] = c119;
        cube[117] = c125;
        cube[118] = c131;
        cube[119] = c137;
        cube[122] = c118;
        cube[123] = c124;
        cube[124] = c130;
        cube[125] = c136;
        cube[128] = c117;
        cube[129] = c123;
        cube[130] = c129;
        cube[131] = c135;
        cube[134] = c116;
        cube[135] = c122;
        cube[136] = c128;
        cube[137] = c134;
        break;
    }

    case R2: {
        char c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137];
        cube[116] = c137;
        cube[117] = c136;
        cube[118] = c135;
        cube[119] = c134;
        cube[122] = c131;
        cube[123] = c130;
        cube[124] = c129;
        cube[125] = c128;
        cube[128] = c125;
        cube[129] = c124;
        cube[130] = c123;
        cube[131] = c122;
        cube[134] = c119;
        cube[135] = c118;
        cube[136] = c117;
        cube[137] = c116;
        break;
    }

    case Rw: {
        char c11 = cube[11], c17 = cube[17], c23 = cube[23], c29 = cube[29],
             c83 = cube[83], c89 = cube[89], c95 = cube[95], c101 = cube[101],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c152 = cube[152], c158 = cube[158], c164 = cube[164], c170 = cube[170],
             c191 = cube[191], c197 = cube[197], c203 = cube[203], c209 = cube[209];
        cube[11] = c83;
        cube[17] = c89;
        cube[23] = c95;
        cube[29] = c101;
        cube[83] = c191;
        cube[89] = c197;
        cube[95] = c203;
        cube[101] = c209;
        cube[116] = c134;
        cube[117] = c128;
        cube[118] = c122;
        cube[119] = c116;
        cube[122] = c135;
        cube[123] = c129;
        cube[124] = c123;
        cube[125] = c117;
        cube[128] = c136;
        cube[129] = c130;
        cube[130] = c124;
        cube[131] = c118;
        cube[134] = c137;
        cube[135] = c131;
        cube[136] = c125;
        cube[137] = c119;
        cube[152] = c29;
        cube[158] = c23;
        cube[164] = c17;
        cube[170] = c11;
        cube[191] = c170;
        cube[197] = c164;
        cube[203] = c158;
        cube[209] = c152;
        break;
    }

    case Rw_PRIME: {
        char c11 = cube[11], c17 = cube[17], c23 = cube[23], c29 = cube[29],
             c83 = cube[83], c89 = cube[89], c95 = cube[95], c101 = cube[101],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c152 = cube[152], c158 = cube[158], c164 = cube[164], c170 = cube[170],
             c191 = cube[191], c197 = cube[197], c203 = cube[203], c209 = cube[209];
        cube[11] = c170;
        cube[17] = c164;
        cube[23] = c158;
        cube[29] = c152;
        cube[83] = c11;
        cube[89] = c17;
        cube[95] = c23;
        cube[101] = c29;
        cube[116] = c119;
        cube[117] = c125;
        cube[118] = c131;
        cube[119] = c137;
        cube[122] = c118;
        cube[123] = c124;
        cube[124] = c130;
        cube[125] = c136;
        cube[128] = c117;
        cube[129] = c123;
        cube[130] = c129;
        cube[131] = c135;
        cube[134] = c116;
        cube[135] = c122;
        cube[136] = c128;
        cube[137] = c134;
        cube[152] = c209;
        cube[158] = c203;
        cube[164] = c197;
        cube[170] = c191;
        cube[191] = c83;
        cube[197] = c89;
        cube[203] = c95;
        cube[209] = c101;
        break;
    }

    case Rw2: {
        char c11 = cube[11], c17 = cube[17], c23 = cube[23], c29 = cube[29],
             c83 = cube[83], c89 = cube[89], c95 = cube[95], c101 = cube[101],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c152 = cube[152], c158 = cube[158], c164 = cube[164], c170 = cube[170],
             c191 = cube[191], c197 = cube[197], c203 = cube[203], c209 = cube[209];
        cube[11] = c191;
        cube[17] = c197;
        cube[23] = c203;
        cube[29] = c209;
        cube[83] = c170;
        cube[89] = c164;
        cube[95] = c158;
        cube[101] = c152;
        cube[116] = c137;
        cube[117] = c136;
        cube[118] = c135;
        cube[119] = c134;
        cube[122] = c131;
        cube[123] = c130;
        cube[124] = c129;
        cube[125] = c128;
        cube[128] = c125;
        cube[129] = c124;
        cube[130] = c123;
        cube[131] = c122;
        cube[134] = c119;
        cube[135] = c118;
        cube[136] = c117;
        cube[137] = c116;
        cube[152] = c101;
        cube[158] = c95;
        cube[164] = c89;
        cube[170] = c83;
        cube[191] = c11;
        cube[197] = c17;
        cube[203] = c23;
        cube[209] = c29;
        break;
    }

    case threeRw: {
        char c10 = cube[10], c11 = cube[11], c16 = cube[16], c17 = cube[17],
             c22 = cube[22], c23 = cube[23], c28 = cube[28], c29 = cube[29],
             c82 = cube[82], c83 = cube[83], c88 = cube[88], c89 = cube[89],
             c94 = cube[94], c95 = cube[95], c100 = cube[100], c101 = cube[101],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c152 = cube[152], c153 = cube[153], c158 = cube[158], c159 = cube[159],
             c164 = cube[164], c165 = cube[165], c170 = cube[170], c171 = cube[171],
             c190 = cube[190], c191 = cube[191], c196 = cube[196], c197 = cube[197],
             c202 = cube[202], c203 = cube[203], c208 = cube[208], c209 = cube[209];
        cube[10] = c82;
        cube[11] = c83;
        cube[16] = c88;
        cube[17] = c89;
        cube[22] = c94;
        cube[23] = c95;
        cube[28] = c100;
        cube[29] = c101;
        cube[82] = c190;
        cube[83] = c191;
        cube[88] = c196;
        cube[89] = c197;
        cube[94] = c202;
        cube[95] = c203;
        cube[100] = c208;
        cube[101] = c209;
        cube[116] = c134;
        cube[117] = c128;
        cube[118] = c122;
        cube[119] = c116;
        cube[122] = c135;
        cube[123] = c129;
        cube[124] = c123;
        cube[125] = c117;
        cube[128] = c136;
        cube[129] = c130;
        cube[130] = c124;
        cube[131] = c118;
        cube[134] = c137;
        cube[135] = c131;
        cube[136] = c125;
        cube[137] = c119;
        cube[152] = c29;
        cube[153] = c28;
        cube[158] = c23;
        cube[159] = c22;
        cube[164] = c17;
        cube[165] = c16;
        cube[170] = c11;
        cube[171] = c10;
        cube[190] = c171;
        cube[191] = c170;
        cube[196] = c165;
        cube[197] = c164;
        cube[202] = c159;
        cube[203] = c158;
        cube[208] = c153;
        cube[209] = c152;
        break;
    }

    case threeRw_PRIME: {
        char c10 = cube[10], c11 = cube[11], c16 = cube[16], c17 = cube[17],
             c22 = cube[22], c23 = cube[23], c28 = cube[28], c29 = cube[29],
             c82 = cube[82], c83 = cube[83], c88 = cube[88], c89 = cube[89],
             c94 = cube[94], c95 = cube[95], c100 = cube[100], c101 = cube[101],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c152 = cube[152], c153 = cube[153], c158 = cube[158], c159 = cube[159],
             c164 = cube[164], c165 = cube[165], c170 = cube[170], c171 = cube[171],
             c190 = cube[190], c191 = cube[191], c196 = cube[196], c197 = cube[197],
             c202 = cube[202], c203 = cube[203], c208 = cube[208], c209 = cube[209];
        cube[10] = c171;
        cube[11] = c170;
        cube[16] = c165;
        cube[17] = c164;
        cube[22] = c159;
        cube[23] = c158;
        cube[28] = c153;
        cube[29] = c152;
        cube[82] = c10;
        cube[83] = c11;
        cube[88] = c16;
        cube[89] = c17;
        cube[94] = c22;
        cube[95] = c23;
        cube[100] = c28;
        cube[101] = c29;
        cube[116] = c119;
        cube[117] = c125;
        cube[118] = c131;
        cube[119] = c137;
        cube[122] = c118;
        cube[123] = c124;
        cube[124] = c130;
        cube[125] = c136;
        cube[128] = c117;
        cube[129] = c123;
        cube[130] = c129;
        cube[131] = c135;
        cube[134] = c116;
        cube[135] = c122;
        cube[136] = c128;
        cube[137] = c134;
        cube[152] = c209;
        cube[153] = c208;
        cube[158] = c203;
        cube[159] = c202;
        cube[164] = c197;
        cube[165] = c196;
        cube[170] = c191;
        cube[171] = c190;
        cube[190] = c82;
        cube[191] = c83;
        cube[196] = c88;
        cube[197] = c89;
        cube[202] = c94;
        cube[203] = c95;
        cube[208] = c100;
        cube[209] = c101;
        break;
    }

    case threeRw2: {
        char c10 = cube[10], c11 = cube[11], c16 = cube[16], c17 = cube[17],
             c22 = cube[22], c23 = cube[23], c28 = cube[28], c29 = cube[29],
             c82 = cube[82], c83 = cube[83], c88 = cube[88], c89 = cube[89],
             c94 = cube[94], c95 = cube[95], c100 = cube[100], c101 = cube[101],
             c116 = cube[116], c117 = cube[117], c118 = cube[118], c119 = cube[119],
             c122 = cube[122], c123 = cube[123], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c152 = cube[152], c153 = cube[153], c158 = cube[158], c159 = cube[159],
             c164 = cube[164], c165 = cube[165], c170 = cube[170], c171 = cube[171],
             c190 = cube[190], c191 = cube[191], c196 = cube[196], c197 = cube[197],
             c202 = cube[202], c203 = cube[203], c208 = cube[208], c209 = cube[209];
        cube[10] = c190;
        cube[11] = c191;
        cube[16] = c196;
        cube[17] = c197;
        cube[22] = c202;
        cube[23] = c203;
        cube[28] = c208;
        cube[29] = c209;
        cube[82] = c171;
        cube[83] = c170;
        cube[88] = c165;
        cube[89] = c164;
        cube[94] = c159;
        cube[95] = c158;
        cube[100] = c153;
        cube[101] = c152;
        cube[116] = c137;
        cube[117] = c136;
        cube[118] = c135;
        cube[119] = c134;
        cube[122] = c131;
        cube[123] = c130;
        cube[124] = c129;
        cube[125] = c128;
        cube[128] = c125;
        cube[129] = c124;
        cube[130] = c123;
        cube[131] = c122;
        cube[134] = c119;
        cube[135] = c118;
        cube[136] = c117;
        cube[137] = c116;
        cube[152] = c101;
        cube[153] = c100;
        cube[158] = c95;
        cube[159] = c94;
        cube[164] = c89;
        cube[165] = c88;
        cube[170] = c83;
        cube[171] = c82;
        cube[190] = c10;
        cube[191] = c11;
        cube[196] = c16;
        cube[197] = c17;
        cube[202] = c22;
        cube[203] = c23;
        cube[208] = c28;
        cube[209] = c29;
        break;
    }

    case B: {
        char c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173];
        cube[152] = c170;
        cube[153] = c164;
        cube[154] = c158;
        cube[155] = c152;
        cube[158] = c171;
        cube[159] = c165;
        cube[160] = c159;
        cube[161] = c153;
        cube[164] = c172;
        cube[165] = c166;
        cube[166] = c160;
        cube[167] = c154;
        cube[170] = c173;
        cube[171] = c167;
        cube[172] = c161;
        cube[173] = c155;
        break;
    }

    case B_PRIME: {
        char c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173];
        cube[152] = c155;
        cube[153] = c161;
        cube[154] = c167;
        cube[155] = c173;
        cube[158] = c154;
        cube[159] = c160;
        cube[160] = c166;
        cube[161] = c172;
        cube[164] = c153;
        cube[165] = c159;
        cube[166] = c165;
        cube[167] = c171;
        cube[170] = c152;
        cube[171] = c158;
        cube[172] = c164;
        cube[173] = c170;
        break;
    }

    case B2: {
        char c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173];
        cube[152] = c173;
        cube[153] = c172;
        cube[154] = c171;
        cube[155] = c170;
        cube[158] = c167;
        cube[159] = c166;
        cube[160] = c165;
        cube[161] = c164;
        cube[164] = c161;
        cube[165] = c160;
        cube[166] = c159;
        cube[167] = c158;
        cube[170] = c155;
        cube[171] = c154;
        cube[172] = c153;
        cube[173] = c152;
        break;
    }

    case Bw: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c44 = cube[44], c50 = cube[50], c56 = cube[56], c62 = cube[62],
             c119 = cube[119], c125 = cube[125], c131 = cube[131], c137 = cube[137],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[8] = c119;
        cube[9] = c125;
        cube[10] = c131;
        cube[11] = c137;
        cube[44] = c11;
        cube[50] = c10;
        cube[56] = c9;
        cube[62] = c8;
        cube[119] = c209;
        cube[125] = c208;
        cube[131] = c207;
        cube[137] = c206;
        cube[152] = c170;
        cube[153] = c164;
        cube[154] = c158;
        cube[155] = c152;
        cube[158] = c171;
        cube[159] = c165;
        cube[160] = c159;
        cube[161] = c153;
        cube[164] = c172;
        cube[165] = c166;
        cube[166] = c160;
        cube[167] = c154;
        cube[170] = c173;
        cube[171] = c167;
        cube[172] = c161;
        cube[173] = c155;
        cube[206] = c44;
        cube[207] = c50;
        cube[208] = c56;
        cube[209] = c62;
        break;
    }

    case Bw_PRIME: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c44 = cube[44], c50 = cube[50], c56 = cube[56], c62 = cube[62],
             c119 = cube[119], c125 = cube[125], c131 = cube[131], c137 = cube[137],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[8] = c62;
        cube[9] = c56;
        cube[10] = c50;
        cube[11] = c44;
        cube[44] = c206;
        cube[50] = c207;
        cube[56] = c208;
        cube[62] = c209;
        cube[119] = c8;
        cube[125] = c9;
        cube[131] = c10;
        cube[137] = c11;
        cube[152] = c155;
        cube[153] = c161;
        cube[154] = c167;
        cube[155] = c173;
        cube[158] = c154;
        cube[159] = c160;
        cube[160] = c166;
        cube[161] = c172;
        cube[164] = c153;
        cube[165] = c159;
        cube[166] = c165;
        cube[167] = c171;
        cube[170] = c152;
        cube[171] = c158;
        cube[172] = c164;
        cube[173] = c170;
        cube[206] = c137;
        cube[207] = c131;
        cube[208] = c125;
        cube[209] = c119;
        break;
    }

    case Bw2: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c44 = cube[44], c50 = cube[50], c56 = cube[56], c62 = cube[62],
             c119 = cube[119], c125 = cube[125], c131 = cube[131], c137 = cube[137],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[8] = c209;
        cube[9] = c208;
        cube[10] = c207;
        cube[11] = c206;
        cube[44] = c137;
        cube[50] = c131;
        cube[56] = c125;
        cube[62] = c119;
        cube[119] = c62;
        cube[125] = c56;
        cube[131] = c50;
        cube[137] = c44;
        cube[152] = c173;
        cube[153] = c172;
        cube[154] = c171;
        cube[155] = c170;
        cube[158] = c167;
        cube[159] = c166;
        cube[160] = c165;
        cube[161] = c164;
        cube[164] = c161;
        cube[165] = c160;
        cube[166] = c159;
        cube[167] = c158;
        cube[170] = c155;
        cube[171] = c154;
        cube[172] = c153;
        cube[173] = c152;
        cube[206] = c11;
        cube[207] = c10;
        cube[208] = c9;
        cube[209] = c8;
        break;
    }

    case threeBw: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c44 = cube[44], c45 = cube[45], c50 = cube[50], c51 = cube[51],
             c56 = cube[56], c57 = cube[57], c62 = cube[62], c63 = cube[63],
             c118 = cube[118], c119 = cube[119], c124 = cube[124], c125 = cube[125],
             c130 = cube[130], c131 = cube[131], c136 = cube[136], c137 = cube[137],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[8] = c119;
        cube[9] = c125;
        cube[10] = c131;
        cube[11] = c137;
        cube[14] = c118;
        cube[15] = c124;
        cube[16] = c130;
        cube[17] = c136;
        cube[44] = c11;
        cube[45] = c17;
        cube[50] = c10;
        cube[51] = c16;
        cube[56] = c9;
        cube[57] = c15;
        cube[62] = c8;
        cube[63] = c14;
        cube[118] = c203;
        cube[119] = c209;
        cube[124] = c202;
        cube[125] = c208;
        cube[130] = c201;
        cube[131] = c207;
        cube[136] = c200;
        cube[137] = c206;
        cube[152] = c170;
        cube[153] = c164;
        cube[154] = c158;
        cube[155] = c152;
        cube[158] = c171;
        cube[159] = c165;
        cube[160] = c159;
        cube[161] = c153;
        cube[164] = c172;
        cube[165] = c166;
        cube[166] = c160;
        cube[167] = c154;
        cube[170] = c173;
        cube[171] = c167;
        cube[172] = c161;
        cube[173] = c155;
        cube[200] = c45;
        cube[201] = c51;
        cube[202] = c57;
        cube[203] = c63;
        cube[206] = c44;
        cube[207] = c50;
        cube[208] = c56;
        cube[209] = c62;
        break;
    }

    case threeBw_PRIME: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c44 = cube[44], c45 = cube[45], c50 = cube[50], c51 = cube[51],
             c56 = cube[56], c57 = cube[57], c62 = cube[62], c63 = cube[63],
             c118 = cube[118], c119 = cube[119], c124 = cube[124], c125 = cube[125],
             c130 = cube[130], c131 = cube[131], c136 = cube[136], c137 = cube[137],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[8] = c62;
        cube[9] = c56;
        cube[10] = c50;
        cube[11] = c44;
        cube[14] = c63;
        cube[15] = c57;
        cube[16] = c51;
        cube[17] = c45;
        cube[44] = c206;
        cube[45] = c200;
        cube[50] = c207;
        cube[51] = c201;
        cube[56] = c208;
        cube[57] = c202;
        cube[62] = c209;
        cube[63] = c203;
        cube[118] = c14;
        cube[119] = c8;
        cube[124] = c15;
        cube[125] = c9;
        cube[130] = c16;
        cube[131] = c10;
        cube[136] = c17;
        cube[137] = c11;
        cube[152] = c155;
        cube[153] = c161;
        cube[154] = c167;
        cube[155] = c173;
        cube[158] = c154;
        cube[159] = c160;
        cube[160] = c166;
        cube[161] = c172;
        cube[164] = c153;
        cube[165] = c159;
        cube[166] = c165;
        cube[167] = c171;
        cube[170] = c152;
        cube[171] = c158;
        cube[172] = c164;
        cube[173] = c170;
        cube[200] = c136;
        cube[201] = c130;
        cube[202] = c124;
        cube[203] = c118;
        cube[206] = c137;
        cube[207] = c131;
        cube[208] = c125;
        cube[209] = c119;
        break;
    }

    case threeBw2: {
        char c8 = cube[8], c9 = cube[9], c10 = cube[10], c11 = cube[11],
             c14 = cube[14], c15 = cube[15], c16 = cube[16], c17 = cube[17],
             c44 = cube[44], c45 = cube[45], c50 = cube[50], c51 = cube[51],
             c56 = cube[56], c57 = cube[57], c62 = cube[62], c63 = cube[63],
             c118 = cube[118], c119 = cube[119], c124 = cube[124], c125 = cube[125],
             c130 = cube[130], c131 = cube[131], c136 = cube[136], c137 = cube[137],
             c152 = cube[152], c153 = cube[153], c154 = cube[154], c155 = cube[155],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c161 = cube[161],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[8] = c209;
        cube[9] = c208;
        cube[10] = c207;
        cube[11] = c206;
        cube[14] = c203;
        cube[15] = c202;
        cube[16] = c201;
        cube[17] = c200;
        cube[44] = c137;
        cube[45] = c136;
        cube[50] = c131;
        cube[51] = c130;
        cube[56] = c125;
        cube[57] = c124;
        cube[62] = c119;
        cube[63] = c118;
        cube[118] = c63;
        cube[119] = c62;
        cube[124] = c57;
        cube[125] = c56;
        cube[130] = c51;
        cube[131] = c50;
        cube[136] = c45;
        cube[137] = c44;
        cube[152] = c173;
        cube[153] = c172;
        cube[154] = c171;
        cube[155] = c170;
        cube[158] = c167;
        cube[159] = c166;
        cube[160] = c165;
        cube[161] = c164;
        cube[164] = c161;
        cube[165] = c160;
        cube[166] = c159;
        cube[167] = c158;
        cube[170] = c155;
        cube[171] = c154;
        cube[172] = c153;
        cube[173] = c152;
        cube[200] = c17;
        cube[201] = c16;
        cube[202] = c15;
        cube[203] = c14;
        cube[206] = c11;
        cube[207] = c10;
        cube[208] = c9;
        cube[209] = c8;
        break;
    }

    case D: {
        char c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[188] = c206;
        cube[189] = c200;
        cube[190] = c194;
        cube[191] = c188;
        cube[194] = c207;
        cube[195] = c201;
        cube[196] = c195;
        cube[197] = c189;
        cube[200] = c208;
        cube[201] = c202;
        cube[202] = c196;
        cube[203] = c190;
        cube[206] = c209;
        cube[207] = c203;
        cube[208] = c197;
        cube[209] = c191;
        break;
    }

    case D_PRIME: {
        char c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[188] = c191;
        cube[189] = c197;
        cube[190] = c203;
        cube[191] = c209;
        cube[194] = c190;
        cube[195] = c196;
        cube[196] = c202;
        cube[197] = c208;
        cube[200] = c189;
        cube[201] = c195;
        cube[202] = c201;
        cube[203] = c207;
        cube[206] = c188;
        cube[207] = c194;
        cube[208] = c200;
        cube[209] = c206;
        break;
    }

    case D2: {
        char c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[188] = c209;
        cube[189] = c208;
        cube[190] = c207;
        cube[191] = c206;
        cube[194] = c203;
        cube[195] = c202;
        cube[196] = c201;
        cube[197] = c200;
        cube[200] = c197;
        cube[201] = c196;
        cube[202] = c195;
        cube[203] = c194;
        cube[206] = c191;
        cube[207] = c190;
        cube[208] = c189;
        cube[209] = c188;
        break;
    }

    case Dw: {
        char c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[62] = c170;
        cube[63] = c171;
        cube[64] = c172;
        cube[65] = c173;
        cube[98] = c62;
        cube[99] = c63;
        cube[100] = c64;
        cube[101] = c65;
        cube[134] = c98;
        cube[135] = c99;
        cube[136] = c100;
        cube[137] = c101;
        cube[170] = c134;
        cube[171] = c135;
        cube[172] = c136;
        cube[173] = c137;
        cube[188] = c206;
        cube[189] = c200;
        cube[190] = c194;
        cube[191] = c188;
        cube[194] = c207;
        cube[195] = c201;
        cube[196] = c195;
        cube[197] = c189;
        cube[200] = c208;
        cube[201] = c202;
        cube[202] = c196;
        cube[203] = c190;
        cube[206] = c209;
        cube[207] = c203;
        cube[208] = c197;
        cube[209] = c191;
        break;
    }

    case Dw_PRIME: {
        char c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[62] = c98;
        cube[63] = c99;
        cube[64] = c100;
        cube[65] = c101;
        cube[98] = c134;
        cube[99] = c135;
        cube[100] = c136;
        cube[101] = c137;
        cube[134] = c170;
        cube[135] = c171;
        cube[136] = c172;
        cube[137] = c173;
        cube[170] = c62;
        cube[171] = c63;
        cube[172] = c64;
        cube[173] = c65;
        cube[188] = c191;
        cube[189] = c197;
        cube[190] = c203;
        cube[191] = c209;
        cube[194] = c190;
        cube[195] = c196;
        cube[196] = c202;
        cube[197] = c208;
        cube[200] = c189;
        cube[201] = c195;
        cube[202] = c201;
        cube[203] = c207;
        cube[206] = c188;
        cube[207] = c194;
        cube[208] = c200;
        cube[209] = c206;
        break;
    }

    case Dw2: {
        char c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[62] = c134;
        cube[63] = c135;
        cube[64] = c136;
        cube[65] = c137;
        cube[98] = c170;
        cube[99] = c171;
        cube[100] = c172;
        cube[101] = c173;
        cube[134] = c62;
        cube[135] = c63;
        cube[136] = c64;
        cube[137] = c65;
        cube[170] = c98;
        cube[171] = c99;
        cube[172] = c100;
        cube[173] = c101;
        cube[188] = c209;
        cube[189] = c208;
        cube[190] = c207;
        cube[191] = c206;
        cube[194] = c203;
        cube[195] = c202;
        cube[196] = c201;
        cube[197] = c200;
        cube[200] = c197;
        cube[201] = c196;
        cube[202] = c195;
        cube[203] = c194;
        cube[206] = c191;
        cube[207] = c190;
        cube[208] = c189;
        cube[209] = c188;
        break;
    }

    case threeDw: {
        char c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[56] = c164;
        cube[57] = c165;
        cube[58] = c166;
        cube[59] = c167;
        cube[62] = c170;
        cube[63] = c171;
        cube[64] = c172;
        cube[65] = c173;
        cube[92] = c56;
        cube[93] = c57;
        cube[94] = c58;
        cube[95] = c59;
        cube[98] = c62;
        cube[99] = c63;
        cube[100] = c64;
        cube[101] = c65;
        cube[128] = c92;
        cube[129] = c93;
        cube[130] = c94;
        cube[131] = c95;
        cube[134] = c98;
        cube[135] = c99;
        cube[136] = c100;
        cube[137] = c101;
        cube[164] = c128;
        cube[165] = c129;
        cube[166] = c130;
        cube[167] = c131;
        cube[170] = c134;
        cube[171] = c135;
        cube[172] = c136;
        cube[173] = c137;
        cube[188] = c206;
        cube[189] = c200;
        cube[190] = c194;
        cube[191] = c188;
        cube[194] = c207;
        cube[195] = c201;
        cube[196] = c195;
        cube[197] = c189;
        cube[200] = c208;
        cube[201] = c202;
        cube[202] = c196;
        cube[203] = c190;
        cube[206] = c209;
        cube[207] = c203;
        cube[208] = c197;
        cube[209] = c191;
        break;
    }

    case threeDw_PRIME: {
        char c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[56] = c92;
        cube[57] = c93;
        cube[58] = c94;
        cube[59] = c95;
        cube[62] = c98;
        cube[63] = c99;
        cube[64] = c100;
        cube[65] = c101;
        cube[92] = c128;
        cube[93] = c129;
        cube[94] = c130;
        cube[95] = c131;
        cube[98] = c134;
        cube[99] = c135;
        cube[100] = c136;
        cube[101] = c137;
        cube[128] = c164;
        cube[129] = c165;
        cube[130] = c166;
        cube[131] = c167;
        cube[134] = c170;
        cube[135] = c171;
        cube[136] = c172;
        cube[137] = c173;
        cube[164] = c56;
        cube[165] = c57;
        cube[166] = c58;
        cube[167] = c59;
        cube[170] = c62;
        cube[171] = c63;
        cube[172] = c64;
        cube[173] = c65;
        cube[188] = c191;
        cube[189] = c197;
        cube[190] = c203;
        cube[191] = c209;
        cube[194] = c190;
        cube[195] = c196;
        cube[196] = c202;
        cube[197] = c208;
        cube[200] = c189;
        cube[201] = c195;
        cube[202] = c201;
        cube[203] = c207;
        cube[206] = c188;
        cube[207] = c194;
        cube[208] = c200;
        cube[209] = c206;
        break;
    }

    case threeDw2: {
        char c56 = cube[56], c57 = cube[57], c58 = cube[58], c59 = cube[59],
             c62 = cube[62], c63 = cube[63], c64 = cube[64], c65 = cube[65],
             c92 = cube[92], c93 = cube[93], c94 = cube[94], c95 = cube[95],
             c98 = cube[98], c99 = cube[99], c100 = cube[100], c101 = cube[101],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c134 = cube[134], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c172 = cube[172], c173 = cube[173],
             c188 = cube[188], c189 = cube[189], c190 = cube[190], c191 = cube[191],
             c194 = cube[194], c195 = cube[195], c196 = cube[196], c197 = cube[197],
             c200 = cube[200], c201 = cube[201], c202 = cube[202], c203 = cube[203],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[56] = c128;
        cube[57] = c129;
        cube[58] = c130;
        cube[59] = c131;
        cube[62] = c134;
        cube[63] = c135;
        cube[64] = c136;
        cube[65] = c137;
        cube[92] = c164;
        cube[93] = c165;
        cube[94] = c166;
        cube[95] = c167;
        cube[98] = c170;
        cube[99] = c171;
        cube[100] = c172;
        cube[101] = c173;
        cube[128] = c56;
        cube[129] = c57;
        cube[130] = c58;
        cube[131] = c59;
        cube[134] = c62;
        cube[135] = c63;
        cube[136] = c64;
        cube[137] = c65;
        cube[164] = c92;
        cube[165] = c93;
        cube[166] = c94;
        cube[167] = c95;
        cube[170] = c98;
        cube[171] = c99;
        cube[172] = c100;
        cube[173] = c101;
        cube[188] = c209;
        cube[189] = c208;
        cube[190] = c207;
        cube[191] = c206;
        cube[194] = c203;
        cube[195] = c202;
        cube[196] = c201;
        cube[197] = c200;
        cube[200] = c197;
        cube[201] = c196;
        cube[202] = c195;
        cube[203] = c194;
        cube[206] = c191;
        cube[207] = c190;
        cube[208] = c189;
        cube[209] = c188;
        break;
    }


    default:
        printf("ERROR: invalid move %d\n", move);
        exit(1);
    }
}
            
void
rotate_777(char *cube, char *cube_tmp, int array_size, move_type move)
{
    /* This was contructed using utils/rotate-printer.py */
    memcpy(cube_tmp, cube, sizeof(char) * array_size);

    switch (move) {
    case U: {
        cube[1] = cube_tmp[43];
        cube[2] = cube_tmp[36];
        cube[3] = cube_tmp[29];
        cube[4] = cube_tmp[22];
        cube[5] = cube_tmp[15];
        cube[6] = cube_tmp[8];
        cube[7] = cube_tmp[1];
        cube[8] = cube_tmp[44];
        cube[9] = cube_tmp[37];
        cube[10] = cube_tmp[30];
        cube[11] = cube_tmp[23];
        cube[12] = cube_tmp[16];
        cube[13] = cube_tmp[9];
        cube[14] = cube_tmp[2];
        cube[15] = cube_tmp[45];
        cube[16] = cube_tmp[38];
        cube[17] = cube_tmp[31];
        cube[18] = cube_tmp[24];
        cube[19] = cube_tmp[17];
        cube[20] = cube_tmp[10];
        cube[21] = cube_tmp[3];
        cube[22] = cube_tmp[46];
        cube[23] = cube_tmp[39];
        cube[24] = cube_tmp[32];
        cube[26] = cube_tmp[18];
        cube[27] = cube_tmp[11];
        cube[28] = cube_tmp[4];
        cube[29] = cube_tmp[47];
        cube[30] = cube_tmp[40];
        cube[31] = cube_tmp[33];
        cube[32] = cube_tmp[26];
        cube[33] = cube_tmp[19];
        cube[34] = cube_tmp[12];
        cube[35] = cube_tmp[5];
        cube[36] = cube_tmp[48];
        cube[37] = cube_tmp[41];
        cube[38] = cube_tmp[34];
        cube[39] = cube_tmp[27];
        cube[40] = cube_tmp[20];
        cube[41] = cube_tmp[13];
        cube[42] = cube_tmp[6];
        cube[43] = cube_tmp[49];
        cube[44] = cube_tmp[42];
        cube[45] = cube_tmp[35];
        cube[46] = cube_tmp[28];
        cube[47] = cube_tmp[21];
        cube[48] = cube_tmp[14];
        cube[49] = cube_tmp[7];
        cube[50] = cube_tmp[99];
        cube[51] = cube_tmp[100];
        cube[52] = cube_tmp[101];
        cube[53] = cube_tmp[102];
        cube[54] = cube_tmp[103];
        cube[55] = cube_tmp[104];
        cube[56] = cube_tmp[105];
        cube[99] = cube_tmp[148];
        cube[100] = cube_tmp[149];
        cube[101] = cube_tmp[150];
        cube[102] = cube_tmp[151];
        cube[103] = cube_tmp[152];
        cube[104] = cube_tmp[153];
        cube[105] = cube_tmp[154];
        cube[148] = cube_tmp[197];
        cube[149] = cube_tmp[198];
        cube[150] = cube_tmp[199];
        cube[151] = cube_tmp[200];
        cube[152] = cube_tmp[201];
        cube[153] = cube_tmp[202];
        cube[154] = cube_tmp[203];
        cube[197] = cube_tmp[50];
        cube[198] = cube_tmp[51];
        cube[199] = cube_tmp[52];
        cube[200] = cube_tmp[53];
        cube[201] = cube_tmp[54];
        cube[202] = cube_tmp[55];
        cube[203] = cube_tmp[56];
        break;
    }

    case U_PRIME: {
        cube[1] = cube_tmp[7];
        cube[2] = cube_tmp[14];
        cube[3] = cube_tmp[21];
        cube[4] = cube_tmp[28];
        cube[5] = cube_tmp[35];
        cube[6] = cube_tmp[42];
        cube[7] = cube_tmp[49];
        cube[8] = cube_tmp[6];
        cube[9] = cube_tmp[13];
        cube[10] = cube_tmp[20];
        cube[11] = cube_tmp[27];
        cube[12] = cube_tmp[34];
        cube[13] = cube_tmp[41];
        cube[14] = cube_tmp[48];
        cube[15] = cube_tmp[5];
        cube[16] = cube_tmp[12];
        cube[17] = cube_tmp[19];
        cube[18] = cube_tmp[26];
        cube[19] = cube_tmp[33];
        cube[20] = cube_tmp[40];
        cube[21] = cube_tmp[47];
        cube[22] = cube_tmp[4];
        cube[23] = cube_tmp[11];
        cube[24] = cube_tmp[18];
        cube[26] = cube_tmp[32];
        cube[27] = cube_tmp[39];
        cube[28] = cube_tmp[46];
        cube[29] = cube_tmp[3];
        cube[30] = cube_tmp[10];
        cube[31] = cube_tmp[17];
        cube[32] = cube_tmp[24];
        cube[33] = cube_tmp[31];
        cube[34] = cube_tmp[38];
        cube[35] = cube_tmp[45];
        cube[36] = cube_tmp[2];
        cube[37] = cube_tmp[9];
        cube[38] = cube_tmp[16];
        cube[39] = cube_tmp[23];
        cube[40] = cube_tmp[30];
        cube[41] = cube_tmp[37];
        cube[42] = cube_tmp[44];
        cube[43] = cube_tmp[1];
        cube[44] = cube_tmp[8];
        cube[45] = cube_tmp[15];
        cube[46] = cube_tmp[22];
        cube[47] = cube_tmp[29];
        cube[48] = cube_tmp[36];
        cube[49] = cube_tmp[43];
        cube[50] = cube_tmp[197];
        cube[51] = cube_tmp[198];
        cube[52] = cube_tmp[199];
        cube[53] = cube_tmp[200];
        cube[54] = cube_tmp[201];
        cube[55] = cube_tmp[202];
        cube[56] = cube_tmp[203];
        cube[99] = cube_tmp[50];
        cube[100] = cube_tmp[51];
        cube[101] = cube_tmp[52];
        cube[102] = cube_tmp[53];
        cube[103] = cube_tmp[54];
        cube[104] = cube_tmp[55];
        cube[105] = cube_tmp[56];
        cube[148] = cube_tmp[99];
        cube[149] = cube_tmp[100];
        cube[150] = cube_tmp[101];
        cube[151] = cube_tmp[102];
        cube[152] = cube_tmp[103];
        cube[153] = cube_tmp[104];
        cube[154] = cube_tmp[105];
        cube[197] = cube_tmp[148];
        cube[198] = cube_tmp[149];
        cube[199] = cube_tmp[150];
        cube[200] = cube_tmp[151];
        cube[201] = cube_tmp[152];
        cube[202] = cube_tmp[153];
        cube[203] = cube_tmp[154];
        break;
    }

    case U2: {
        cube[1] = cube_tmp[49];
        cube[2] = cube_tmp[48];
        cube[3] = cube_tmp[47];
        cube[4] = cube_tmp[46];
        cube[5] = cube_tmp[45];
        cube[6] = cube_tmp[44];
        cube[7] = cube_tmp[43];
        cube[8] = cube_tmp[42];
        cube[9] = cube_tmp[41];
        cube[10] = cube_tmp[40];
        cube[11] = cube_tmp[39];
        cube[12] = cube_tmp[38];
        cube[13] = cube_tmp[37];
        cube[14] = cube_tmp[36];
        cube[15] = cube_tmp[35];
        cube[16] = cube_tmp[34];
        cube[17] = cube_tmp[33];
        cube[18] = cube_tmp[32];
        cube[19] = cube_tmp[31];
        cube[20] = cube_tmp[30];
        cube[21] = cube_tmp[29];
        cube[22] = cube_tmp[28];
        cube[23] = cube_tmp[27];
        cube[24] = cube_tmp[26];
        cube[26] = cube_tmp[24];
        cube[27] = cube_tmp[23];
        cube[28] = cube_tmp[22];
        cube[29] = cube_tmp[21];
        cube[30] = cube_tmp[20];
        cube[31] = cube_tmp[19];
        cube[32] = cube_tmp[18];
        cube[33] = cube_tmp[17];
        cube[34] = cube_tmp[16];
        cube[35] = cube_tmp[15];
        cube[36] = cube_tmp[14];
        cube[37] = cube_tmp[13];
        cube[38] = cube_tmp[12];
        cube[39] = cube_tmp[11];
        cube[40] = cube_tmp[10];
        cube[41] = cube_tmp[9];
        cube[42] = cube_tmp[8];
        cube[43] = cube_tmp[7];
        cube[44] = cube_tmp[6];
        cube[45] = cube_tmp[5];
        cube[46] = cube_tmp[4];
        cube[47] = cube_tmp[3];
        cube[48] = cube_tmp[2];
        cube[49] = cube_tmp[1];
        cube[50] = cube_tmp[148];
        cube[51] = cube_tmp[149];
        cube[52] = cube_tmp[150];
        cube[53] = cube_tmp[151];
        cube[54] = cube_tmp[152];
        cube[55] = cube_tmp[153];
        cube[56] = cube_tmp[154];
        cube[99] = cube_tmp[197];
        cube[100] = cube_tmp[198];
        cube[101] = cube_tmp[199];
        cube[102] = cube_tmp[200];
        cube[103] = cube_tmp[201];
        cube[104] = cube_tmp[202];
        cube[105] = cube_tmp[203];
        cube[148] = cube_tmp[50];
        cube[149] = cube_tmp[51];
        cube[150] = cube_tmp[52];
        cube[151] = cube_tmp[53];
        cube[152] = cube_tmp[54];
        cube[153] = cube_tmp[55];
        cube[154] = cube_tmp[56];
        cube[197] = cube_tmp[99];
        cube[198] = cube_tmp[100];
        cube[199] = cube_tmp[101];
        cube[200] = cube_tmp[102];
        cube[201] = cube_tmp[103];
        cube[202] = cube_tmp[104];
        cube[203] = cube_tmp[105];
        break;
    }

    case Uw: {
        cube[1] = cube_tmp[43];
        cube[2] = cube_tmp[36];
        cube[3] = cube_tmp[29];
        cube[4] = cube_tmp[22];
        cube[5] = cube_tmp[15];
        cube[6] = cube_tmp[8];
        cube[7] = cube_tmp[1];
        cube[8] = cube_tmp[44];
        cube[9] = cube_tmp[37];
        cube[10] = cube_tmp[30];
        cube[11] = cube_tmp[23];
        cube[12] = cube_tmp[16];
        cube[13] = cube_tmp[9];
        cube[14] = cube_tmp[2];
        cube[15] = cube_tmp[45];
        cube[16] = cube_tmp[38];
        cube[17] = cube_tmp[31];
        cube[18] = cube_tmp[24];
        cube[19] = cube_tmp[17];
        cube[20] = cube_tmp[10];
        cube[21] = cube_tmp[3];
        cube[22] = cube_tmp[46];
        cube[23] = cube_tmp[39];
        cube[24] = cube_tmp[32];
        cube[26] = cube_tmp[18];
        cube[27] = cube_tmp[11];
        cube[28] = cube_tmp[4];
        cube[29] = cube_tmp[47];
        cube[30] = cube_tmp[40];
        cube[31] = cube_tmp[33];
        cube[32] = cube_tmp[26];
        cube[33] = cube_tmp[19];
        cube[34] = cube_tmp[12];
        cube[35] = cube_tmp[5];
        cube[36] = cube_tmp[48];
        cube[37] = cube_tmp[41];
        cube[38] = cube_tmp[34];
        cube[39] = cube_tmp[27];
        cube[40] = cube_tmp[20];
        cube[41] = cube_tmp[13];
        cube[42] = cube_tmp[6];
        cube[43] = cube_tmp[49];
        cube[44] = cube_tmp[42];
        cube[45] = cube_tmp[35];
        cube[46] = cube_tmp[28];
        cube[47] = cube_tmp[21];
        cube[48] = cube_tmp[14];
        cube[49] = cube_tmp[7];
        cube[50] = cube_tmp[99];
        cube[51] = cube_tmp[100];
        cube[52] = cube_tmp[101];
        cube[53] = cube_tmp[102];
        cube[54] = cube_tmp[103];
        cube[55] = cube_tmp[104];
        cube[56] = cube_tmp[105];
        cube[57] = cube_tmp[106];
        cube[58] = cube_tmp[107];
        cube[59] = cube_tmp[108];
        cube[60] = cube_tmp[109];
        cube[61] = cube_tmp[110];
        cube[62] = cube_tmp[111];
        cube[63] = cube_tmp[112];
        cube[99] = cube_tmp[148];
        cube[100] = cube_tmp[149];
        cube[101] = cube_tmp[150];
        cube[102] = cube_tmp[151];
        cube[103] = cube_tmp[152];
        cube[104] = cube_tmp[153];
        cube[105] = cube_tmp[154];
        cube[106] = cube_tmp[155];
        cube[107] = cube_tmp[156];
        cube[108] = cube_tmp[157];
        cube[109] = cube_tmp[158];
        cube[110] = cube_tmp[159];
        cube[111] = cube_tmp[160];
        cube[112] = cube_tmp[161];
        cube[148] = cube_tmp[197];
        cube[149] = cube_tmp[198];
        cube[150] = cube_tmp[199];
        cube[151] = cube_tmp[200];
        cube[152] = cube_tmp[201];
        cube[153] = cube_tmp[202];
        cube[154] = cube_tmp[203];
        cube[155] = cube_tmp[204];
        cube[156] = cube_tmp[205];
        cube[157] = cube_tmp[206];
        cube[158] = cube_tmp[207];
        cube[159] = cube_tmp[208];
        cube[160] = cube_tmp[209];
        cube[161] = cube_tmp[210];
        cube[197] = cube_tmp[50];
        cube[198] = cube_tmp[51];
        cube[199] = cube_tmp[52];
        cube[200] = cube_tmp[53];
        cube[201] = cube_tmp[54];
        cube[202] = cube_tmp[55];
        cube[203] = cube_tmp[56];
        cube[204] = cube_tmp[57];
        cube[205] = cube_tmp[58];
        cube[206] = cube_tmp[59];
        cube[207] = cube_tmp[60];
        cube[208] = cube_tmp[61];
        cube[209] = cube_tmp[62];
        cube[210] = cube_tmp[63];
        break;
    }

    case Uw_PRIME: {
        cube[1] = cube_tmp[7];
        cube[2] = cube_tmp[14];
        cube[3] = cube_tmp[21];
        cube[4] = cube_tmp[28];
        cube[5] = cube_tmp[35];
        cube[6] = cube_tmp[42];
        cube[7] = cube_tmp[49];
        cube[8] = cube_tmp[6];
        cube[9] = cube_tmp[13];
        cube[10] = cube_tmp[20];
        cube[11] = cube_tmp[27];
        cube[12] = cube_tmp[34];
        cube[13] = cube_tmp[41];
        cube[14] = cube_tmp[48];
        cube[15] = cube_tmp[5];
        cube[16] = cube_tmp[12];
        cube[17] = cube_tmp[19];
        cube[18] = cube_tmp[26];
        cube[19] = cube_tmp[33];
        cube[20] = cube_tmp[40];
        cube[21] = cube_tmp[47];
        cube[22] = cube_tmp[4];
        cube[23] = cube_tmp[11];
        cube[24] = cube_tmp[18];
        cube[26] = cube_tmp[32];
        cube[27] = cube_tmp[39];
        cube[28] = cube_tmp[46];
        cube[29] = cube_tmp[3];
        cube[30] = cube_tmp[10];
        cube[31] = cube_tmp[17];
        cube[32] = cube_tmp[24];
        cube[33] = cube_tmp[31];
        cube[34] = cube_tmp[38];
        cube[35] = cube_tmp[45];
        cube[36] = cube_tmp[2];
        cube[37] = cube_tmp[9];
        cube[38] = cube_tmp[16];
        cube[39] = cube_tmp[23];
        cube[40] = cube_tmp[30];
        cube[41] = cube_tmp[37];
        cube[42] = cube_tmp[44];
        cube[43] = cube_tmp[1];
        cube[44] = cube_tmp[8];
        cube[45] = cube_tmp[15];
        cube[46] = cube_tmp[22];
        cube[47] = cube_tmp[29];
        cube[48] = cube_tmp[36];
        cube[49] = cube_tmp[43];
        cube[50] = cube_tmp[197];
        cube[51] = cube_tmp[198];
        cube[52] = cube_tmp[199];
        cube[53] = cube_tmp[200];
        cube[54] = cube_tmp[201];
        cube[55] = cube_tmp[202];
        cube[56] = cube_tmp[203];
        cube[57] = cube_tmp[204];
        cube[58] = cube_tmp[205];
        cube[59] = cube_tmp[206];
        cube[60] = cube_tmp[207];
        cube[61] = cube_tmp[208];
        cube[62] = cube_tmp[209];
        cube[63] = cube_tmp[210];
        cube[99] = cube_tmp[50];
        cube[100] = cube_tmp[51];
        cube[101] = cube_tmp[52];
        cube[102] = cube_tmp[53];
        cube[103] = cube_tmp[54];
        cube[104] = cube_tmp[55];
        cube[105] = cube_tmp[56];
        cube[106] = cube_tmp[57];
        cube[107] = cube_tmp[58];
        cube[108] = cube_tmp[59];
        cube[109] = cube_tmp[60];
        cube[110] = cube_tmp[61];
        cube[111] = cube_tmp[62];
        cube[112] = cube_tmp[63];
        cube[148] = cube_tmp[99];
        cube[149] = cube_tmp[100];
        cube[150] = cube_tmp[101];
        cube[151] = cube_tmp[102];
        cube[152] = cube_tmp[103];
        cube[153] = cube_tmp[104];
        cube[154] = cube_tmp[105];
        cube[155] = cube_tmp[106];
        cube[156] = cube_tmp[107];
        cube[157] = cube_tmp[108];
        cube[158] = cube_tmp[109];
        cube[159] = cube_tmp[110];
        cube[160] = cube_tmp[111];
        cube[161] = cube_tmp[112];
        cube[197] = cube_tmp[148];
        cube[198] = cube_tmp[149];
        cube[199] = cube_tmp[150];
        cube[200] = cube_tmp[151];
        cube[201] = cube_tmp[152];
        cube[202] = cube_tmp[153];
        cube[203] = cube_tmp[154];
        cube[204] = cube_tmp[155];
        cube[205] = cube_tmp[156];
        cube[206] = cube_tmp[157];
        cube[207] = cube_tmp[158];
        cube[208] = cube_tmp[159];
        cube[209] = cube_tmp[160];
        cube[210] = cube_tmp[161];
        break;
    }

    case Uw2: {
        cube[1] = cube_tmp[49];
        cube[2] = cube_tmp[48];
        cube[3] = cube_tmp[47];
        cube[4] = cube_tmp[46];
        cube[5] = cube_tmp[45];
        cube[6] = cube_tmp[44];
        cube[7] = cube_tmp[43];
        cube[8] = cube_tmp[42];
        cube[9] = cube_tmp[41];
        cube[10] = cube_tmp[40];
        cube[11] = cube_tmp[39];
        cube[12] = cube_tmp[38];
        cube[13] = cube_tmp[37];
        cube[14] = cube_tmp[36];
        cube[15] = cube_tmp[35];
        cube[16] = cube_tmp[34];
        cube[17] = cube_tmp[33];
        cube[18] = cube_tmp[32];
        cube[19] = cube_tmp[31];
        cube[20] = cube_tmp[30];
        cube[21] = cube_tmp[29];
        cube[22] = cube_tmp[28];
        cube[23] = cube_tmp[27];
        cube[24] = cube_tmp[26];
        cube[26] = cube_tmp[24];
        cube[27] = cube_tmp[23];
        cube[28] = cube_tmp[22];
        cube[29] = cube_tmp[21];
        cube[30] = cube_tmp[20];
        cube[31] = cube_tmp[19];
        cube[32] = cube_tmp[18];
        cube[33] = cube_tmp[17];
        cube[34] = cube_tmp[16];
        cube[35] = cube_tmp[15];
        cube[36] = cube_tmp[14];
        cube[37] = cube_tmp[13];
        cube[38] = cube_tmp[12];
        cube[39] = cube_tmp[11];
        cube[40] = cube_tmp[10];
        cube[41] = cube_tmp[9];
        cube[42] = cube_tmp[8];
        cube[43] = cube_tmp[7];
        cube[44] = cube_tmp[6];
        cube[45] = cube_tmp[5];
        cube[46] = cube_tmp[4];
        cube[47] = cube_tmp[3];
        cube[48] = cube_tmp[2];
        cube[49] = cube_tmp[1];
        cube[50] = cube_tmp[148];
        cube[51] = cube_tmp[149];
        cube[52] = cube_tmp[150];
        cube[53] = cube_tmp[151];
        cube[54] = cube_tmp[152];
        cube[55] = cube_tmp[153];
        cube[56] = cube_tmp[154];
        cube[57] = cube_tmp[155];
        cube[58] = cube_tmp[156];
        cube[59] = cube_tmp[157];
        cube[60] = cube_tmp[158];
        cube[61] = cube_tmp[159];
        cube[62] = cube_tmp[160];
        cube[63] = cube_tmp[161];
        cube[99] = cube_tmp[197];
        cube[100] = cube_tmp[198];
        cube[101] = cube_tmp[199];
        cube[102] = cube_tmp[200];
        cube[103] = cube_tmp[201];
        cube[104] = cube_tmp[202];
        cube[105] = cube_tmp[203];
        cube[106] = cube_tmp[204];
        cube[107] = cube_tmp[205];
        cube[108] = cube_tmp[206];
        cube[109] = cube_tmp[207];
        cube[110] = cube_tmp[208];
        cube[111] = cube_tmp[209];
        cube[112] = cube_tmp[210];
        cube[148] = cube_tmp[50];
        cube[149] = cube_tmp[51];
        cube[150] = cube_tmp[52];
        cube[151] = cube_tmp[53];
        cube[152] = cube_tmp[54];
        cube[153] = cube_tmp[55];
        cube[154] = cube_tmp[56];
        cube[155] = cube_tmp[57];
        cube[156] = cube_tmp[58];
        cube[157] = cube_tmp[59];
        cube[158] = cube_tmp[60];
        cube[159] = cube_tmp[61];
        cube[160] = cube_tmp[62];
        cube[161] = cube_tmp[63];
        cube[197] = cube_tmp[99];
        cube[198] = cube_tmp[100];
        cube[199] = cube_tmp[101];
        cube[200] = cube_tmp[102];
        cube[201] = cube_tmp[103];
        cube[202] = cube_tmp[104];
        cube[203] = cube_tmp[105];
        cube[204] = cube_tmp[106];
        cube[205] = cube_tmp[107];
        cube[206] = cube_tmp[108];
        cube[207] = cube_tmp[109];
        cube[208] = cube_tmp[110];
        cube[209] = cube_tmp[111];
        cube[210] = cube_tmp[112];
        break;
    }

    case threeUw: {
        cube[1] = cube_tmp[43];
        cube[2] = cube_tmp[36];
        cube[3] = cube_tmp[29];
        cube[4] = cube_tmp[22];
        cube[5] = cube_tmp[15];
        cube[6] = cube_tmp[8];
        cube[7] = cube_tmp[1];
        cube[8] = cube_tmp[44];
        cube[9] = cube_tmp[37];
        cube[10] = cube_tmp[30];
        cube[11] = cube_tmp[23];
        cube[12] = cube_tmp[16];
        cube[13] = cube_tmp[9];
        cube[14] = cube_tmp[2];
        cube[15] = cube_tmp[45];
        cube[16] = cube_tmp[38];
        cube[17] = cube_tmp[31];
        cube[18] = cube_tmp[24];
        cube[19] = cube_tmp[17];
        cube[20] = cube_tmp[10];
        cube[21] = cube_tmp[3];
        cube[22] = cube_tmp[46];
        cube[23] = cube_tmp[39];
        cube[24] = cube_tmp[32];
        cube[26] = cube_tmp[18];
        cube[27] = cube_tmp[11];
        cube[28] = cube_tmp[4];
        cube[29] = cube_tmp[47];
        cube[30] = cube_tmp[40];
        cube[31] = cube_tmp[33];
        cube[32] = cube_tmp[26];
        cube[33] = cube_tmp[19];
        cube[34] = cube_tmp[12];
        cube[35] = cube_tmp[5];
        cube[36] = cube_tmp[48];
        cube[37] = cube_tmp[41];
        cube[38] = cube_tmp[34];
        cube[39] = cube_tmp[27];
        cube[40] = cube_tmp[20];
        cube[41] = cube_tmp[13];
        cube[42] = cube_tmp[6];
        cube[43] = cube_tmp[49];
        cube[44] = cube_tmp[42];
        cube[45] = cube_tmp[35];
        cube[46] = cube_tmp[28];
        cube[47] = cube_tmp[21];
        cube[48] = cube_tmp[14];
        cube[49] = cube_tmp[7];
        cube[50] = cube_tmp[99];
        cube[51] = cube_tmp[100];
        cube[52] = cube_tmp[101];
        cube[53] = cube_tmp[102];
        cube[54] = cube_tmp[103];
        cube[55] = cube_tmp[104];
        cube[56] = cube_tmp[105];
        cube[57] = cube_tmp[106];
        cube[58] = cube_tmp[107];
        cube[59] = cube_tmp[108];
        cube[60] = cube_tmp[109];
        cube[61] = cube_tmp[110];
        cube[62] = cube_tmp[111];
        cube[63] = cube_tmp[112];
        cube[64] = cube_tmp[113];
        cube[65] = cube_tmp[114];
        cube[66] = cube_tmp[115];
        cube[67] = cube_tmp[116];
        cube[68] = cube_tmp[117];
        cube[69] = cube_tmp[118];
        cube[70] = cube_tmp[119];
        cube[99] = cube_tmp[148];
        cube[100] = cube_tmp[149];
        cube[101] = cube_tmp[150];
        cube[102] = cube_tmp[151];
        cube[103] = cube_tmp[152];
        cube[104] = cube_tmp[153];
        cube[105] = cube_tmp[154];
        cube[106] = cube_tmp[155];
        cube[107] = cube_tmp[156];
        cube[108] = cube_tmp[157];
        cube[109] = cube_tmp[158];
        cube[110] = cube_tmp[159];
        cube[111] = cube_tmp[160];
        cube[112] = cube_tmp[161];
        cube[113] = cube_tmp[162];
        cube[114] = cube_tmp[163];
        cube[115] = cube_tmp[164];
        cube[116] = cube_tmp[165];
        cube[117] = cube_tmp[166];
        cube[118] = cube_tmp[167];
        cube[119] = cube_tmp[168];
        cube[148] = cube_tmp[197];
        cube[149] = cube_tmp[198];
        cube[150] = cube_tmp[199];
        cube[151] = cube_tmp[200];
        cube[152] = cube_tmp[201];
        cube[153] = cube_tmp[202];
        cube[154] = cube_tmp[203];
        cube[155] = cube_tmp[204];
        cube[156] = cube_tmp[205];
        cube[157] = cube_tmp[206];
        cube[158] = cube_tmp[207];
        cube[159] = cube_tmp[208];
        cube[160] = cube_tmp[209];
        cube[161] = cube_tmp[210];
        cube[162] = cube_tmp[211];
        cube[163] = cube_tmp[212];
        cube[164] = cube_tmp[213];
        cube[165] = cube_tmp[214];
        cube[166] = cube_tmp[215];
        cube[167] = cube_tmp[216];
        cube[168] = cube_tmp[217];
        cube[197] = cube_tmp[50];
        cube[198] = cube_tmp[51];
        cube[199] = cube_tmp[52];
        cube[200] = cube_tmp[53];
        cube[201] = cube_tmp[54];
        cube[202] = cube_tmp[55];
        cube[203] = cube_tmp[56];
        cube[204] = cube_tmp[57];
        cube[205] = cube_tmp[58];
        cube[206] = cube_tmp[59];
        cube[207] = cube_tmp[60];
        cube[208] = cube_tmp[61];
        cube[209] = cube_tmp[62];
        cube[210] = cube_tmp[63];
        cube[211] = cube_tmp[64];
        cube[212] = cube_tmp[65];
        cube[213] = cube_tmp[66];
        cube[214] = cube_tmp[67];
        cube[215] = cube_tmp[68];
        cube[216] = cube_tmp[69];
        cube[217] = cube_tmp[70];
        break;
    }

    case threeUw_PRIME: {
        cube[1] = cube_tmp[7];
        cube[2] = cube_tmp[14];
        cube[3] = cube_tmp[21];
        cube[4] = cube_tmp[28];
        cube[5] = cube_tmp[35];
        cube[6] = cube_tmp[42];
        cube[7] = cube_tmp[49];
        cube[8] = cube_tmp[6];
        cube[9] = cube_tmp[13];
        cube[10] = cube_tmp[20];
        cube[11] = cube_tmp[27];
        cube[12] = cube_tmp[34];
        cube[13] = cube_tmp[41];
        cube[14] = cube_tmp[48];
        cube[15] = cube_tmp[5];
        cube[16] = cube_tmp[12];
        cube[17] = cube_tmp[19];
        cube[18] = cube_tmp[26];
        cube[19] = cube_tmp[33];
        cube[20] = cube_tmp[40];
        cube[21] = cube_tmp[47];
        cube[22] = cube_tmp[4];
        cube[23] = cube_tmp[11];
        cube[24] = cube_tmp[18];
        cube[26] = cube_tmp[32];
        cube[27] = cube_tmp[39];
        cube[28] = cube_tmp[46];
        cube[29] = cube_tmp[3];
        cube[30] = cube_tmp[10];
        cube[31] = cube_tmp[17];
        cube[32] = cube_tmp[24];
        cube[33] = cube_tmp[31];
        cube[34] = cube_tmp[38];
        cube[35] = cube_tmp[45];
        cube[36] = cube_tmp[2];
        cube[37] = cube_tmp[9];
        cube[38] = cube_tmp[16];
        cube[39] = cube_tmp[23];
        cube[40] = cube_tmp[30];
        cube[41] = cube_tmp[37];
        cube[42] = cube_tmp[44];
        cube[43] = cube_tmp[1];
        cube[44] = cube_tmp[8];
        cube[45] = cube_tmp[15];
        cube[46] = cube_tmp[22];
        cube[47] = cube_tmp[29];
        cube[48] = cube_tmp[36];
        cube[49] = cube_tmp[43];
        cube[50] = cube_tmp[197];
        cube[51] = cube_tmp[198];
        cube[52] = cube_tmp[199];
        cube[53] = cube_tmp[200];
        cube[54] = cube_tmp[201];
        cube[55] = cube_tmp[202];
        cube[56] = cube_tmp[203];
        cube[57] = cube_tmp[204];
        cube[58] = cube_tmp[205];
        cube[59] = cube_tmp[206];
        cube[60] = cube_tmp[207];
        cube[61] = cube_tmp[208];
        cube[62] = cube_tmp[209];
        cube[63] = cube_tmp[210];
        cube[64] = cube_tmp[211];
        cube[65] = cube_tmp[212];
        cube[66] = cube_tmp[213];
        cube[67] = cube_tmp[214];
        cube[68] = cube_tmp[215];
        cube[69] = cube_tmp[216];
        cube[70] = cube_tmp[217];
        cube[99] = cube_tmp[50];
        cube[100] = cube_tmp[51];
        cube[101] = cube_tmp[52];
        cube[102] = cube_tmp[53];
        cube[103] = cube_tmp[54];
        cube[104] = cube_tmp[55];
        cube[105] = cube_tmp[56];
        cube[106] = cube_tmp[57];
        cube[107] = cube_tmp[58];
        cube[108] = cube_tmp[59];
        cube[109] = cube_tmp[60];
        cube[110] = cube_tmp[61];
        cube[111] = cube_tmp[62];
        cube[112] = cube_tmp[63];
        cube[113] = cube_tmp[64];
        cube[114] = cube_tmp[65];
        cube[115] = cube_tmp[66];
        cube[116] = cube_tmp[67];
        cube[117] = cube_tmp[68];
        cube[118] = cube_tmp[69];
        cube[119] = cube_tmp[70];
        cube[148] = cube_tmp[99];
        cube[149] = cube_tmp[100];
        cube[150] = cube_tmp[101];
        cube[151] = cube_tmp[102];
        cube[152] = cube_tmp[103];
        cube[153] = cube_tmp[104];
        cube[154] = cube_tmp[105];
        cube[155] = cube_tmp[106];
        cube[156] = cube_tmp[107];
        cube[157] = cube_tmp[108];
        cube[158] = cube_tmp[109];
        cube[159] = cube_tmp[110];
        cube[160] = cube_tmp[111];
        cube[161] = cube_tmp[112];
        cube[162] = cube_tmp[113];
        cube[163] = cube_tmp[114];
        cube[164] = cube_tmp[115];
        cube[165] = cube_tmp[116];
        cube[166] = cube_tmp[117];
        cube[167] = cube_tmp[118];
        cube[168] = cube_tmp[119];
        cube[197] = cube_tmp[148];
        cube[198] = cube_tmp[149];
        cube[199] = cube_tmp[150];
        cube[200] = cube_tmp[151];
        cube[201] = cube_tmp[152];
        cube[202] = cube_tmp[153];
        cube[203] = cube_tmp[154];
        cube[204] = cube_tmp[155];
        cube[205] = cube_tmp[156];
        cube[206] = cube_tmp[157];
        cube[207] = cube_tmp[158];
        cube[208] = cube_tmp[159];
        cube[209] = cube_tmp[160];
        cube[210] = cube_tmp[161];
        cube[211] = cube_tmp[162];
        cube[212] = cube_tmp[163];
        cube[213] = cube_tmp[164];
        cube[214] = cube_tmp[165];
        cube[215] = cube_tmp[166];
        cube[216] = cube_tmp[167];
        cube[217] = cube_tmp[168];
        break;
    }

    case threeUw2: {
        cube[1] = cube_tmp[49];
        cube[2] = cube_tmp[48];
        cube[3] = cube_tmp[47];
        cube[4] = cube_tmp[46];
        cube[5] = cube_tmp[45];
        cube[6] = cube_tmp[44];
        cube[7] = cube_tmp[43];
        cube[8] = cube_tmp[42];
        cube[9] = cube_tmp[41];
        cube[10] = cube_tmp[40];
        cube[11] = cube_tmp[39];
        cube[12] = cube_tmp[38];
        cube[13] = cube_tmp[37];
        cube[14] = cube_tmp[36];
        cube[15] = cube_tmp[35];
        cube[16] = cube_tmp[34];
        cube[17] = cube_tmp[33];
        cube[18] = cube_tmp[32];
        cube[19] = cube_tmp[31];
        cube[20] = cube_tmp[30];
        cube[21] = cube_tmp[29];
        cube[22] = cube_tmp[28];
        cube[23] = cube_tmp[27];
        cube[24] = cube_tmp[26];
        cube[26] = cube_tmp[24];
        cube[27] = cube_tmp[23];
        cube[28] = cube_tmp[22];
        cube[29] = cube_tmp[21];
        cube[30] = cube_tmp[20];
        cube[31] = cube_tmp[19];
        cube[32] = cube_tmp[18];
        cube[33] = cube_tmp[17];
        cube[34] = cube_tmp[16];
        cube[35] = cube_tmp[15];
        cube[36] = cube_tmp[14];
        cube[37] = cube_tmp[13];
        cube[38] = cube_tmp[12];
        cube[39] = cube_tmp[11];
        cube[40] = cube_tmp[10];
        cube[41] = cube_tmp[9];
        cube[42] = cube_tmp[8];
        cube[43] = cube_tmp[7];
        cube[44] = cube_tmp[6];
        cube[45] = cube_tmp[5];
        cube[46] = cube_tmp[4];
        cube[47] = cube_tmp[3];
        cube[48] = cube_tmp[2];
        cube[49] = cube_tmp[1];
        cube[50] = cube_tmp[148];
        cube[51] = cube_tmp[149];
        cube[52] = cube_tmp[150];
        cube[53] = cube_tmp[151];
        cube[54] = cube_tmp[152];
        cube[55] = cube_tmp[153];
        cube[56] = cube_tmp[154];
        cube[57] = cube_tmp[155];
        cube[58] = cube_tmp[156];
        cube[59] = cube_tmp[157];
        cube[60] = cube_tmp[158];
        cube[61] = cube_tmp[159];
        cube[62] = cube_tmp[160];
        cube[63] = cube_tmp[161];
        cube[64] = cube_tmp[162];
        cube[65] = cube_tmp[163];
        cube[66] = cube_tmp[164];
        cube[67] = cube_tmp[165];
        cube[68] = cube_tmp[166];
        cube[69] = cube_tmp[167];
        cube[70] = cube_tmp[168];
        cube[99] = cube_tmp[197];
        cube[100] = cube_tmp[198];
        cube[101] = cube_tmp[199];
        cube[102] = cube_tmp[200];
        cube[103] = cube_tmp[201];
        cube[104] = cube_tmp[202];
        cube[105] = cube_tmp[203];
        cube[106] = cube_tmp[204];
        cube[107] = cube_tmp[205];
        cube[108] = cube_tmp[206];
        cube[109] = cube_tmp[207];
        cube[110] = cube_tmp[208];
        cube[111] = cube_tmp[209];
        cube[112] = cube_tmp[210];
        cube[113] = cube_tmp[211];
        cube[114] = cube_tmp[212];
        cube[115] = cube_tmp[213];
        cube[116] = cube_tmp[214];
        cube[117] = cube_tmp[215];
        cube[118] = cube_tmp[216];
        cube[119] = cube_tmp[217];
        cube[148] = cube_tmp[50];
        cube[149] = cube_tmp[51];
        cube[150] = cube_tmp[52];
        cube[151] = cube_tmp[53];
        cube[152] = cube_tmp[54];
        cube[153] = cube_tmp[55];
        cube[154] = cube_tmp[56];
        cube[155] = cube_tmp[57];
        cube[156] = cube_tmp[58];
        cube[157] = cube_tmp[59];
        cube[158] = cube_tmp[60];
        cube[159] = cube_tmp[61];
        cube[160] = cube_tmp[62];
        cube[161] = cube_tmp[63];
        cube[162] = cube_tmp[64];
        cube[163] = cube_tmp[65];
        cube[164] = cube_tmp[66];
        cube[165] = cube_tmp[67];
        cube[166] = cube_tmp[68];
        cube[167] = cube_tmp[69];
        cube[168] = cube_tmp[70];
        cube[197] = cube_tmp[99];
        cube[198] = cube_tmp[100];
        cube[199] = cube_tmp[101];
        cube[200] = cube_tmp[102];
        cube[201] = cube_tmp[103];
        cube[202] = cube_tmp[104];
        cube[203] = cube_tmp[105];
        cube[204] = cube_tmp[106];
        cube[205] = cube_tmp[107];
        cube[206] = cube_tmp[108];
        cube[207] = cube_tmp[109];
        cube[208] = cube_tmp[110];
        cube[209] = cube_tmp[111];
        cube[210] = cube_tmp[112];
        cube[211] = cube_tmp[113];
        cube[212] = cube_tmp[114];
        cube[213] = cube_tmp[115];
        cube[214] = cube_tmp[116];
        cube[215] = cube_tmp[117];
        cube[216] = cube_tmp[118];
        cube[217] = cube_tmp[119];
        break;
    }

    case L: {
        cube[1] = cube_tmp[245];
        cube[8] = cube_tmp[238];
        cube[15] = cube_tmp[231];
        cube[22] = cube_tmp[224];
        cube[29] = cube_tmp[217];
        cube[36] = cube_tmp[210];
        cube[43] = cube_tmp[203];
        cube[50] = cube_tmp[92];
        cube[51] = cube_tmp[85];
        cube[52] = cube_tmp[78];
        cube[53] = cube_tmp[71];
        cube[54] = cube_tmp[64];
        cube[55] = cube_tmp[57];
        cube[56] = cube_tmp[50];
        cube[57] = cube_tmp[93];
        cube[58] = cube_tmp[86];
        cube[59] = cube_tmp[79];
        cube[60] = cube_tmp[72];
        cube[61] = cube_tmp[65];
        cube[62] = cube_tmp[58];
        cube[63] = cube_tmp[51];
        cube[64] = cube_tmp[94];
        cube[65] = cube_tmp[87];
        cube[66] = cube_tmp[80];
        cube[67] = cube_tmp[73];
        cube[68] = cube_tmp[66];
        cube[69] = cube_tmp[59];
        cube[70] = cube_tmp[52];
        cube[71] = cube_tmp[95];
        cube[72] = cube_tmp[88];
        cube[73] = cube_tmp[81];
        cube[75] = cube_tmp[67];
        cube[76] = cube_tmp[60];
        cube[77] = cube_tmp[53];
        cube[78] = cube_tmp[96];
        cube[79] = cube_tmp[89];
        cube[80] = cube_tmp[82];
        cube[81] = cube_tmp[75];
        cube[82] = cube_tmp[68];
        cube[83] = cube_tmp[61];
        cube[84] = cube_tmp[54];
        cube[85] = cube_tmp[97];
        cube[86] = cube_tmp[90];
        cube[87] = cube_tmp[83];
        cube[88] = cube_tmp[76];
        cube[89] = cube_tmp[69];
        cube[90] = cube_tmp[62];
        cube[91] = cube_tmp[55];
        cube[92] = cube_tmp[98];
        cube[93] = cube_tmp[91];
        cube[94] = cube_tmp[84];
        cube[95] = cube_tmp[77];
        cube[96] = cube_tmp[70];
        cube[97] = cube_tmp[63];
        cube[98] = cube_tmp[56];
        cube[99] = cube_tmp[1];
        cube[106] = cube_tmp[8];
        cube[113] = cube_tmp[15];
        cube[120] = cube_tmp[22];
        cube[127] = cube_tmp[29];
        cube[134] = cube_tmp[36];
        cube[141] = cube_tmp[43];
        cube[203] = cube_tmp[288];
        cube[210] = cube_tmp[281];
        cube[217] = cube_tmp[274];
        cube[224] = cube_tmp[267];
        cube[231] = cube_tmp[260];
        cube[238] = cube_tmp[253];
        cube[245] = cube_tmp[246];
        cube[246] = cube_tmp[99];
        cube[253] = cube_tmp[106];
        cube[260] = cube_tmp[113];
        cube[267] = cube_tmp[120];
        cube[274] = cube_tmp[127];
        cube[281] = cube_tmp[134];
        cube[288] = cube_tmp[141];
        break;
    }

    case L_PRIME: {
        cube[1] = cube_tmp[99];
        cube[8] = cube_tmp[106];
        cube[15] = cube_tmp[113];
        cube[22] = cube_tmp[120];
        cube[29] = cube_tmp[127];
        cube[36] = cube_tmp[134];
        cube[43] = cube_tmp[141];
        cube[50] = cube_tmp[56];
        cube[51] = cube_tmp[63];
        cube[52] = cube_tmp[70];
        cube[53] = cube_tmp[77];
        cube[54] = cube_tmp[84];
        cube[55] = cube_tmp[91];
        cube[56] = cube_tmp[98];
        cube[57] = cube_tmp[55];
        cube[58] = cube_tmp[62];
        cube[59] = cube_tmp[69];
        cube[60] = cube_tmp[76];
        cube[61] = cube_tmp[83];
        cube[62] = cube_tmp[90];
        cube[63] = cube_tmp[97];
        cube[64] = cube_tmp[54];
        cube[65] = cube_tmp[61];
        cube[66] = cube_tmp[68];
        cube[67] = cube_tmp[75];
        cube[68] = cube_tmp[82];
        cube[69] = cube_tmp[89];
        cube[70] = cube_tmp[96];
        cube[71] = cube_tmp[53];
        cube[72] = cube_tmp[60];
        cube[73] = cube_tmp[67];
        cube[75] = cube_tmp[81];
        cube[76] = cube_tmp[88];
        cube[77] = cube_tmp[95];
        cube[78] = cube_tmp[52];
        cube[79] = cube_tmp[59];
        cube[80] = cube_tmp[66];
        cube[81] = cube_tmp[73];
        cube[82] = cube_tmp[80];
        cube[83] = cube_tmp[87];
        cube[84] = cube_tmp[94];
        cube[85] = cube_tmp[51];
        cube[86] = cube_tmp[58];
        cube[87] = cube_tmp[65];
        cube[88] = cube_tmp[72];
        cube[89] = cube_tmp[79];
        cube[90] = cube_tmp[86];
        cube[91] = cube_tmp[93];
        cube[92] = cube_tmp[50];
        cube[93] = cube_tmp[57];
        cube[94] = cube_tmp[64];
        cube[95] = cube_tmp[71];
        cube[96] = cube_tmp[78];
        cube[97] = cube_tmp[85];
        cube[98] = cube_tmp[92];
        cube[99] = cube_tmp[246];
        cube[106] = cube_tmp[253];
        cube[113] = cube_tmp[260];
        cube[120] = cube_tmp[267];
        cube[127] = cube_tmp[274];
        cube[134] = cube_tmp[281];
        cube[141] = cube_tmp[288];
        cube[203] = cube_tmp[43];
        cube[210] = cube_tmp[36];
        cube[217] = cube_tmp[29];
        cube[224] = cube_tmp[22];
        cube[231] = cube_tmp[15];
        cube[238] = cube_tmp[8];
        cube[245] = cube_tmp[1];
        cube[246] = cube_tmp[245];
        cube[253] = cube_tmp[238];
        cube[260] = cube_tmp[231];
        cube[267] = cube_tmp[224];
        cube[274] = cube_tmp[217];
        cube[281] = cube_tmp[210];
        cube[288] = cube_tmp[203];
        break;
    }

    case L2: {
        cube[1] = cube_tmp[246];
        cube[8] = cube_tmp[253];
        cube[15] = cube_tmp[260];
        cube[22] = cube_tmp[267];
        cube[29] = cube_tmp[274];
        cube[36] = cube_tmp[281];
        cube[43] = cube_tmp[288];
        cube[50] = cube_tmp[98];
        cube[51] = cube_tmp[97];
        cube[52] = cube_tmp[96];
        cube[53] = cube_tmp[95];
        cube[54] = cube_tmp[94];
        cube[55] = cube_tmp[93];
        cube[56] = cube_tmp[92];
        cube[57] = cube_tmp[91];
        cube[58] = cube_tmp[90];
        cube[59] = cube_tmp[89];
        cube[60] = cube_tmp[88];
        cube[61] = cube_tmp[87];
        cube[62] = cube_tmp[86];
        cube[63] = cube_tmp[85];
        cube[64] = cube_tmp[84];
        cube[65] = cube_tmp[83];
        cube[66] = cube_tmp[82];
        cube[67] = cube_tmp[81];
        cube[68] = cube_tmp[80];
        cube[69] = cube_tmp[79];
        cube[70] = cube_tmp[78];
        cube[71] = cube_tmp[77];
        cube[72] = cube_tmp[76];
        cube[73] = cube_tmp[75];
        cube[75] = cube_tmp[73];
        cube[76] = cube_tmp[72];
        cube[77] = cube_tmp[71];
        cube[78] = cube_tmp[70];
        cube[79] = cube_tmp[69];
        cube[80] = cube_tmp[68];
        cube[81] = cube_tmp[67];
        cube[82] = cube_tmp[66];
        cube[83] = cube_tmp[65];
        cube[84] = cube_tmp[64];
        cube[85] = cube_tmp[63];
        cube[86] = cube_tmp[62];
        cube[87] = cube_tmp[61];
        cube[88] = cube_tmp[60];
        cube[89] = cube_tmp[59];
        cube[90] = cube_tmp[58];
        cube[91] = cube_tmp[57];
        cube[92] = cube_tmp[56];
        cube[93] = cube_tmp[55];
        cube[94] = cube_tmp[54];
        cube[95] = cube_tmp[53];
        cube[96] = cube_tmp[52];
        cube[97] = cube_tmp[51];
        cube[98] = cube_tmp[50];
        cube[99] = cube_tmp[245];
        cube[106] = cube_tmp[238];
        cube[113] = cube_tmp[231];
        cube[120] = cube_tmp[224];
        cube[127] = cube_tmp[217];
        cube[134] = cube_tmp[210];
        cube[141] = cube_tmp[203];
        cube[203] = cube_tmp[141];
        cube[210] = cube_tmp[134];
        cube[217] = cube_tmp[127];
        cube[224] = cube_tmp[120];
        cube[231] = cube_tmp[113];
        cube[238] = cube_tmp[106];
        cube[245] = cube_tmp[99];
        cube[246] = cube_tmp[1];
        cube[253] = cube_tmp[8];
        cube[260] = cube_tmp[15];
        cube[267] = cube_tmp[22];
        cube[274] = cube_tmp[29];
        cube[281] = cube_tmp[36];
        cube[288] = cube_tmp[43];
        break;
    }

    case Lw: {
        cube[1] = cube_tmp[245];
        cube[2] = cube_tmp[244];
        cube[8] = cube_tmp[238];
        cube[9] = cube_tmp[237];
        cube[15] = cube_tmp[231];
        cube[16] = cube_tmp[230];
        cube[22] = cube_tmp[224];
        cube[23] = cube_tmp[223];
        cube[29] = cube_tmp[217];
        cube[30] = cube_tmp[216];
        cube[36] = cube_tmp[210];
        cube[37] = cube_tmp[209];
        cube[43] = cube_tmp[203];
        cube[44] = cube_tmp[202];
        cube[50] = cube_tmp[92];
        cube[51] = cube_tmp[85];
        cube[52] = cube_tmp[78];
        cube[53] = cube_tmp[71];
        cube[54] = cube_tmp[64];
        cube[55] = cube_tmp[57];
        cube[56] = cube_tmp[50];
        cube[57] = cube_tmp[93];
        cube[58] = cube_tmp[86];
        cube[59] = cube_tmp[79];
        cube[60] = cube_tmp[72];
        cube[61] = cube_tmp[65];
        cube[62] = cube_tmp[58];
        cube[63] = cube_tmp[51];
        cube[64] = cube_tmp[94];
        cube[65] = cube_tmp[87];
        cube[66] = cube_tmp[80];
        cube[67] = cube_tmp[73];
        cube[68] = cube_tmp[66];
        cube[69] = cube_tmp[59];
        cube[70] = cube_tmp[52];
        cube[71] = cube_tmp[95];
        cube[72] = cube_tmp[88];
        cube[73] = cube_tmp[81];
        cube[75] = cube_tmp[67];
        cube[76] = cube_tmp[60];
        cube[77] = cube_tmp[53];
        cube[78] = cube_tmp[96];
        cube[79] = cube_tmp[89];
        cube[80] = cube_tmp[82];
        cube[81] = cube_tmp[75];
        cube[82] = cube_tmp[68];
        cube[83] = cube_tmp[61];
        cube[84] = cube_tmp[54];
        cube[85] = cube_tmp[97];
        cube[86] = cube_tmp[90];
        cube[87] = cube_tmp[83];
        cube[88] = cube_tmp[76];
        cube[89] = cube_tmp[69];
        cube[90] = cube_tmp[62];
        cube[91] = cube_tmp[55];
        cube[92] = cube_tmp[98];
        cube[93] = cube_tmp[91];
        cube[94] = cube_tmp[84];
        cube[95] = cube_tmp[77];
        cube[96] = cube_tmp[70];
        cube[97] = cube_tmp[63];
        cube[98] = cube_tmp[56];
        cube[99] = cube_tmp[1];
        cube[100] = cube_tmp[2];
        cube[106] = cube_tmp[8];
        cube[107] = cube_tmp[9];
        cube[113] = cube_tmp[15];
        cube[114] = cube_tmp[16];
        cube[120] = cube_tmp[22];
        cube[121] = cube_tmp[23];
        cube[127] = cube_tmp[29];
        cube[128] = cube_tmp[30];
        cube[134] = cube_tmp[36];
        cube[135] = cube_tmp[37];
        cube[141] = cube_tmp[43];
        cube[142] = cube_tmp[44];
        cube[202] = cube_tmp[289];
        cube[203] = cube_tmp[288];
        cube[209] = cube_tmp[282];
        cube[210] = cube_tmp[281];
        cube[216] = cube_tmp[275];
        cube[217] = cube_tmp[274];
        cube[223] = cube_tmp[268];
        cube[224] = cube_tmp[267];
        cube[230] = cube_tmp[261];
        cube[231] = cube_tmp[260];
        cube[237] = cube_tmp[254];
        cube[238] = cube_tmp[253];
        cube[244] = cube_tmp[247];
        cube[245] = cube_tmp[246];
        cube[246] = cube_tmp[99];
        cube[247] = cube_tmp[100];
        cube[253] = cube_tmp[106];
        cube[254] = cube_tmp[107];
        cube[260] = cube_tmp[113];
        cube[261] = cube_tmp[114];
        cube[267] = cube_tmp[120];
        cube[268] = cube_tmp[121];
        cube[274] = cube_tmp[127];
        cube[275] = cube_tmp[128];
        cube[281] = cube_tmp[134];
        cube[282] = cube_tmp[135];
        cube[288] = cube_tmp[141];
        cube[289] = cube_tmp[142];
        break;
    }

    case Lw_PRIME: {
        cube[1] = cube_tmp[99];
        cube[2] = cube_tmp[100];
        cube[8] = cube_tmp[106];
        cube[9] = cube_tmp[107];
        cube[15] = cube_tmp[113];
        cube[16] = cube_tmp[114];
        cube[22] = cube_tmp[120];
        cube[23] = cube_tmp[121];
        cube[29] = cube_tmp[127];
        cube[30] = cube_tmp[128];
        cube[36] = cube_tmp[134];
        cube[37] = cube_tmp[135];
        cube[43] = cube_tmp[141];
        cube[44] = cube_tmp[142];
        cube[50] = cube_tmp[56];
        cube[51] = cube_tmp[63];
        cube[52] = cube_tmp[70];
        cube[53] = cube_tmp[77];
        cube[54] = cube_tmp[84];
        cube[55] = cube_tmp[91];
        cube[56] = cube_tmp[98];
        cube[57] = cube_tmp[55];
        cube[58] = cube_tmp[62];
        cube[59] = cube_tmp[69];
        cube[60] = cube_tmp[76];
        cube[61] = cube_tmp[83];
        cube[62] = cube_tmp[90];
        cube[63] = cube_tmp[97];
        cube[64] = cube_tmp[54];
        cube[65] = cube_tmp[61];
        cube[66] = cube_tmp[68];
        cube[67] = cube_tmp[75];
        cube[68] = cube_tmp[82];
        cube[69] = cube_tmp[89];
        cube[70] = cube_tmp[96];
        cube[71] = cube_tmp[53];
        cube[72] = cube_tmp[60];
        cube[73] = cube_tmp[67];
        cube[75] = cube_tmp[81];
        cube[76] = cube_tmp[88];
        cube[77] = cube_tmp[95];
        cube[78] = cube_tmp[52];
        cube[79] = cube_tmp[59];
        cube[80] = cube_tmp[66];
        cube[81] = cube_tmp[73];
        cube[82] = cube_tmp[80];
        cube[83] = cube_tmp[87];
        cube[84] = cube_tmp[94];
        cube[85] = cube_tmp[51];
        cube[86] = cube_tmp[58];
        cube[87] = cube_tmp[65];
        cube[88] = cube_tmp[72];
        cube[89] = cube_tmp[79];
        cube[90] = cube_tmp[86];
        cube[91] = cube_tmp[93];
        cube[92] = cube_tmp[50];
        cube[93] = cube_tmp[57];
        cube[94] = cube_tmp[64];
        cube[95] = cube_tmp[71];
        cube[96] = cube_tmp[78];
        cube[97] = cube_tmp[85];
        cube[98] = cube_tmp[92];
        cube[99] = cube_tmp[246];
        cube[100] = cube_tmp[247];
        cube[106] = cube_tmp[253];
        cube[107] = cube_tmp[254];
        cube[113] = cube_tmp[260];
        cube[114] = cube_tmp[261];
        cube[120] = cube_tmp[267];
        cube[121] = cube_tmp[268];
        cube[127] = cube_tmp[274];
        cube[128] = cube_tmp[275];
        cube[134] = cube_tmp[281];
        cube[135] = cube_tmp[282];
        cube[141] = cube_tmp[288];
        cube[142] = cube_tmp[289];
        cube[202] = cube_tmp[44];
        cube[203] = cube_tmp[43];
        cube[209] = cube_tmp[37];
        cube[210] = cube_tmp[36];
        cube[216] = cube_tmp[30];
        cube[217] = cube_tmp[29];
        cube[223] = cube_tmp[23];
        cube[224] = cube_tmp[22];
        cube[230] = cube_tmp[16];
        cube[231] = cube_tmp[15];
        cube[237] = cube_tmp[9];
        cube[238] = cube_tmp[8];
        cube[244] = cube_tmp[2];
        cube[245] = cube_tmp[1];
        cube[246] = cube_tmp[245];
        cube[247] = cube_tmp[244];
        cube[253] = cube_tmp[238];
        cube[254] = cube_tmp[237];
        cube[260] = cube_tmp[231];
        cube[261] = cube_tmp[230];
        cube[267] = cube_tmp[224];
        cube[268] = cube_tmp[223];
        cube[274] = cube_tmp[217];
        cube[275] = cube_tmp[216];
        cube[281] = cube_tmp[210];
        cube[282] = cube_tmp[209];
        cube[288] = cube_tmp[203];
        cube[289] = cube_tmp[202];
        break;
    }

    case Lw2: {
        cube[1] = cube_tmp[246];
        cube[2] = cube_tmp[247];
        cube[8] = cube_tmp[253];
        cube[9] = cube_tmp[254];
        cube[15] = cube_tmp[260];
        cube[16] = cube_tmp[261];
        cube[22] = cube_tmp[267];
        cube[23] = cube_tmp[268];
        cube[29] = cube_tmp[274];
        cube[30] = cube_tmp[275];
        cube[36] = cube_tmp[281];
        cube[37] = cube_tmp[282];
        cube[43] = cube_tmp[288];
        cube[44] = cube_tmp[289];
        cube[50] = cube_tmp[98];
        cube[51] = cube_tmp[97];
        cube[52] = cube_tmp[96];
        cube[53] = cube_tmp[95];
        cube[54] = cube_tmp[94];
        cube[55] = cube_tmp[93];
        cube[56] = cube_tmp[92];
        cube[57] = cube_tmp[91];
        cube[58] = cube_tmp[90];
        cube[59] = cube_tmp[89];
        cube[60] = cube_tmp[88];
        cube[61] = cube_tmp[87];
        cube[62] = cube_tmp[86];
        cube[63] = cube_tmp[85];
        cube[64] = cube_tmp[84];
        cube[65] = cube_tmp[83];
        cube[66] = cube_tmp[82];
        cube[67] = cube_tmp[81];
        cube[68] = cube_tmp[80];
        cube[69] = cube_tmp[79];
        cube[70] = cube_tmp[78];
        cube[71] = cube_tmp[77];
        cube[72] = cube_tmp[76];
        cube[73] = cube_tmp[75];
        cube[75] = cube_tmp[73];
        cube[76] = cube_tmp[72];
        cube[77] = cube_tmp[71];
        cube[78] = cube_tmp[70];
        cube[79] = cube_tmp[69];
        cube[80] = cube_tmp[68];
        cube[81] = cube_tmp[67];
        cube[82] = cube_tmp[66];
        cube[83] = cube_tmp[65];
        cube[84] = cube_tmp[64];
        cube[85] = cube_tmp[63];
        cube[86] = cube_tmp[62];
        cube[87] = cube_tmp[61];
        cube[88] = cube_tmp[60];
        cube[89] = cube_tmp[59];
        cube[90] = cube_tmp[58];
        cube[91] = cube_tmp[57];
        cube[92] = cube_tmp[56];
        cube[93] = cube_tmp[55];
        cube[94] = cube_tmp[54];
        cube[95] = cube_tmp[53];
        cube[96] = cube_tmp[52];
        cube[97] = cube_tmp[51];
        cube[98] = cube_tmp[50];
        cube[99] = cube_tmp[245];
        cube[100] = cube_tmp[244];
        cube[106] = cube_tmp[238];
        cube[107] = cube_tmp[237];
        cube[113] = cube_tmp[231];
        cube[114] = cube_tmp[230];
        cube[120] = cube_tmp[224];
        cube[121] = cube_tmp[223];
        cube[127] = cube_tmp[217];
        cube[128] = cube_tmp[216];
        cube[134] = cube_tmp[210];
        cube[135] = cube_tmp[209];
        cube[141] = cube_tmp[203];
        cube[142] = cube_tmp[202];
        cube[202] = cube_tmp[142];
        cube[203] = cube_tmp[141];
        cube[209] = cube_tmp[135];
        cube[210] = cube_tmp[134];
        cube[216] = cube_tmp[128];
        cube[217] = cube_tmp[127];
        cube[223] = cube_tmp[121];
        cube[224] = cube_tmp[120];
        cube[230] = cube_tmp[114];
        cube[231] = cube_tmp[113];
        cube[237] = cube_tmp[107];
        cube[238] = cube_tmp[106];
        cube[244] = cube_tmp[100];
        cube[245] = cube_tmp[99];
        cube[246] = cube_tmp[1];
        cube[247] = cube_tmp[2];
        cube[253] = cube_tmp[8];
        cube[254] = cube_tmp[9];
        cube[260] = cube_tmp[15];
        cube[261] = cube_tmp[16];
        cube[267] = cube_tmp[22];
        cube[268] = cube_tmp[23];
        cube[274] = cube_tmp[29];
        cube[275] = cube_tmp[30];
        cube[281] = cube_tmp[36];
        cube[282] = cube_tmp[37];
        cube[288] = cube_tmp[43];
        cube[289] = cube_tmp[44];
        break;
    }

    case threeLw: {
        cube[1] = cube_tmp[245];
        cube[2] = cube_tmp[244];
        cube[3] = cube_tmp[243];
        cube[8] = cube_tmp[238];
        cube[9] = cube_tmp[237];
        cube[10] = cube_tmp[236];
        cube[15] = cube_tmp[231];
        cube[16] = cube_tmp[230];
        cube[17] = cube_tmp[229];
        cube[22] = cube_tmp[224];
        cube[23] = cube_tmp[223];
        cube[24] = cube_tmp[222];
        cube[29] = cube_tmp[217];
        cube[30] = cube_tmp[216];
        cube[31] = cube_tmp[215];
        cube[36] = cube_tmp[210];
        cube[37] = cube_tmp[209];
        cube[38] = cube_tmp[208];
        cube[43] = cube_tmp[203];
        cube[44] = cube_tmp[202];
        cube[45] = cube_tmp[201];
        cube[50] = cube_tmp[92];
        cube[51] = cube_tmp[85];
        cube[52] = cube_tmp[78];
        cube[53] = cube_tmp[71];
        cube[54] = cube_tmp[64];
        cube[55] = cube_tmp[57];
        cube[56] = cube_tmp[50];
        cube[57] = cube_tmp[93];
        cube[58] = cube_tmp[86];
        cube[59] = cube_tmp[79];
        cube[60] = cube_tmp[72];
        cube[61] = cube_tmp[65];
        cube[62] = cube_tmp[58];
        cube[63] = cube_tmp[51];
        cube[64] = cube_tmp[94];
        cube[65] = cube_tmp[87];
        cube[66] = cube_tmp[80];
        cube[67] = cube_tmp[73];
        cube[68] = cube_tmp[66];
        cube[69] = cube_tmp[59];
        cube[70] = cube_tmp[52];
        cube[71] = cube_tmp[95];
        cube[72] = cube_tmp[88];
        cube[73] = cube_tmp[81];
        cube[75] = cube_tmp[67];
        cube[76] = cube_tmp[60];
        cube[77] = cube_tmp[53];
        cube[78] = cube_tmp[96];
        cube[79] = cube_tmp[89];
        cube[80] = cube_tmp[82];
        cube[81] = cube_tmp[75];
        cube[82] = cube_tmp[68];
        cube[83] = cube_tmp[61];
        cube[84] = cube_tmp[54];
        cube[85] = cube_tmp[97];
        cube[86] = cube_tmp[90];
        cube[87] = cube_tmp[83];
        cube[88] = cube_tmp[76];
        cube[89] = cube_tmp[69];
        cube[90] = cube_tmp[62];
        cube[91] = cube_tmp[55];
        cube[92] = cube_tmp[98];
        cube[93] = cube_tmp[91];
        cube[94] = cube_tmp[84];
        cube[95] = cube_tmp[77];
        cube[96] = cube_tmp[70];
        cube[97] = cube_tmp[63];
        cube[98] = cube_tmp[56];
        cube[99] = cube_tmp[1];
        cube[100] = cube_tmp[2];
        cube[101] = cube_tmp[3];
        cube[106] = cube_tmp[8];
        cube[107] = cube_tmp[9];
        cube[108] = cube_tmp[10];
        cube[113] = cube_tmp[15];
        cube[114] = cube_tmp[16];
        cube[115] = cube_tmp[17];
        cube[120] = cube_tmp[22];
        cube[121] = cube_tmp[23];
        cube[122] = cube_tmp[24];
        cube[127] = cube_tmp[29];
        cube[128] = cube_tmp[30];
        cube[129] = cube_tmp[31];
        cube[134] = cube_tmp[36];
        cube[135] = cube_tmp[37];
        cube[136] = cube_tmp[38];
        cube[141] = cube_tmp[43];
        cube[142] = cube_tmp[44];
        cube[143] = cube_tmp[45];
        cube[201] = cube_tmp[290];
        cube[202] = cube_tmp[289];
        cube[203] = cube_tmp[288];
        cube[208] = cube_tmp[283];
        cube[209] = cube_tmp[282];
        cube[210] = cube_tmp[281];
        cube[215] = cube_tmp[276];
        cube[216] = cube_tmp[275];
        cube[217] = cube_tmp[274];
        cube[222] = cube_tmp[269];
        cube[223] = cube_tmp[268];
        cube[224] = cube_tmp[267];
        cube[229] = cube_tmp[262];
        cube[230] = cube_tmp[261];
        cube[231] = cube_tmp[260];
        cube[236] = cube_tmp[255];
        cube[237] = cube_tmp[254];
        cube[238] = cube_tmp[253];
        cube[243] = cube_tmp[248];
        cube[244] = cube_tmp[247];
        cube[245] = cube_tmp[246];
        cube[246] = cube_tmp[99];
        cube[247] = cube_tmp[100];
        cube[248] = cube_tmp[101];
        cube[253] = cube_tmp[106];
        cube[254] = cube_tmp[107];
        cube[255] = cube_tmp[108];
        cube[260] = cube_tmp[113];
        cube[261] = cube_tmp[114];
        cube[262] = cube_tmp[115];
        cube[267] = cube_tmp[120];
        cube[268] = cube_tmp[121];
        cube[269] = cube_tmp[122];
        cube[274] = cube_tmp[127];
        cube[275] = cube_tmp[128];
        cube[276] = cube_tmp[129];
        cube[281] = cube_tmp[134];
        cube[282] = cube_tmp[135];
        cube[283] = cube_tmp[136];
        cube[288] = cube_tmp[141];
        cube[289] = cube_tmp[142];
        cube[290] = cube_tmp[143];
        break;
    }

    case threeLw_PRIME: {
        cube[1] = cube_tmp[99];
        cube[2] = cube_tmp[100];
        cube[3] = cube_tmp[101];
        cube[8] = cube_tmp[106];
        cube[9] = cube_tmp[107];
        cube[10] = cube_tmp[108];
        cube[15] = cube_tmp[113];
        cube[16] = cube_tmp[114];
        cube[17] = cube_tmp[115];
        cube[22] = cube_tmp[120];
        cube[23] = cube_tmp[121];
        cube[24] = cube_tmp[122];
        cube[29] = cube_tmp[127];
        cube[30] = cube_tmp[128];
        cube[31] = cube_tmp[129];
        cube[36] = cube_tmp[134];
        cube[37] = cube_tmp[135];
        cube[38] = cube_tmp[136];
        cube[43] = cube_tmp[141];
        cube[44] = cube_tmp[142];
        cube[45] = cube_tmp[143];
        cube[50] = cube_tmp[56];
        cube[51] = cube_tmp[63];
        cube[52] = cube_tmp[70];
        cube[53] = cube_tmp[77];
        cube[54] = cube_tmp[84];
        cube[55] = cube_tmp[91];
        cube[56] = cube_tmp[98];
        cube[57] = cube_tmp[55];
        cube[58] = cube_tmp[62];
        cube[59] = cube_tmp[69];
        cube[60] = cube_tmp[76];
        cube[61] = cube_tmp[83];
        cube[62] = cube_tmp[90];
        cube[63] = cube_tmp[97];
        cube[64] = cube_tmp[54];
        cube[65] = cube_tmp[61];
        cube[66] = cube_tmp[68];
        cube[67] = cube_tmp[75];
        cube[68] = cube_tmp[82];
        cube[69] = cube_tmp[89];
        cube[70] = cube_tmp[96];
        cube[71] = cube_tmp[53];
        cube[72] = cube_tmp[60];
        cube[73] = cube_tmp[67];
        cube[75] = cube_tmp[81];
        cube[76] = cube_tmp[88];
        cube[77] = cube_tmp[95];
        cube[78] = cube_tmp[52];
        cube[79] = cube_tmp[59];
        cube[80] = cube_tmp[66];
        cube[81] = cube_tmp[73];
        cube[82] = cube_tmp[80];
        cube[83] = cube_tmp[87];
        cube[84] = cube_tmp[94];
        cube[85] = cube_tmp[51];
        cube[86] = cube_tmp[58];
        cube[87] = cube_tmp[65];
        cube[88] = cube_tmp[72];
        cube[89] = cube_tmp[79];
        cube[90] = cube_tmp[86];
        cube[91] = cube_tmp[93];
        cube[92] = cube_tmp[50];
        cube[93] = cube_tmp[57];
        cube[94] = cube_tmp[64];
        cube[95] = cube_tmp[71];
        cube[96] = cube_tmp[78];
        cube[97] = cube_tmp[85];
        cube[98] = cube_tmp[92];
        cube[99] = cube_tmp[246];
        cube[100] = cube_tmp[247];
        cube[101] = cube_tmp[248];
        cube[106] = cube_tmp[253];
        cube[107] = cube_tmp[254];
        cube[108] = cube_tmp[255];
        cube[113] = cube_tmp[260];
        cube[114] = cube_tmp[261];
        cube[115] = cube_tmp[262];
        cube[120] = cube_tmp[267];
        cube[121] = cube_tmp[268];
        cube[122] = cube_tmp[269];
        cube[127] = cube_tmp[274];
        cube[128] = cube_tmp[275];
        cube[129] = cube_tmp[276];
        cube[134] = cube_tmp[281];
        cube[135] = cube_tmp[282];
        cube[136] = cube_tmp[283];
        cube[141] = cube_tmp[288];
        cube[142] = cube_tmp[289];
        cube[143] = cube_tmp[290];
        cube[201] = cube_tmp[45];
        cube[202] = cube_tmp[44];
        cube[203] = cube_tmp[43];
        cube[208] = cube_tmp[38];
        cube[209] = cube_tmp[37];
        cube[210] = cube_tmp[36];
        cube[215] = cube_tmp[31];
        cube[216] = cube_tmp[30];
        cube[217] = cube_tmp[29];
        cube[222] = cube_tmp[24];
        cube[223] = cube_tmp[23];
        cube[224] = cube_tmp[22];
        cube[229] = cube_tmp[17];
        cube[230] = cube_tmp[16];
        cube[231] = cube_tmp[15];
        cube[236] = cube_tmp[10];
        cube[237] = cube_tmp[9];
        cube[238] = cube_tmp[8];
        cube[243] = cube_tmp[3];
        cube[244] = cube_tmp[2];
        cube[245] = cube_tmp[1];
        cube[246] = cube_tmp[245];
        cube[247] = cube_tmp[244];
        cube[248] = cube_tmp[243];
        cube[253] = cube_tmp[238];
        cube[254] = cube_tmp[237];
        cube[255] = cube_tmp[236];
        cube[260] = cube_tmp[231];
        cube[261] = cube_tmp[230];
        cube[262] = cube_tmp[229];
        cube[267] = cube_tmp[224];
        cube[268] = cube_tmp[223];
        cube[269] = cube_tmp[222];
        cube[274] = cube_tmp[217];
        cube[275] = cube_tmp[216];
        cube[276] = cube_tmp[215];
        cube[281] = cube_tmp[210];
        cube[282] = cube_tmp[209];
        cube[283] = cube_tmp[208];
        cube[288] = cube_tmp[203];
        cube[289] = cube_tmp[202];
        cube[290] = cube_tmp[201];
        break;
    }

    case threeLw2: {
        cube[1] = cube_tmp[246];
        cube[2] = cube_tmp[247];
        cube[3] = cube_tmp[248];
        cube[8] = cube_tmp[253];
        cube[9] = cube_tmp[254];
        cube[10] = cube_tmp[255];
        cube[15] = cube_tmp[260];
        cube[16] = cube_tmp[261];
        cube[17] = cube_tmp[262];
        cube[22] = cube_tmp[267];
        cube[23] = cube_tmp[268];
        cube[24] = cube_tmp[269];
        cube[29] = cube_tmp[274];
        cube[30] = cube_tmp[275];
        cube[31] = cube_tmp[276];
        cube[36] = cube_tmp[281];
        cube[37] = cube_tmp[282];
        cube[38] = cube_tmp[283];
        cube[43] = cube_tmp[288];
        cube[44] = cube_tmp[289];
        cube[45] = cube_tmp[290];
        cube[50] = cube_tmp[98];
        cube[51] = cube_tmp[97];
        cube[52] = cube_tmp[96];
        cube[53] = cube_tmp[95];
        cube[54] = cube_tmp[94];
        cube[55] = cube_tmp[93];
        cube[56] = cube_tmp[92];
        cube[57] = cube_tmp[91];
        cube[58] = cube_tmp[90];
        cube[59] = cube_tmp[89];
        cube[60] = cube_tmp[88];
        cube[61] = cube_tmp[87];
        cube[62] = cube_tmp[86];
        cube[63] = cube_tmp[85];
        cube[64] = cube_tmp[84];
        cube[65] = cube_tmp[83];
        cube[66] = cube_tmp[82];
        cube[67] = cube_tmp[81];
        cube[68] = cube_tmp[80];
        cube[69] = cube_tmp[79];
        cube[70] = cube_tmp[78];
        cube[71] = cube_tmp[77];
        cube[72] = cube_tmp[76];
        cube[73] = cube_tmp[75];
        cube[75] = cube_tmp[73];
        cube[76] = cube_tmp[72];
        cube[77] = cube_tmp[71];
        cube[78] = cube_tmp[70];
        cube[79] = cube_tmp[69];
        cube[80] = cube_tmp[68];
        cube[81] = cube_tmp[67];
        cube[82] = cube_tmp[66];
        cube[83] = cube_tmp[65];
        cube[84] = cube_tmp[64];
        cube[85] = cube_tmp[63];
        cube[86] = cube_tmp[62];
        cube[87] = cube_tmp[61];
        cube[88] = cube_tmp[60];
        cube[89] = cube_tmp[59];
        cube[90] = cube_tmp[58];
        cube[91] = cube_tmp[57];
        cube[92] = cube_tmp[56];
        cube[93] = cube_tmp[55];
        cube[94] = cube_tmp[54];
        cube[95] = cube_tmp[53];
        cube[96] = cube_tmp[52];
        cube[97] = cube_tmp[51];
        cube[98] = cube_tmp[50];
        cube[99] = cube_tmp[245];
        cube[100] = cube_tmp[244];
        cube[101] = cube_tmp[243];
        cube[106] = cube_tmp[238];
        cube[107] = cube_tmp[237];
        cube[108] = cube_tmp[236];
        cube[113] = cube_tmp[231];
        cube[114] = cube_tmp[230];
        cube[115] = cube_tmp[229];
        cube[120] = cube_tmp[224];
        cube[121] = cube_tmp[223];
        cube[122] = cube_tmp[222];
        cube[127] = cube_tmp[217];
        cube[128] = cube_tmp[216];
        cube[129] = cube_tmp[215];
        cube[134] = cube_tmp[210];
        cube[135] = cube_tmp[209];
        cube[136] = cube_tmp[208];
        cube[141] = cube_tmp[203];
        cube[142] = cube_tmp[202];
        cube[143] = cube_tmp[201];
        cube[201] = cube_tmp[143];
        cube[202] = cube_tmp[142];
        cube[203] = cube_tmp[141];
        cube[208] = cube_tmp[136];
        cube[209] = cube_tmp[135];
        cube[210] = cube_tmp[134];
        cube[215] = cube_tmp[129];
        cube[216] = cube_tmp[128];
        cube[217] = cube_tmp[127];
        cube[222] = cube_tmp[122];
        cube[223] = cube_tmp[121];
        cube[224] = cube_tmp[120];
        cube[229] = cube_tmp[115];
        cube[230] = cube_tmp[114];
        cube[231] = cube_tmp[113];
        cube[236] = cube_tmp[108];
        cube[237] = cube_tmp[107];
        cube[238] = cube_tmp[106];
        cube[243] = cube_tmp[101];
        cube[244] = cube_tmp[100];
        cube[245] = cube_tmp[99];
        cube[246] = cube_tmp[1];
        cube[247] = cube_tmp[2];
        cube[248] = cube_tmp[3];
        cube[253] = cube_tmp[8];
        cube[254] = cube_tmp[9];
        cube[255] = cube_tmp[10];
        cube[260] = cube_tmp[15];
        cube[261] = cube_tmp[16];
        cube[262] = cube_tmp[17];
        cube[267] = cube_tmp[22];
        cube[268] = cube_tmp[23];
        cube[269] = cube_tmp[24];
        cube[274] = cube_tmp[29];
        cube[275] = cube_tmp[30];
        cube[276] = cube_tmp[31];
        cube[281] = cube_tmp[36];
        cube[282] = cube_tmp[37];
        cube[283] = cube_tmp[38];
        cube[288] = cube_tmp[43];
        cube[289] = cube_tmp[44];
        cube[290] = cube_tmp[45];
        break;
    }

    case F: {
        cube[43] = cube_tmp[98];
        cube[44] = cube_tmp[91];
        cube[45] = cube_tmp[84];
        cube[46] = cube_tmp[77];
        cube[47] = cube_tmp[70];
        cube[48] = cube_tmp[63];
        cube[49] = cube_tmp[56];
        cube[56] = cube_tmp[246];
        cube[63] = cube_tmp[247];
        cube[70] = cube_tmp[248];
        cube[77] = cube_tmp[249];
        cube[84] = cube_tmp[250];
        cube[91] = cube_tmp[251];
        cube[98] = cube_tmp[252];
        cube[99] = cube_tmp[141];
        cube[100] = cube_tmp[134];
        cube[101] = cube_tmp[127];
        cube[102] = cube_tmp[120];
        cube[103] = cube_tmp[113];
        cube[104] = cube_tmp[106];
        cube[105] = cube_tmp[99];
        cube[106] = cube_tmp[142];
        cube[107] = cube_tmp[135];
        cube[108] = cube_tmp[128];
        cube[109] = cube_tmp[121];
        cube[110] = cube_tmp[114];
        cube[111] = cube_tmp[107];
        cube[112] = cube_tmp[100];
        cube[113] = cube_tmp[143];
        cube[114] = cube_tmp[136];
        cube[115] = cube_tmp[129];
        cube[116] = cube_tmp[122];
        cube[117] = cube_tmp[115];
        cube[118] = cube_tmp[108];
        cube[119] = cube_tmp[101];
        cube[120] = cube_tmp[144];
        cube[121] = cube_tmp[137];
        cube[122] = cube_tmp[130];
        cube[124] = cube_tmp[116];
        cube[125] = cube_tmp[109];
        cube[126] = cube_tmp[102];
        cube[127] = cube_tmp[145];
        cube[128] = cube_tmp[138];
        cube[129] = cube_tmp[131];
        cube[130] = cube_tmp[124];
        cube[131] = cube_tmp[117];
        cube[132] = cube_tmp[110];
        cube[133] = cube_tmp[103];
        cube[134] = cube_tmp[146];
        cube[135] = cube_tmp[139];
        cube[136] = cube_tmp[132];
        cube[137] = cube_tmp[125];
        cube[138] = cube_tmp[118];
        cube[139] = cube_tmp[111];
        cube[140] = cube_tmp[104];
        cube[141] = cube_tmp[147];
        cube[142] = cube_tmp[140];
        cube[143] = cube_tmp[133];
        cube[144] = cube_tmp[126];
        cube[145] = cube_tmp[119];
        cube[146] = cube_tmp[112];
        cube[147] = cube_tmp[105];
        cube[148] = cube_tmp[43];
        cube[155] = cube_tmp[44];
        cube[162] = cube_tmp[45];
        cube[169] = cube_tmp[46];
        cube[176] = cube_tmp[47];
        cube[183] = cube_tmp[48];
        cube[190] = cube_tmp[49];
        cube[246] = cube_tmp[190];
        cube[247] = cube_tmp[183];
        cube[248] = cube_tmp[176];
        cube[249] = cube_tmp[169];
        cube[250] = cube_tmp[162];
        cube[251] = cube_tmp[155];
        cube[252] = cube_tmp[148];
        break;
    }

    case F_PRIME: {
        cube[43] = cube_tmp[148];
        cube[44] = cube_tmp[155];
        cube[45] = cube_tmp[162];
        cube[46] = cube_tmp[169];
        cube[47] = cube_tmp[176];
        cube[48] = cube_tmp[183];
        cube[49] = cube_tmp[190];
        cube[56] = cube_tmp[49];
        cube[63] = cube_tmp[48];
        cube[70] = cube_tmp[47];
        cube[77] = cube_tmp[46];
        cube[84] = cube_tmp[45];
        cube[91] = cube_tmp[44];
        cube[98] = cube_tmp[43];
        cube[99] = cube_tmp[105];
        cube[100] = cube_tmp[112];
        cube[101] = cube_tmp[119];
        cube[102] = cube_tmp[126];
        cube[103] = cube_tmp[133];
        cube[104] = cube_tmp[140];
        cube[105] = cube_tmp[147];
        cube[106] = cube_tmp[104];
        cube[107] = cube_tmp[111];
        cube[108] = cube_tmp[118];
        cube[109] = cube_tmp[125];
        cube[110] = cube_tmp[132];
        cube[111] = cube_tmp[139];
        cube[112] = cube_tmp[146];
        cube[113] = cube_tmp[103];
        cube[114] = cube_tmp[110];
        cube[115] = cube_tmp[117];
        cube[116] = cube_tmp[124];
        cube[117] = cube_tmp[131];
        cube[118] = cube_tmp[138];
        cube[119] = cube_tmp[145];
        cube[120] = cube_tmp[102];
        cube[121] = cube_tmp[109];
        cube[122] = cube_tmp[116];
        cube[124] = cube_tmp[130];
        cube[125] = cube_tmp[137];
        cube[126] = cube_tmp[144];
        cube[127] = cube_tmp[101];
        cube[128] = cube_tmp[108];
        cube[129] = cube_tmp[115];
        cube[130] = cube_tmp[122];
        cube[131] = cube_tmp[129];
        cube[132] = cube_tmp[136];
        cube[133] = cube_tmp[143];
        cube[134] = cube_tmp[100];
        cube[135] = cube_tmp[107];
        cube[136] = cube_tmp[114];
        cube[137] = cube_tmp[121];
        cube[138] = cube_tmp[128];
        cube[139] = cube_tmp[135];
        cube[140] = cube_tmp[142];
        cube[141] = cube_tmp[99];
        cube[142] = cube_tmp[106];
        cube[143] = cube_tmp[113];
        cube[144] = cube_tmp[120];
        cube[145] = cube_tmp[127];
        cube[146] = cube_tmp[134];
        cube[147] = cube_tmp[141];
        cube[148] = cube_tmp[252];
        cube[155] = cube_tmp[251];
        cube[162] = cube_tmp[250];
        cube[169] = cube_tmp[249];
        cube[176] = cube_tmp[248];
        cube[183] = cube_tmp[247];
        cube[190] = cube_tmp[246];
        cube[246] = cube_tmp[56];
        cube[247] = cube_tmp[63];
        cube[248] = cube_tmp[70];
        cube[249] = cube_tmp[77];
        cube[250] = cube_tmp[84];
        cube[251] = cube_tmp[91];
        cube[252] = cube_tmp[98];
        break;
    }

    case F2: {
        cube[43] = cube_tmp[252];
        cube[44] = cube_tmp[251];
        cube[45] = cube_tmp[250];
        cube[46] = cube_tmp[249];
        cube[47] = cube_tmp[248];
        cube[48] = cube_tmp[247];
        cube[49] = cube_tmp[246];
        cube[56] = cube_tmp[190];
        cube[63] = cube_tmp[183];
        cube[70] = cube_tmp[176];
        cube[77] = cube_tmp[169];
        cube[84] = cube_tmp[162];
        cube[91] = cube_tmp[155];
        cube[98] = cube_tmp[148];
        cube[99] = cube_tmp[147];
        cube[100] = cube_tmp[146];
        cube[101] = cube_tmp[145];
        cube[102] = cube_tmp[144];
        cube[103] = cube_tmp[143];
        cube[104] = cube_tmp[142];
        cube[105] = cube_tmp[141];
        cube[106] = cube_tmp[140];
        cube[107] = cube_tmp[139];
        cube[108] = cube_tmp[138];
        cube[109] = cube_tmp[137];
        cube[110] = cube_tmp[136];
        cube[111] = cube_tmp[135];
        cube[112] = cube_tmp[134];
        cube[113] = cube_tmp[133];
        cube[114] = cube_tmp[132];
        cube[115] = cube_tmp[131];
        cube[116] = cube_tmp[130];
        cube[117] = cube_tmp[129];
        cube[118] = cube_tmp[128];
        cube[119] = cube_tmp[127];
        cube[120] = cube_tmp[126];
        cube[121] = cube_tmp[125];
        cube[122] = cube_tmp[124];
        cube[124] = cube_tmp[122];
        cube[125] = cube_tmp[121];
        cube[126] = cube_tmp[120];
        cube[127] = cube_tmp[119];
        cube[128] = cube_tmp[118];
        cube[129] = cube_tmp[117];
        cube[130] = cube_tmp[116];
        cube[131] = cube_tmp[115];
        cube[132] = cube_tmp[114];
        cube[133] = cube_tmp[113];
        cube[134] = cube_tmp[112];
        cube[135] = cube_tmp[111];
        cube[136] = cube_tmp[110];
        cube[137] = cube_tmp[109];
        cube[138] = cube_tmp[108];
        cube[139] = cube_tmp[107];
        cube[140] = cube_tmp[106];
        cube[141] = cube_tmp[105];
        cube[142] = cube_tmp[104];
        cube[143] = cube_tmp[103];
        cube[144] = cube_tmp[102];
        cube[145] = cube_tmp[101];
        cube[146] = cube_tmp[100];
        cube[147] = cube_tmp[99];
        cube[148] = cube_tmp[98];
        cube[155] = cube_tmp[91];
        cube[162] = cube_tmp[84];
        cube[169] = cube_tmp[77];
        cube[176] = cube_tmp[70];
        cube[183] = cube_tmp[63];
        cube[190] = cube_tmp[56];
        cube[246] = cube_tmp[49];
        cube[247] = cube_tmp[48];
        cube[248] = cube_tmp[47];
        cube[249] = cube_tmp[46];
        cube[250] = cube_tmp[45];
        cube[251] = cube_tmp[44];
        cube[252] = cube_tmp[43];
        break;
    }

    case Fw: {
        cube[36] = cube_tmp[97];
        cube[37] = cube_tmp[90];
        cube[38] = cube_tmp[83];
        cube[39] = cube_tmp[76];
        cube[40] = cube_tmp[69];
        cube[41] = cube_tmp[62];
        cube[42] = cube_tmp[55];
        cube[43] = cube_tmp[98];
        cube[44] = cube_tmp[91];
        cube[45] = cube_tmp[84];
        cube[46] = cube_tmp[77];
        cube[47] = cube_tmp[70];
        cube[48] = cube_tmp[63];
        cube[49] = cube_tmp[56];
        cube[55] = cube_tmp[253];
        cube[56] = cube_tmp[246];
        cube[62] = cube_tmp[254];
        cube[63] = cube_tmp[247];
        cube[69] = cube_tmp[255];
        cube[70] = cube_tmp[248];
        cube[76] = cube_tmp[256];
        cube[77] = cube_tmp[249];
        cube[83] = cube_tmp[257];
        cube[84] = cube_tmp[250];
        cube[90] = cube_tmp[258];
        cube[91] = cube_tmp[251];
        cube[97] = cube_tmp[259];
        cube[98] = cube_tmp[252];
        cube[99] = cube_tmp[141];
        cube[100] = cube_tmp[134];
        cube[101] = cube_tmp[127];
        cube[102] = cube_tmp[120];
        cube[103] = cube_tmp[113];
        cube[104] = cube_tmp[106];
        cube[105] = cube_tmp[99];
        cube[106] = cube_tmp[142];
        cube[107] = cube_tmp[135];
        cube[108] = cube_tmp[128];
        cube[109] = cube_tmp[121];
        cube[110] = cube_tmp[114];
        cube[111] = cube_tmp[107];
        cube[112] = cube_tmp[100];
        cube[113] = cube_tmp[143];
        cube[114] = cube_tmp[136];
        cube[115] = cube_tmp[129];
        cube[116] = cube_tmp[122];
        cube[117] = cube_tmp[115];
        cube[118] = cube_tmp[108];
        cube[119] = cube_tmp[101];
        cube[120] = cube_tmp[144];
        cube[121] = cube_tmp[137];
        cube[122] = cube_tmp[130];
        cube[124] = cube_tmp[116];
        cube[125] = cube_tmp[109];
        cube[126] = cube_tmp[102];
        cube[127] = cube_tmp[145];
        cube[128] = cube_tmp[138];
        cube[129] = cube_tmp[131];
        cube[130] = cube_tmp[124];
        cube[131] = cube_tmp[117];
        cube[132] = cube_tmp[110];
        cube[133] = cube_tmp[103];
        cube[134] = cube_tmp[146];
        cube[135] = cube_tmp[139];
        cube[136] = cube_tmp[132];
        cube[137] = cube_tmp[125];
        cube[138] = cube_tmp[118];
        cube[139] = cube_tmp[111];
        cube[140] = cube_tmp[104];
        cube[141] = cube_tmp[147];
        cube[142] = cube_tmp[140];
        cube[143] = cube_tmp[133];
        cube[144] = cube_tmp[126];
        cube[145] = cube_tmp[119];
        cube[146] = cube_tmp[112];
        cube[147] = cube_tmp[105];
        cube[148] = cube_tmp[43];
        cube[149] = cube_tmp[36];
        cube[155] = cube_tmp[44];
        cube[156] = cube_tmp[37];
        cube[162] = cube_tmp[45];
        cube[163] = cube_tmp[38];
        cube[169] = cube_tmp[46];
        cube[170] = cube_tmp[39];
        cube[176] = cube_tmp[47];
        cube[177] = cube_tmp[40];
        cube[183] = cube_tmp[48];
        cube[184] = cube_tmp[41];
        cube[190] = cube_tmp[49];
        cube[191] = cube_tmp[42];
        cube[246] = cube_tmp[190];
        cube[247] = cube_tmp[183];
        cube[248] = cube_tmp[176];
        cube[249] = cube_tmp[169];
        cube[250] = cube_tmp[162];
        cube[251] = cube_tmp[155];
        cube[252] = cube_tmp[148];
        cube[253] = cube_tmp[191];
        cube[254] = cube_tmp[184];
        cube[255] = cube_tmp[177];
        cube[256] = cube_tmp[170];
        cube[257] = cube_tmp[163];
        cube[258] = cube_tmp[156];
        cube[259] = cube_tmp[149];
        break;
    }

    case Fw_PRIME: {
        cube[36] = cube_tmp[149];
        cube[37] = cube_tmp[156];
        cube[38] = cube_tmp[163];
        cube[39] = cube_tmp[170];
        cube[40] = cube_tmp[177];
        cube[41] = cube_tmp[184];
        cube[42] = cube_tmp[191];
        cube[43] = cube_tmp[148];
        cube[44] = cube_tmp[155];
        cube[45] = cube_tmp[162];
        cube[46] = cube_tmp[169];
        cube[47] = cube_tmp[176];
        cube[48] = cube_tmp[183];
        cube[49] = cube_tmp[190];
        cube[55] = cube_tmp[42];
        cube[56] = cube_tmp[49];
        cube[62] = cube_tmp[41];
        cube[63] = cube_tmp[48];
        cube[69] = cube_tmp[40];
        cube[70] = cube_tmp[47];
        cube[76] = cube_tmp[39];
        cube[77] = cube_tmp[46];
        cube[83] = cube_tmp[38];
        cube[84] = cube_tmp[45];
        cube[90] = cube_tmp[37];
        cube[91] = cube_tmp[44];
        cube[97] = cube_tmp[36];
        cube[98] = cube_tmp[43];
        cube[99] = cube_tmp[105];
        cube[100] = cube_tmp[112];
        cube[101] = cube_tmp[119];
        cube[102] = cube_tmp[126];
        cube[103] = cube_tmp[133];
        cube[104] = cube_tmp[140];
        cube[105] = cube_tmp[147];
        cube[106] = cube_tmp[104];
        cube[107] = cube_tmp[111];
        cube[108] = cube_tmp[118];
        cube[109] = cube_tmp[125];
        cube[110] = cube_tmp[132];
        cube[111] = cube_tmp[139];
        cube[112] = cube_tmp[146];
        cube[113] = cube_tmp[103];
        cube[114] = cube_tmp[110];
        cube[115] = cube_tmp[117];
        cube[116] = cube_tmp[124];
        cube[117] = cube_tmp[131];
        cube[118] = cube_tmp[138];
        cube[119] = cube_tmp[145];
        cube[120] = cube_tmp[102];
        cube[121] = cube_tmp[109];
        cube[122] = cube_tmp[116];
        cube[124] = cube_tmp[130];
        cube[125] = cube_tmp[137];
        cube[126] = cube_tmp[144];
        cube[127] = cube_tmp[101];
        cube[128] = cube_tmp[108];
        cube[129] = cube_tmp[115];
        cube[130] = cube_tmp[122];
        cube[131] = cube_tmp[129];
        cube[132] = cube_tmp[136];
        cube[133] = cube_tmp[143];
        cube[134] = cube_tmp[100];
        cube[135] = cube_tmp[107];
        cube[136] = cube_tmp[114];
        cube[137] = cube_tmp[121];
        cube[138] = cube_tmp[128];
        cube[139] = cube_tmp[135];
        cube[140] = cube_tmp[142];
        cube[141] = cube_tmp[99];
        cube[142] = cube_tmp[106];
        cube[143] = cube_tmp[113];
        cube[144] = cube_tmp[120];
        cube[145] = cube_tmp[127];
        cube[146] = cube_tmp[134];
        cube[147] = cube_tmp[141];
        cube[148] = cube_tmp[252];
        cube[149] = cube_tmp[259];
        cube[155] = cube_tmp[251];
        cube[156] = cube_tmp[258];
        cube[162] = cube_tmp[250];
        cube[163] = cube_tmp[257];
        cube[169] = cube_tmp[249];
        cube[170] = cube_tmp[256];
        cube[176] = cube_tmp[248];
        cube[177] = cube_tmp[255];
        cube[183] = cube_tmp[247];
        cube[184] = cube_tmp[254];
        cube[190] = cube_tmp[246];
        cube[191] = cube_tmp[253];
        cube[246] = cube_tmp[56];
        cube[247] = cube_tmp[63];
        cube[248] = cube_tmp[70];
        cube[249] = cube_tmp[77];
        cube[250] = cube_tmp[84];
        cube[251] = cube_tmp[91];
        cube[252] = cube_tmp[98];
        cube[253] = cube_tmp[55];
        cube[254] = cube_tmp[62];
        cube[255] = cube_tmp[69];
        cube[256] = cube_tmp[76];
        cube[257] = cube_tmp[83];
        cube[258] = cube_tmp[90];
        cube[259] = cube_tmp[97];
        break;
    }

    case Fw2: {
        cube[36] = cube_tmp[259];
        cube[37] = cube_tmp[258];
        cube[38] = cube_tmp[257];
        cube[39] = cube_tmp[256];
        cube[40] = cube_tmp[255];
        cube[41] = cube_tmp[254];
        cube[42] = cube_tmp[253];
        cube[43] = cube_tmp[252];
        cube[44] = cube_tmp[251];
        cube[45] = cube_tmp[250];
        cube[46] = cube_tmp[249];
        cube[47] = cube_tmp[248];
        cube[48] = cube_tmp[247];
        cube[49] = cube_tmp[246];
        cube[55] = cube_tmp[191];
        cube[56] = cube_tmp[190];
        cube[62] = cube_tmp[184];
        cube[63] = cube_tmp[183];
        cube[69] = cube_tmp[177];
        cube[70] = cube_tmp[176];
        cube[76] = cube_tmp[170];
        cube[77] = cube_tmp[169];
        cube[83] = cube_tmp[163];
        cube[84] = cube_tmp[162];
        cube[90] = cube_tmp[156];
        cube[91] = cube_tmp[155];
        cube[97] = cube_tmp[149];
        cube[98] = cube_tmp[148];
        cube[99] = cube_tmp[147];
        cube[100] = cube_tmp[146];
        cube[101] = cube_tmp[145];
        cube[102] = cube_tmp[144];
        cube[103] = cube_tmp[143];
        cube[104] = cube_tmp[142];
        cube[105] = cube_tmp[141];
        cube[106] = cube_tmp[140];
        cube[107] = cube_tmp[139];
        cube[108] = cube_tmp[138];
        cube[109] = cube_tmp[137];
        cube[110] = cube_tmp[136];
        cube[111] = cube_tmp[135];
        cube[112] = cube_tmp[134];
        cube[113] = cube_tmp[133];
        cube[114] = cube_tmp[132];
        cube[115] = cube_tmp[131];
        cube[116] = cube_tmp[130];
        cube[117] = cube_tmp[129];
        cube[118] = cube_tmp[128];
        cube[119] = cube_tmp[127];
        cube[120] = cube_tmp[126];
        cube[121] = cube_tmp[125];
        cube[122] = cube_tmp[124];
        cube[124] = cube_tmp[122];
        cube[125] = cube_tmp[121];
        cube[126] = cube_tmp[120];
        cube[127] = cube_tmp[119];
        cube[128] = cube_tmp[118];
        cube[129] = cube_tmp[117];
        cube[130] = cube_tmp[116];
        cube[131] = cube_tmp[115];
        cube[132] = cube_tmp[114];
        cube[133] = cube_tmp[113];
        cube[134] = cube_tmp[112];
        cube[135] = cube_tmp[111];
        cube[136] = cube_tmp[110];
        cube[137] = cube_tmp[109];
        cube[138] = cube_tmp[108];
        cube[139] = cube_tmp[107];
        cube[140] = cube_tmp[106];
        cube[141] = cube_tmp[105];
        cube[142] = cube_tmp[104];
        cube[143] = cube_tmp[103];
        cube[144] = cube_tmp[102];
        cube[145] = cube_tmp[101];
        cube[146] = cube_tmp[100];
        cube[147] = cube_tmp[99];
        cube[148] = cube_tmp[98];
        cube[149] = cube_tmp[97];
        cube[155] = cube_tmp[91];
        cube[156] = cube_tmp[90];
        cube[162] = cube_tmp[84];
        cube[163] = cube_tmp[83];
        cube[169] = cube_tmp[77];
        cube[170] = cube_tmp[76];
        cube[176] = cube_tmp[70];
        cube[177] = cube_tmp[69];
        cube[183] = cube_tmp[63];
        cube[184] = cube_tmp[62];
        cube[190] = cube_tmp[56];
        cube[191] = cube_tmp[55];
        cube[246] = cube_tmp[49];
        cube[247] = cube_tmp[48];
        cube[248] = cube_tmp[47];
        cube[249] = cube_tmp[46];
        cube[250] = cube_tmp[45];
        cube[251] = cube_tmp[44];
        cube[252] = cube_tmp[43];
        cube[253] = cube_tmp[42];
        cube[254] = cube_tmp[41];
        cube[255] = cube_tmp[40];
        cube[256] = cube_tmp[39];
        cube[257] = cube_tmp[38];
        cube[258] = cube_tmp[37];
        cube[259] = cube_tmp[36];
        break;
    }

    case threeFw: {
        cube[29] = cube_tmp[96];
        cube[30] = cube_tmp[89];
        cube[31] = cube_tmp[82];
        cube[32] = cube_tmp[75];
        cube[33] = cube_tmp[68];
        cube[34] = cube_tmp[61];
        cube[35] = cube_tmp[54];
        cube[36] = cube_tmp[97];
        cube[37] = cube_tmp[90];
        cube[38] = cube_tmp[83];
        cube[39] = cube_tmp[76];
        cube[40] = cube_tmp[69];
        cube[41] = cube_tmp[62];
        cube[42] = cube_tmp[55];
        cube[43] = cube_tmp[98];
        cube[44] = cube_tmp[91];
        cube[45] = cube_tmp[84];
        cube[46] = cube_tmp[77];
        cube[47] = cube_tmp[70];
        cube[48] = cube_tmp[63];
        cube[49] = cube_tmp[56];
        cube[54] = cube_tmp[260];
        cube[55] = cube_tmp[253];
        cube[56] = cube_tmp[246];
        cube[61] = cube_tmp[261];
        cube[62] = cube_tmp[254];
        cube[63] = cube_tmp[247];
        cube[68] = cube_tmp[262];
        cube[69] = cube_tmp[255];
        cube[70] = cube_tmp[248];
        cube[75] = cube_tmp[263];
        cube[76] = cube_tmp[256];
        cube[77] = cube_tmp[249];
        cube[82] = cube_tmp[264];
        cube[83] = cube_tmp[257];
        cube[84] = cube_tmp[250];
        cube[89] = cube_tmp[265];
        cube[90] = cube_tmp[258];
        cube[91] = cube_tmp[251];
        cube[96] = cube_tmp[266];
        cube[97] = cube_tmp[259];
        cube[98] = cube_tmp[252];
        cube[99] = cube_tmp[141];
        cube[100] = cube_tmp[134];
        cube[101] = cube_tmp[127];
        cube[102] = cube_tmp[120];
        cube[103] = cube_tmp[113];
        cube[104] = cube_tmp[106];
        cube[105] = cube_tmp[99];
        cube[106] = cube_tmp[142];
        cube[107] = cube_tmp[135];
        cube[108] = cube_tmp[128];
        cube[109] = cube_tmp[121];
        cube[110] = cube_tmp[114];
        cube[111] = cube_tmp[107];
        cube[112] = cube_tmp[100];
        cube[113] = cube_tmp[143];
        cube[114] = cube_tmp[136];
        cube[115] = cube_tmp[129];
        cube[116] = cube_tmp[122];
        cube[117] = cube_tmp[115];
        cube[118] = cube_tmp[108];
        cube[119] = cube_tmp[101];
        cube[120] = cube_tmp[144];
        cube[121] = cube_tmp[137];
        cube[122] = cube_tmp[130];
        cube[124] = cube_tmp[116];
        cube[125] = cube_tmp[109];
        cube[126] = cube_tmp[102];
        cube[127] = cube_tmp[145];
        cube[128] = cube_tmp[138];
        cube[129] = cube_tmp[131];
        cube[130] = cube_tmp[124];
        cube[131] = cube_tmp[117];
        cube[132] = cube_tmp[110];
        cube[133] = cube_tmp[103];
        cube[134] = cube_tmp[146];
        cube[135] = cube_tmp[139];
        cube[136] = cube_tmp[132];
        cube[137] = cube_tmp[125];
        cube[138] = cube_tmp[118];
        cube[139] = cube_tmp[111];
        cube[140] = cube_tmp[104];
        cube[141] = cube_tmp[147];
        cube[142] = cube_tmp[140];
        cube[143] = cube_tmp[133];
        cube[144] = cube_tmp[126];
        cube[145] = cube_tmp[119];
        cube[146] = cube_tmp[112];
        cube[147] = cube_tmp[105];
        cube[148] = cube_tmp[43];
        cube[149] = cube_tmp[36];
        cube[150] = cube_tmp[29];
        cube[155] = cube_tmp[44];
        cube[156] = cube_tmp[37];
        cube[157] = cube_tmp[30];
        cube[162] = cube_tmp[45];
        cube[163] = cube_tmp[38];
        cube[164] = cube_tmp[31];
        cube[169] = cube_tmp[46];
        cube[170] = cube_tmp[39];
        cube[171] = cube_tmp[32];
        cube[176] = cube_tmp[47];
        cube[177] = cube_tmp[40];
        cube[178] = cube_tmp[33];
        cube[183] = cube_tmp[48];
        cube[184] = cube_tmp[41];
        cube[185] = cube_tmp[34];
        cube[190] = cube_tmp[49];
        cube[191] = cube_tmp[42];
        cube[192] = cube_tmp[35];
        cube[246] = cube_tmp[190];
        cube[247] = cube_tmp[183];
        cube[248] = cube_tmp[176];
        cube[249] = cube_tmp[169];
        cube[250] = cube_tmp[162];
        cube[251] = cube_tmp[155];
        cube[252] = cube_tmp[148];
        cube[253] = cube_tmp[191];
        cube[254] = cube_tmp[184];
        cube[255] = cube_tmp[177];
        cube[256] = cube_tmp[170];
        cube[257] = cube_tmp[163];
        cube[258] = cube_tmp[156];
        cube[259] = cube_tmp[149];
        cube[260] = cube_tmp[192];
        cube[261] = cube_tmp[185];
        cube[262] = cube_tmp[178];
        cube[263] = cube_tmp[171];
        cube[264] = cube_tmp[164];
        cube[265] = cube_tmp[157];
        cube[266] = cube_tmp[150];
        break;
    }

    case threeFw_PRIME: {
        cube[29] = cube_tmp[150];
        cube[30] = cube_tmp[157];
        cube[31] = cube_tmp[164];
        cube[32] = cube_tmp[171];
        cube[33] = cube_tmp[178];
        cube[34] = cube_tmp[185];
        cube[35] = cube_tmp[192];
        cube[36] = cube_tmp[149];
        cube[37] = cube_tmp[156];
        cube[38] = cube_tmp[163];
        cube[39] = cube_tmp[170];
        cube[40] = cube_tmp[177];
        cube[41] = cube_tmp[184];
        cube[42] = cube_tmp[191];
        cube[43] = cube_tmp[148];
        cube[44] = cube_tmp[155];
        cube[45] = cube_tmp[162];
        cube[46] = cube_tmp[169];
        cube[47] = cube_tmp[176];
        cube[48] = cube_tmp[183];
        cube[49] = cube_tmp[190];
        cube[54] = cube_tmp[35];
        cube[55] = cube_tmp[42];
        cube[56] = cube_tmp[49];
        cube[61] = cube_tmp[34];
        cube[62] = cube_tmp[41];
        cube[63] = cube_tmp[48];
        cube[68] = cube_tmp[33];
        cube[69] = cube_tmp[40];
        cube[70] = cube_tmp[47];
        cube[75] = cube_tmp[32];
        cube[76] = cube_tmp[39];
        cube[77] = cube_tmp[46];
        cube[82] = cube_tmp[31];
        cube[83] = cube_tmp[38];
        cube[84] = cube_tmp[45];
        cube[89] = cube_tmp[30];
        cube[90] = cube_tmp[37];
        cube[91] = cube_tmp[44];
        cube[96] = cube_tmp[29];
        cube[97] = cube_tmp[36];
        cube[98] = cube_tmp[43];
        cube[99] = cube_tmp[105];
        cube[100] = cube_tmp[112];
        cube[101] = cube_tmp[119];
        cube[102] = cube_tmp[126];
        cube[103] = cube_tmp[133];
        cube[104] = cube_tmp[140];
        cube[105] = cube_tmp[147];
        cube[106] = cube_tmp[104];
        cube[107] = cube_tmp[111];
        cube[108] = cube_tmp[118];
        cube[109] = cube_tmp[125];
        cube[110] = cube_tmp[132];
        cube[111] = cube_tmp[139];
        cube[112] = cube_tmp[146];
        cube[113] = cube_tmp[103];
        cube[114] = cube_tmp[110];
        cube[115] = cube_tmp[117];
        cube[116] = cube_tmp[124];
        cube[117] = cube_tmp[131];
        cube[118] = cube_tmp[138];
        cube[119] = cube_tmp[145];
        cube[120] = cube_tmp[102];
        cube[121] = cube_tmp[109];
        cube[122] = cube_tmp[116];
        cube[124] = cube_tmp[130];
        cube[125] = cube_tmp[137];
        cube[126] = cube_tmp[144];
        cube[127] = cube_tmp[101];
        cube[128] = cube_tmp[108];
        cube[129] = cube_tmp[115];
        cube[130] = cube_tmp[122];
        cube[131] = cube_tmp[129];
        cube[132] = cube_tmp[136];
        cube[133] = cube_tmp[143];
        cube[134] = cube_tmp[100];
        cube[135] = cube_tmp[107];
        cube[136] = cube_tmp[114];
        cube[137] = cube_tmp[121];
        cube[138] = cube_tmp[128];
        cube[139] = cube_tmp[135];
        cube[140] = cube_tmp[142];
        cube[141] = cube_tmp[99];
        cube[142] = cube_tmp[106];
        cube[143] = cube_tmp[113];
        cube[144] = cube_tmp[120];
        cube[145] = cube_tmp[127];
        cube[146] = cube_tmp[134];
        cube[147] = cube_tmp[141];
        cube[148] = cube_tmp[252];
        cube[149] = cube_tmp[259];
        cube[150] = cube_tmp[266];
        cube[155] = cube_tmp[251];
        cube[156] = cube_tmp[258];
        cube[157] = cube_tmp[265];
        cube[162] = cube_tmp[250];
        cube[163] = cube_tmp[257];
        cube[164] = cube_tmp[264];
        cube[169] = cube_tmp[249];
        cube[170] = cube_tmp[256];
        cube[171] = cube_tmp[263];
        cube[176] = cube_tmp[248];
        cube[177] = cube_tmp[255];
        cube[178] = cube_tmp[262];
        cube[183] = cube_tmp[247];
        cube[184] = cube_tmp[254];
        cube[185] = cube_tmp[261];
        cube[190] = cube_tmp[246];
        cube[191] = cube_tmp[253];
        cube[192] = cube_tmp[260];
        cube[246] = cube_tmp[56];
        cube[247] = cube_tmp[63];
        cube[248] = cube_tmp[70];
        cube[249] = cube_tmp[77];
        cube[250] = cube_tmp[84];
        cube[251] = cube_tmp[91];
        cube[252] = cube_tmp[98];
        cube[253] = cube_tmp[55];
        cube[254] = cube_tmp[62];
        cube[255] = cube_tmp[69];
        cube[256] = cube_tmp[76];
        cube[257] = cube_tmp[83];
        cube[258] = cube_tmp[90];
        cube[259] = cube_tmp[97];
        cube[260] = cube_tmp[54];
        cube[261] = cube_tmp[61];
        cube[262] = cube_tmp[68];
        cube[263] = cube_tmp[75];
        cube[264] = cube_tmp[82];
        cube[265] = cube_tmp[89];
        cube[266] = cube_tmp[96];
        break;
    }

    case threeFw2: {
        cube[29] = cube_tmp[266];
        cube[30] = cube_tmp[265];
        cube[31] = cube_tmp[264];
        cube[32] = cube_tmp[263];
        cube[33] = cube_tmp[262];
        cube[34] = cube_tmp[261];
        cube[35] = cube_tmp[260];
        cube[36] = cube_tmp[259];
        cube[37] = cube_tmp[258];
        cube[38] = cube_tmp[257];
        cube[39] = cube_tmp[256];
        cube[40] = cube_tmp[255];
        cube[41] = cube_tmp[254];
        cube[42] = cube_tmp[253];
        cube[43] = cube_tmp[252];
        cube[44] = cube_tmp[251];
        cube[45] = cube_tmp[250];
        cube[46] = cube_tmp[249];
        cube[47] = cube_tmp[248];
        cube[48] = cube_tmp[247];
        cube[49] = cube_tmp[246];
        cube[54] = cube_tmp[192];
        cube[55] = cube_tmp[191];
        cube[56] = cube_tmp[190];
        cube[61] = cube_tmp[185];
        cube[62] = cube_tmp[184];
        cube[63] = cube_tmp[183];
        cube[68] = cube_tmp[178];
        cube[69] = cube_tmp[177];
        cube[70] = cube_tmp[176];
        cube[75] = cube_tmp[171];
        cube[76] = cube_tmp[170];
        cube[77] = cube_tmp[169];
        cube[82] = cube_tmp[164];
        cube[83] = cube_tmp[163];
        cube[84] = cube_tmp[162];
        cube[89] = cube_tmp[157];
        cube[90] = cube_tmp[156];
        cube[91] = cube_tmp[155];
        cube[96] = cube_tmp[150];
        cube[97] = cube_tmp[149];
        cube[98] = cube_tmp[148];
        cube[99] = cube_tmp[147];
        cube[100] = cube_tmp[146];
        cube[101] = cube_tmp[145];
        cube[102] = cube_tmp[144];
        cube[103] = cube_tmp[143];
        cube[104] = cube_tmp[142];
        cube[105] = cube_tmp[141];
        cube[106] = cube_tmp[140];
        cube[107] = cube_tmp[139];
        cube[108] = cube_tmp[138];
        cube[109] = cube_tmp[137];
        cube[110] = cube_tmp[136];
        cube[111] = cube_tmp[135];
        cube[112] = cube_tmp[134];
        cube[113] = cube_tmp[133];
        cube[114] = cube_tmp[132];
        cube[115] = cube_tmp[131];
        cube[116] = cube_tmp[130];
        cube[117] = cube_tmp[129];
        cube[118] = cube_tmp[128];
        cube[119] = cube_tmp[127];
        cube[120] = cube_tmp[126];
        cube[121] = cube_tmp[125];
        cube[122] = cube_tmp[124];
        cube[124] = cube_tmp[122];
        cube[125] = cube_tmp[121];
        cube[126] = cube_tmp[120];
        cube[127] = cube_tmp[119];
        cube[128] = cube_tmp[118];
        cube[129] = cube_tmp[117];
        cube[130] = cube_tmp[116];
        cube[131] = cube_tmp[115];
        cube[132] = cube_tmp[114];
        cube[133] = cube_tmp[113];
        cube[134] = cube_tmp[112];
        cube[135] = cube_tmp[111];
        cube[136] = cube_tmp[110];
        cube[137] = cube_tmp[109];
        cube[138] = cube_tmp[108];
        cube[139] = cube_tmp[107];
        cube[140] = cube_tmp[106];
        cube[141] = cube_tmp[105];
        cube[142] = cube_tmp[104];
        cube[143] = cube_tmp[103];
        cube[144] = cube_tmp[102];
        cube[145] = cube_tmp[101];
        cube[146] = cube_tmp[100];
        cube[147] = cube_tmp[99];
        cube[148] = cube_tmp[98];
        cube[149] = cube_tmp[97];
        cube[150] = cube_tmp[96];
        cube[155] = cube_tmp[91];
        cube[156] = cube_tmp[90];
        cube[157] = cube_tmp[89];
        cube[162] = cube_tmp[84];
        cube[163] = cube_tmp[83];
        cube[164] = cube_tmp[82];
        cube[169] = cube_tmp[77];
        cube[170] = cube_tmp[76];
        cube[171] = cube_tmp[75];
        cube[176] = cube_tmp[70];
        cube[177] = cube_tmp[69];
        cube[178] = cube_tmp[68];
        cube[183] = cube_tmp[63];
        cube[184] = cube_tmp[62];
        cube[185] = cube_tmp[61];
        cube[190] = cube_tmp[56];
        cube[191] = cube_tmp[55];
        cube[192] = cube_tmp[54];
        cube[246] = cube_tmp[49];
        cube[247] = cube_tmp[48];
        cube[248] = cube_tmp[47];
        cube[249] = cube_tmp[46];
        cube[250] = cube_tmp[45];
        cube[251] = cube_tmp[44];
        cube[252] = cube_tmp[43];
        cube[253] = cube_tmp[42];
        cube[254] = cube_tmp[41];
        cube[255] = cube_tmp[40];
        cube[256] = cube_tmp[39];
        cube[257] = cube_tmp[38];
        cube[258] = cube_tmp[37];
        cube[259] = cube_tmp[36];
        cube[260] = cube_tmp[35];
        cube[261] = cube_tmp[34];
        cube[262] = cube_tmp[33];
        cube[263] = cube_tmp[32];
        cube[264] = cube_tmp[31];
        cube[265] = cube_tmp[30];
        cube[266] = cube_tmp[29];
        break;
    }

    case R: {
        cube[7] = cube_tmp[105];
        cube[14] = cube_tmp[112];
        cube[21] = cube_tmp[119];
        cube[28] = cube_tmp[126];
        cube[35] = cube_tmp[133];
        cube[42] = cube_tmp[140];
        cube[49] = cube_tmp[147];
        cube[105] = cube_tmp[252];
        cube[112] = cube_tmp[259];
        cube[119] = cube_tmp[266];
        cube[126] = cube_tmp[273];
        cube[133] = cube_tmp[280];
        cube[140] = cube_tmp[287];
        cube[147] = cube_tmp[294];
        cube[148] = cube_tmp[190];
        cube[149] = cube_tmp[183];
        cube[150] = cube_tmp[176];
        cube[151] = cube_tmp[169];
        cube[152] = cube_tmp[162];
        cube[153] = cube_tmp[155];
        cube[154] = cube_tmp[148];
        cube[155] = cube_tmp[191];
        cube[156] = cube_tmp[184];
        cube[157] = cube_tmp[177];
        cube[158] = cube_tmp[170];
        cube[159] = cube_tmp[163];
        cube[160] = cube_tmp[156];
        cube[161] = cube_tmp[149];
        cube[162] = cube_tmp[192];
        cube[163] = cube_tmp[185];
        cube[164] = cube_tmp[178];
        cube[165] = cube_tmp[171];
        cube[166] = cube_tmp[164];
        cube[167] = cube_tmp[157];
        cube[168] = cube_tmp[150];
        cube[169] = cube_tmp[193];
        cube[170] = cube_tmp[186];
        cube[171] = cube_tmp[179];
        cube[173] = cube_tmp[165];
        cube[174] = cube_tmp[158];
        cube[175] = cube_tmp[151];
        cube[176] = cube_tmp[194];
        cube[177] = cube_tmp[187];
        cube[178] = cube_tmp[180];
        cube[179] = cube_tmp[173];
        cube[180] = cube_tmp[166];
        cube[181] = cube_tmp[159];
        cube[182] = cube_tmp[152];
        cube[183] = cube_tmp[195];
        cube[184] = cube_tmp[188];
        cube[185] = cube_tmp[181];
        cube[186] = cube_tmp[174];
        cube[187] = cube_tmp[167];
        cube[188] = cube_tmp[160];
        cube[189] = cube_tmp[153];
        cube[190] = cube_tmp[196];
        cube[191] = cube_tmp[189];
        cube[192] = cube_tmp[182];
        cube[193] = cube_tmp[175];
        cube[194] = cube_tmp[168];
        cube[195] = cube_tmp[161];
        cube[196] = cube_tmp[154];
        cube[197] = cube_tmp[49];
        cube[204] = cube_tmp[42];
        cube[211] = cube_tmp[35];
        cube[218] = cube_tmp[28];
        cube[225] = cube_tmp[21];
        cube[232] = cube_tmp[14];
        cube[239] = cube_tmp[7];
        cube[252] = cube_tmp[239];
        cube[259] = cube_tmp[232];
        cube[266] = cube_tmp[225];
        cube[273] = cube_tmp[218];
        cube[280] = cube_tmp[211];
        cube[287] = cube_tmp[204];
        cube[294] = cube_tmp[197];
        break;
    }

    case R_PRIME: {
        cube[7] = cube_tmp[239];
        cube[14] = cube_tmp[232];
        cube[21] = cube_tmp[225];
        cube[28] = cube_tmp[218];
        cube[35] = cube_tmp[211];
        cube[42] = cube_tmp[204];
        cube[49] = cube_tmp[197];
        cube[105] = cube_tmp[7];
        cube[112] = cube_tmp[14];
        cube[119] = cube_tmp[21];
        cube[126] = cube_tmp[28];
        cube[133] = cube_tmp[35];
        cube[140] = cube_tmp[42];
        cube[147] = cube_tmp[49];
        cube[148] = cube_tmp[154];
        cube[149] = cube_tmp[161];
        cube[150] = cube_tmp[168];
        cube[151] = cube_tmp[175];
        cube[152] = cube_tmp[182];
        cube[153] = cube_tmp[189];
        cube[154] = cube_tmp[196];
        cube[155] = cube_tmp[153];
        cube[156] = cube_tmp[160];
        cube[157] = cube_tmp[167];
        cube[158] = cube_tmp[174];
        cube[159] = cube_tmp[181];
        cube[160] = cube_tmp[188];
        cube[161] = cube_tmp[195];
        cube[162] = cube_tmp[152];
        cube[163] = cube_tmp[159];
        cube[164] = cube_tmp[166];
        cube[165] = cube_tmp[173];
        cube[166] = cube_tmp[180];
        cube[167] = cube_tmp[187];
        cube[168] = cube_tmp[194];
        cube[169] = cube_tmp[151];
        cube[170] = cube_tmp[158];
        cube[171] = cube_tmp[165];
        cube[173] = cube_tmp[179];
        cube[174] = cube_tmp[186];
        cube[175] = cube_tmp[193];
        cube[176] = cube_tmp[150];
        cube[177] = cube_tmp[157];
        cube[178] = cube_tmp[164];
        cube[179] = cube_tmp[171];
        cube[180] = cube_tmp[178];
        cube[181] = cube_tmp[185];
        cube[182] = cube_tmp[192];
        cube[183] = cube_tmp[149];
        cube[184] = cube_tmp[156];
        cube[185] = cube_tmp[163];
        cube[186] = cube_tmp[170];
        cube[187] = cube_tmp[177];
        cube[188] = cube_tmp[184];
        cube[189] = cube_tmp[191];
        cube[190] = cube_tmp[148];
        cube[191] = cube_tmp[155];
        cube[192] = cube_tmp[162];
        cube[193] = cube_tmp[169];
        cube[194] = cube_tmp[176];
        cube[195] = cube_tmp[183];
        cube[196] = cube_tmp[190];
        cube[197] = cube_tmp[294];
        cube[204] = cube_tmp[287];
        cube[211] = cube_tmp[280];
        cube[218] = cube_tmp[273];
        cube[225] = cube_tmp[266];
        cube[232] = cube_tmp[259];
        cube[239] = cube_tmp[252];
        cube[252] = cube_tmp[105];
        cube[259] = cube_tmp[112];
        cube[266] = cube_tmp[119];
        cube[273] = cube_tmp[126];
        cube[280] = cube_tmp[133];
        cube[287] = cube_tmp[140];
        cube[294] = cube_tmp[147];
        break;
    }

    case R2: {
        cube[7] = cube_tmp[252];
        cube[14] = cube_tmp[259];
        cube[21] = cube_tmp[266];
        cube[28] = cube_tmp[273];
        cube[35] = cube_tmp[280];
        cube[42] = cube_tmp[287];
        cube[49] = cube_tmp[294];
        cube[105] = cube_tmp[239];
        cube[112] = cube_tmp[232];
        cube[119] = cube_tmp[225];
        cube[126] = cube_tmp[218];
        cube[133] = cube_tmp[211];
        cube[140] = cube_tmp[204];
        cube[147] = cube_tmp[197];
        cube[148] = cube_tmp[196];
        cube[149] = cube_tmp[195];
        cube[150] = cube_tmp[194];
        cube[151] = cube_tmp[193];
        cube[152] = cube_tmp[192];
        cube[153] = cube_tmp[191];
        cube[154] = cube_tmp[190];
        cube[155] = cube_tmp[189];
        cube[156] = cube_tmp[188];
        cube[157] = cube_tmp[187];
        cube[158] = cube_tmp[186];
        cube[159] = cube_tmp[185];
        cube[160] = cube_tmp[184];
        cube[161] = cube_tmp[183];
        cube[162] = cube_tmp[182];
        cube[163] = cube_tmp[181];
        cube[164] = cube_tmp[180];
        cube[165] = cube_tmp[179];
        cube[166] = cube_tmp[178];
        cube[167] = cube_tmp[177];
        cube[168] = cube_tmp[176];
        cube[169] = cube_tmp[175];
        cube[170] = cube_tmp[174];
        cube[171] = cube_tmp[173];
        cube[173] = cube_tmp[171];
        cube[174] = cube_tmp[170];
        cube[175] = cube_tmp[169];
        cube[176] = cube_tmp[168];
        cube[177] = cube_tmp[167];
        cube[178] = cube_tmp[166];
        cube[179] = cube_tmp[165];
        cube[180] = cube_tmp[164];
        cube[181] = cube_tmp[163];
        cube[182] = cube_tmp[162];
        cube[183] = cube_tmp[161];
        cube[184] = cube_tmp[160];
        cube[185] = cube_tmp[159];
        cube[186] = cube_tmp[158];
        cube[187] = cube_tmp[157];
        cube[188] = cube_tmp[156];
        cube[189] = cube_tmp[155];
        cube[190] = cube_tmp[154];
        cube[191] = cube_tmp[153];
        cube[192] = cube_tmp[152];
        cube[193] = cube_tmp[151];
        cube[194] = cube_tmp[150];
        cube[195] = cube_tmp[149];
        cube[196] = cube_tmp[148];
        cube[197] = cube_tmp[147];
        cube[204] = cube_tmp[140];
        cube[211] = cube_tmp[133];
        cube[218] = cube_tmp[126];
        cube[225] = cube_tmp[119];
        cube[232] = cube_tmp[112];
        cube[239] = cube_tmp[105];
        cube[252] = cube_tmp[7];
        cube[259] = cube_tmp[14];
        cube[266] = cube_tmp[21];
        cube[273] = cube_tmp[28];
        cube[280] = cube_tmp[35];
        cube[287] = cube_tmp[42];
        cube[294] = cube_tmp[49];
        break;
    }

    case Rw: {
        cube[6] = cube_tmp[104];
        cube[7] = cube_tmp[105];
        cube[13] = cube_tmp[111];
        cube[14] = cube_tmp[112];
        cube[20] = cube_tmp[118];
        cube[21] = cube_tmp[119];
        cube[27] = cube_tmp[125];
        cube[28] = cube_tmp[126];
        cube[34] = cube_tmp[132];
        cube[35] = cube_tmp[133];
        cube[41] = cube_tmp[139];
        cube[42] = cube_tmp[140];
        cube[48] = cube_tmp[146];
        cube[49] = cube_tmp[147];
        cube[104] = cube_tmp[251];
        cube[105] = cube_tmp[252];
        cube[111] = cube_tmp[258];
        cube[112] = cube_tmp[259];
        cube[118] = cube_tmp[265];
        cube[119] = cube_tmp[266];
        cube[125] = cube_tmp[272];
        cube[126] = cube_tmp[273];
        cube[132] = cube_tmp[279];
        cube[133] = cube_tmp[280];
        cube[139] = cube_tmp[286];
        cube[140] = cube_tmp[287];
        cube[146] = cube_tmp[293];
        cube[147] = cube_tmp[294];
        cube[148] = cube_tmp[190];
        cube[149] = cube_tmp[183];
        cube[150] = cube_tmp[176];
        cube[151] = cube_tmp[169];
        cube[152] = cube_tmp[162];
        cube[153] = cube_tmp[155];
        cube[154] = cube_tmp[148];
        cube[155] = cube_tmp[191];
        cube[156] = cube_tmp[184];
        cube[157] = cube_tmp[177];
        cube[158] = cube_tmp[170];
        cube[159] = cube_tmp[163];
        cube[160] = cube_tmp[156];
        cube[161] = cube_tmp[149];
        cube[162] = cube_tmp[192];
        cube[163] = cube_tmp[185];
        cube[164] = cube_tmp[178];
        cube[165] = cube_tmp[171];
        cube[166] = cube_tmp[164];
        cube[167] = cube_tmp[157];
        cube[168] = cube_tmp[150];
        cube[169] = cube_tmp[193];
        cube[170] = cube_tmp[186];
        cube[171] = cube_tmp[179];
        cube[173] = cube_tmp[165];
        cube[174] = cube_tmp[158];
        cube[175] = cube_tmp[151];
        cube[176] = cube_tmp[194];
        cube[177] = cube_tmp[187];
        cube[178] = cube_tmp[180];
        cube[179] = cube_tmp[173];
        cube[180] = cube_tmp[166];
        cube[181] = cube_tmp[159];
        cube[182] = cube_tmp[152];
        cube[183] = cube_tmp[195];
        cube[184] = cube_tmp[188];
        cube[185] = cube_tmp[181];
        cube[186] = cube_tmp[174];
        cube[187] = cube_tmp[167];
        cube[188] = cube_tmp[160];
        cube[189] = cube_tmp[153];
        cube[190] = cube_tmp[196];
        cube[191] = cube_tmp[189];
        cube[192] = cube_tmp[182];
        cube[193] = cube_tmp[175];
        cube[194] = cube_tmp[168];
        cube[195] = cube_tmp[161];
        cube[196] = cube_tmp[154];
        cube[197] = cube_tmp[49];
        cube[198] = cube_tmp[48];
        cube[204] = cube_tmp[42];
        cube[205] = cube_tmp[41];
        cube[211] = cube_tmp[35];
        cube[212] = cube_tmp[34];
        cube[218] = cube_tmp[28];
        cube[219] = cube_tmp[27];
        cube[225] = cube_tmp[21];
        cube[226] = cube_tmp[20];
        cube[232] = cube_tmp[14];
        cube[233] = cube_tmp[13];
        cube[239] = cube_tmp[7];
        cube[240] = cube_tmp[6];
        cube[251] = cube_tmp[240];
        cube[252] = cube_tmp[239];
        cube[258] = cube_tmp[233];
        cube[259] = cube_tmp[232];
        cube[265] = cube_tmp[226];
        cube[266] = cube_tmp[225];
        cube[272] = cube_tmp[219];
        cube[273] = cube_tmp[218];
        cube[279] = cube_tmp[212];
        cube[280] = cube_tmp[211];
        cube[286] = cube_tmp[205];
        cube[287] = cube_tmp[204];
        cube[293] = cube_tmp[198];
        cube[294] = cube_tmp[197];
        break;
    }

    case Rw_PRIME: {
        cube[6] = cube_tmp[240];
        cube[7] = cube_tmp[239];
        cube[13] = cube_tmp[233];
        cube[14] = cube_tmp[232];
        cube[20] = cube_tmp[226];
        cube[21] = cube_tmp[225];
        cube[27] = cube_tmp[219];
        cube[28] = cube_tmp[218];
        cube[34] = cube_tmp[212];
        cube[35] = cube_tmp[211];
        cube[41] = cube_tmp[205];
        cube[42] = cube_tmp[204];
        cube[48] = cube_tmp[198];
        cube[49] = cube_tmp[197];
        cube[104] = cube_tmp[6];
        cube[105] = cube_tmp[7];
        cube[111] = cube_tmp[13];
        cube[112] = cube_tmp[14];
        cube[118] = cube_tmp[20];
        cube[119] = cube_tmp[21];
        cube[125] = cube_tmp[27];
        cube[126] = cube_tmp[28];
        cube[132] = cube_tmp[34];
        cube[133] = cube_tmp[35];
        cube[139] = cube_tmp[41];
        cube[140] = cube_tmp[42];
        cube[146] = cube_tmp[48];
        cube[147] = cube_tmp[49];
        cube[148] = cube_tmp[154];
        cube[149] = cube_tmp[161];
        cube[150] = cube_tmp[168];
        cube[151] = cube_tmp[175];
        cube[152] = cube_tmp[182];
        cube[153] = cube_tmp[189];
        cube[154] = cube_tmp[196];
        cube[155] = cube_tmp[153];
        cube[156] = cube_tmp[160];
        cube[157] = cube_tmp[167];
        cube[158] = cube_tmp[174];
        cube[159] = cube_tmp[181];
        cube[160] = cube_tmp[188];
        cube[161] = cube_tmp[195];
        cube[162] = cube_tmp[152];
        cube[163] = cube_tmp[159];
        cube[164] = cube_tmp[166];
        cube[165] = cube_tmp[173];
        cube[166] = cube_tmp[180];
        cube[167] = cube_tmp[187];
        cube[168] = cube_tmp[194];
        cube[169] = cube_tmp[151];
        cube[170] = cube_tmp[158];
        cube[171] = cube_tmp[165];
        cube[173] = cube_tmp[179];
        cube[174] = cube_tmp[186];
        cube[175] = cube_tmp[193];
        cube[176] = cube_tmp[150];
        cube[177] = cube_tmp[157];
        cube[178] = cube_tmp[164];
        cube[179] = cube_tmp[171];
        cube[180] = cube_tmp[178];
        cube[181] = cube_tmp[185];
        cube[182] = cube_tmp[192];
        cube[183] = cube_tmp[149];
        cube[184] = cube_tmp[156];
        cube[185] = cube_tmp[163];
        cube[186] = cube_tmp[170];
        cube[187] = cube_tmp[177];
        cube[188] = cube_tmp[184];
        cube[189] = cube_tmp[191];
        cube[190] = cube_tmp[148];
        cube[191] = cube_tmp[155];
        cube[192] = cube_tmp[162];
        cube[193] = cube_tmp[169];
        cube[194] = cube_tmp[176];
        cube[195] = cube_tmp[183];
        cube[196] = cube_tmp[190];
        cube[197] = cube_tmp[294];
        cube[198] = cube_tmp[293];
        cube[204] = cube_tmp[287];
        cube[205] = cube_tmp[286];
        cube[211] = cube_tmp[280];
        cube[212] = cube_tmp[279];
        cube[218] = cube_tmp[273];
        cube[219] = cube_tmp[272];
        cube[225] = cube_tmp[266];
        cube[226] = cube_tmp[265];
        cube[232] = cube_tmp[259];
        cube[233] = cube_tmp[258];
        cube[239] = cube_tmp[252];
        cube[240] = cube_tmp[251];
        cube[251] = cube_tmp[104];
        cube[252] = cube_tmp[105];
        cube[258] = cube_tmp[111];
        cube[259] = cube_tmp[112];
        cube[265] = cube_tmp[118];
        cube[266] = cube_tmp[119];
        cube[272] = cube_tmp[125];
        cube[273] = cube_tmp[126];
        cube[279] = cube_tmp[132];
        cube[280] = cube_tmp[133];
        cube[286] = cube_tmp[139];
        cube[287] = cube_tmp[140];
        cube[293] = cube_tmp[146];
        cube[294] = cube_tmp[147];
        break;
    }

    case Rw2: {
        cube[6] = cube_tmp[251];
        cube[7] = cube_tmp[252];
        cube[13] = cube_tmp[258];
        cube[14] = cube_tmp[259];
        cube[20] = cube_tmp[265];
        cube[21] = cube_tmp[266];
        cube[27] = cube_tmp[272];
        cube[28] = cube_tmp[273];
        cube[34] = cube_tmp[279];
        cube[35] = cube_tmp[280];
        cube[41] = cube_tmp[286];
        cube[42] = cube_tmp[287];
        cube[48] = cube_tmp[293];
        cube[49] = cube_tmp[294];
        cube[104] = cube_tmp[240];
        cube[105] = cube_tmp[239];
        cube[111] = cube_tmp[233];
        cube[112] = cube_tmp[232];
        cube[118] = cube_tmp[226];
        cube[119] = cube_tmp[225];
        cube[125] = cube_tmp[219];
        cube[126] = cube_tmp[218];
        cube[132] = cube_tmp[212];
        cube[133] = cube_tmp[211];
        cube[139] = cube_tmp[205];
        cube[140] = cube_tmp[204];
        cube[146] = cube_tmp[198];
        cube[147] = cube_tmp[197];
        cube[148] = cube_tmp[196];
        cube[149] = cube_tmp[195];
        cube[150] = cube_tmp[194];
        cube[151] = cube_tmp[193];
        cube[152] = cube_tmp[192];
        cube[153] = cube_tmp[191];
        cube[154] = cube_tmp[190];
        cube[155] = cube_tmp[189];
        cube[156] = cube_tmp[188];
        cube[157] = cube_tmp[187];
        cube[158] = cube_tmp[186];
        cube[159] = cube_tmp[185];
        cube[160] = cube_tmp[184];
        cube[161] = cube_tmp[183];
        cube[162] = cube_tmp[182];
        cube[163] = cube_tmp[181];
        cube[164] = cube_tmp[180];
        cube[165] = cube_tmp[179];
        cube[166] = cube_tmp[178];
        cube[167] = cube_tmp[177];
        cube[168] = cube_tmp[176];
        cube[169] = cube_tmp[175];
        cube[170] = cube_tmp[174];
        cube[171] = cube_tmp[173];
        cube[173] = cube_tmp[171];
        cube[174] = cube_tmp[170];
        cube[175] = cube_tmp[169];
        cube[176] = cube_tmp[168];
        cube[177] = cube_tmp[167];
        cube[178] = cube_tmp[166];
        cube[179] = cube_tmp[165];
        cube[180] = cube_tmp[164];
        cube[181] = cube_tmp[163];
        cube[182] = cube_tmp[162];
        cube[183] = cube_tmp[161];
        cube[184] = cube_tmp[160];
        cube[185] = cube_tmp[159];
        cube[186] = cube_tmp[158];
        cube[187] = cube_tmp[157];
        cube[188] = cube_tmp[156];
        cube[189] = cube_tmp[155];
        cube[190] = cube_tmp[154];
        cube[191] = cube_tmp[153];
        cube[192] = cube_tmp[152];
        cube[193] = cube_tmp[151];
        cube[194] = cube_tmp[150];
        cube[195] = cube_tmp[149];
        cube[196] = cube_tmp[148];
        cube[197] = cube_tmp[147];
        cube[198] = cube_tmp[146];
        cube[204] = cube_tmp[140];
        cube[205] = cube_tmp[139];
        cube[211] = cube_tmp[133];
        cube[212] = cube_tmp[132];
        cube[218] = cube_tmp[126];
        cube[219] = cube_tmp[125];
        cube[225] = cube_tmp[119];
        cube[226] = cube_tmp[118];
        cube[232] = cube_tmp[112];
        cube[233] = cube_tmp[111];
        cube[239] = cube_tmp[105];
        cube[240] = cube_tmp[104];
        cube[251] = cube_tmp[6];
        cube[252] = cube_tmp[7];
        cube[258] = cube_tmp[13];
        cube[259] = cube_tmp[14];
        cube[265] = cube_tmp[20];
        cube[266] = cube_tmp[21];
        cube[272] = cube_tmp[27];
        cube[273] = cube_tmp[28];
        cube[279] = cube_tmp[34];
        cube[280] = cube_tmp[35];
        cube[286] = cube_tmp[41];
        cube[287] = cube_tmp[42];
        cube[293] = cube_tmp[48];
        cube[294] = cube_tmp[49];
        break;
    }

    case threeRw: {
        cube[5] = cube_tmp[103];
        cube[6] = cube_tmp[104];
        cube[7] = cube_tmp[105];
        cube[12] = cube_tmp[110];
        cube[13] = cube_tmp[111];
        cube[14] = cube_tmp[112];
        cube[19] = cube_tmp[117];
        cube[20] = cube_tmp[118];
        cube[21] = cube_tmp[119];
        cube[26] = cube_tmp[124];
        cube[27] = cube_tmp[125];
        cube[28] = cube_tmp[126];
        cube[33] = cube_tmp[131];
        cube[34] = cube_tmp[132];
        cube[35] = cube_tmp[133];
        cube[40] = cube_tmp[138];
        cube[41] = cube_tmp[139];
        cube[42] = cube_tmp[140];
        cube[47] = cube_tmp[145];
        cube[48] = cube_tmp[146];
        cube[49] = cube_tmp[147];
        cube[103] = cube_tmp[250];
        cube[104] = cube_tmp[251];
        cube[105] = cube_tmp[252];
        cube[110] = cube_tmp[257];
        cube[111] = cube_tmp[258];
        cube[112] = cube_tmp[259];
        cube[117] = cube_tmp[264];
        cube[118] = cube_tmp[265];
        cube[119] = cube_tmp[266];
        cube[124] = cube_tmp[271];
        cube[125] = cube_tmp[272];
        cube[126] = cube_tmp[273];
        cube[131] = cube_tmp[278];
        cube[132] = cube_tmp[279];
        cube[133] = cube_tmp[280];
        cube[138] = cube_tmp[285];
        cube[139] = cube_tmp[286];
        cube[140] = cube_tmp[287];
        cube[145] = cube_tmp[292];
        cube[146] = cube_tmp[293];
        cube[147] = cube_tmp[294];
        cube[148] = cube_tmp[190];
        cube[149] = cube_tmp[183];
        cube[150] = cube_tmp[176];
        cube[151] = cube_tmp[169];
        cube[152] = cube_tmp[162];
        cube[153] = cube_tmp[155];
        cube[154] = cube_tmp[148];
        cube[155] = cube_tmp[191];
        cube[156] = cube_tmp[184];
        cube[157] = cube_tmp[177];
        cube[158] = cube_tmp[170];
        cube[159] = cube_tmp[163];
        cube[160] = cube_tmp[156];
        cube[161] = cube_tmp[149];
        cube[162] = cube_tmp[192];
        cube[163] = cube_tmp[185];
        cube[164] = cube_tmp[178];
        cube[165] = cube_tmp[171];
        cube[166] = cube_tmp[164];
        cube[167] = cube_tmp[157];
        cube[168] = cube_tmp[150];
        cube[169] = cube_tmp[193];
        cube[170] = cube_tmp[186];
        cube[171] = cube_tmp[179];
        cube[173] = cube_tmp[165];
        cube[174] = cube_tmp[158];
        cube[175] = cube_tmp[151];
        cube[176] = cube_tmp[194];
        cube[177] = cube_tmp[187];
        cube[178] = cube_tmp[180];
        cube[179] = cube_tmp[173];
        cube[180] = cube_tmp[166];
        cube[181] = cube_tmp[159];
        cube[182] = cube_tmp[152];
        cube[183] = cube_tmp[195];
        cube[184] = cube_tmp[188];
        cube[185] = cube_tmp[181];
        cube[186] = cube_tmp[174];
        cube[187] = cube_tmp[167];
        cube[188] = cube_tmp[160];
        cube[189] = cube_tmp[153];
        cube[190] = cube_tmp[196];
        cube[191] = cube_tmp[189];
        cube[192] = cube_tmp[182];
        cube[193] = cube_tmp[175];
        cube[194] = cube_tmp[168];
        cube[195] = cube_tmp[161];
        cube[196] = cube_tmp[154];
        cube[197] = cube_tmp[49];
        cube[198] = cube_tmp[48];
        cube[199] = cube_tmp[47];
        cube[204] = cube_tmp[42];
        cube[205] = cube_tmp[41];
        cube[206] = cube_tmp[40];
        cube[211] = cube_tmp[35];
        cube[212] = cube_tmp[34];
        cube[213] = cube_tmp[33];
        cube[218] = cube_tmp[28];
        cube[219] = cube_tmp[27];
        cube[220] = cube_tmp[26];
        cube[225] = cube_tmp[21];
        cube[226] = cube_tmp[20];
        cube[227] = cube_tmp[19];
        cube[232] = cube_tmp[14];
        cube[233] = cube_tmp[13];
        cube[234] = cube_tmp[12];
        cube[239] = cube_tmp[7];
        cube[240] = cube_tmp[6];
        cube[241] = cube_tmp[5];
        cube[250] = cube_tmp[241];
        cube[251] = cube_tmp[240];
        cube[252] = cube_tmp[239];
        cube[257] = cube_tmp[234];
        cube[258] = cube_tmp[233];
        cube[259] = cube_tmp[232];
        cube[264] = cube_tmp[227];
        cube[265] = cube_tmp[226];
        cube[266] = cube_tmp[225];
        cube[271] = cube_tmp[220];
        cube[272] = cube_tmp[219];
        cube[273] = cube_tmp[218];
        cube[278] = cube_tmp[213];
        cube[279] = cube_tmp[212];
        cube[280] = cube_tmp[211];
        cube[285] = cube_tmp[206];
        cube[286] = cube_tmp[205];
        cube[287] = cube_tmp[204];
        cube[292] = cube_tmp[199];
        cube[293] = cube_tmp[198];
        cube[294] = cube_tmp[197];
        break;
    }

    case threeRw_PRIME: {
        cube[5] = cube_tmp[241];
        cube[6] = cube_tmp[240];
        cube[7] = cube_tmp[239];
        cube[12] = cube_tmp[234];
        cube[13] = cube_tmp[233];
        cube[14] = cube_tmp[232];
        cube[19] = cube_tmp[227];
        cube[20] = cube_tmp[226];
        cube[21] = cube_tmp[225];
        cube[26] = cube_tmp[220];
        cube[27] = cube_tmp[219];
        cube[28] = cube_tmp[218];
        cube[33] = cube_tmp[213];
        cube[34] = cube_tmp[212];
        cube[35] = cube_tmp[211];
        cube[40] = cube_tmp[206];
        cube[41] = cube_tmp[205];
        cube[42] = cube_tmp[204];
        cube[47] = cube_tmp[199];
        cube[48] = cube_tmp[198];
        cube[49] = cube_tmp[197];
        cube[103] = cube_tmp[5];
        cube[104] = cube_tmp[6];
        cube[105] = cube_tmp[7];
        cube[110] = cube_tmp[12];
        cube[111] = cube_tmp[13];
        cube[112] = cube_tmp[14];
        cube[117] = cube_tmp[19];
        cube[118] = cube_tmp[20];
        cube[119] = cube_tmp[21];
        cube[124] = cube_tmp[26];
        cube[125] = cube_tmp[27];
        cube[126] = cube_tmp[28];
        cube[131] = cube_tmp[33];
        cube[132] = cube_tmp[34];
        cube[133] = cube_tmp[35];
        cube[138] = cube_tmp[40];
        cube[139] = cube_tmp[41];
        cube[140] = cube_tmp[42];
        cube[145] = cube_tmp[47];
        cube[146] = cube_tmp[48];
        cube[147] = cube_tmp[49];
        cube[148] = cube_tmp[154];
        cube[149] = cube_tmp[161];
        cube[150] = cube_tmp[168];
        cube[151] = cube_tmp[175];
        cube[152] = cube_tmp[182];
        cube[153] = cube_tmp[189];
        cube[154] = cube_tmp[196];
        cube[155] = cube_tmp[153];
        cube[156] = cube_tmp[160];
        cube[157] = cube_tmp[167];
        cube[158] = cube_tmp[174];
        cube[159] = cube_tmp[181];
        cube[160] = cube_tmp[188];
        cube[161] = cube_tmp[195];
        cube[162] = cube_tmp[152];
        cube[163] = cube_tmp[159];
        cube[164] = cube_tmp[166];
        cube[165] = cube_tmp[173];
        cube[166] = cube_tmp[180];
        cube[167] = cube_tmp[187];
        cube[168] = cube_tmp[194];
        cube[169] = cube_tmp[151];
        cube[170] = cube_tmp[158];
        cube[171] = cube_tmp[165];
        cube[173] = cube_tmp[179];
        cube[174] = cube_tmp[186];
        cube[175] = cube_tmp[193];
        cube[176] = cube_tmp[150];
        cube[177] = cube_tmp[157];
        cube[178] = cube_tmp[164];
        cube[179] = cube_tmp[171];
        cube[180] = cube_tmp[178];
        cube[181] = cube_tmp[185];
        cube[182] = cube_tmp[192];
        cube[183] = cube_tmp[149];
        cube[184] = cube_tmp[156];
        cube[185] = cube_tmp[163];
        cube[186] = cube_tmp[170];
        cube[187] = cube_tmp[177];
        cube[188] = cube_tmp[184];
        cube[189] = cube_tmp[191];
        cube[190] = cube_tmp[148];
        cube[191] = cube_tmp[155];
        cube[192] = cube_tmp[162];
        cube[193] = cube_tmp[169];
        cube[194] = cube_tmp[176];
        cube[195] = cube_tmp[183];
        cube[196] = cube_tmp[190];
        cube[197] = cube_tmp[294];
        cube[198] = cube_tmp[293];
        cube[199] = cube_tmp[292];
        cube[204] = cube_tmp[287];
        cube[205] = cube_tmp[286];
        cube[206] = cube_tmp[285];
        cube[211] = cube_tmp[280];
        cube[212] = cube_tmp[279];
        cube[213] = cube_tmp[278];
        cube[218] = cube_tmp[273];
        cube[219] = cube_tmp[272];
        cube[220] = cube_tmp[271];
        cube[225] = cube_tmp[266];
        cube[226] = cube_tmp[265];
        cube[227] = cube_tmp[264];
        cube[232] = cube_tmp[259];
        cube[233] = cube_tmp[258];
        cube[234] = cube_tmp[257];
        cube[239] = cube_tmp[252];
        cube[240] = cube_tmp[251];
        cube[241] = cube_tmp[250];
        cube[250] = cube_tmp[103];
        cube[251] = cube_tmp[104];
        cube[252] = cube_tmp[105];
        cube[257] = cube_tmp[110];
        cube[258] = cube_tmp[111];
        cube[259] = cube_tmp[112];
        cube[264] = cube_tmp[117];
        cube[265] = cube_tmp[118];
        cube[266] = cube_tmp[119];
        cube[271] = cube_tmp[124];
        cube[272] = cube_tmp[125];
        cube[273] = cube_tmp[126];
        cube[278] = cube_tmp[131];
        cube[279] = cube_tmp[132];
        cube[280] = cube_tmp[133];
        cube[285] = cube_tmp[138];
        cube[286] = cube_tmp[139];
        cube[287] = cube_tmp[140];
        cube[292] = cube_tmp[145];
        cube[293] = cube_tmp[146];
        cube[294] = cube_tmp[147];
        break;
    }

    case threeRw2: {
        cube[5] = cube_tmp[250];
        cube[6] = cube_tmp[251];
        cube[7] = cube_tmp[252];
        cube[12] = cube_tmp[257];
        cube[13] = cube_tmp[258];
        cube[14] = cube_tmp[259];
        cube[19] = cube_tmp[264];
        cube[20] = cube_tmp[265];
        cube[21] = cube_tmp[266];
        cube[26] = cube_tmp[271];
        cube[27] = cube_tmp[272];
        cube[28] = cube_tmp[273];
        cube[33] = cube_tmp[278];
        cube[34] = cube_tmp[279];
        cube[35] = cube_tmp[280];
        cube[40] = cube_tmp[285];
        cube[41] = cube_tmp[286];
        cube[42] = cube_tmp[287];
        cube[47] = cube_tmp[292];
        cube[48] = cube_tmp[293];
        cube[49] = cube_tmp[294];
        cube[103] = cube_tmp[241];
        cube[104] = cube_tmp[240];
        cube[105] = cube_tmp[239];
        cube[110] = cube_tmp[234];
        cube[111] = cube_tmp[233];
        cube[112] = cube_tmp[232];
        cube[117] = cube_tmp[227];
        cube[118] = cube_tmp[226];
        cube[119] = cube_tmp[225];
        cube[124] = cube_tmp[220];
        cube[125] = cube_tmp[219];
        cube[126] = cube_tmp[218];
        cube[131] = cube_tmp[213];
        cube[132] = cube_tmp[212];
        cube[133] = cube_tmp[211];
        cube[138] = cube_tmp[206];
        cube[139] = cube_tmp[205];
        cube[140] = cube_tmp[204];
        cube[145] = cube_tmp[199];
        cube[146] = cube_tmp[198];
        cube[147] = cube_tmp[197];
        cube[148] = cube_tmp[196];
        cube[149] = cube_tmp[195];
        cube[150] = cube_tmp[194];
        cube[151] = cube_tmp[193];
        cube[152] = cube_tmp[192];
        cube[153] = cube_tmp[191];
        cube[154] = cube_tmp[190];
        cube[155] = cube_tmp[189];
        cube[156] = cube_tmp[188];
        cube[157] = cube_tmp[187];
        cube[158] = cube_tmp[186];
        cube[159] = cube_tmp[185];
        cube[160] = cube_tmp[184];
        cube[161] = cube_tmp[183];
        cube[162] = cube_tmp[182];
        cube[163] = cube_tmp[181];
        cube[164] = cube_tmp[180];
        cube[165] = cube_tmp[179];
        cube[166] = cube_tmp[178];
        cube[167] = cube_tmp[177];
        cube[168] = cube_tmp[176];
        cube[169] = cube_tmp[175];
        cube[170] = cube_tmp[174];
        cube[171] = cube_tmp[173];
        cube[173] = cube_tmp[171];
        cube[174] = cube_tmp[170];
        cube[175] = cube_tmp[169];
        cube[176] = cube_tmp[168];
        cube[177] = cube_tmp[167];
        cube[178] = cube_tmp[166];
        cube[179] = cube_tmp[165];
        cube[180] = cube_tmp[164];
        cube[181] = cube_tmp[163];
        cube[182] = cube_tmp[162];
        cube[183] = cube_tmp[161];
        cube[184] = cube_tmp[160];
        cube[185] = cube_tmp[159];
        cube[186] = cube_tmp[158];
        cube[187] = cube_tmp[157];
        cube[188] = cube_tmp[156];
        cube[189] = cube_tmp[155];
        cube[190] = cube_tmp[154];
        cube[191] = cube_tmp[153];
        cube[192] = cube_tmp[152];
        cube[193] = cube_tmp[151];
        cube[194] = cube_tmp[150];
        cube[195] = cube_tmp[149];
        cube[196] = cube_tmp[148];
        cube[197] = cube_tmp[147];
        cube[198] = cube_tmp[146];
        cube[199] = cube_tmp[145];
        cube[204] = cube_tmp[140];
        cube[205] = cube_tmp[139];
        cube[206] = cube_tmp[138];
        cube[211] = cube_tmp[133];
        cube[212] = cube_tmp[132];
        cube[213] = cube_tmp[131];
        cube[218] = cube_tmp[126];
        cube[219] = cube_tmp[125];
        cube[220] = cube_tmp[124];
        cube[225] = cube_tmp[119];
        cube[226] = cube_tmp[118];
        cube[227] = cube_tmp[117];
        cube[232] = cube_tmp[112];
        cube[233] = cube_tmp[111];
        cube[234] = cube_tmp[110];
        cube[239] = cube_tmp[105];
        cube[240] = cube_tmp[104];
        cube[241] = cube_tmp[103];
        cube[250] = cube_tmp[5];
        cube[251] = cube_tmp[6];
        cube[252] = cube_tmp[7];
        cube[257] = cube_tmp[12];
        cube[258] = cube_tmp[13];
        cube[259] = cube_tmp[14];
        cube[264] = cube_tmp[19];
        cube[265] = cube_tmp[20];
        cube[266] = cube_tmp[21];
        cube[271] = cube_tmp[26];
        cube[272] = cube_tmp[27];
        cube[273] = cube_tmp[28];
        cube[278] = cube_tmp[33];
        cube[279] = cube_tmp[34];
        cube[280] = cube_tmp[35];
        cube[285] = cube_tmp[40];
        cube[286] = cube_tmp[41];
        cube[287] = cube_tmp[42];
        cube[292] = cube_tmp[47];
        cube[293] = cube_tmp[48];
        cube[294] = cube_tmp[49];
        break;
    }

    case B: {
        cube[1] = cube_tmp[154];
        cube[2] = cube_tmp[161];
        cube[3] = cube_tmp[168];
        cube[4] = cube_tmp[175];
        cube[5] = cube_tmp[182];
        cube[6] = cube_tmp[189];
        cube[7] = cube_tmp[196];
        cube[50] = cube_tmp[7];
        cube[57] = cube_tmp[6];
        cube[64] = cube_tmp[5];
        cube[71] = cube_tmp[4];
        cube[78] = cube_tmp[3];
        cube[85] = cube_tmp[2];
        cube[92] = cube_tmp[1];
        cube[154] = cube_tmp[294];
        cube[161] = cube_tmp[293];
        cube[168] = cube_tmp[292];
        cube[175] = cube_tmp[291];
        cube[182] = cube_tmp[290];
        cube[189] = cube_tmp[289];
        cube[196] = cube_tmp[288];
        cube[197] = cube_tmp[239];
        cube[198] = cube_tmp[232];
        cube[199] = cube_tmp[225];
        cube[200] = cube_tmp[218];
        cube[201] = cube_tmp[211];
        cube[202] = cube_tmp[204];
        cube[203] = cube_tmp[197];
        cube[204] = cube_tmp[240];
        cube[205] = cube_tmp[233];
        cube[206] = cube_tmp[226];
        cube[207] = cube_tmp[219];
        cube[208] = cube_tmp[212];
        cube[209] = cube_tmp[205];
        cube[210] = cube_tmp[198];
        cube[211] = cube_tmp[241];
        cube[212] = cube_tmp[234];
        cube[213] = cube_tmp[227];
        cube[214] = cube_tmp[220];
        cube[215] = cube_tmp[213];
        cube[216] = cube_tmp[206];
        cube[217] = cube_tmp[199];
        cube[218] = cube_tmp[242];
        cube[219] = cube_tmp[235];
        cube[220] = cube_tmp[228];
        cube[222] = cube_tmp[214];
        cube[223] = cube_tmp[207];
        cube[224] = cube_tmp[200];
        cube[225] = cube_tmp[243];
        cube[226] = cube_tmp[236];
        cube[227] = cube_tmp[229];
        cube[228] = cube_tmp[222];
        cube[229] = cube_tmp[215];
        cube[230] = cube_tmp[208];
        cube[231] = cube_tmp[201];
        cube[232] = cube_tmp[244];
        cube[233] = cube_tmp[237];
        cube[234] = cube_tmp[230];
        cube[235] = cube_tmp[223];
        cube[236] = cube_tmp[216];
        cube[237] = cube_tmp[209];
        cube[238] = cube_tmp[202];
        cube[239] = cube_tmp[245];
        cube[240] = cube_tmp[238];
        cube[241] = cube_tmp[231];
        cube[242] = cube_tmp[224];
        cube[243] = cube_tmp[217];
        cube[244] = cube_tmp[210];
        cube[245] = cube_tmp[203];
        cube[288] = cube_tmp[50];
        cube[289] = cube_tmp[57];
        cube[290] = cube_tmp[64];
        cube[291] = cube_tmp[71];
        cube[292] = cube_tmp[78];
        cube[293] = cube_tmp[85];
        cube[294] = cube_tmp[92];
        break;
    }

    case B_PRIME: {
        cube[1] = cube_tmp[92];
        cube[2] = cube_tmp[85];
        cube[3] = cube_tmp[78];
        cube[4] = cube_tmp[71];
        cube[5] = cube_tmp[64];
        cube[6] = cube_tmp[57];
        cube[7] = cube_tmp[50];
        cube[50] = cube_tmp[288];
        cube[57] = cube_tmp[289];
        cube[64] = cube_tmp[290];
        cube[71] = cube_tmp[291];
        cube[78] = cube_tmp[292];
        cube[85] = cube_tmp[293];
        cube[92] = cube_tmp[294];
        cube[154] = cube_tmp[1];
        cube[161] = cube_tmp[2];
        cube[168] = cube_tmp[3];
        cube[175] = cube_tmp[4];
        cube[182] = cube_tmp[5];
        cube[189] = cube_tmp[6];
        cube[196] = cube_tmp[7];
        cube[197] = cube_tmp[203];
        cube[198] = cube_tmp[210];
        cube[199] = cube_tmp[217];
        cube[200] = cube_tmp[224];
        cube[201] = cube_tmp[231];
        cube[202] = cube_tmp[238];
        cube[203] = cube_tmp[245];
        cube[204] = cube_tmp[202];
        cube[205] = cube_tmp[209];
        cube[206] = cube_tmp[216];
        cube[207] = cube_tmp[223];
        cube[208] = cube_tmp[230];
        cube[209] = cube_tmp[237];
        cube[210] = cube_tmp[244];
        cube[211] = cube_tmp[201];
        cube[212] = cube_tmp[208];
        cube[213] = cube_tmp[215];
        cube[214] = cube_tmp[222];
        cube[215] = cube_tmp[229];
        cube[216] = cube_tmp[236];
        cube[217] = cube_tmp[243];
        cube[218] = cube_tmp[200];
        cube[219] = cube_tmp[207];
        cube[220] = cube_tmp[214];
        cube[222] = cube_tmp[228];
        cube[223] = cube_tmp[235];
        cube[224] = cube_tmp[242];
        cube[225] = cube_tmp[199];
        cube[226] = cube_tmp[206];
        cube[227] = cube_tmp[213];
        cube[228] = cube_tmp[220];
        cube[229] = cube_tmp[227];
        cube[230] = cube_tmp[234];
        cube[231] = cube_tmp[241];
        cube[232] = cube_tmp[198];
        cube[233] = cube_tmp[205];
        cube[234] = cube_tmp[212];
        cube[235] = cube_tmp[219];
        cube[236] = cube_tmp[226];
        cube[237] = cube_tmp[233];
        cube[238] = cube_tmp[240];
        cube[239] = cube_tmp[197];
        cube[240] = cube_tmp[204];
        cube[241] = cube_tmp[211];
        cube[242] = cube_tmp[218];
        cube[243] = cube_tmp[225];
        cube[244] = cube_tmp[232];
        cube[245] = cube_tmp[239];
        cube[288] = cube_tmp[196];
        cube[289] = cube_tmp[189];
        cube[290] = cube_tmp[182];
        cube[291] = cube_tmp[175];
        cube[292] = cube_tmp[168];
        cube[293] = cube_tmp[161];
        cube[294] = cube_tmp[154];
        break;
    }

    case B2: {
        cube[1] = cube_tmp[294];
        cube[2] = cube_tmp[293];
        cube[3] = cube_tmp[292];
        cube[4] = cube_tmp[291];
        cube[5] = cube_tmp[290];
        cube[6] = cube_tmp[289];
        cube[7] = cube_tmp[288];
        cube[50] = cube_tmp[196];
        cube[57] = cube_tmp[189];
        cube[64] = cube_tmp[182];
        cube[71] = cube_tmp[175];
        cube[78] = cube_tmp[168];
        cube[85] = cube_tmp[161];
        cube[92] = cube_tmp[154];
        cube[154] = cube_tmp[92];
        cube[161] = cube_tmp[85];
        cube[168] = cube_tmp[78];
        cube[175] = cube_tmp[71];
        cube[182] = cube_tmp[64];
        cube[189] = cube_tmp[57];
        cube[196] = cube_tmp[50];
        cube[197] = cube_tmp[245];
        cube[198] = cube_tmp[244];
        cube[199] = cube_tmp[243];
        cube[200] = cube_tmp[242];
        cube[201] = cube_tmp[241];
        cube[202] = cube_tmp[240];
        cube[203] = cube_tmp[239];
        cube[204] = cube_tmp[238];
        cube[205] = cube_tmp[237];
        cube[206] = cube_tmp[236];
        cube[207] = cube_tmp[235];
        cube[208] = cube_tmp[234];
        cube[209] = cube_tmp[233];
        cube[210] = cube_tmp[232];
        cube[211] = cube_tmp[231];
        cube[212] = cube_tmp[230];
        cube[213] = cube_tmp[229];
        cube[214] = cube_tmp[228];
        cube[215] = cube_tmp[227];
        cube[216] = cube_tmp[226];
        cube[217] = cube_tmp[225];
        cube[218] = cube_tmp[224];
        cube[219] = cube_tmp[223];
        cube[220] = cube_tmp[222];
        cube[222] = cube_tmp[220];
        cube[223] = cube_tmp[219];
        cube[224] = cube_tmp[218];
        cube[225] = cube_tmp[217];
        cube[226] = cube_tmp[216];
        cube[227] = cube_tmp[215];
        cube[228] = cube_tmp[214];
        cube[229] = cube_tmp[213];
        cube[230] = cube_tmp[212];
        cube[231] = cube_tmp[211];
        cube[232] = cube_tmp[210];
        cube[233] = cube_tmp[209];
        cube[234] = cube_tmp[208];
        cube[235] = cube_tmp[207];
        cube[236] = cube_tmp[206];
        cube[237] = cube_tmp[205];
        cube[238] = cube_tmp[204];
        cube[239] = cube_tmp[203];
        cube[240] = cube_tmp[202];
        cube[241] = cube_tmp[201];
        cube[242] = cube_tmp[200];
        cube[243] = cube_tmp[199];
        cube[244] = cube_tmp[198];
        cube[245] = cube_tmp[197];
        cube[288] = cube_tmp[7];
        cube[289] = cube_tmp[6];
        cube[290] = cube_tmp[5];
        cube[291] = cube_tmp[4];
        cube[292] = cube_tmp[3];
        cube[293] = cube_tmp[2];
        cube[294] = cube_tmp[1];
        break;
    }

    case Bw: {
        cube[1] = cube_tmp[154];
        cube[2] = cube_tmp[161];
        cube[3] = cube_tmp[168];
        cube[4] = cube_tmp[175];
        cube[5] = cube_tmp[182];
        cube[6] = cube_tmp[189];
        cube[7] = cube_tmp[196];
        cube[8] = cube_tmp[153];
        cube[9] = cube_tmp[160];
        cube[10] = cube_tmp[167];
        cube[11] = cube_tmp[174];
        cube[12] = cube_tmp[181];
        cube[13] = cube_tmp[188];
        cube[14] = cube_tmp[195];
        cube[50] = cube_tmp[7];
        cube[51] = cube_tmp[14];
        cube[57] = cube_tmp[6];
        cube[58] = cube_tmp[13];
        cube[64] = cube_tmp[5];
        cube[65] = cube_tmp[12];
        cube[71] = cube_tmp[4];
        cube[72] = cube_tmp[11];
        cube[78] = cube_tmp[3];
        cube[79] = cube_tmp[10];
        cube[85] = cube_tmp[2];
        cube[86] = cube_tmp[9];
        cube[92] = cube_tmp[1];
        cube[93] = cube_tmp[8];
        cube[153] = cube_tmp[287];
        cube[154] = cube_tmp[294];
        cube[160] = cube_tmp[286];
        cube[161] = cube_tmp[293];
        cube[167] = cube_tmp[285];
        cube[168] = cube_tmp[292];
        cube[174] = cube_tmp[284];
        cube[175] = cube_tmp[291];
        cube[181] = cube_tmp[283];
        cube[182] = cube_tmp[290];
        cube[188] = cube_tmp[282];
        cube[189] = cube_tmp[289];
        cube[195] = cube_tmp[281];
        cube[196] = cube_tmp[288];
        cube[197] = cube_tmp[239];
        cube[198] = cube_tmp[232];
        cube[199] = cube_tmp[225];
        cube[200] = cube_tmp[218];
        cube[201] = cube_tmp[211];
        cube[202] = cube_tmp[204];
        cube[203] = cube_tmp[197];
        cube[204] = cube_tmp[240];
        cube[205] = cube_tmp[233];
        cube[206] = cube_tmp[226];
        cube[207] = cube_tmp[219];
        cube[208] = cube_tmp[212];
        cube[209] = cube_tmp[205];
        cube[210] = cube_tmp[198];
        cube[211] = cube_tmp[241];
        cube[212] = cube_tmp[234];
        cube[213] = cube_tmp[227];
        cube[214] = cube_tmp[220];
        cube[215] = cube_tmp[213];
        cube[216] = cube_tmp[206];
        cube[217] = cube_tmp[199];
        cube[218] = cube_tmp[242];
        cube[219] = cube_tmp[235];
        cube[220] = cube_tmp[228];
        cube[222] = cube_tmp[214];
        cube[223] = cube_tmp[207];
        cube[224] = cube_tmp[200];
        cube[225] = cube_tmp[243];
        cube[226] = cube_tmp[236];
        cube[227] = cube_tmp[229];
        cube[228] = cube_tmp[222];
        cube[229] = cube_tmp[215];
        cube[230] = cube_tmp[208];
        cube[231] = cube_tmp[201];
        cube[232] = cube_tmp[244];
        cube[233] = cube_tmp[237];
        cube[234] = cube_tmp[230];
        cube[235] = cube_tmp[223];
        cube[236] = cube_tmp[216];
        cube[237] = cube_tmp[209];
        cube[238] = cube_tmp[202];
        cube[239] = cube_tmp[245];
        cube[240] = cube_tmp[238];
        cube[241] = cube_tmp[231];
        cube[242] = cube_tmp[224];
        cube[243] = cube_tmp[217];
        cube[244] = cube_tmp[210];
        cube[245] = cube_tmp[203];
        cube[281] = cube_tmp[51];
        cube[282] = cube_tmp[58];
        cube[283] = cube_tmp[65];
        cube[284] = cube_tmp[72];
        cube[285] = cube_tmp[79];
        cube[286] = cube_tmp[86];
        cube[287] = cube_tmp[93];
        cube[288] = cube_tmp[50];
        cube[289] = cube_tmp[57];
        cube[290] = cube_tmp[64];
        cube[291] = cube_tmp[71];
        cube[292] = cube_tmp[78];
        cube[293] = cube_tmp[85];
        cube[294] = cube_tmp[92];
        break;
    }

    case Bw_PRIME: {
        cube[1] = cube_tmp[92];
        cube[2] = cube_tmp[85];
        cube[3] = cube_tmp[78];
        cube[4] = cube_tmp[71];
        cube[5] = cube_tmp[64];
        cube[6] = cube_tmp[57];
        cube[7] = cube_tmp[50];
        cube[8] = cube_tmp[93];
        cube[9] = cube_tmp[86];
        cube[10] = cube_tmp[79];
        cube[11] = cube_tmp[72];
        cube[12] = cube_tmp[65];
        cube[13] = cube_tmp[58];
        cube[14] = cube_tmp[51];
        cube[50] = cube_tmp[288];
        cube[51] = cube_tmp[281];
        cube[57] = cube_tmp[289];
        cube[58] = cube_tmp[282];
        cube[64] = cube_tmp[290];
        cube[65] = cube_tmp[283];
        cube[71] = cube_tmp[291];
        cube[72] = cube_tmp[284];
        cube[78] = cube_tmp[292];
        cube[79] = cube_tmp[285];
        cube[85] = cube_tmp[293];
        cube[86] = cube_tmp[286];
        cube[92] = cube_tmp[294];
        cube[93] = cube_tmp[287];
        cube[153] = cube_tmp[8];
        cube[154] = cube_tmp[1];
        cube[160] = cube_tmp[9];
        cube[161] = cube_tmp[2];
        cube[167] = cube_tmp[10];
        cube[168] = cube_tmp[3];
        cube[174] = cube_tmp[11];
        cube[175] = cube_tmp[4];
        cube[181] = cube_tmp[12];
        cube[182] = cube_tmp[5];
        cube[188] = cube_tmp[13];
        cube[189] = cube_tmp[6];
        cube[195] = cube_tmp[14];
        cube[196] = cube_tmp[7];
        cube[197] = cube_tmp[203];
        cube[198] = cube_tmp[210];
        cube[199] = cube_tmp[217];
        cube[200] = cube_tmp[224];
        cube[201] = cube_tmp[231];
        cube[202] = cube_tmp[238];
        cube[203] = cube_tmp[245];
        cube[204] = cube_tmp[202];
        cube[205] = cube_tmp[209];
        cube[206] = cube_tmp[216];
        cube[207] = cube_tmp[223];
        cube[208] = cube_tmp[230];
        cube[209] = cube_tmp[237];
        cube[210] = cube_tmp[244];
        cube[211] = cube_tmp[201];
        cube[212] = cube_tmp[208];
        cube[213] = cube_tmp[215];
        cube[214] = cube_tmp[222];
        cube[215] = cube_tmp[229];
        cube[216] = cube_tmp[236];
        cube[217] = cube_tmp[243];
        cube[218] = cube_tmp[200];
        cube[219] = cube_tmp[207];
        cube[220] = cube_tmp[214];
        cube[222] = cube_tmp[228];
        cube[223] = cube_tmp[235];
        cube[224] = cube_tmp[242];
        cube[225] = cube_tmp[199];
        cube[226] = cube_tmp[206];
        cube[227] = cube_tmp[213];
        cube[228] = cube_tmp[220];
        cube[229] = cube_tmp[227];
        cube[230] = cube_tmp[234];
        cube[231] = cube_tmp[241];
        cube[232] = cube_tmp[198];
        cube[233] = cube_tmp[205];
        cube[234] = cube_tmp[212];
        cube[235] = cube_tmp[219];
        cube[236] = cube_tmp[226];
        cube[237] = cube_tmp[233];
        cube[238] = cube_tmp[240];
        cube[239] = cube_tmp[197];
        cube[240] = cube_tmp[204];
        cube[241] = cube_tmp[211];
        cube[242] = cube_tmp[218];
        cube[243] = cube_tmp[225];
        cube[244] = cube_tmp[232];
        cube[245] = cube_tmp[239];
        cube[281] = cube_tmp[195];
        cube[282] = cube_tmp[188];
        cube[283] = cube_tmp[181];
        cube[284] = cube_tmp[174];
        cube[285] = cube_tmp[167];
        cube[286] = cube_tmp[160];
        cube[287] = cube_tmp[153];
        cube[288] = cube_tmp[196];
        cube[289] = cube_tmp[189];
        cube[290] = cube_tmp[182];
        cube[291] = cube_tmp[175];
        cube[292] = cube_tmp[168];
        cube[293] = cube_tmp[161];
        cube[294] = cube_tmp[154];
        break;
    }

    case Bw2: {
        cube[1] = cube_tmp[294];
        cube[2] = cube_tmp[293];
        cube[3] = cube_tmp[292];
        cube[4] = cube_tmp[291];
        cube[5] = cube_tmp[290];
        cube[6] = cube_tmp[289];
        cube[7] = cube_tmp[288];
        cube[8] = cube_tmp[287];
        cube[9] = cube_tmp[286];
        cube[10] = cube_tmp[285];
        cube[11] = cube_tmp[284];
        cube[12] = cube_tmp[283];
        cube[13] = cube_tmp[282];
        cube[14] = cube_tmp[281];
        cube[50] = cube_tmp[196];
        cube[51] = cube_tmp[195];
        cube[57] = cube_tmp[189];
        cube[58] = cube_tmp[188];
        cube[64] = cube_tmp[182];
        cube[65] = cube_tmp[181];
        cube[71] = cube_tmp[175];
        cube[72] = cube_tmp[174];
        cube[78] = cube_tmp[168];
        cube[79] = cube_tmp[167];
        cube[85] = cube_tmp[161];
        cube[86] = cube_tmp[160];
        cube[92] = cube_tmp[154];
        cube[93] = cube_tmp[153];
        cube[153] = cube_tmp[93];
        cube[154] = cube_tmp[92];
        cube[160] = cube_tmp[86];
        cube[161] = cube_tmp[85];
        cube[167] = cube_tmp[79];
        cube[168] = cube_tmp[78];
        cube[174] = cube_tmp[72];
        cube[175] = cube_tmp[71];
        cube[181] = cube_tmp[65];
        cube[182] = cube_tmp[64];
        cube[188] = cube_tmp[58];
        cube[189] = cube_tmp[57];
        cube[195] = cube_tmp[51];
        cube[196] = cube_tmp[50];
        cube[197] = cube_tmp[245];
        cube[198] = cube_tmp[244];
        cube[199] = cube_tmp[243];
        cube[200] = cube_tmp[242];
        cube[201] = cube_tmp[241];
        cube[202] = cube_tmp[240];
        cube[203] = cube_tmp[239];
        cube[204] = cube_tmp[238];
        cube[205] = cube_tmp[237];
        cube[206] = cube_tmp[236];
        cube[207] = cube_tmp[235];
        cube[208] = cube_tmp[234];
        cube[209] = cube_tmp[233];
        cube[210] = cube_tmp[232];
        cube[211] = cube_tmp[231];
        cube[212] = cube_tmp[230];
        cube[213] = cube_tmp[229];
        cube[214] = cube_tmp[228];
        cube[215] = cube_tmp[227];
        cube[216] = cube_tmp[226];
        cube[217] = cube_tmp[225];
        cube[218] = cube_tmp[224];
        cube[219] = cube_tmp[223];
        cube[220] = cube_tmp[222];
        cube[222] = cube_tmp[220];
        cube[223] = cube_tmp[219];
        cube[224] = cube_tmp[218];
        cube[225] = cube_tmp[217];
        cube[226] = cube_tmp[216];
        cube[227] = cube_tmp[215];
        cube[228] = cube_tmp[214];
        cube[229] = cube_tmp[213];
        cube[230] = cube_tmp[212];
        cube[231] = cube_tmp[211];
        cube[232] = cube_tmp[210];
        cube[233] = cube_tmp[209];
        cube[234] = cube_tmp[208];
        cube[235] = cube_tmp[207];
        cube[236] = cube_tmp[206];
        cube[237] = cube_tmp[205];
        cube[238] = cube_tmp[204];
        cube[239] = cube_tmp[203];
        cube[240] = cube_tmp[202];
        cube[241] = cube_tmp[201];
        cube[242] = cube_tmp[200];
        cube[243] = cube_tmp[199];
        cube[244] = cube_tmp[198];
        cube[245] = cube_tmp[197];
        cube[281] = cube_tmp[14];
        cube[282] = cube_tmp[13];
        cube[283] = cube_tmp[12];
        cube[284] = cube_tmp[11];
        cube[285] = cube_tmp[10];
        cube[286] = cube_tmp[9];
        cube[287] = cube_tmp[8];
        cube[288] = cube_tmp[7];
        cube[289] = cube_tmp[6];
        cube[290] = cube_tmp[5];
        cube[291] = cube_tmp[4];
        cube[292] = cube_tmp[3];
        cube[293] = cube_tmp[2];
        cube[294] = cube_tmp[1];
        break;
    }

    case threeBw: {
        cube[1] = cube_tmp[154];
        cube[2] = cube_tmp[161];
        cube[3] = cube_tmp[168];
        cube[4] = cube_tmp[175];
        cube[5] = cube_tmp[182];
        cube[6] = cube_tmp[189];
        cube[7] = cube_tmp[196];
        cube[8] = cube_tmp[153];
        cube[9] = cube_tmp[160];
        cube[10] = cube_tmp[167];
        cube[11] = cube_tmp[174];
        cube[12] = cube_tmp[181];
        cube[13] = cube_tmp[188];
        cube[14] = cube_tmp[195];
        cube[15] = cube_tmp[152];
        cube[16] = cube_tmp[159];
        cube[17] = cube_tmp[166];
        cube[18] = cube_tmp[173];
        cube[19] = cube_tmp[180];
        cube[20] = cube_tmp[187];
        cube[21] = cube_tmp[194];
        cube[50] = cube_tmp[7];
        cube[51] = cube_tmp[14];
        cube[52] = cube_tmp[21];
        cube[57] = cube_tmp[6];
        cube[58] = cube_tmp[13];
        cube[59] = cube_tmp[20];
        cube[64] = cube_tmp[5];
        cube[65] = cube_tmp[12];
        cube[66] = cube_tmp[19];
        cube[71] = cube_tmp[4];
        cube[72] = cube_tmp[11];
        cube[73] = cube_tmp[18];
        cube[78] = cube_tmp[3];
        cube[79] = cube_tmp[10];
        cube[80] = cube_tmp[17];
        cube[85] = cube_tmp[2];
        cube[86] = cube_tmp[9];
        cube[87] = cube_tmp[16];
        cube[92] = cube_tmp[1];
        cube[93] = cube_tmp[8];
        cube[94] = cube_tmp[15];
        cube[152] = cube_tmp[280];
        cube[153] = cube_tmp[287];
        cube[154] = cube_tmp[294];
        cube[159] = cube_tmp[279];
        cube[160] = cube_tmp[286];
        cube[161] = cube_tmp[293];
        cube[166] = cube_tmp[278];
        cube[167] = cube_tmp[285];
        cube[168] = cube_tmp[292];
        cube[173] = cube_tmp[277];
        cube[174] = cube_tmp[284];
        cube[175] = cube_tmp[291];
        cube[180] = cube_tmp[276];
        cube[181] = cube_tmp[283];
        cube[182] = cube_tmp[290];
        cube[187] = cube_tmp[275];
        cube[188] = cube_tmp[282];
        cube[189] = cube_tmp[289];
        cube[194] = cube_tmp[274];
        cube[195] = cube_tmp[281];
        cube[196] = cube_tmp[288];
        cube[197] = cube_tmp[239];
        cube[198] = cube_tmp[232];
        cube[199] = cube_tmp[225];
        cube[200] = cube_tmp[218];
        cube[201] = cube_tmp[211];
        cube[202] = cube_tmp[204];
        cube[203] = cube_tmp[197];
        cube[204] = cube_tmp[240];
        cube[205] = cube_tmp[233];
        cube[206] = cube_tmp[226];
        cube[207] = cube_tmp[219];
        cube[208] = cube_tmp[212];
        cube[209] = cube_tmp[205];
        cube[210] = cube_tmp[198];
        cube[211] = cube_tmp[241];
        cube[212] = cube_tmp[234];
        cube[213] = cube_tmp[227];
        cube[214] = cube_tmp[220];
        cube[215] = cube_tmp[213];
        cube[216] = cube_tmp[206];
        cube[217] = cube_tmp[199];
        cube[218] = cube_tmp[242];
        cube[219] = cube_tmp[235];
        cube[220] = cube_tmp[228];
        cube[222] = cube_tmp[214];
        cube[223] = cube_tmp[207];
        cube[224] = cube_tmp[200];
        cube[225] = cube_tmp[243];
        cube[226] = cube_tmp[236];
        cube[227] = cube_tmp[229];
        cube[228] = cube_tmp[222];
        cube[229] = cube_tmp[215];
        cube[230] = cube_tmp[208];
        cube[231] = cube_tmp[201];
        cube[232] = cube_tmp[244];
        cube[233] = cube_tmp[237];
        cube[234] = cube_tmp[230];
        cube[235] = cube_tmp[223];
        cube[236] = cube_tmp[216];
        cube[237] = cube_tmp[209];
        cube[238] = cube_tmp[202];
        cube[239] = cube_tmp[245];
        cube[240] = cube_tmp[238];
        cube[241] = cube_tmp[231];
        cube[242] = cube_tmp[224];
        cube[243] = cube_tmp[217];
        cube[244] = cube_tmp[210];
        cube[245] = cube_tmp[203];
        cube[274] = cube_tmp[52];
        cube[275] = cube_tmp[59];
        cube[276] = cube_tmp[66];
        cube[277] = cube_tmp[73];
        cube[278] = cube_tmp[80];
        cube[279] = cube_tmp[87];
        cube[280] = cube_tmp[94];
        cube[281] = cube_tmp[51];
        cube[282] = cube_tmp[58];
        cube[283] = cube_tmp[65];
        cube[284] = cube_tmp[72];
        cube[285] = cube_tmp[79];
        cube[286] = cube_tmp[86];
        cube[287] = cube_tmp[93];
        cube[288] = cube_tmp[50];
        cube[289] = cube_tmp[57];
        cube[290] = cube_tmp[64];
        cube[291] = cube_tmp[71];
        cube[292] = cube_tmp[78];
        cube[293] = cube_tmp[85];
        cube[294] = cube_tmp[92];
        break;
    }

    case threeBw_PRIME: {
        cube[1] = cube_tmp[92];
        cube[2] = cube_tmp[85];
        cube[3] = cube_tmp[78];
        cube[4] = cube_tmp[71];
        cube[5] = cube_tmp[64];
        cube[6] = cube_tmp[57];
        cube[7] = cube_tmp[50];
        cube[8] = cube_tmp[93];
        cube[9] = cube_tmp[86];
        cube[10] = cube_tmp[79];
        cube[11] = cube_tmp[72];
        cube[12] = cube_tmp[65];
        cube[13] = cube_tmp[58];
        cube[14] = cube_tmp[51];
        cube[15] = cube_tmp[94];
        cube[16] = cube_tmp[87];
        cube[17] = cube_tmp[80];
        cube[18] = cube_tmp[73];
        cube[19] = cube_tmp[66];
        cube[20] = cube_tmp[59];
        cube[21] = cube_tmp[52];
        cube[50] = cube_tmp[288];
        cube[51] = cube_tmp[281];
        cube[52] = cube_tmp[274];
        cube[57] = cube_tmp[289];
        cube[58] = cube_tmp[282];
        cube[59] = cube_tmp[275];
        cube[64] = cube_tmp[290];
        cube[65] = cube_tmp[283];
        cube[66] = cube_tmp[276];
        cube[71] = cube_tmp[291];
        cube[72] = cube_tmp[284];
        cube[73] = cube_tmp[277];
        cube[78] = cube_tmp[292];
        cube[79] = cube_tmp[285];
        cube[80] = cube_tmp[278];
        cube[85] = cube_tmp[293];
        cube[86] = cube_tmp[286];
        cube[87] = cube_tmp[279];
        cube[92] = cube_tmp[294];
        cube[93] = cube_tmp[287];
        cube[94] = cube_tmp[280];
        cube[152] = cube_tmp[15];
        cube[153] = cube_tmp[8];
        cube[154] = cube_tmp[1];
        cube[159] = cube_tmp[16];
        cube[160] = cube_tmp[9];
        cube[161] = cube_tmp[2];
        cube[166] = cube_tmp[17];
        cube[167] = cube_tmp[10];
        cube[168] = cube_tmp[3];
        cube[173] = cube_tmp[18];
        cube[174] = cube_tmp[11];
        cube[175] = cube_tmp[4];
        cube[180] = cube_tmp[19];
        cube[181] = cube_tmp[12];
        cube[182] = cube_tmp[5];
        cube[187] = cube_tmp[20];
        cube[188] = cube_tmp[13];
        cube[189] = cube_tmp[6];
        cube[194] = cube_tmp[21];
        cube[195] = cube_tmp[14];
        cube[196] = cube_tmp[7];
        cube[197] = cube_tmp[203];
        cube[198] = cube_tmp[210];
        cube[199] = cube_tmp[217];
        cube[200] = cube_tmp[224];
        cube[201] = cube_tmp[231];
        cube[202] = cube_tmp[238];
        cube[203] = cube_tmp[245];
        cube[204] = cube_tmp[202];
        cube[205] = cube_tmp[209];
        cube[206] = cube_tmp[216];
        cube[207] = cube_tmp[223];
        cube[208] = cube_tmp[230];
        cube[209] = cube_tmp[237];
        cube[210] = cube_tmp[244];
        cube[211] = cube_tmp[201];
        cube[212] = cube_tmp[208];
        cube[213] = cube_tmp[215];
        cube[214] = cube_tmp[222];
        cube[215] = cube_tmp[229];
        cube[216] = cube_tmp[236];
        cube[217] = cube_tmp[243];
        cube[218] = cube_tmp[200];
        cube[219] = cube_tmp[207];
        cube[220] = cube_tmp[214];
        cube[222] = cube_tmp[228];
        cube[223] = cube_tmp[235];
        cube[224] = cube_tmp[242];
        cube[225] = cube_tmp[199];
        cube[226] = cube_tmp[206];
        cube[227] = cube_tmp[213];
        cube[228] = cube_tmp[220];
        cube[229] = cube_tmp[227];
        cube[230] = cube_tmp[234];
        cube[231] = cube_tmp[241];
        cube[232] = cube_tmp[198];
        cube[233] = cube_tmp[205];
        cube[234] = cube_tmp[212];
        cube[235] = cube_tmp[219];
        cube[236] = cube_tmp[226];
        cube[237] = cube_tmp[233];
        cube[238] = cube_tmp[240];
        cube[239] = cube_tmp[197];
        cube[240] = cube_tmp[204];
        cube[241] = cube_tmp[211];
        cube[242] = cube_tmp[218];
        cube[243] = cube_tmp[225];
        cube[244] = cube_tmp[232];
        cube[245] = cube_tmp[239];
        cube[274] = cube_tmp[194];
        cube[275] = cube_tmp[187];
        cube[276] = cube_tmp[180];
        cube[277] = cube_tmp[173];
        cube[278] = cube_tmp[166];
        cube[279] = cube_tmp[159];
        cube[280] = cube_tmp[152];
        cube[281] = cube_tmp[195];
        cube[282] = cube_tmp[188];
        cube[283] = cube_tmp[181];
        cube[284] = cube_tmp[174];
        cube[285] = cube_tmp[167];
        cube[286] = cube_tmp[160];
        cube[287] = cube_tmp[153];
        cube[288] = cube_tmp[196];
        cube[289] = cube_tmp[189];
        cube[290] = cube_tmp[182];
        cube[291] = cube_tmp[175];
        cube[292] = cube_tmp[168];
        cube[293] = cube_tmp[161];
        cube[294] = cube_tmp[154];
        break;
    }

    case threeBw2: {
        cube[1] = cube_tmp[294];
        cube[2] = cube_tmp[293];
        cube[3] = cube_tmp[292];
        cube[4] = cube_tmp[291];
        cube[5] = cube_tmp[290];
        cube[6] = cube_tmp[289];
        cube[7] = cube_tmp[288];
        cube[8] = cube_tmp[287];
        cube[9] = cube_tmp[286];
        cube[10] = cube_tmp[285];
        cube[11] = cube_tmp[284];
        cube[12] = cube_tmp[283];
        cube[13] = cube_tmp[282];
        cube[14] = cube_tmp[281];
        cube[15] = cube_tmp[280];
        cube[16] = cube_tmp[279];
        cube[17] = cube_tmp[278];
        cube[18] = cube_tmp[277];
        cube[19] = cube_tmp[276];
        cube[20] = cube_tmp[275];
        cube[21] = cube_tmp[274];
        cube[50] = cube_tmp[196];
        cube[51] = cube_tmp[195];
        cube[52] = cube_tmp[194];
        cube[57] = cube_tmp[189];
        cube[58] = cube_tmp[188];
        cube[59] = cube_tmp[187];
        cube[64] = cube_tmp[182];
        cube[65] = cube_tmp[181];
        cube[66] = cube_tmp[180];
        cube[71] = cube_tmp[175];
        cube[72] = cube_tmp[174];
        cube[73] = cube_tmp[173];
        cube[78] = cube_tmp[168];
        cube[79] = cube_tmp[167];
        cube[80] = cube_tmp[166];
        cube[85] = cube_tmp[161];
        cube[86] = cube_tmp[160];
        cube[87] = cube_tmp[159];
        cube[92] = cube_tmp[154];
        cube[93] = cube_tmp[153];
        cube[94] = cube_tmp[152];
        cube[152] = cube_tmp[94];
        cube[153] = cube_tmp[93];
        cube[154] = cube_tmp[92];
        cube[159] = cube_tmp[87];
        cube[160] = cube_tmp[86];
        cube[161] = cube_tmp[85];
        cube[166] = cube_tmp[80];
        cube[167] = cube_tmp[79];
        cube[168] = cube_tmp[78];
        cube[173] = cube_tmp[73];
        cube[174] = cube_tmp[72];
        cube[175] = cube_tmp[71];
        cube[180] = cube_tmp[66];
        cube[181] = cube_tmp[65];
        cube[182] = cube_tmp[64];
        cube[187] = cube_tmp[59];
        cube[188] = cube_tmp[58];
        cube[189] = cube_tmp[57];
        cube[194] = cube_tmp[52];
        cube[195] = cube_tmp[51];
        cube[196] = cube_tmp[50];
        cube[197] = cube_tmp[245];
        cube[198] = cube_tmp[244];
        cube[199] = cube_tmp[243];
        cube[200] = cube_tmp[242];
        cube[201] = cube_tmp[241];
        cube[202] = cube_tmp[240];
        cube[203] = cube_tmp[239];
        cube[204] = cube_tmp[238];
        cube[205] = cube_tmp[237];
        cube[206] = cube_tmp[236];
        cube[207] = cube_tmp[235];
        cube[208] = cube_tmp[234];
        cube[209] = cube_tmp[233];
        cube[210] = cube_tmp[232];
        cube[211] = cube_tmp[231];
        cube[212] = cube_tmp[230];
        cube[213] = cube_tmp[229];
        cube[214] = cube_tmp[228];
        cube[215] = cube_tmp[227];
        cube[216] = cube_tmp[226];
        cube[217] = cube_tmp[225];
        cube[218] = cube_tmp[224];
        cube[219] = cube_tmp[223];
        cube[220] = cube_tmp[222];
        cube[222] = cube_tmp[220];
        cube[223] = cube_tmp[219];
        cube[224] = cube_tmp[218];
        cube[225] = cube_tmp[217];
        cube[226] = cube_tmp[216];
        cube[227] = cube_tmp[215];
        cube[228] = cube_tmp[214];
        cube[229] = cube_tmp[213];
        cube[230] = cube_tmp[212];
        cube[231] = cube_tmp[211];
        cube[232] = cube_tmp[210];
        cube[233] = cube_tmp[209];
        cube[234] = cube_tmp[208];
        cube[235] = cube_tmp[207];
        cube[236] = cube_tmp[206];
        cube[237] = cube_tmp[205];
        cube[238] = cube_tmp[204];
        cube[239] = cube_tmp[203];
        cube[240] = cube_tmp[202];
        cube[241] = cube_tmp[201];
        cube[242] = cube_tmp[200];
        cube[243] = cube_tmp[199];
        cube[244] = cube_tmp[198];
        cube[245] = cube_tmp[197];
        cube[274] = cube_tmp[21];
        cube[275] = cube_tmp[20];
        cube[276] = cube_tmp[19];
        cube[277] = cube_tmp[18];
        cube[278] = cube_tmp[17];
        cube[279] = cube_tmp[16];
        cube[280] = cube_tmp[15];
        cube[281] = cube_tmp[14];
        cube[282] = cube_tmp[13];
        cube[283] = cube_tmp[12];
        cube[284] = cube_tmp[11];
        cube[285] = cube_tmp[10];
        cube[286] = cube_tmp[9];
        cube[287] = cube_tmp[8];
        cube[288] = cube_tmp[7];
        cube[289] = cube_tmp[6];
        cube[290] = cube_tmp[5];
        cube[291] = cube_tmp[4];
        cube[292] = cube_tmp[3];
        cube[293] = cube_tmp[2];
        cube[294] = cube_tmp[1];
        break;
    }

    case D: {
        cube[92] = cube_tmp[239];
        cube[93] = cube_tmp[240];
        cube[94] = cube_tmp[241];
        cube[95] = cube_tmp[242];
        cube[96] = cube_tmp[243];
        cube[97] = cube_tmp[244];
        cube[98] = cube_tmp[245];
        cube[141] = cube_tmp[92];
        cube[142] = cube_tmp[93];
        cube[143] = cube_tmp[94];
        cube[144] = cube_tmp[95];
        cube[145] = cube_tmp[96];
        cube[146] = cube_tmp[97];
        cube[147] = cube_tmp[98];
        cube[190] = cube_tmp[141];
        cube[191] = cube_tmp[142];
        cube[192] = cube_tmp[143];
        cube[193] = cube_tmp[144];
        cube[194] = cube_tmp[145];
        cube[195] = cube_tmp[146];
        cube[196] = cube_tmp[147];
        cube[239] = cube_tmp[190];
        cube[240] = cube_tmp[191];
        cube[241] = cube_tmp[192];
        cube[242] = cube_tmp[193];
        cube[243] = cube_tmp[194];
        cube[244] = cube_tmp[195];
        cube[245] = cube_tmp[196];
        cube[246] = cube_tmp[288];
        cube[247] = cube_tmp[281];
        cube[248] = cube_tmp[274];
        cube[249] = cube_tmp[267];
        cube[250] = cube_tmp[260];
        cube[251] = cube_tmp[253];
        cube[252] = cube_tmp[246];
        cube[253] = cube_tmp[289];
        cube[254] = cube_tmp[282];
        cube[255] = cube_tmp[275];
        cube[256] = cube_tmp[268];
        cube[257] = cube_tmp[261];
        cube[258] = cube_tmp[254];
        cube[259] = cube_tmp[247];
        cube[260] = cube_tmp[290];
        cube[261] = cube_tmp[283];
        cube[262] = cube_tmp[276];
        cube[263] = cube_tmp[269];
        cube[264] = cube_tmp[262];
        cube[265] = cube_tmp[255];
        cube[266] = cube_tmp[248];
        cube[267] = cube_tmp[291];
        cube[268] = cube_tmp[284];
        cube[269] = cube_tmp[277];
        cube[271] = cube_tmp[263];
        cube[272] = cube_tmp[256];
        cube[273] = cube_tmp[249];
        cube[274] = cube_tmp[292];
        cube[275] = cube_tmp[285];
        cube[276] = cube_tmp[278];
        cube[277] = cube_tmp[271];
        cube[278] = cube_tmp[264];
        cube[279] = cube_tmp[257];
        cube[280] = cube_tmp[250];
        cube[281] = cube_tmp[293];
        cube[282] = cube_tmp[286];
        cube[283] = cube_tmp[279];
        cube[284] = cube_tmp[272];
        cube[285] = cube_tmp[265];
        cube[286] = cube_tmp[258];
        cube[287] = cube_tmp[251];
        cube[288] = cube_tmp[294];
        cube[289] = cube_tmp[287];
        cube[290] = cube_tmp[280];
        cube[291] = cube_tmp[273];
        cube[292] = cube_tmp[266];
        cube[293] = cube_tmp[259];
        cube[294] = cube_tmp[252];
        break;
    }

    case D_PRIME: {
        cube[92] = cube_tmp[141];
        cube[93] = cube_tmp[142];
        cube[94] = cube_tmp[143];
        cube[95] = cube_tmp[144];
        cube[96] = cube_tmp[145];
        cube[97] = cube_tmp[146];
        cube[98] = cube_tmp[147];
        cube[141] = cube_tmp[190];
        cube[142] = cube_tmp[191];
        cube[143] = cube_tmp[192];
        cube[144] = cube_tmp[193];
        cube[145] = cube_tmp[194];
        cube[146] = cube_tmp[195];
        cube[147] = cube_tmp[196];
        cube[190] = cube_tmp[239];
        cube[191] = cube_tmp[240];
        cube[192] = cube_tmp[241];
        cube[193] = cube_tmp[242];
        cube[194] = cube_tmp[243];
        cube[195] = cube_tmp[244];
        cube[196] = cube_tmp[245];
        cube[239] = cube_tmp[92];
        cube[240] = cube_tmp[93];
        cube[241] = cube_tmp[94];
        cube[242] = cube_tmp[95];
        cube[243] = cube_tmp[96];
        cube[244] = cube_tmp[97];
        cube[245] = cube_tmp[98];
        cube[246] = cube_tmp[252];
        cube[247] = cube_tmp[259];
        cube[248] = cube_tmp[266];
        cube[249] = cube_tmp[273];
        cube[250] = cube_tmp[280];
        cube[251] = cube_tmp[287];
        cube[252] = cube_tmp[294];
        cube[253] = cube_tmp[251];
        cube[254] = cube_tmp[258];
        cube[255] = cube_tmp[265];
        cube[256] = cube_tmp[272];
        cube[257] = cube_tmp[279];
        cube[258] = cube_tmp[286];
        cube[259] = cube_tmp[293];
        cube[260] = cube_tmp[250];
        cube[261] = cube_tmp[257];
        cube[262] = cube_tmp[264];
        cube[263] = cube_tmp[271];
        cube[264] = cube_tmp[278];
        cube[265] = cube_tmp[285];
        cube[266] = cube_tmp[292];
        cube[267] = cube_tmp[249];
        cube[268] = cube_tmp[256];
        cube[269] = cube_tmp[263];
        cube[271] = cube_tmp[277];
        cube[272] = cube_tmp[284];
        cube[273] = cube_tmp[291];
        cube[274] = cube_tmp[248];
        cube[275] = cube_tmp[255];
        cube[276] = cube_tmp[262];
        cube[277] = cube_tmp[269];
        cube[278] = cube_tmp[276];
        cube[279] = cube_tmp[283];
        cube[280] = cube_tmp[290];
        cube[281] = cube_tmp[247];
        cube[282] = cube_tmp[254];
        cube[283] = cube_tmp[261];
        cube[284] = cube_tmp[268];
        cube[285] = cube_tmp[275];
        cube[286] = cube_tmp[282];
        cube[287] = cube_tmp[289];
        cube[288] = cube_tmp[246];
        cube[289] = cube_tmp[253];
        cube[290] = cube_tmp[260];
        cube[291] = cube_tmp[267];
        cube[292] = cube_tmp[274];
        cube[293] = cube_tmp[281];
        cube[294] = cube_tmp[288];
        break;
    }

    case D2: {
        cube[92] = cube_tmp[190];
        cube[93] = cube_tmp[191];
        cube[94] = cube_tmp[192];
        cube[95] = cube_tmp[193];
        cube[96] = cube_tmp[194];
        cube[97] = cube_tmp[195];
        cube[98] = cube_tmp[196];
        cube[141] = cube_tmp[239];
        cube[142] = cube_tmp[240];
        cube[143] = cube_tmp[241];
        cube[144] = cube_tmp[242];
        cube[145] = cube_tmp[243];
        cube[146] = cube_tmp[244];
        cube[147] = cube_tmp[245];
        cube[190] = cube_tmp[92];
        cube[191] = cube_tmp[93];
        cube[192] = cube_tmp[94];
        cube[193] = cube_tmp[95];
        cube[194] = cube_tmp[96];
        cube[195] = cube_tmp[97];
        cube[196] = cube_tmp[98];
        cube[239] = cube_tmp[141];
        cube[240] = cube_tmp[142];
        cube[241] = cube_tmp[143];
        cube[242] = cube_tmp[144];
        cube[243] = cube_tmp[145];
        cube[244] = cube_tmp[146];
        cube[245] = cube_tmp[147];
        cube[246] = cube_tmp[294];
        cube[247] = cube_tmp[293];
        cube[248] = cube_tmp[292];
        cube[249] = cube_tmp[291];
        cube[250] = cube_tmp[290];
        cube[251] = cube_tmp[289];
        cube[252] = cube_tmp[288];
        cube[253] = cube_tmp[287];
        cube[254] = cube_tmp[286];
        cube[255] = cube_tmp[285];
        cube[256] = cube_tmp[284];
        cube[257] = cube_tmp[283];
        cube[258] = cube_tmp[282];
        cube[259] = cube_tmp[281];
        cube[260] = cube_tmp[280];
        cube[261] = cube_tmp[279];
        cube[262] = cube_tmp[278];
        cube[263] = cube_tmp[277];
        cube[264] = cube_tmp[276];
        cube[265] = cube_tmp[275];
        cube[266] = cube_tmp[274];
        cube[267] = cube_tmp[273];
        cube[268] = cube_tmp[272];
        cube[269] = cube_tmp[271];
        cube[271] = cube_tmp[269];
        cube[272] = cube_tmp[268];
        cube[273] = cube_tmp[267];
        cube[274] = cube_tmp[266];
        cube[275] = cube_tmp[265];
        cube[276] = cube_tmp[264];
        cube[277] = cube_tmp[263];
        cube[278] = cube_tmp[262];
        cube[279] = cube_tmp[261];
        cube[280] = cube_tmp[260];
        cube[281] = cube_tmp[259];
        cube[282] = cube_tmp[258];
        cube[283] = cube_tmp[257];
        cube[284] = cube_tmp[256];
        cube[285] = cube_tmp[255];
        cube[286] = cube_tmp[254];
        cube[287] = cube_tmp[253];
        cube[288] = cube_tmp[252];
        cube[289] = cube_tmp[251];
        cube[290] = cube_tmp[250];
        cube[291] = cube_tmp[249];
        cube[292] = cube_tmp[248];
        cube[293] = cube_tmp[247];
        cube[294] = cube_tmp[246];
        break;
    }

    case Dw: {
        cube[85] = cube_tmp[232];
        cube[86] = cube_tmp[233];
        cube[87] = cube_tmp[234];
        cube[88] = cube_tmp[235];
        cube[89] = cube_tmp[236];
        cube[90] = cube_tmp[237];
        cube[91] = cube_tmp[238];
        cube[92] = cube_tmp[239];
        cube[93] = cube_tmp[240];
        cube[94] = cube_tmp[241];
        cube[95] = cube_tmp[242];
        cube[96] = cube_tmp[243];
        cube[97] = cube_tmp[244];
        cube[98] = cube_tmp[245];
        cube[134] = cube_tmp[85];
        cube[135] = cube_tmp[86];
        cube[136] = cube_tmp[87];
        cube[137] = cube_tmp[88];
        cube[138] = cube_tmp[89];
        cube[139] = cube_tmp[90];
        cube[140] = cube_tmp[91];
        cube[141] = cube_tmp[92];
        cube[142] = cube_tmp[93];
        cube[143] = cube_tmp[94];
        cube[144] = cube_tmp[95];
        cube[145] = cube_tmp[96];
        cube[146] = cube_tmp[97];
        cube[147] = cube_tmp[98];
        cube[183] = cube_tmp[134];
        cube[184] = cube_tmp[135];
        cube[185] = cube_tmp[136];
        cube[186] = cube_tmp[137];
        cube[187] = cube_tmp[138];
        cube[188] = cube_tmp[139];
        cube[189] = cube_tmp[140];
        cube[190] = cube_tmp[141];
        cube[191] = cube_tmp[142];
        cube[192] = cube_tmp[143];
        cube[193] = cube_tmp[144];
        cube[194] = cube_tmp[145];
        cube[195] = cube_tmp[146];
        cube[196] = cube_tmp[147];
        cube[232] = cube_tmp[183];
        cube[233] = cube_tmp[184];
        cube[234] = cube_tmp[185];
        cube[235] = cube_tmp[186];
        cube[236] = cube_tmp[187];
        cube[237] = cube_tmp[188];
        cube[238] = cube_tmp[189];
        cube[239] = cube_tmp[190];
        cube[240] = cube_tmp[191];
        cube[241] = cube_tmp[192];
        cube[242] = cube_tmp[193];
        cube[243] = cube_tmp[194];
        cube[244] = cube_tmp[195];
        cube[245] = cube_tmp[196];
        cube[246] = cube_tmp[288];
        cube[247] = cube_tmp[281];
        cube[248] = cube_tmp[274];
        cube[249] = cube_tmp[267];
        cube[250] = cube_tmp[260];
        cube[251] = cube_tmp[253];
        cube[252] = cube_tmp[246];
        cube[253] = cube_tmp[289];
        cube[254] = cube_tmp[282];
        cube[255] = cube_tmp[275];
        cube[256] = cube_tmp[268];
        cube[257] = cube_tmp[261];
        cube[258] = cube_tmp[254];
        cube[259] = cube_tmp[247];
        cube[260] = cube_tmp[290];
        cube[261] = cube_tmp[283];
        cube[262] = cube_tmp[276];
        cube[263] = cube_tmp[269];
        cube[264] = cube_tmp[262];
        cube[265] = cube_tmp[255];
        cube[266] = cube_tmp[248];
        cube[267] = cube_tmp[291];
        cube[268] = cube_tmp[284];
        cube[269] = cube_tmp[277];
        cube[271] = cube_tmp[263];
        cube[272] = cube_tmp[256];
        cube[273] = cube_tmp[249];
        cube[274] = cube_tmp[292];
        cube[275] = cube_tmp[285];
        cube[276] = cube_tmp[278];
        cube[277] = cube_tmp[271];
        cube[278] = cube_tmp[264];
        cube[279] = cube_tmp[257];
        cube[280] = cube_tmp[250];
        cube[281] = cube_tmp[293];
        cube[282] = cube_tmp[286];
        cube[283] = cube_tmp[279];
        cube[284] = cube_tmp[272];
        cube[285] = cube_tmp[265];
        cube[286] = cube_tmp[258];
        cube[287] = cube_tmp[251];
        cube[288] = cube_tmp[294];
        cube[289] = cube_tmp[287];
        cube[290] = cube_tmp[280];
        cube[291] = cube_tmp[273];
        cube[292] = cube_tmp[266];
        cube[293] = cube_tmp[259];
        cube[294] = cube_tmp[252];
        break;
    }

    case Dw_PRIME: {
        cube[85] = cube_tmp[134];
        cube[86] = cube_tmp[135];
        cube[87] = cube_tmp[136];
        cube[88] = cube_tmp[137];
        cube[89] = cube_tmp[138];
        cube[90] = cube_tmp[139];
        cube[91] = cube_tmp[140];
        cube[92] = cube_tmp[141];
        cube[93] = cube_tmp[142];
        cube[94] = cube_tmp[143];
        cube[95] = cube_tmp[144];
        cube[96] = cube_tmp[145];
        cube[97] = cube_tmp[146];
        cube[98] = cube_tmp[147];
        cube[134] = cube_tmp[183];
        cube[135] = cube_tmp[184];
        cube[136] = cube_tmp[185];
        cube[137] = cube_tmp[186];
        cube[138] = cube_tmp[187];
        cube[139] = cube_tmp[188];
        cube[140] = cube_tmp[189];
        cube[141] = cube_tmp[190];
        cube[142] = cube_tmp[191];
        cube[143] = cube_tmp[192];
        cube[144] = cube_tmp[193];
        cube[145] = cube_tmp[194];
        cube[146] = cube_tmp[195];
        cube[147] = cube_tmp[196];
        cube[183] = cube_tmp[232];
        cube[184] = cube_tmp[233];
        cube[185] = cube_tmp[234];
        cube[186] = cube_tmp[235];
        cube[187] = cube_tmp[236];
        cube[188] = cube_tmp[237];
        cube[189] = cube_tmp[238];
        cube[190] = cube_tmp[239];
        cube[191] = cube_tmp[240];
        cube[192] = cube_tmp[241];
        cube[193] = cube_tmp[242];
        cube[194] = cube_tmp[243];
        cube[195] = cube_tmp[244];
        cube[196] = cube_tmp[245];
        cube[232] = cube_tmp[85];
        cube[233] = cube_tmp[86];
        cube[234] = cube_tmp[87];
        cube[235] = cube_tmp[88];
        cube[236] = cube_tmp[89];
        cube[237] = cube_tmp[90];
        cube[238] = cube_tmp[91];
        cube[239] = cube_tmp[92];
        cube[240] = cube_tmp[93];
        cube[241] = cube_tmp[94];
        cube[242] = cube_tmp[95];
        cube[243] = cube_tmp[96];
        cube[244] = cube_tmp[97];
        cube[245] = cube_tmp[98];
        cube[246] = cube_tmp[252];
        cube[247] = cube_tmp[259];
        cube[248] = cube_tmp[266];
        cube[249] = cube_tmp[273];
        cube[250] = cube_tmp[280];
        cube[251] = cube_tmp[287];
        cube[252] = cube_tmp[294];
        cube[253] = cube_tmp[251];
        cube[254] = cube_tmp[258];
        cube[255] = cube_tmp[265];
        cube[256] = cube_tmp[272];
        cube[257] = cube_tmp[279];
        cube[258] = cube_tmp[286];
        cube[259] = cube_tmp[293];
        cube[260] = cube_tmp[250];
        cube[261] = cube_tmp[257];
        cube[262] = cube_tmp[264];
        cube[263] = cube_tmp[271];
        cube[264] = cube_tmp[278];
        cube[265] = cube_tmp[285];
        cube[266] = cube_tmp[292];
        cube[267] = cube_tmp[249];
        cube[268] = cube_tmp[256];
        cube[269] = cube_tmp[263];
        cube[271] = cube_tmp[277];
        cube[272] = cube_tmp[284];
        cube[273] = cube_tmp[291];
        cube[274] = cube_tmp[248];
        cube[275] = cube_tmp[255];
        cube[276] = cube_tmp[262];
        cube[277] = cube_tmp[269];
        cube[278] = cube_tmp[276];
        cube[279] = cube_tmp[283];
        cube[280] = cube_tmp[290];
        cube[281] = cube_tmp[247];
        cube[282] = cube_tmp[254];
        cube[283] = cube_tmp[261];
        cube[284] = cube_tmp[268];
        cube[285] = cube_tmp[275];
        cube[286] = cube_tmp[282];
        cube[287] = cube_tmp[289];
        cube[288] = cube_tmp[246];
        cube[289] = cube_tmp[253];
        cube[290] = cube_tmp[260];
        cube[291] = cube_tmp[267];
        cube[292] = cube_tmp[274];
        cube[293] = cube_tmp[281];
        cube[294] = cube_tmp[288];
        break;
    }

    case Dw2: {
        cube[85] = cube_tmp[183];
        cube[86] = cube_tmp[184];
        cube[87] = cube_tmp[185];
        cube[88] = cube_tmp[186];
        cube[89] = cube_tmp[187];
        cube[90] = cube_tmp[188];
        cube[91] = cube_tmp[189];
        cube[92] = cube_tmp[190];
        cube[93] = cube_tmp[191];
        cube[94] = cube_tmp[192];
        cube[95] = cube_tmp[193];
        cube[96] = cube_tmp[194];
        cube[97] = cube_tmp[195];
        cube[98] = cube_tmp[196];
        cube[134] = cube_tmp[232];
        cube[135] = cube_tmp[233];
        cube[136] = cube_tmp[234];
        cube[137] = cube_tmp[235];
        cube[138] = cube_tmp[236];
        cube[139] = cube_tmp[237];
        cube[140] = cube_tmp[238];
        cube[141] = cube_tmp[239];
        cube[142] = cube_tmp[240];
        cube[143] = cube_tmp[241];
        cube[144] = cube_tmp[242];
        cube[145] = cube_tmp[243];
        cube[146] = cube_tmp[244];
        cube[147] = cube_tmp[245];
        cube[183] = cube_tmp[85];
        cube[184] = cube_tmp[86];
        cube[185] = cube_tmp[87];
        cube[186] = cube_tmp[88];
        cube[187] = cube_tmp[89];
        cube[188] = cube_tmp[90];
        cube[189] = cube_tmp[91];
        cube[190] = cube_tmp[92];
        cube[191] = cube_tmp[93];
        cube[192] = cube_tmp[94];
        cube[193] = cube_tmp[95];
        cube[194] = cube_tmp[96];
        cube[195] = cube_tmp[97];
        cube[196] = cube_tmp[98];
        cube[232] = cube_tmp[134];
        cube[233] = cube_tmp[135];
        cube[234] = cube_tmp[136];
        cube[235] = cube_tmp[137];
        cube[236] = cube_tmp[138];
        cube[237] = cube_tmp[139];
        cube[238] = cube_tmp[140];
        cube[239] = cube_tmp[141];
        cube[240] = cube_tmp[142];
        cube[241] = cube_tmp[143];
        cube[242] = cube_tmp[144];
        cube[243] = cube_tmp[145];
        cube[244] = cube_tmp[146];
        cube[245] = cube_tmp[147];
        cube[246] = cube_tmp[294];
        cube[247] = cube_tmp[293];
        cube[248] = cube_tmp[292];
        cube[249] = cube_tmp[291];
        cube[250] = cube_tmp[290];
        cube[251] = cube_tmp[289];
        cube[252] = cube_tmp[288];
        cube[253] = cube_tmp[287];
        cube[254] = cube_tmp[286];
        cube[255] = cube_tmp[285];
        cube[256] = cube_tmp[284];
        cube[257] = cube_tmp[283];
        cube[258] = cube_tmp[282];
        cube[259] = cube_tmp[281];
        cube[260] = cube_tmp[280];
        cube[261] = cube_tmp[279];
        cube[262] = cube_tmp[278];
        cube[263] = cube_tmp[277];
        cube[264] = cube_tmp[276];
        cube[265] = cube_tmp[275];
        cube[266] = cube_tmp[274];
        cube[267] = cube_tmp[273];
        cube[268] = cube_tmp[272];
        cube[269] = cube_tmp[271];
        cube[271] = cube_tmp[269];
        cube[272] = cube_tmp[268];
        cube[273] = cube_tmp[267];
        cube[274] = cube_tmp[266];
        cube[275] = cube_tmp[265];
        cube[276] = cube_tmp[264];
        cube[277] = cube_tmp[263];
        cube[278] = cube_tmp[262];
        cube[279] = cube_tmp[261];
        cube[280] = cube_tmp[260];
        cube[281] = cube_tmp[259];
        cube[282] = cube_tmp[258];
        cube[283] = cube_tmp[257];
        cube[284] = cube_tmp[256];
        cube[285] = cube_tmp[255];
        cube[286] = cube_tmp[254];
        cube[287] = cube_tmp[253];
        cube[288] = cube_tmp[252];
        cube[289] = cube_tmp[251];
        cube[290] = cube_tmp[250];
        cube[291] = cube_tmp[249];
        cube[292] = cube_tmp[248];
        cube[293] = cube_tmp[247];
        cube[294] = cube_tmp[246];
        break;
    }

    case threeDw: {
        cube[78] = cube_tmp[225];
        cube[79] = cube_tmp[226];
        cube[80] = cube_tmp[227];
        cube[81] = cube_tmp[228];
        cube[82] = cube_tmp[229];
        cube[83] = cube_tmp[230];
        cube[84] = cube_tmp[231];
        cube[85] = cube_tmp[232];
        cube[86] = cube_tmp[233];
        cube[87] = cube_tmp[234];
        cube[88] = cube_tmp[235];
        cube[89] = cube_tmp[236];
        cube[90] = cube_tmp[237];
        cube[91] = cube_tmp[238];
        cube[92] = cube_tmp[239];
        cube[93] = cube_tmp[240];
        cube[94] = cube_tmp[241];
        cube[95] = cube_tmp[242];
        cube[96] = cube_tmp[243];
        cube[97] = cube_tmp[244];
        cube[98] = cube_tmp[245];
        cube[127] = cube_tmp[78];
        cube[128] = cube_tmp[79];
        cube[129] = cube_tmp[80];
        cube[130] = cube_tmp[81];
        cube[131] = cube_tmp[82];
        cube[132] = cube_tmp[83];
        cube[133] = cube_tmp[84];
        cube[134] = cube_tmp[85];
        cube[135] = cube_tmp[86];
        cube[136] = cube_tmp[87];
        cube[137] = cube_tmp[88];
        cube[138] = cube_tmp[89];
        cube[139] = cube_tmp[90];
        cube[140] = cube_tmp[91];
        cube[141] = cube_tmp[92];
        cube[142] = cube_tmp[93];
        cube[143] = cube_tmp[94];
        cube[144] = cube_tmp[95];
        cube[145] = cube_tmp[96];
        cube[146] = cube_tmp[97];
        cube[147] = cube_tmp[98];
        cube[176] = cube_tmp[127];
        cube[177] = cube_tmp[128];
        cube[178] = cube_tmp[129];
        cube[179] = cube_tmp[130];
        cube[180] = cube_tmp[131];
        cube[181] = cube_tmp[132];
        cube[182] = cube_tmp[133];
        cube[183] = cube_tmp[134];
        cube[184] = cube_tmp[135];
        cube[185] = cube_tmp[136];
        cube[186] = cube_tmp[137];
        cube[187] = cube_tmp[138];
        cube[188] = cube_tmp[139];
        cube[189] = cube_tmp[140];
        cube[190] = cube_tmp[141];
        cube[191] = cube_tmp[142];
        cube[192] = cube_tmp[143];
        cube[193] = cube_tmp[144];
        cube[194] = cube_tmp[145];
        cube[195] = cube_tmp[146];
        cube[196] = cube_tmp[147];
        cube[225] = cube_tmp[176];
        cube[226] = cube_tmp[177];
        cube[227] = cube_tmp[178];
        cube[228] = cube_tmp[179];
        cube[229] = cube_tmp[180];
        cube[230] = cube_tmp[181];
        cube[231] = cube_tmp[182];
        cube[232] = cube_tmp[183];
        cube[233] = cube_tmp[184];
        cube[234] = cube_tmp[185];
        cube[235] = cube_tmp[186];
        cube[236] = cube_tmp[187];
        cube[237] = cube_tmp[188];
        cube[238] = cube_tmp[189];
        cube[239] = cube_tmp[190];
        cube[240] = cube_tmp[191];
        cube[241] = cube_tmp[192];
        cube[242] = cube_tmp[193];
        cube[243] = cube_tmp[194];
        cube[244] = cube_tmp[195];
        cube[245] = cube_tmp[196];
        cube[246] = cube_tmp[288];
        cube[247] = cube_tmp[281];
        cube[248] = cube_tmp[274];
        cube[249] = cube_tmp[267];
        cube[250] = cube_tmp[260];
        cube[251] = cube_tmp[253];
        cube[252] = cube_tmp[246];
        cube[253] = cube_tmp[289];
        cube[254] = cube_tmp[282];
        cube[255] = cube_tmp[275];
        cube[256] = cube_tmp[268];
        cube[257] = cube_tmp[261];
        cube[258] = cube_tmp[254];
        cube[259] = cube_tmp[247];
        cube[260] = cube_tmp[290];
        cube[261] = cube_tmp[283];
        cube[262] = cube_tmp[276];
        cube[263] = cube_tmp[269];
        cube[264] = cube_tmp[262];
        cube[265] = cube_tmp[255];
        cube[266] = cube_tmp[248];
        cube[267] = cube_tmp[291];
        cube[268] = cube_tmp[284];
        cube[269] = cube_tmp[277];
        cube[271] = cube_tmp[263];
        cube[272] = cube_tmp[256];
        cube[273] = cube_tmp[249];
        cube[274] = cube_tmp[292];
        cube[275] = cube_tmp[285];
        cube[276] = cube_tmp[278];
        cube[277] = cube_tmp[271];
        cube[278] = cube_tmp[264];
        cube[279] = cube_tmp[257];
        cube[280] = cube_tmp[250];
        cube[281] = cube_tmp[293];
        cube[282] = cube_tmp[286];
        cube[283] = cube_tmp[279];
        cube[284] = cube_tmp[272];
        cube[285] = cube_tmp[265];
        cube[286] = cube_tmp[258];
        cube[287] = cube_tmp[251];
        cube[288] = cube_tmp[294];
        cube[289] = cube_tmp[287];
        cube[290] = cube_tmp[280];
        cube[291] = cube_tmp[273];
        cube[292] = cube_tmp[266];
        cube[293] = cube_tmp[259];
        cube[294] = cube_tmp[252];
        break;
    }

    case threeDw_PRIME: {
        cube[78] = cube_tmp[127];
        cube[79] = cube_tmp[128];
        cube[80] = cube_tmp[129];
        cube[81] = cube_tmp[130];
        cube[82] = cube_tmp[131];
        cube[83] = cube_tmp[132];
        cube[84] = cube_tmp[133];
        cube[85] = cube_tmp[134];
        cube[86] = cube_tmp[135];
        cube[87] = cube_tmp[136];
        cube[88] = cube_tmp[137];
        cube[89] = cube_tmp[138];
        cube[90] = cube_tmp[139];
        cube[91] = cube_tmp[140];
        cube[92] = cube_tmp[141];
        cube[93] = cube_tmp[142];
        cube[94] = cube_tmp[143];
        cube[95] = cube_tmp[144];
        cube[96] = cube_tmp[145];
        cube[97] = cube_tmp[146];
        cube[98] = cube_tmp[147];
        cube[127] = cube_tmp[176];
        cube[128] = cube_tmp[177];
        cube[129] = cube_tmp[178];
        cube[130] = cube_tmp[179];
        cube[131] = cube_tmp[180];
        cube[132] = cube_tmp[181];
        cube[133] = cube_tmp[182];
        cube[134] = cube_tmp[183];
        cube[135] = cube_tmp[184];
        cube[136] = cube_tmp[185];
        cube[137] = cube_tmp[186];
        cube[138] = cube_tmp[187];
        cube[139] = cube_tmp[188];
        cube[140] = cube_tmp[189];
        cube[141] = cube_tmp[190];
        cube[142] = cube_tmp[191];
        cube[143] = cube_tmp[192];
        cube[144] = cube_tmp[193];
        cube[145] = cube_tmp[194];
        cube[146] = cube_tmp[195];
        cube[147] = cube_tmp[196];
        cube[176] = cube_tmp[225];
        cube[177] = cube_tmp[226];
        cube[178] = cube_tmp[227];
        cube[179] = cube_tmp[228];
        cube[180] = cube_tmp[229];
        cube[181] = cube_tmp[230];
        cube[182] = cube_tmp[231];
        cube[183] = cube_tmp[232];
        cube[184] = cube_tmp[233];
        cube[185] = cube_tmp[234];
        cube[186] = cube_tmp[235];
        cube[187] = cube_tmp[236];
        cube[188] = cube_tmp[237];
        cube[189] = cube_tmp[238];
        cube[190] = cube_tmp[239];
        cube[191] = cube_tmp[240];
        cube[192] = cube_tmp[241];
        cube[193] = cube_tmp[242];
        cube[194] = cube_tmp[243];
        cube[195] = cube_tmp[244];
        cube[196] = cube_tmp[245];
        cube[225] = cube_tmp[78];
        cube[226] = cube_tmp[79];
        cube[227] = cube_tmp[80];
        cube[228] = cube_tmp[81];
        cube[229] = cube_tmp[82];
        cube[230] = cube_tmp[83];
        cube[231] = cube_tmp[84];
        cube[232] = cube_tmp[85];
        cube[233] = cube_tmp[86];
        cube[234] = cube_tmp[87];
        cube[235] = cube_tmp[88];
        cube[236] = cube_tmp[89];
        cube[237] = cube_tmp[90];
        cube[238] = cube_tmp[91];
        cube[239] = cube_tmp[92];
        cube[240] = cube_tmp[93];
        cube[241] = cube_tmp[94];
        cube[242] = cube_tmp[95];
        cube[243] = cube_tmp[96];
        cube[244] = cube_tmp[97];
        cube[245] = cube_tmp[98];
        cube[246] = cube_tmp[252];
        cube[247] = cube_tmp[259];
        cube[248] = cube_tmp[266];
        cube[249] = cube_tmp[273];
        cube[250] = cube_tmp[280];
        cube[251] = cube_tmp[287];
        cube[252] = cube_tmp[294];
        cube[253] = cube_tmp[251];
        cube[254] = cube_tmp[258];
        cube[255] = cube_tmp[265];
        cube[256] = cube_tmp[272];
        cube[257] = cube_tmp[279];
        cube[258] = cube_tmp[286];
        cube[259] = cube_tmp[293];
        cube[260] = cube_tmp[250];
        cube[261] = cube_tmp[257];
        cube[262] = cube_tmp[264];
        cube[263] = cube_tmp[271];
        cube[264] = cube_tmp[278];
        cube[265] = cube_tmp[285];
        cube[266] = cube_tmp[292];
        cube[267] = cube_tmp[249];
        cube[268] = cube_tmp[256];
        cube[269] = cube_tmp[263];
        cube[271] = cube_tmp[277];
        cube[272] = cube_tmp[284];
        cube[273] = cube_tmp[291];
        cube[274] = cube_tmp[248];
        cube[275] = cube_tmp[255];
        cube[276] = cube_tmp[262];
        cube[277] = cube_tmp[269];
        cube[278] = cube_tmp[276];
        cube[279] = cube_tmp[283];
        cube[280] = cube_tmp[290];
        cube[281] = cube_tmp[247];
        cube[282] = cube_tmp[254];
        cube[283] = cube_tmp[261];
        cube[284] = cube_tmp[268];
        cube[285] = cube_tmp[275];
        cube[286] = cube_tmp[282];
        cube[287] = cube_tmp[289];
        cube[288] = cube_tmp[246];
        cube[289] = cube_tmp[253];
        cube[290] = cube_tmp[260];
        cube[291] = cube_tmp[267];
        cube[292] = cube_tmp[274];
        cube[293] = cube_tmp[281];
        cube[294] = cube_tmp[288];
        break;
    }

    case threeDw2: {
        cube[78] = cube_tmp[176];
        cube[79] = cube_tmp[177];
        cube[80] = cube_tmp[178];
        cube[81] = cube_tmp[179];
        cube[82] = cube_tmp[180];
        cube[83] = cube_tmp[181];
        cube[84] = cube_tmp[182];
        cube[85] = cube_tmp[183];
        cube[86] = cube_tmp[184];
        cube[87] = cube_tmp[185];
        cube[88] = cube_tmp[186];
        cube[89] = cube_tmp[187];
        cube[90] = cube_tmp[188];
        cube[91] = cube_tmp[189];
        cube[92] = cube_tmp[190];
        cube[93] = cube_tmp[191];
        cube[94] = cube_tmp[192];
        cube[95] = cube_tmp[193];
        cube[96] = cube_tmp[194];
        cube[97] = cube_tmp[195];
        cube[98] = cube_tmp[196];
        cube[127] = cube_tmp[225];
        cube[128] = cube_tmp[226];
        cube[129] = cube_tmp[227];
        cube[130] = cube_tmp[228];
        cube[131] = cube_tmp[229];
        cube[132] = cube_tmp[230];
        cube[133] = cube_tmp[231];
        cube[134] = cube_tmp[232];
        cube[135] = cube_tmp[233];
        cube[136] = cube_tmp[234];
        cube[137] = cube_tmp[235];
        cube[138] = cube_tmp[236];
        cube[139] = cube_tmp[237];
        cube[140] = cube_tmp[238];
        cube[141] = cube_tmp[239];
        cube[142] = cube_tmp[240];
        cube[143] = cube_tmp[241];
        cube[144] = cube_tmp[242];
        cube[145] = cube_tmp[243];
        cube[146] = cube_tmp[244];
        cube[147] = cube_tmp[245];
        cube[176] = cube_tmp[78];
        cube[177] = cube_tmp[79];
        cube[178] = cube_tmp[80];
        cube[179] = cube_tmp[81];
        cube[180] = cube_tmp[82];
        cube[181] = cube_tmp[83];
        cube[182] = cube_tmp[84];
        cube[183] = cube_tmp[85];
        cube[184] = cube_tmp[86];
        cube[185] = cube_tmp[87];
        cube[186] = cube_tmp[88];
        cube[187] = cube_tmp[89];
        cube[188] = cube_tmp[90];
        cube[189] = cube_tmp[91];
        cube[190] = cube_tmp[92];
        cube[191] = cube_tmp[93];
        cube[192] = cube_tmp[94];
        cube[193] = cube_tmp[95];
        cube[194] = cube_tmp[96];
        cube[195] = cube_tmp[97];
        cube[196] = cube_tmp[98];
        cube[225] = cube_tmp[127];
        cube[226] = cube_tmp[128];
        cube[227] = cube_tmp[129];
        cube[228] = cube_tmp[130];
        cube[229] = cube_tmp[131];
        cube[230] = cube_tmp[132];
        cube[231] = cube_tmp[133];
        cube[232] = cube_tmp[134];
        cube[233] = cube_tmp[135];
        cube[234] = cube_tmp[136];
        cube[235] = cube_tmp[137];
        cube[236] = cube_tmp[138];
        cube[237] = cube_tmp[139];
        cube[238] = cube_tmp[140];
        cube[239] = cube_tmp[141];
        cube[240] = cube_tmp[142];
        cube[241] = cube_tmp[143];
        cube[242] = cube_tmp[144];
        cube[243] = cube_tmp[145];
        cube[244] = cube_tmp[146];
        cube[245] = cube_tmp[147];
        cube[246] = cube_tmp[294];
        cube[247] = cube_tmp[293];
        cube[248] = cube_tmp[292];
        cube[249] = cube_tmp[291];
        cube[250] = cube_tmp[290];
        cube[251] = cube_tmp[289];
        cube[252] = cube_tmp[288];
        cube[253] = cube_tmp[287];
        cube[254] = cube_tmp[286];
        cube[255] = cube_tmp[285];
        cube[256] = cube_tmp[284];
        cube[257] = cube_tmp[283];
        cube[258] = cube_tmp[282];
        cube[259] = cube_tmp[281];
        cube[260] = cube_tmp[280];
        cube[261] = cube_tmp[279];
        cube[262] = cube_tmp[278];
        cube[263] = cube_tmp[277];
        cube[264] = cube_tmp[276];
        cube[265] = cube_tmp[275];
        cube[266] = cube_tmp[274];
        cube[267] = cube_tmp[273];
        cube[268] = cube_tmp[272];
        cube[269] = cube_tmp[271];
        cube[271] = cube_tmp[269];
        cube[272] = cube_tmp[268];
        cube[273] = cube_tmp[267];
        cube[274] = cube_tmp[266];
        cube[275] = cube_tmp[265];
        cube[276] = cube_tmp[264];
        cube[277] = cube_tmp[263];
        cube[278] = cube_tmp[262];
        cube[279] = cube_tmp[261];
        cube[280] = cube_tmp[260];
        cube[281] = cube_tmp[259];
        cube[282] = cube_tmp[258];
        cube[283] = cube_tmp[257];
        cube[284] = cube_tmp[256];
        cube[285] = cube_tmp[255];
        cube[286] = cube_tmp[254];
        cube[287] = cube_tmp[253];
        cube[288] = cube_tmp[252];
        cube[289] = cube_tmp[251];
        cube[290] = cube_tmp[250];
        cube[291] = cube_tmp[249];
        cube[292] = cube_tmp[248];
        cube[293] = cube_tmp[247];
        cube[294] = cube_tmp[246];
        break;
    }


    default:
        printf("ERROR: invalid move %d\n", move);
        exit(1);
    }
}
            
void
rotate_777_centers(char *cube, char *cube_tmp, int array_size, move_type move)
{
    /* This was contructed using utils/rotate-printer.py */
    (void)cube_tmp;
    (void)array_size;

    switch (move) {
    case U: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c23 = cube[23], c24 = cube[24],
             c26 = cube[26], c27 = cube[27], c30 = cube[30], c31 = cube[31],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c38 = cube[38], c39 = cube[39], c40 = cube[40], c41 = cube[41];
        cube[9] = c37;
        cube[10] = c30;
        cube[11] = c23;
        cube[12] = c16;
        cube[13] = c9;
        cube[16] = c38;
        cube[17] = c31;
        cube[18] = c24;
        cube[19] = c17;
        cube[20] = c10;
        cube[23] = c39;
        cube[24] = c32;
        cube[26] = c18;
        cube[27] = c11;
        cube[30] = c40;
        cube[31] = c33;
        cube[32] = c26;
        cube[33] = c19;
        cube[34] = c12;
        cube[37] = c41;
        cube[38] = c34;
        cube[39] = c27;
        cube[40] = c20;
        cube[41] = c13;
        break;
    }

    case U_PRIME: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c23 = cube[23], c24 = cube[24],
             c26 = cube[26], c27 = cube[27], c30 = cube[30], c31 = cube[31],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c38 = cube[38], c39 = cube[39], c40 = cube[40], c41 = cube[41];
        cube[9] = c13;
        cube[10] = c20;
        cube[11] = c27;
        cube[12] = c34;
        cube[13] = c41;
        cube[16] = c12;
        cube[17] = c19;
        cube[18] = c26;
        cube[19] = c33;
        cube[20] = c40;
        cube[23] = c11;
        cube[24] = c18;
        cube[26] = c32;
        cube[27] = c39;
        cube[30] = c10;
        cube[31] = c17;
        cube[32] = c24;
        cube[33] = c31;
        cube[34] = c38;
        cube[37] = c9;
        cube[38] = c16;
        cube[39] = c23;
        cube[40] = c30;
        cube[41] = c37;
        break;
    }

    case U2: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c23 = cube[23], c24 = cube[24],
             c26 = cube[26], c27 = cube[27], c30 = cube[30], c31 = cube[31],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c38 = cube[38], c39 = cube[39], c40 = cube[40], c41 = cube[41];
        cube[9] = c41;
        cube[10] = c40;
        cube[11] = c39;
        cube[12] = c38;
        cube[13] = c37;
        cube[16] = c34;
        cube[17] = c33;
        cube[18] = c32;
        cube[19] = c31;
        cube[20] = c30;
        cube[23] = c27;
        cube[24] = c26;
        cube[26] = c24;
        cube[27] = c23;
        cube[30] = c20;
        cube[31] = c19;
        cube[32] = c18;
        cube[33] = c17;
        cube[34] = c16;
        cube[37] = c13;
        cube[38] = c12;
        cube[39] = c11;
        cube[40] = c10;
        cube[41] = c9;
        break;
    }

    case Uw: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c23 = cube[23], c24 = cube[24],
             c26 = cube[26], c27 = cube[27], c30 = cube[30], c31 = cube[31],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c38 = cube[38], c39 = cube[39], c40 = cube[40], c41 = cube[41],
             c58 = cube[58], c59 = cube[59], c60 = cube[60], c61 = cube[61],
             c62 = cube[62], c107 = cube[107], c108 = cube[108], c109 = cube[109],
             c110 = cube[110], c111 = cube[111], c156 = cube[156], c157 = cube[157],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c205 = cube[205],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[9] = c37;
        cube[10] = c30;
        cube[11] = c23;
        cube[12] = c16;
        cube[13] = c9;
        cube[16] = c38;
        cube[17] = c31;
        cube[18] = c24;
        cube[19] = c17;
        cube[20] = c10;
        cube[23] = c39;
        cube[24] = c32;
        cube[26] = c18;
        cube[27] = c11;
        cube[30] = c40;
        cube[31] = c33;
        cube[32] = c26;
        cube[33] = c19;
        cube[34] = c12;
        cube[37] = c41;
        cube[38] = c34;
        cube[39] = c27;
        cube[40] = c20;
        cube[41] = c13;
        cube[58] = c107;
        cube[59] = c108;
        cube[60] = c109;
        cube[61] = c110;
        cube[62] = c111;
        cube[107] = c156;
        cube[108] = c157;
        cube[109] = c158;
        cube[110] = c159;
        cube[111] = c160;
        cube[156] = c205;
        cube[157] = c206;
        cube[158] = c207;
        cube[159] = c208;
        cube[160] = c209;
        cube[205] = c58;
        cube[206] = c59;
        cube[207] = c60;
        cube[208] = c61;
        cube[209] = c62;
        break;
    }

    case Uw_PRIME: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c23 = cube[23], c24 = cube[24],
             c26 = cube[26], c27 = cube[27], c30 = cube[30], c31 = cube[31],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c38 = cube[38], c39 = cube[39], c40 = cube[40], c41 = cube[41],
             c58 = cube[58], c59 = cube[59], c60 = cube[60], c61 = cube[61],
             c62 = cube[62], c107 = cube[107], c108 = cube[108], c109 = cube[109],
             c110 = cube[110], c111 = cube[111], c156 = cube[156], c157 = cube[157],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c205 = cube[205],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[9] = c13;
        cube[10] = c20;
        cube[11] = c27;
        cube[12] = c34;
        cube[13] = c41;
        cube[16] = c12;
        cube[17] = c19;
        cube[18] = c26;
        cube[19] = c33;
        cube[20] = c40;
        cube[23] = c11;
        cube[24] = c18;
        cube[26] = c32;
        cube[27] = c39;
        cube[30] = c10;
        cube[31] = c17;
        cube[32] = c24;
        cube[33] = c31;
        cube[34] = c38;
        cube[37] = c9;
        cube[38] = c16;
        cube[39] = c23;
        cube[40] = c30;
        cube[41] = c37;
        cube[58] = c205;
        cube[59] = c206;
        cube[60] = c207;
        cube[61] = c208;
        cube[62] = c209;
        cube[107] = c58;
        cube[108] = c59;
        cube[109] = c60;
        cube[110] = c61;
        cube[111] = c62;
        cube[156] = c107;
        cube[157] = c108;
        cube[158] = c109;
        cube[159] = c110;
        cube[160] = c111;
        cube[205] = c156;
        cube[206] = c157;
        cube[207] = c158;
        cube[208] = c159;
        cube[209] = c160;
        break;
    }

    case Uw2: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c23 = cube[23], c24 = cube[24],
             c26 = cube[26], c27 = cube[27], c30 = cube[30], c31 = cube[31],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c38 = cube[38], c39 = cube[39], c40 = cube[40], c41 = cube[41],
             c58 = cube[58], c59 = cube[59], c60 = cube[60], c61 = cube[61],
             c62 = cube[62], c107 = cube[107], c108 = cube[108], c109 = cube[109],
             c110 = cube[110], c111 = cube[111], c156 = cube[156], c157 = cube[157],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c205 = cube[205],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209];
        cube[9] = c41;
        cube[10] = c40;
        cube[11] = c39;
        cube[12] = c38;
        cube[13] = c37;
        cube[16] = c34;
        cube[17] = c33;
        cube[18] = c32;
        cube[19] = c31;
        cube[20] = c30;
        cube[23] = c27;
        cube[24] = c26;
        cube[26] = c24;
        cube[27] = c23;
        cube[30] = c20;
        cube[31] = c19;
        cube[32] = c18;
        cube[33] = c17;
        cube[34] = c16;
        cube[37] = c13;
        cube[38] = c12;
        cube[39] = c11;
        cube[40] = c10;
        cube[41] = c9;
        cube[58] = c156;
        cube[59] = c157;
        cube[60] = c158;
        cube[61] = c159;
        cube[62] = c160;
        cube[107] = c205;
        cube[108] = c206;
        cube[109] = c207;
        cube[110] = c208;
        cube[111] = c209;
        cube[156] = c58;
        cube[157] = c59;
        cube[158] = c60;
        cube[159] = c61;
        cube[160] = c62;
        cube[205] = c107;
        cube[206] = c108;
        cube[207] = c109;
        cube[208] = c110;
        cube[209] = c111;
        break;
    }

    case threeUw: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c23 = cube[23], c24 = cube[24],
             c26 = cube[26], c27 = cube[27], c30 = cube[30], c31 = cube[31],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c38 = cube[38], c39 = cube[39], c40 = cube[40], c41 = cube[41],
             c58 = cube[58], c59 = cube[59], c60 = cube[60], c61 = cube[61],
             c62 = cube[62], c65 = cube[65], c66 = cube[66], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c107 = cube[107], c108 = cube[108],
             c109 = cube[109], c110 = cube[110], c111 = cube[111], c114 = cube[114],
             c115 = cube[115], c116 = cube[116], c117 = cube[117], c118 = cube[118],
             c156 = cube[156], c157 = cube[157], c158 = cube[158], c159 = cube[159],
             c160 = cube[160], c163 = cube[163], c164 = cube[164], c165 = cube[165],
             c166 = cube[166], c167 = cube[167], c205 = cube[205], c206 = cube[206],
             c207 = cube[207], c208 = cube[208], c209 = cube[209], c212 = cube[212],
             c213 = cube[213], c214 = cube[214], c215 = cube[215], c216 = cube[216];
        cube[9] = c37;
        cube[10] = c30;
        cube[11] = c23;
        cube[12] = c16;
        cube[13] = c9;
        cube[16] = c38;
        cube[17] = c31;
        cube[18] = c24;
        cube[19] = c17;
        cube[20] = c10;
        cube[23] = c39;
        cube[24] = c32;
        cube[26] = c18;
        cube[27] = c11;
        cube[30] = c40;
        cube[31] = c33;
        cube[32] = c26;
        cube[33] = c19;
        cube[34] = c12;
        cube[37] = c41;
        cube[38] = c34;
        cube[39] = c27;
        cube[40] = c20;
        cube[41] = c13;
        cube[58] = c107;
        cube[59] = c108;
        cube[60] = c109;
        cube[61] = c110;
        cube[62] = c111;
        cube[65] = c114;
        cube[66] = c115;
        cube[67] = c116;
        cube[68] = c117;
        cube[69] = c118;
        cube[107] = c156;
        cube[108] = c157;
        cube[109] = c158;
        cube[110] = c159;
        cube[111] = c160;
        cube[114] = c163;
        cube[115] = c164;
        cube[116] = c165;
        cube[117] = c166;
        cube[118] = c167;
        cube[156] = c205;
        cube[157] = c206;
        cube[158] = c207;
        cube[159] = c208;
        cube[160] = c209;
        cube[163] = c212;
        cube[164] = c213;
        cube[165] = c214;
        cube[166] = c215;
        cube[167] = c216;
        cube[205] = c58;
        cube[206] = c59;
        cube[207] = c60;
        cube[208] = c61;
        cube[209] = c62;
        cube[212] = c65;
        cube[213] = c66;
        cube[214] = c67;
        cube[215] = c68;
        cube[216] = c69;
        break;
    }

    case threeUw_PRIME: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c23 = cube[23], c24 = cube[24],
             c26 = cube[26], c27 = cube[27], c30 = cube[30], c31 = cube[31],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c38 = cube[38], c39 = cube[39], c40 = cube[40], c41 = cube[41],
             c58 = cube[58], c59 = cube[59], c60 = cube[60], c61 = cube[61],
             c62 = cube[62], c65 = cube[65], c66 = cube[66], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c107 = cube[107], c108 = cube[108],
             c109 = cube[109], c110 = cube[110], c111 = cube[111], c114 = cube[114],
             c115 = cube[115], c116 = cube[116], c117 = cube[117], c118 = cube[118],
             c156 = cube[156], c157 = cube[157], c158 = cube[158], c159 = cube[159],
             c160 = cube[160], c163 = cube[163], c164 = cube[164], c165 = cube[165],
             c166 = cube[166], c167 = cube[167], c205 = cube[205], c206 = cube[206],
             c207 = cube[207], c208 = cube[208], c209 = cube[209], c212 = cube[212],
             c213 = cube[213], c214 = cube[214], c215 = cube[215], c216 = cube[216];
        cube[9] = c13;
        cube[10] = c20;
        cube[11] = c27;
        cube[12] = c34;
        cube[13] = c41;
        cube[16] = c12;
        cube[17] = c19;
        cube[18] = c26;
        cube[19] = c33;
        cube[20] = c40;
        cube[23] = c11;
        cube[24] = c18;
        cube[26] = c32;
        cube[27] = c39;
        cube[30] = c10;
        cube[31] = c17;
        cube[32] = c24;
        cube[33] = c31;
        cube[34] = c38;
        cube[37] = c9;
        cube[38] = c16;
        cube[39] = c23;
        cube[40] = c30;
        cube[41] = c37;
        cube[58] = c205;
        cube[59] = c206;
        cube[60] = c207;
        cube[61] = c208;
        cube[62] = c209;
        cube[65] = c212;
        cube[66] = c213;
        cube[67] = c214;
        cube[68] = c215;
        cube[69] = c216;
        cube[107] = c58;
        cube[108] = c59;
        cube[109] = c60;
        cube[110] = c61;
        cube[111] = c62;
        cube[114] = c65;
        cube[115] = c66;
        cube[116] = c67;
        cube[117] = c68;
        cube[118] = c69;
        cube[156] = c107;
        cube[157] = c108;
        cube[158] = c109;
        cube[159] = c110;
        cube[160] = c111;
        cube[163] = c114;
        cube[164] = c115;
        cube[165] = c116;
        cube[166] = c117;
        cube[167] = c118;
        cube[205] = c156;
        cube[206] = c157;
        cube[207] = c158;
        cube[208] = c159;
        cube[209] = c160;
        cube[212] = c163;
        cube[213] = c164;
        cube[214] = c165;
        cube[215] = c166;
        cube[216] = c167;
        break;
    }

    case threeUw2: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c23 = cube[23], c24 = cube[24],
             c26 = cube[26], c27 = cube[27], c30 = cube[30], c31 = cube[31],
             c32 = cube[32], c33 = cube[33], c34 = cube[34], c37 = cube[37],
             c38 = cube[38], c39 = cube[39], c40 = cube[40], c41 = cube[41],
             c58 = cube[58], c59 = cube[59], c60 = cube[60], c61 = cube[61],
             c62 = cube[62], c65 = cube[65], c66 = cube[66], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c107 = cube[107], c108 = cube[108],
             c109 = cube[109], c110 = cube[110], c111 = cube[111], c114 = cube[114],
             c115 = cube[115], c116 = cube[116], c117 = cube[117], c118 = cube[118],
             c156 = cube[156], c157 = cube[157], c158 = cube[158], c159 = cube[159],
             c160 = cube[160], c163 = cube[163], c164 = cube[164], c165 = cube[165],
             c166 = cube[166], c167 = cube[167], c205 = cube[205], c206 = cube[206],
             c207 = cube[207], c208 = cube[208], c209 = cube[209], c212 = cube[212],
             c213 = cube[213], c214 = cube[214], c215 = cube[215], c216 = cube[216];
        cube[9] = c41;
        cube[10] = c40;
        cube[11] = c39;
        cube[12] = c38;
        cube[13] = c37;
        cube[16] = c34;
        cube[17] = c33;
        cube[18] = c32;
        cube[19] = c31;
        cube[20] = c30;
        cube[23] = c27;
        cube[24] = c26;
        cube[26] = c24;
        cube[27] = c23;
        cube[30] = c20;
        cube[31] = c19;
        cube[32] = c18;
        cube[33] = c17;
        cube[34] = c16;
        cube[37] = c13;
        cube[38] = c12;
        cube[39] = c11;
        cube[40] = c10;
        cube[41] = c9;
        cube[58] = c156;
        cube[59] = c157;
        cube[60] = c158;
        cube[61] = c159;
        cube[62] = c160;
        cube[65] = c163;
        cube[66] = c164;
        cube[67] = c165;
        cube[68] = c166;
        cube[69] = c167;
        cube[107] = c205;
        cube[108] = c206;
        cube[109] = c207;
        cube[110] = c208;
        cube[111] = c209;
        cube[114] = c212;
        cube[115] = c213;
        cube[116] = c214;
        cube[117] = c215;
        cube[118] = c216;
        cube[156] = c58;
        cube[157] = c59;
        cube[158] = c60;
        cube[159] = c61;
        cube[160] = c62;
        cube[163] = c65;
        cube[164] = c66;
        cube[165] = c67;
        cube[166] = c68;
        cube[167] = c69;
        cube[205] = c107;
        cube[206] = c108;
        cube[207] = c109;
        cube[208] = c110;
        cube[209] = c111;
        cube[212] = c114;
        cube[213] = c115;
        cube[214] = c116;
        cube[215] = c117;
        cube[216] = c118;
        break;
    }

    case L: {
        char c58 = cube[58], c59 = cube[59], c60 = cube[60], c61 = cube[61],
             c62 = cube[62], c65 = cube[65], c66 = cube[66], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c72 = cube[72], c73 = cube[73],
             c75 = cube[75], c76 = cube[76], c79 = cube[79], c80 = cube[80],
             c81 = cube[81], c82 = cube[82], c83 = cube[83], c86 = cube[86],
             c87 = cube[87], c88 = cube[88], c89 = cube[89], c90 = cube[90];
        cube[58] = c86;
        cube[59] = c79;
        cube[60] = c72;
        cube[61] = c65;
        cube[62] = c58;
        cube[65] = c87;
        cube[66] = c80;
        cube[67] = c73;
        cube[68] = c66;
        cube[69] = c59;
        cube[72] = c88;
        cube[73] = c81;
        cube[75] = c67;
        cube[76] = c60;
        cube[79] = c89;
        cube[80] = c82;
        cube[81] = c75;
        cube[82] = c68;
        cube[83] = c61;
        cube[86] = c90;
        cube[87] = c83;
        cube[88] = c76;
        cube[89] = c69;
        cube[90] = c62;
        break;
    }

    case L_PRIME: {
        char c58 = cube[58], c59 = cube[59], c60 = cube[60], c61 = cube[61],
             c62 = cube[62], c65 = cube[65], c66 = cube[66], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c72 = cube[72], c73 = cube[73],
             c75 = cube[75], c76 = cube[76], c79 = cube[79], c80 = cube[80],
             c81 = cube[81], c82 = cube[82], c83 = cube[83], c86 = cube[86],
             c87 = cube[87], c88 = cube[88], c89 = cube[89], c90 = cube[90];
        cube[58] = c62;
        cube[59] = c69;
        cube[60] = c76;
        cube[61] = c83;
        cube[62] = c90;
        cube[65] = c61;
        cube[66] = c68;
        cube[67] = c75;
        cube[68] = c82;
        cube[69] = c89;
        cube[72] = c60;
        cube[73] = c67;
        cube[75] = c81;
        cube[76] = c88;
        cube[79] = c59;
        cube[80] = c66;
        cube[81] = c73;
        cube[82] = c80;
        cube[83] = c87;
        cube[86] = c58;
        cube[87] = c65;
        cube[88] = c72;
        cube[89] = c79;
        cube[90] = c86;
        break;
    }

    case L2: {
        char c58 = cube[58], c59 = cube[59], c60 = cube[60], c61 = cube[61],
             c62 = cube[62], c65 = cube[65], c66 = cube[66], c67 = cube[67],
             c68 = cube[68], c69 = cube[69], c72 = cube[72], c73 = cube[73],
             c75 = cube[75], c76 = cube[76], c79 = cube[79], c80 = cube[80],
             c81 = cube[81], c82 = cube[82], c83 = cube[83], c86 = cube[86],
             c87 = cube[87], c88 = cube[88], c89 = cube[89], c90 = cube[90];
        cube[58] = c90;
        cube[59] = c89;
        cube[60] = c88;
        cube[61] = c87;
        cube[62] = c86;
        cube[65] = c83;
        cube[66] = c82;
        cube[67] = c81;
        cube[68] = c80;
        cube[69] = c79;
        cube[72] = c76;
        cube[73] = c75;
        cube[75] = c73;
        cube[76] = c72;
        cube[79] = c69;
        cube[80] = c68;
        cube[81] = c67;
        cube[82] = c66;
        cube[83] = c65;
        cube[86] = c62;
        cube[87] = c61;
        cube[88] = c60;
        cube[89] = c59;
        cube[90] = c58;
        break;
    }

    case Lw: {
        char c9 = cube[9], c16 = cube[16], c23 = cube[23], c30 = cube[30],
             c37 = cube[37], c58 = cube[58], c59 = cube[59], c60 = cube[60],
             c61 = cube[61], c62 = cube[62], c65 = cube[65], c66 = cube[66],
             c67 = cube[67], c68 = cube[68], c69 = cube[69], c72 = cube[72],
             c73 = cube[73], c75 = cube[75], c76 = cube[76], c79 = cube[79],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c90 = cube[90], c107 = cube[107], c114 = cube[114], c121 = cube[121],
             c128 = cube[128], c135 = cube[135], c209 = cube[209], c216 = cube[216],
             c223 = cube[223], c230 = cube[230], c237 = cube[237], c254 = cube[254],
             c261 = cube[261], c268 = cube[268], c275 = cube[275], c282 = cube[282];
        cube[9] = c237;
        cube[16] = c230;
        cube[23] = c223;
        cube[30] = c216;
        cube[37] = c209;
        cube[58] = c86;
        cube[59] = c79;
        cube[60] = c72;
        cube[61] = c65;
        cube[62] = c58;
        cube[65] = c87;
        cube[66] = c80;
        cube[67] = c73;
        cube[68] = c66;
        cube[69] = c59;
        cube[72] = c88;
        cube[73] = c81;
        cube[75] = c67;
        cube[76] = c60;
        cube[79] = c89;
        cube[80] = c82;
        cube[81] = c75;
        cube[82] = c68;
        cube[83] = c61;
        cube[86] = c90;
        cube[87] = c83;
        cube[88] = c76;
        cube[89] = c69;
        cube[90] = c62;
        cube[107] = c9;
        cube[114] = c16;
        cube[121] = c23;
        cube[128] = c30;
        cube[135] = c37;
        cube[209] = c282;
        cube[216] = c275;
        cube[223] = c268;
        cube[230] = c261;
        cube[237] = c254;
        cube[254] = c107;
        cube[261] = c114;
        cube[268] = c121;
        cube[275] = c128;
        cube[282] = c135;
        break;
    }

    case Lw_PRIME: {
        char c9 = cube[9], c16 = cube[16], c23 = cube[23], c30 = cube[30],
             c37 = cube[37], c58 = cube[58], c59 = cube[59], c60 = cube[60],
             c61 = cube[61], c62 = cube[62], c65 = cube[65], c66 = cube[66],
             c67 = cube[67], c68 = cube[68], c69 = cube[69], c72 = cube[72],
             c73 = cube[73], c75 = cube[75], c76 = cube[76], c79 = cube[79],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c90 = cube[90], c107 = cube[107], c114 = cube[114], c121 = cube[121],
             c128 = cube[128], c135 = cube[135], c209 = cube[209], c216 = cube[216],
             c223 = cube[223], c230 = cube[230], c237 = cube[237], c254 = cube[254],
             c261 = cube[261], c268 = cube[268], c275 = cube[275], c282 = cube[282];
        cube[9] = c107;
        cube[16] = c114;
        cube[23] = c121;
        cube[30] = c128;
        cube[37] = c135;
        cube[58] = c62;
        cube[59] = c69;
        cube[60] = c76;
        cube[61] = c83;
        cube[62] = c90;
        cube[65] = c61;
        cube[66] = c68;
        cube[67] = c75;
        cube[68] = c82;
        cube[69] = c89;
        cube[72] = c60;
        cube[73] = c67;
        cube[75] = c81;
        cube[76] = c88;
        cube[79] = c59;
        cube[80] = c66;
        cube[81] = c73;
        cube[82] = c80;
        cube[83] = c87;
        cube[86] = c58;
        cube[87] = c65;
        cube[88] = c72;
        cube[89] = c79;
        cube[90] = c86;
        cube[107] = c254;
        cube[114] = c261;
        cube[121] = c268;
        cube[128] = c275;
        cube[135] = c282;
        cube[209] = c37;
        cube[216] = c30;
        cube[223] = c23;
        cube[230] = c16;
        cube[237] = c9;
        cube[254] = c237;
        cube[261] = c230;
        cube[268] = c223;
        cube[275] = c216;
        cube[282] = c209;
        break;
    }

    case Lw2: {
        char c9 = cube[9], c16 = cube[16], c23 = cube[23], c30 = cube[30],
             c37 = cube[37], c58 = cube[58], c59 = cube[59], c60 = cube[60],
             c61 = cube[61], c62 = cube[62], c65 = cube[65], c66 = cube[66],
             c67 = cube[67], c68 = cube[68], c69 = cube[69], c72 = cube[72],
             c73 = cube[73], c75 = cube[75], c76 = cube[76], c79 = cube[79],
             c80 = cube[80], c81 = cube[81], c82 = cube[82], c83 = cube[83],
             c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c90 = cube[90], c107 = cube[107], c114 = cube[114], c121 = cube[121],
             c128 = cube[128], c135 = cube[135], c209 = cube[209], c216 = cube[216],
             c223 = cube[223], c230 = cube[230], c237 = cube[237], c254 = cube[254],
             c261 = cube[261], c268 = cube[268], c275 = cube[275], c282 = cube[282];
        cube[9] = c254;
        cube[16] = c261;
        cube[23] = c268;
        cube[30] = c275;
        cube[37] = c282;
        cube[58] = c90;
        cube[59] = c89;
        cube[60] = c88;
        cube[61] = c87;
        cube[62] = c86;
        cube[65] = c83;
        cube[66] = c82;
        cube[67] = c81;
        cube[68] = c80;
        cube[69] = c79;
        cube[72] = c76;
        cube[73] = c75;
        cube[75] = c73;
        cube[76] = c72;
        cube[79] = c69;
        cube[80] = c68;
        cube[81] = c67;
        cube[82] = c66;
        cube[83] = c65;
        cube[86] = c62;
        cube[87] = c61;
        cube[88] = c60;
        cube[89] = c59;
        cube[90] = c58;
        cube[107] = c237;
        cube[114] = c230;
        cube[121] = c223;
        cube[128] = c216;
        cube[135] = c209;
        cube[209] = c135;
        cube[216] = c128;
        cube[223] = c121;
        cube[230] = c114;
        cube[237] = c107;
        cube[254] = c9;
        cube[261] = c16;
        cube[268] = c23;
        cube[275] = c30;
        cube[282] = c37;
        break;
    }

    case threeLw: {
        char c9 = cube[9], c10 = cube[10], c16 = cube[16], c17 = cube[17],
             c23 = cube[23], c24 = cube[24], c30 = cube[30], c31 = cube[31],
             c37 = cube[37], c38 = cube[38], c58 = cube[58], c59 = cube[59],
             c60 = cube[60], c61 = cube[61], c62 = cube[62], c65 = cube[65],
             c66 = cube[66], c67 = cube[67], c68 = cube[68], c69 = cube[69],
             c72 = cube[72], c73 = cube[73], c75 = cube[75], c76 = cube[76],
             c79 = cube[79], c80 = cube[80], c81 = cube[81], c82 = cube[82],
             c83 = cube[83], c86 = cube[86], c87 = cube[87], c88 = cube[88],
             c89 = cube[89], c90 = cube[90], c107 = cube[107], c108 = cube[108],
             c114 = cube[114], c115 = cube[115], c121 = cube[121], c122 = cube[122],
             c128 = cube[128], c129 = cube[129], c135 = cube[135], c136 = cube[136],
             c208 = cube[208], c209 = cube[209], c215 = cube[215], c216 = cube[216],
             c222 = cube[222], c223 = cube[223], c229 = cube[229], c230 = cube[230],
             c236 = cube[236], c237 = cube[237], c254 = cube[254], c255 = cube[255],
             c261 = cube[261], c262 = cube[262], c268 = cube[268], c269 = cube[269],
             c275 = cube[275], c276 = cube[276], c282 = cube[282], c283 = cube[283];
        cube[9] = c237;
        cube[10] = c236;
        cube[16] = c230;
        cube[17] = c229;
        cube[23] = c223;
        cube[24] = c222;
        cube[30] = c216;
        cube[31] = c215;
        cube[37] = c209;
        cube[38] = c208;
        cube[58] = c86;
        cube[59] = c79;
        cube[60] = c72;
        cube[61] = c65;
        cube[62] = c58;
        cube[65] = c87;
        cube[66] = c80;
        cube[67] = c73;
        cube[68] = c66;
        cube[69] = c59;
        cube[72] = c88;
        cube[73] = c81;
        cube[75] = c67;
        cube[76] = c60;
        cube[79] = c89;
        cube[80] = c82;
        cube[81] = c75;
        cube[82] = c68;
        cube[83] = c61;
        cube[86] = c90;
        cube[87] = c83;
        cube[88] = c76;
        cube[89] = c69;
        cube[90] = c62;
        cube[107] = c9;
        cube[108] = c10;
        cube[114] = c16;
        cube[115] = c17;
        cube[121] = c23;
        cube[122] = c24;
        cube[128] = c30;
        cube[129] = c31;
        cube[135] = c37;
        cube[136] = c38;
        cube[208] = c283;
        cube[209] = c282;
        cube[215] = c276;
        cube[216] = c275;
        cube[222] = c269;
        cube[223] = c268;
        cube[229] = c262;
        cube[230] = c261;
        cube[236] = c255;
        cube[237] = c254;
        cube[254] = c107;
        cube[255] = c108;
        cube[261] = c114;
        cube[262] = c115;
        cube[268] = c121;
        cube[269] = c122;
        cube[275] = c128;
        cube[276] = c129;
        cube[282] = c135;
        cube[283] = c136;
        break;
    }

    case threeLw_PRIME: {
        char c9 = cube[9], c10 = cube[10], c16 = cube[16], c17 = cube[17],
             c23 = cube[23], c24 = cube[24], c30 = cube[30], c31 = cube[31],
             c37 = cube[37], c38 = cube[38], c58 = cube[58], c59 = cube[59],
             c60 = cube[60], c61 = cube[61], c62 = cube[62], c65 = cube[65],
             c66 = cube[66], c67 = cube[67], c68 = cube[68], c69 = cube[69],
             c72 = cube[72], c73 = cube[73], c75 = cube[75], c76 = cube[76],
             c79 = cube[79], c80 = cube[80], c81 = cube[81], c82 = cube[82],
             c83 = cube[83], c86 = cube[86], c87 = cube[87], c88 = cube[88],
             c89 = cube[89], c90 = cube[90], c107 = cube[107], c108 = cube[108],
             c114 = cube[114], c115 = cube[115], c121 = cube[121], c122 = cube[122],
             c128 = cube[128], c129 = cube[129], c135 = cube[135], c136 = cube[136],
             c208 = cube[208], c209 = cube[209], c215 = cube[215], c216 = cube[216],
             c222 = cube[222], c223 = cube[223], c229 = cube[229], c230 = cube[230],
             c236 = cube[236], c237 = cube[237], c254 = cube[254], c255 = cube[255],
             c261 = cube[261], c262 = cube[262], c268 = cube[268], c269 = cube[269],
             c275 = cube[275], c276 = cube[276], c282 = cube[282], c283 = cube[283];
        cube[9] = c107;
        cube[10] = c108;
        cube[16] = c114;
        cube[17] = c115;
        cube[23] = c121;
        cube[24] = c122;
        cube[30] = c128;
        cube[31] = c129;
        cube[37] = c135;
        cube[38] = c136;
        cube[58] = c62;
        cube[59] = c69;
        cube[60] = c76;
        cube[61] = c83;
        cube[62] = c90;
        cube[65] = c61;
        cube[66] = c68;
        cube[67] = c75;
        cube[68] = c82;
        cube[69] = c89;
        cube[72] = c60;
        cube[73] = c67;
        cube[75] = c81;
        cube[76] = c88;
        cube[79] = c59;
        cube[80] = c66;
        cube[81] = c73;
        cube[82] = c80;
        cube[83] = c87;
        cube[86] = c58;
        cube[87] = c65;
        cube[88] = c72;
        cube[89] = c79;
        cube[90] = c86;
        cube[107] = c254;
        cube[108] = c255;
        cube[114] = c261;
        cube[115] = c262;
        cube[121] = c268;
        cube[122] = c269;
        cube[128] = c275;
        cube[129] = c276;
        cube[135] = c282;
        cube[136] = c283;
        cube[208] = c38;
        cube[209] = c37;
        cube[215] = c31;
        cube[216] = c30;
        cube[222] = c24;
        cube[223] = c23;
        cube[229] = c17;
        cube[230] = c16;
        cube[236] = c10;
        cube[237] = c9;
        cube[254] = c237;
        cube[255] = c236;
        cube[261] = c230;
        cube[262] = c229;
        cube[268] = c223;
        cube[269] = c222;
        cube[275] = c216;
        cube[276] = c215;
        cube[282] = c209;
        cube[283] = c208;
        break;
    }

    case threeLw2: {
        char c9 = cube[9], c10 = cube[10], c16 = cube[16], c17 = cube[17],
             c23 = cube[23], c24 = cube[24], c30 = cube[30], c31 = cube[31],
             c37 = cube[37], c38 = cube[38], c58 = cube[58], c59 = cube[59],
             c60 = cube[60], c61 = cube[61], c62 = cube[62], c65 = cube[65],
             c66 = cube[66], c67 = cube[67], c68 = cube[68], c69 = cube[69],
             c72 = cube[72], c73 = cube[73], c75 = cube[75], c76 = cube[76],
             c79 = cube[79], c80 = cube[80], c81 = cube[81], c82 = cube[82],
             c83 = cube[83], c86 = cube[86], c87 = cube[87], c88 = cube[88],
             c89 = cube[89], c90 = cube[90], c107 = cube[107], c108 = cube[108],
             c114 = cube[114], c115 = cube[115], c121 = cube[121], c122 = cube[122],
             c128 = cube[128], c129 = cube[129], c135 = cube[135], c136 = cube[136],
             c208 = cube[208], c209 = cube[209], c215 = cube[215], c216 = cube[216],
             c222 = cube[222], c223 = cube[223], c229 = cube[229], c230 = cube[230],
             c236 = cube[236], c237 = cube[237], c254 = cube[254], c255 = cube[255],
             c261 = cube[261], c262 = cube[262], c268 = cube[268], c269 = cube[269],
             c275 = cube[275], c276 = cube[276], c282 = cube[282], c283 = cube[283];
        cube[9] = c254;
        cube[10] = c255;
        cube[16] = c261;
        cube[17] = c262;
        cube[23] = c268;
        cube[24] = c269;
        cube[30] = c275;
        cube[31] = c276;
        cube[37] = c282;
        cube[38] = c283;
        cube[58] = c90;
        cube[59] = c89;
        cube[60] = c88;
        cube[61] = c87;
        cube[62] = c86;
        cube[65] = c83;
        cube[66] = c82;
        cube[67] = c81;
        cube[68] = c80;
        cube[69] = c79;
        cube[72] = c76;
        cube[73] = c75;
        cube[75] = c73;
        cube[76] = c72;
        cube[79] = c69;
        cube[80] = c68;
        cube[81] = c67;
        cube[82] = c66;
        cube[83] = c65;
        cube[86] = c62;
        cube[87] = c61;
        cube[88] = c60;
        cube[89] = c59;
        cube[90] = c58;
        cube[107] = c237;
        cube[108] = c236;
        cube[114] = c230;
        cube[115] = c229;
        cube[121] = c223;
        cube[122] = c222;
        cube[128] = c216;
        cube[129] = c215;
        cube[135] = c209;
        cube[136] = c208;
        cube[208] = c136;
        cube[209] = c135;
        cube[215] = c129;
        cube[216] = c128;
        cube[222] = c122;
        cube[223] = c121;
        cube[229] = c115;
        cube[230] = c114;
        cube[236] = c108;
        cube[237] = c107;
        cube[254] = c9;
        cube[255] = c10;
        cube[261] = c16;
        cube[262] = c17;
        cube[268] = c23;
        cube[269] = c24;
        cube[275] = c30;
        cube[276] = c31;
        cube[282] = c37;
        cube[283] = c38;
        break;
    }

    case F: {
        char c107 = cube[107], c108 = cube[108], c109 = cube[109], c110 = cube[110],
             c111 = cube[111], c114 = cube[114], c115 = cube[115], c116 = cube[116],
             c117 = cube[117], c118 = cube[118], c121 = cube[121], c122 = cube[122],
             c124 = cube[124], c125 = cube[125], c128 = cube[128], c129 = cube[129],
             c130 = cube[130], c131 = cube[131], c132 = cube[132], c135 = cube[135],
             c136 = cube[136], c137 = cube[137], c138 = cube[138], c139 = cube[139];
        cube[107] = c135;
        cube[108] = c128;
        cube[109] = c121;
        cube[110] = c114;
        cube[111] = c107;
        cube[114] = c136;
        cube[115] = c129;
        cube[116] = c122;
        cube[117] = c115;
        cube[118] = c108;
        cube[121] = c137;
        cube[122] = c130;
        cube[124] = c116;
        cube[125] = c109;
        cube[128] = c138;
        cube[129] = c131;
        cube[130] = c124;
        cube[131] = c117;
        cube[132] = c110;
        cube[135] = c139;
        cube[136] = c132;
        cube[137] = c125;
        cube[138] = c118;
        cube[139] = c111;
        break;
    }

    case F_PRIME: {
        char c107 = cube[107], c108 = cube[108], c109 = cube[109], c110 = cube[110],
             c111 = cube[111], c114 = cube[114], c115 = cube[115], c116 = cube[116],
             c117 = cube[117], c118 = cube[118], c121 = cube[121], c122 = cube[122],
             c124 = cube[124], c125 = cube[125], c128 = cube[128], c129 = cube[129],
             c130 = cube[130], c131 = cube[131], c132 = cube[132], c135 = cube[135],
             c136 = cube[136], c137 = cube[137], c138 = cube[138], c139 = cube[139];
        cube[107] = c111;
        cube[108] = c118;
        cube[109] = c125;
        cube[110] = c132;
        cube[111] = c139;
        cube[114] = c110;
        cube[115] = c117;
        cube[116] = c124;
        cube[117] = c131;
        cube[118] = c138;
        cube[121] = c109;
        cube[122] = c116;
        cube[124] = c130;
        cube[125] = c137;
        cube[128] = c108;
        cube[129] = c115;
        cube[130] = c122;
        cube[131] = c129;
        cube[132] = c136;
        cube[135] = c107;
        cube[136] = c114;
        cube[137] = c121;
        cube[138] = c128;
        cube[139] = c135;
        break;
    }

    case F2: {
        char c107 = cube[107], c108 = cube[108], c109 = cube[109], c110 = cube[110],
             c111 = cube[111], c114 = cube[114], c115 = cube[115], c116 = cube[116],
             c117 = cube[117], c118 = cube[118], c121 = cube[121], c122 = cube[122],
             c124 = cube[124], c125 = cube[125], c128 = cube[128], c129 = cube[129],
             c130 = cube[130], c131 = cube[131], c132 = cube[132], c135 = cube[135],
             c136 = cube[136], c137 = cube[137], c138 = cube[138], c139 = cube[139];
        cube[107] = c139;
        cube[108] = c138;
        cube[109] = c137;
        cube[110] = c136;
        cube[111] = c135;
        cube[114] = c132;
        cube[115] = c131;
        cube[116] = c130;
        cube[117] = c129;
        cube[118] = c128;
        cube[121] = c125;
        cube[122] = c124;
        cube[124] = c122;
        cube[125] = c121;
        cube[128] = c118;
        cube[129] = c117;
        cube[130] = c116;
        cube[131] = c115;
        cube[132] = c114;
        cube[135] = c111;
        cube[136] = c110;
        cube[137] = c109;
        cube[138] = c108;
        cube[139] = c107;
        break;
    }

    case Fw: {
        char c37 = cube[37], c38 = cube[38], c39 = cube[39], c40 = cube[40],
             c41 = cube[41], c62 = cube[62], c69 = cube[69], c76 = cube[76],
             c83 = cube[83], c90 = cube[90], c107 = cube[107], c108 = cube[108],
             c109 = cube[109], c110 = cube[110], c111 = cube[111], c114 = cube[114],
             c115 = cube[115], c116 = cube[116], c117 = cube[117], c118 = cube[118],
             c121 = cube[121], c122 = cube[122], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c132 = cube[132], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c138 = cube[138], c139 = cube[139], c156 = cube[156], c163 = cube[163],
             c170 = cube[170], c177 = cube[177], c184 = cube[184], c254 = cube[254],
             c255 = cube[255], c256 = cube[256], c257 = cube[257], c258 = cube[258];
        cube[37] = c90;
        cube[38] = c83;
        cube[39] = c76;
        cube[40] = c69;
        cube[41] = c62;
        cube[62] = c254;
        cube[69] = c255;
        cube[76] = c256;
        cube[83] = c257;
        cube[90] = c258;
        cube[107] = c135;
        cube[108] = c128;
        cube[109] = c121;
        cube[110] = c114;
        cube[111] = c107;
        cube[114] = c136;
        cube[115] = c129;
        cube[116] = c122;
        cube[117] = c115;
        cube[118] = c108;
        cube[121] = c137;
        cube[122] = c130;
        cube[124] = c116;
        cube[125] = c109;
        cube[128] = c138;
        cube[129] = c131;
        cube[130] = c124;
        cube[131] = c117;
        cube[132] = c110;
        cube[135] = c139;
        cube[136] = c132;
        cube[137] = c125;
        cube[138] = c118;
        cube[139] = c111;
        cube[156] = c37;
        cube[163] = c38;
        cube[170] = c39;
        cube[177] = c40;
        cube[184] = c41;
        cube[254] = c184;
        cube[255] = c177;
        cube[256] = c170;
        cube[257] = c163;
        cube[258] = c156;
        break;
    }

    case Fw_PRIME: {
        char c37 = cube[37], c38 = cube[38], c39 = cube[39], c40 = cube[40],
             c41 = cube[41], c62 = cube[62], c69 = cube[69], c76 = cube[76],
             c83 = cube[83], c90 = cube[90], c107 = cube[107], c108 = cube[108],
             c109 = cube[109], c110 = cube[110], c111 = cube[111], c114 = cube[114],
             c115 = cube[115], c116 = cube[116], c117 = cube[117], c118 = cube[118],
             c121 = cube[121], c122 = cube[122], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c132 = cube[132], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c138 = cube[138], c139 = cube[139], c156 = cube[156], c163 = cube[163],
             c170 = cube[170], c177 = cube[177], c184 = cube[184], c254 = cube[254],
             c255 = cube[255], c256 = cube[256], c257 = cube[257], c258 = cube[258];
        cube[37] = c156;
        cube[38] = c163;
        cube[39] = c170;
        cube[40] = c177;
        cube[41] = c184;
        cube[62] = c41;
        cube[69] = c40;
        cube[76] = c39;
        cube[83] = c38;
        cube[90] = c37;
        cube[107] = c111;
        cube[108] = c118;
        cube[109] = c125;
        cube[110] = c132;
        cube[111] = c139;
        cube[114] = c110;
        cube[115] = c117;
        cube[116] = c124;
        cube[117] = c131;
        cube[118] = c138;
        cube[121] = c109;
        cube[122] = c116;
        cube[124] = c130;
        cube[125] = c137;
        cube[128] = c108;
        cube[129] = c115;
        cube[130] = c122;
        cube[131] = c129;
        cube[132] = c136;
        cube[135] = c107;
        cube[136] = c114;
        cube[137] = c121;
        cube[138] = c128;
        cube[139] = c135;
        cube[156] = c258;
        cube[163] = c257;
        cube[170] = c256;
        cube[177] = c255;
        cube[184] = c254;
        cube[254] = c62;
        cube[255] = c69;
        cube[256] = c76;
        cube[257] = c83;
        cube[258] = c90;
        break;
    }

    case Fw2: {
        char c37 = cube[37], c38 = cube[38], c39 = cube[39], c40 = cube[40],
             c41 = cube[41], c62 = cube[62], c69 = cube[69], c76 = cube[76],
             c83 = cube[83], c90 = cube[90], c107 = cube[107], c108 = cube[108],
             c109 = cube[109], c110 = cube[110], c111 = cube[111], c114 = cube[114],
             c115 = cube[115], c116 = cube[116], c117 = cube[117], c118 = cube[118],
             c121 = cube[121], c122 = cube[122], c124 = cube[124], c125 = cube[125],
             c128 = cube[128], c129 = cube[129], c130 = cube[130], c131 = cube[131],
             c132 = cube[132], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c138 = cube[138], c139 = cube[139], c156 = cube[156], c163 = cube[163],
             c170 = cube[170], c177 = cube[177], c184 = cube[184], c254 = cube[254],
             c255 = cube[255], c256 = cube[256], c257 = cube[257], c258 = cube[258];
        cube[37] = c258;
        cube[38] = c257;
        cube[39] = c256;
        cube[40] = c255;
        cube[41] = c254;
        cube[62] = c184;
        cube[69] = c177;
        cube[76] = c170;
        cube[83] = c163;
        cube[90] = c156;
        cube[107] = c139;
        cube[108] = c138;
        cube[109] = c137;
        cube[110] = c136;
        cube[111] = c135;
        cube[114] = c132;
        cube[115] = c131;
        cube[116] = c130;
        cube[117] = c129;
        cube[118] = c128;
        cube[121] = c125;
        cube[122] = c124;
        cube[124] = c122;
        cube[125] = c121;
        cube[128] = c118;
        cube[129] = c117;
        cube[130] = c116;
        cube[131] = c115;
        cube[132] = c114;
        cube[135] = c111;
        cube[136] = c110;
        cube[137] = c109;
        cube[138] = c108;
        cube[139] = c107;
        cube[156] = c90;
        cube[163] = c83;
        cube[170] = c76;
        cube[177] = c69;
        cube[184] = c62;
        cube[254] = c41;
        cube[255] = c40;
        cube[256] = c39;
        cube[257] = c38;
        cube[258] = c37;
        break;
    }

    case threeFw: {
        char c30 = cube[30], c31 = cube[31], c32 = cube[32], c33 = cube[33],
             c34 = cube[34], c37 = cube[37], c38 = cube[38], c39 = cube[39],
             c40 = cube[40], c41 = cube[41], c61 = cube[61], c62 = cube[62],
             c68 = cube[68], c69 = cube[69], c75 = cube[75], c76 = cube[76],
             c82 = cube[82], c83 = cube[83], c89 = cube[89], c90 = cube[90],
             c107 = cube[107], c108 = cube[108], c109 = cube[109], c110 = cube[110],
             c111 = cube[111], c114 = cube[114], c115 = cube[115], c116 = cube[116],
             c117 = cube[117], c118 = cube[118], c121 = cube[121], c122 = cube[122],
             c124 = cube[124], c125 = cube[125], c128 = cube[128], c129 = cube[129],
             c130 = cube[130], c131 = cube[131], c132 = cube[132], c135 = cube[135],
             c136 = cube[136], c137 = cube[137], c138 = cube[138], c139 = cube[139],
             c156 = cube[156], c157 = cube[157], c163 = cube[163], c164 = cube[164],
             c170 = cube[170], c171 = cube[171], c177 = cube[177], c178 = cube[178],
             c184 = cube[184], c185 = cube[185], c254 = cube[254], c255 = cube[255],
             c256 = cube[256], c257 = cube[257], c258 = cube[258], c261 = cube[261],
             c262 = cube[262], c263 = cube[263], c264 = cube[264], c265 = cube[265];
        cube[30] = c89;
        cube[31] = c82;
        cube[32] = c75;
        cube[33] = c68;
        cube[34] = c61;
        cube[37] = c90;
        cube[38] = c83;
        cube[39] = c76;
        cube[40] = c69;
        cube[41] = c62;
        cube[61] = c261;
        cube[62] = c254;
        cube[68] = c262;
        cube[69] = c255;
        cube[75] = c263;
        cube[76] = c256;
        cube[82] = c264;
        cube[83] = c257;
        cube[89] = c265;
        cube[90] = c258;
        cube[107] = c135;
        cube[108] = c128;
        cube[109] = c121;
        cube[110] = c114;
        cube[111] = c107;
        cube[114] = c136;
        cube[115] = c129;
        cube[116] = c122;
        cube[117] = c115;
        cube[118] = c108;
        cube[121] = c137;
        cube[122] = c130;
        cube[124] = c116;
        cube[125] = c109;
        cube[128] = c138;
        cube[129] = c131;
        cube[130] = c124;
        cube[131] = c117;
        cube[132] = c110;
        cube[135] = c139;
        cube[136] = c132;
        cube[137] = c125;
        cube[138] = c118;
        cube[139] = c111;
        cube[156] = c37;
        cube[157] = c30;
        cube[163] = c38;
        cube[164] = c31;
        cube[170] = c39;
        cube[171] = c32;
        cube[177] = c40;
        cube[178] = c33;
        cube[184] = c41;
        cube[185] = c34;
        cube[254] = c184;
        cube[255] = c177;
        cube[256] = c170;
        cube[257] = c163;
        cube[258] = c156;
        cube[261] = c185;
        cube[262] = c178;
        cube[263] = c171;
        cube[264] = c164;
        cube[265] = c157;
        break;
    }

    case threeFw_PRIME: {
        char c30 = cube[30], c31 = cube[31], c32 = cube[32], c33 = cube[33],
             c34 = cube[34], c37 = cube[37], c38 = cube[38], c39 = cube[39],
             c40 = cube[40], c41 = cube[41], c61 = cube[61], c62 = cube[62],
             c68 = cube[68], c69 = cube[69], c75 = cube[75], c76 = cube[76],
             c82 = cube[82], c83 = cube[83], c89 = cube[89], c90 = cube[90],
             c107 = cube[107], c108 = cube[108], c109 = cube[109], c110 = cube[110],
             c111 = cube[111], c114 = cube[114], c115 = cube[115], c116 = cube[116],
             c117 = cube[117], c118 = cube[118], c121 = cube[121], c122 = cube[122],
             c124 = cube[124], c125 = cube[125], c128 = cube[128], c129 = cube[129],
             c130 = cube[130], c131 = cube[131], c132 = cube[132], c135 = cube[135],
             c136 = cube[136], c137 = cube[137], c138 = cube[138], c139 = cube[139],
             c156 = cube[156], c157 = cube[157], c163 = cube[163], c164 = cube[164],
             c170 = cube[170], c171 = cube[171], c177 = cube[177], c178 = cube[178],
             c184 = cube[184], c185 = cube[185], c254 = cube[254], c255 = cube[255],
             c256 = cube[256], c257 = cube[257], c258 = cube[258], c261 = cube[261],
             c262 = cube[262], c263 = cube[263], c264 = cube[264], c265 = cube[265];
        cube[30] = c157;
        cube[31] = c164;
        cube[32] = c171;
        cube[33] = c178;
        cube[34] = c185;
        cube[37] = c156;
        cube[38] = c163;
        cube[39] = c170;
        cube[40] = c177;
        cube[41] = c184;
        cube[61] = c34;
        cube[62] = c41;
        cube[68] = c33;
        cube[69] = c40;
        cube[75] = c32;
        cube[76] = c39;
        cube[82] = c31;
        cube[83] = c38;
        cube[89] = c30;
        cube[90] = c37;
        cube[107] = c111;
        cube[108] = c118;
        cube[109] = c125;
        cube[110] = c132;
        cube[111] = c139;
        cube[114] = c110;
        cube[115] = c117;
        cube[116] = c124;
        cube[117] = c131;
        cube[118] = c138;
        cube[121] = c109;
        cube[122] = c116;
        cube[124] = c130;
        cube[125] = c137;
        cube[128] = c108;
        cube[129] = c115;
        cube[130] = c122;
        cube[131] = c129;
        cube[132] = c136;
        cube[135] = c107;
        cube[136] = c114;
        cube[137] = c121;
        cube[138] = c128;
        cube[139] = c135;
        cube[156] = c258;
        cube[157] = c265;
        cube[163] = c257;
        cube[164] = c264;
        cube[170] = c256;
        cube[171] = c263;
        cube[177] = c255;
        cube[178] = c262;
        cube[184] = c254;
        cube[185] = c261;
        cube[254] = c62;
        cube[255] = c69;
        cube[256] = c76;
        cube[257] = c83;
        cube[258] = c90;
        cube[261] = c61;
        cube[262] = c68;
        cube[263] = c75;
        cube[264] = c82;
        cube[265] = c89;
        break;
    }

    case threeFw2: {
        char c30 = cube[30], c31 = cube[31], c32 = cube[32], c33 = cube[33],
             c34 = cube[34], c37 = cube[37], c38 = cube[38], c39 = cube[39],
             c40 = cube[40], c41 = cube[41], c61 = cube[61], c62 = cube[62],
             c68 = cube[68], c69 = cube[69], c75 = cube[75], c76 = cube[76],
             c82 = cube[82], c83 = cube[83], c89 = cube[89], c90 = cube[90],
             c107 = cube[107], c108 = cube[108], c109 = cube[109], c110 = cube[110],
             c111 = cube[111], c114 = cube[114], c115 = cube[115], c116 = cube[116],
             c117 = cube[117], c118 = cube[118], c121 = cube[121], c122 = cube[122],
             c124 = cube[124], c125 = cube[125], c128 = cube[128], c129 = cube[129],
             c130 = cube[130], c131 = cube[131], c132 = cube[132], c135 = cube[135],
             c136 = cube[136], c137 = cube[137], c138 = cube[138], c139 = cube[139],
             c156 = cube[156], c157 = cube[157], c163 = cube[163], c164 = cube[164],
             c170 = cube[170], c171 = cube[171], c177 = cube[177], c178 = cube[178],
             c184 = cube[184], c185 = cube[185], c254 = cube[254], c255 = cube[255],
             c256 = cube[256], c257 = cube[257], c258 = cube[258], c261 = cube[261],
             c262 = cube[262], c263 = cube[263], c264 = cube[264], c265 = cube[265];
        cube[30] = c265;
        cube[31] = c264;
        cube[32] = c263;
        cube[33] = c262;
        cube[34] = c261;
        cube[37] = c258;
        cube[38] = c257;
        cube[39] = c256;
        cube[40] = c255;
        cube[41] = c254;
        cube[61] = c185;
        cube[62] = c184;
        cube[68] = c178;
        cube[69] = c177;
        cube[75] = c171;
        cube[76] = c170;
        cube[82] = c164;
        cube[83] = c163;
        cube[89] = c157;
        cube[90] = c156;
        cube[107] = c139;
        cube[108] = c138;
        cube[109] = c137;
        cube[110] = c136;
        cube[111] = c135;
        cube[114] = c132;
        cube[115] = c131;
        cube[116] = c130;
        cube[117] = c129;
        cube[118] = c128;
        cube[121] = c125;
        cube[122] = c124;
        cube[124] = c122;
        cube[125] = c121;
        cube[128] = c118;
        cube[129] = c117;
        cube[130] = c116;
        cube[131] = c115;
        cube[132] = c114;
        cube[135] = c111;
        cube[136] = c110;
        cube[137] = c109;
        cube[138] = c108;
        cube[139] = c107;
        cube[156] = c90;
        cube[157] = c89;
        cube[163] = c83;
        cube[164] = c82;
        cube[170] = c76;
        cube[171] = c75;
        cube[177] = c69;
        cube[178] = c68;
        cube[184] = c62;
        cube[185] = c61;
        cube[254] = c41;
        cube[255] = c40;
        cube[256] = c39;
        cube[257] = c38;
        cube[258] = c37;
        cube[261] = c34;
        cube[262] = c33;
        cube[263] = c32;
        cube[264] = c31;
        cube[265] = c30;
        break;
    }

    case R: {
        char c156 = cube[156], c157 = cube[157], c158 = cube[158], c159 = cube[159],
             c160 = cube[160], c163 = cube[163], c164 = cube[164], c165 = cube[165],
             c166 = cube[166], c167 = cube[167], c170 = cube[170], c171 = cube[171],
             c173 = cube[173], c174 = cube[174], c177 = cube[177], c178 = cube[178],
             c179 = cube[179], c180 = cube[180], c181 = cube[181], c184 = cube[184],
             c185 = cube[185], c186 = cube[186], c187 = cube[187], c188 = cube[188];
        cube[156] = c184;
        cube[157] = c177;
        cube[158] = c170;
        cube[159] = c163;
        cube[160] = c156;
        cube[163] = c185;
        cube[164] = c178;
        cube[165] = c171;
        cube[166] = c164;
        cube[167] = c157;
        cube[170] = c186;
        cube[171] = c179;
        cube[173] = c165;
        cube[174] = c158;
        cube[177] = c187;
        cube[178] = c180;
        cube[179] = c173;
        cube[180] = c166;
        cube[181] = c159;
        cube[184] = c188;
        cube[185] = c181;
        cube[186] = c174;
        cube[187] = c167;
        cube[188] = c160;
        break;
    }

    case R_PRIME: {
        char c156 = cube[156], c157 = cube[157], c158 = cube[158], c159 = cube[159],
             c160 = cube[160], c163 = cube[163], c164 = cube[164], c165 = cube[165],
             c166 = cube[166], c167 = cube[167], c170 = cube[170], c171 = cube[171],
             c173 = cube[173], c174 = cube[174], c177 = cube[177], c178 = cube[178],
             c179 = cube[179], c180 = cube[180], c181 = cube[181], c184 = cube[184],
             c185 = cube[185], c186 = cube[186], c187 = cube[187], c188 = cube[188];
        cube[156] = c160;
        cube[157] = c167;
        cube[158] = c174;
        cube[159] = c181;
        cube[160] = c188;
        cube[163] = c159;
        cube[164] = c166;
        cube[165] = c173;
        cube[166] = c180;
        cube[167] = c187;
        cube[170] = c158;
        cube[171] = c165;
        cube[173] = c179;
        cube[174] = c186;
        cube[177] = c157;
        cube[178] = c164;
        cube[179] = c171;
        cube[180] = c178;
        cube[181] = c185;
        cube[184] = c156;
        cube[185] = c163;
        cube[186] = c170;
        cube[187] = c177;
        cube[188] = c184;
        break;
    }

    case R2: {
        char c156 = cube[156], c157 = cube[157], c158 = cube[158], c159 = cube[159],
             c160 = cube[160], c163 = cube[163], c164 = cube[164], c165 = cube[165],
             c166 = cube[166], c167 = cube[167], c170 = cube[170], c171 = cube[171],
             c173 = cube[173], c174 = cube[174], c177 = cube[177], c178 = cube[178],
             c179 = cube[179], c180 = cube[180], c181 = cube[181], c184 = cube[184],
             c185 = cube[185], c186 = cube[186], c187 = cube[187], c188 = cube[188];
        cube[156] = c188;
        cube[157] = c187;
        cube[158] = c186;
        cube[159] = c185;
        cube[160] = c184;
        cube[163] = c181;
        cube[164] = c180;
        cube[165] = c179;
        cube[166] = c178;
        cube[167] = c177;
        cube[170] = c174;
        cube[171] = c173;
        cube[173] = c171;
        cube[174] = c170;
        cube[177] = c167;
        cube[178] = c166;
        cube[179] = c165;
        cube[180] = c164;
        cube[181] = c163;
        cube[184] = c160;
        cube[185] = c159;
        cube[186] = c158;
        cube[187] = c157;
        cube[188] = c156;
        break;
    }

    case Rw: {
        char c13 = cube[13], c20 = cube[20], c27 = cube[27], c34 = cube[34],
             c41 = cube[41], c111 = cube[111], c118 = cube[118], c125 = cube[125],
             c132 = cube[132], c139 = cube[139], c156 = cube[156], c157 = cube[157],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c163 = cube[163],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c173 = cube[173], c174 = cube[174],
             c177 = cube[177], c178 = cube[178], c179 = cube[179], c180 = cube[180],
             c181 = cube[181], c184 = cube[184], c185 = cube[185], c186 = cube[186],
             c187 = cube[187], c188 = cube[188], c205 = cube[205], c212 = cube[212],
             c219 = cube[219], c226 = cube[226], c233 = cube[233], c258 = cube[258],
             c265 = cube[265], c272 = cube[272], c279 = cube[279], c286 = cube[286];
        cube[13] = c111;
        cube[20] = c118;
        cube[27] = c125;
        cube[34] = c132;
        cube[41] = c139;
        cube[111] = c258;
        cube[118] = c265;
        cube[125] = c272;
        cube[132] = c279;
        cube[139] = c286;
        cube[156] = c184;
        cube[157] = c177;
        cube[158] = c170;
        cube[159] = c163;
        cube[160] = c156;
        cube[163] = c185;
        cube[164] = c178;
        cube[165] = c171;
        cube[166] = c164;
        cube[167] = c157;
        cube[170] = c186;
        cube[171] = c179;
        cube[173] = c165;
        cube[174] = c158;
        cube[177] = c187;
        cube[178] = c180;
        cube[179] = c173;
        cube[180] = c166;
        cube[181] = c159;
        cube[184] = c188;
        cube[185] = c181;
        cube[186] = c174;
        cube[187] = c167;
        cube[188] = c160;
        cube[205] = c41;
        cube[212] = c34;
        cube[219] = c27;
        cube[226] = c20;
        cube[233] = c13;
        cube[258] = c233;
        cube[265] = c226;
        cube[272] = c219;
        cube[279] = c212;
        cube[286] = c205;
        break;
    }

    case Rw_PRIME: {
        char c13 = cube[13], c20 = cube[20], c27 = cube[27], c34 = cube[34],
             c41 = cube[41], c111 = cube[111], c118 = cube[118], c125 = cube[125],
             c132 = cube[132], c139 = cube[139], c156 = cube[156], c157 = cube[157],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c163 = cube[163],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c173 = cube[173], c174 = cube[174],
             c177 = cube[177], c178 = cube[178], c179 = cube[179], c180 = cube[180],
             c181 = cube[181], c184 = cube[184], c185 = cube[185], c186 = cube[186],
             c187 = cube[187], c188 = cube[188], c205 = cube[205], c212 = cube[212],
             c219 = cube[219], c226 = cube[226], c233 = cube[233], c258 = cube[258],
             c265 = cube[265], c272 = cube[272], c279 = cube[279], c286 = cube[286];
        cube[13] = c233;
        cube[20] = c226;
        cube[27] = c219;
        cube[34] = c212;
        cube[41] = c205;
        cube[111] = c13;
        cube[118] = c20;
        cube[125] = c27;
        cube[132] = c34;
        cube[139] = c41;
        cube[156] = c160;
        cube[157] = c167;
        cube[158] = c174;
        cube[159] = c181;
        cube[160] = c188;
        cube[163] = c159;
        cube[164] = c166;
        cube[165] = c173;
        cube[166] = c180;
        cube[167] = c187;
        cube[170] = c158;
        cube[171] = c165;
        cube[173] = c179;
        cube[174] = c186;
        cube[177] = c157;
        cube[178] = c164;
        cube[179] = c171;
        cube[180] = c178;
        cube[181] = c185;
        cube[184] = c156;
        cube[185] = c163;
        cube[186] = c170;
        cube[187] = c177;
        cube[188] = c184;
        cube[205] = c286;
        cube[212] = c279;
        cube[219] = c272;
        cube[226] = c265;
        cube[233] = c258;
        cube[258] = c111;
        cube[265] = c118;
        cube[272] = c125;
        cube[279] = c132;
        cube[286] = c139;
        break;
    }

    case Rw2: {
        char c13 = cube[13], c20 = cube[20], c27 = cube[27], c34 = cube[34],
             c41 = cube[41], c111 = cube[111], c118 = cube[118], c125 = cube[125],
             c132 = cube[132], c139 = cube[139], c156 = cube[156], c157 = cube[157],
             c158 = cube[158], c159 = cube[159], c160 = cube[160], c163 = cube[163],
             c164 = cube[164], c165 = cube[165], c166 = cube[166], c167 = cube[167],
             c170 = cube[170], c171 = cube[171], c173 = cube[173], c174 = cube[174],
             c177 = cube[177], c178 = cube[178], c179 = cube[179], c180 = cube[180],
             c181 = cube[181], c184 = cube[184], c185 = cube[185], c186 = cube[186],
             c187 = cube[187], c188 = cube[188], c205 = cube[205], c212 = cube[212],
             c219 = cube[219], c226 = cube[226], c233 = cube[233], c258 = cube[258],
             c265 = cube[265], c272 = cube[272], c279 = cube[279], c286 = cube[286];
        cube[13] = c258;
        cube[20] = c265;
        cube[27] = c272;
        cube[34] = c279;
        cube[41] = c286;
        cube[111] = c233;
        cube[118] = c226;
        cube[125] = c219;
        cube[132] = c212;
        cube[139] = c205;
        cube[156] = c188;
        cube[157] = c187;
        cube[158] = c186;
        cube[159] = c185;
        cube[160] = c184;
        cube[163] = c181;
        cube[164] = c180;
        cube[165] = c179;
        cube[166] = c178;
        cube[167] = c177;
        cube[170] = c174;
        cube[171] = c173;
        cube[173] = c171;
        cube[174] = c170;
        cube[177] = c167;
        cube[178] = c166;
        cube[179] = c165;
        cube[180] = c164;
        cube[181] = c163;
        cube[184] = c160;
        cube[185] = c159;
        cube[186] = c158;
        cube[187] = c157;
        cube[188] = c156;
        cube[205] = c139;
        cube[212] = c132;
        cube[219] = c125;
        cube[226] = c118;
        cube[233] = c111;
        cube[258] = c13;
        cube[265] = c20;
        cube[272] = c27;
        cube[279] = c34;
        cube[286] = c41;
        break;
    }

    case threeRw: {
        char c12 = cube[12], c13 = cube[13], c19 = cube[19], c20 = cube[20],
             c26 = cube[26], c27 = cube[27], c33 = cube[33], c34 = cube[34],
             c40 = cube[40], c41 = cube[41], c110 = cube[110], c111 = cube[111],
             c117 = cube[117], c118 = cube[118], c124 = cube[124], c125 = cube[125],
             c131 = cube[131], c132 = cube[132], c138 = cube[138], c139 = cube[139],
             c156 = cube[156], c157 = cube[157], c158 = cube[158], c159 = cube[159],
             c160 = cube[160], c163 = cube[163], c164 = cube[164], c165 = cube[165],
             c166 = cube[166], c167 = cube[167], c170 = cube[170], c171 = cube[171],
             c173 = cube[173], c174 = cube[174], c177 = cube[177], c178 = cube[178],
             c179 = cube[179], c180 = cube[180], c181 = cube[181], c184 = cube[184],
             c185 = cube[185], c186 = cube[186], c187 = cube[187], c188 = cube[188],
             c205 = cube[205], c206 = cube[206], c212 = cube[212], c213 = cube[213],
             c219 = cube[219], c220 = cube[220], c226 = cube[226], c227 = cube[227],
             c233 = cube[233], c234 = cube[234], c257 = cube[257], c258 = cube[258],
             c264 = cube[264], c265 = cube[265], c271 = cube[271], c272 = cube[272],
             c278 = cube[278], c279 = cube[279], c285 = cube[285], c286 = cube[286];
        cube[12] = c110;
        cube[13] = c111;
        cube[19] = c117;
        cube[20] = c118;
        cube[26] = c124;
        cube[27] = c125;
        cube[33] = c131;
        cube[34] = c132;
        cube[40] = c138;
        cube[41] = c139;
        cube[110] = c257;
        cube[111] = c258;
        cube[117] = c264;
        cube[118] = c265;
        cube[124] = c271;
        cube[125] = c272;
        cube[131] = c278;
        cube[132] = c279;
        cube[138] = c285;
        cube[139] = c286;
        cube[156] = c184;
        cube[157] = c177;
        cube[158] = c170;
        cube[159] = c163;
        cube[160] = c156;
        cube[163] = c185;
        cube[164] = c178;
        cube[165] = c171;
        cube[166] = c164;
        cube[167] = c157;
        cube[170] = c186;
        cube[171] = c179;
        cube[173] = c165;
        cube[174] = c158;
        cube[177] = c187;
        cube[178] = c180;
        cube[179] = c173;
        cube[180] = c166;
        cube[181] = c159;
        cube[184] = c188;
        cube[185] = c181;
        cube[186] = c174;
        cube[187] = c167;
        cube[188] = c160;
        cube[205] = c41;
        cube[206] = c40;
        cube[212] = c34;
        cube[213] = c33;
        cube[219] = c27;
        cube[220] = c26;
        cube[226] = c20;
        cube[227] = c19;
        cube[233] = c13;
        cube[234] = c12;
        cube[257] = c234;
        cube[258] = c233;
        cube[264] = c227;
        cube[265] = c226;
        cube[271] = c220;
        cube[272] = c219;
        cube[278] = c213;
        cube[279] = c212;
        cube[285] = c206;
        cube[286] = c205;
        break;
    }

    case threeRw_PRIME: {
        char c12 = cube[12], c13 = cube[13], c19 = cube[19], c20 = cube[20],
             c26 = cube[26], c27 = cube[27], c33 = cube[33], c34 = cube[34],
             c40 = cube[40], c41 = cube[41], c110 = cube[110], c111 = cube[111],
             c117 = cube[117], c118 = cube[118], c124 = cube[124], c125 = cube[125],
             c131 = cube[131], c132 = cube[132], c138 = cube[138], c139 = cube[139],
             c156 = cube[156], c157 = cube[157], c158 = cube[158], c159 = cube[159],
             c160 = cube[160], c163 = cube[163], c164 = cube[164], c165 = cube[165],
             c166 = cube[166], c167 = cube[167], c170 = cube[170], c171 = cube[171],
             c173 = cube[173], c174 = cube[174], c177 = cube[177], c178 = cube[178],
             c179 = cube[179], c180 = cube[180], c181 = cube[181], c184 = cube[184],
             c185 = cube[185], c186 = cube[186], c187 = cube[187], c188 = cube[188],
             c205 = cube[205], c206 = cube[206], c212 = cube[212], c213 = cube[213],
             c219 = cube[219], c220 = cube[220], c226 = cube[226], c227 = cube[227],
             c233 = cube[233], c234 = cube[234], c257 = cube[257], c258 = cube[258],
             c264 = cube[264], c265 = cube[265], c271 = cube[271], c272 = cube[272],
             c278 = cube[278], c279 = cube[279], c285 = cube[285], c286 = cube[286];
        cube[12] = c234;
        cube[13] = c233;
        cube[19] = c227;
        cube[20] = c226;
        cube[26] = c220;
        cube[27] = c219;
        cube[33] = c213;
        cube[34] = c212;
        cube[40] = c206;
        cube[41] = c205;
        cube[110] = c12;
        cube[111] = c13;
        cube[117] = c19;
        cube[118] = c20;
        cube[124] = c26;
        cube[125] = c27;
        cube[131] = c33;
        cube[132] = c34;
        cube[138] = c40;
        cube[139] = c41;
        cube[156] = c160;
        cube[157] = c167;
        cube[158] = c174;
        cube[159] = c181;
        cube[160] = c188;
        cube[163] = c159;
        cube[164] = c166;
        cube[165] = c173;
        cube[166] = c180;
        cube[167] = c187;
        cube[170] = c158;
        cube[171] = c165;
        cube[173] = c179;
        cube[174] = c186;
        cube[177] = c157;
        cube[178] = c164;
        cube[179] = c171;
        cube[180] = c178;
        cube[181] = c185;
        cube[184] = c156;
        cube[185] = c163;
        cube[186] = c170;
        cube[187] = c177;
        cube[188] = c184;
        cube[205] = c286;
        cube[206] = c285;
        cube[212] = c279;
        cube[213] = c278;
        cube[219] = c272;
        cube[220] = c271;
        cube[226] = c265;
        cube[227] = c264;
        cube[233] = c258;
        cube[234] = c257;
        cube[257] = c110;
        cube[258] = c111;
        cube[264] = c117;
        cube[265] = c118;
        cube[271] = c124;
        cube[272] = c125;
        cube[278] = c131;
        cube[279] = c132;
        cube[285] = c138;
        cube[286] = c139;
        break;
    }

    case threeRw2: {
        char c12 = cube[12], c13 = cube[13], c19 = cube[19], c20 = cube[20],
             c26 = cube[26], c27 = cube[27], c33 = cube[33], c34 = cube[34],
             c40 = cube[40], c41 = cube[41], c110 = cube[110], c111 = cube[111],
             c117 = cube[117], c118 = cube[118], c124 = cube[124], c125 = cube[125],
             c131 = cube[131], c132 = cube[132], c138 = cube[138], c139 = cube[139],
             c156 = cube[156], c157 = cube[157], c158 = cube[158], c159 = cube[159],
             c160 = cube[160], c163 = cube[163], c164 = cube[164], c165 = cube[165],
             c166 = cube[166], c167 = cube[167], c170 = cube[170], c171 = cube[171],
             c173 = cube[173], c174 = cube[174], c177 = cube[177], c178 = cube[178],
             c179 = cube[179], c180 = cube[180], c181 = cube[181], c184 = cube[184],
             c185 = cube[185], c186 = cube[186], c187 = cube[187], c188 = cube[188],
             c205 = cube[205], c206 = cube[206], c212 = cube[212], c213 = cube[213],
             c219 = cube[219], c220 = cube[220], c226 = cube[226], c227 = cube[227],
             c233 = cube[233], c234 = cube[234], c257 = cube[257], c258 = cube[258],
             c264 = cube[264], c265 = cube[265], c271 = cube[271], c272 = cube[272],
             c278 = cube[278], c279 = cube[279], c285 = cube[285], c286 = cube[286];
        cube[12] = c257;
        cube[13] = c258;
        cube[19] = c264;
        cube[20] = c265;
        cube[26] = c271;
        cube[27] = c272;
        cube[33] = c278;
        cube[34] = c279;
        cube[40] = c285;
        cube[41] = c286;
        cube[110] = c234;
        cube[111] = c233;
        cube[117] = c227;
        cube[118] = c226;
        cube[124] = c220;
        cube[125] = c219;
        cube[131] = c213;
        cube[132] = c212;
        cube[138] = c206;
        cube[139] = c205;
        cube[156] = c188;
        cube[157] = c187;
        cube[158] = c186;
        cube[159] = c185;
        cube[160] = c184;
        cube[163] = c181;
        cube[164] = c180;
        cube[165] = c179;
        cube[166] = c178;
        cube[167] = c177;
        cube[170] = c174;
        cube[171] = c173;
        cube[173] = c171;
        cube[174] = c170;
        cube[177] = c167;
        cube[178] = c166;
        cube[179] = c165;
        cube[180] = c164;
        cube[181] = c163;
        cube[184] = c160;
        cube[185] = c159;
        cube[186] = c158;
        cube[187] = c157;
        cube[188] = c156;
        cube[205] = c139;
        cube[206] = c138;
        cube[212] = c132;
        cube[213] = c131;
        cube[219] = c125;
        cube[220] = c124;
        cube[226] = c118;
        cube[227] = c117;
        cube[233] = c111;
        cube[234] = c110;
        cube[257] = c12;
        cube[258] = c13;
        cube[264] = c19;
        cube[265] = c20;
        cube[271] = c26;
        cube[272] = c27;
        cube[278] = c33;
        cube[279] = c34;
        cube[285] = c40;
        cube[286] = c41;
        break;
    }

    case B: {
        char c205 = cube[205], c206 = cube[206], c207 = cube[207], c208 = cube[208],
             c209 = cube[209], c212 = cube[212], c213 = cube[213], c214 = cube[214],
             c215 = cube[215], c216 = cube[216], c219 = cube[219], c220 = cube[220],
             c222 = cube[222], c223 = cube[223], c226 = cube[226], c227 = cube[227],
             c228 = cube[228], c229 = cube[229], c230 = cube[230], c233 = cube[233],
             c234 = cube[234], c235 = cube[235], c236 = cube[236], c237 = cube[237];
        cube[205] = c233;
        cube[206] = c226;
        cube[207] = c219;
        cube[208] = c212;
        cube[209] = c205;
        cube[212] = c234;
        cube[213] = c227;
        cube[214] = c220;
        cube[215] = c213;
        cube[216] = c206;
        cube[219] = c235;
        cube[220] = c228;
        cube[222] = c214;
        cube[223] = c207;
        cube[226] = c236;
        cube[227] = c229;
        cube[228] = c222;
        cube[229] = c215;
        cube[230] = c208;
        cube[233] = c237;
        cube[234] = c230;
        cube[235] = c223;
        cube[236] = c216;
        cube[237] = c209;
        break;
    }

    case B_PRIME: {
        char c205 = cube[205], c206 = cube[206], c207 = cube[207], c208 = cube[208],
             c209 = cube[209], c212 = cube[212], c213 = cube[213], c214 = cube[214],
             c215 = cube[215], c216 = cube[216], c219 = cube[219], c220 = cube[220],
             c222 = cube[222], c223 = cube[223], c226 = cube[226], c227 = cube[227],
             c228 = cube[228], c229 = cube[229], c230 = cube[230], c233 = cube[233],
             c234 = cube[234], c235 = cube[235], c236 = cube[236], c237 = cube[237];
        cube[205] = c209;
        cube[206] = c216;
        cube[207] = c223;
        cube[208] = c230;
        cube[209] = c237;
        cube[212] = c208;
        cube[213] = c215;
        cube[214] = c222;
        cube[215] = c229;
        cube[216] = c236;
        cube[219] = c207;
        cube[220] = c214;
        cube[222] = c228;
        cube[223] = c235;
        cube[226] = c206;
        cube[227] = c213;
        cube[228] = c220;
        cube[229] = c227;
        cube[230] = c234;
        cube[233] = c205;
        cube[234] = c212;
        cube[235] = c219;
        cube[236] = c226;
        cube[237] = c233;
        break;
    }

    case B2: {
        char c205 = cube[205], c206 = cube[206], c207 = cube[207], c208 = cube[208],
             c209 = cube[209], c212 = cube[212], c213 = cube[213], c214 = cube[214],
             c215 = cube[215], c216 = cube[216], c219 = cube[219], c220 = cube[220],
             c222 = cube[222], c223 = cube[223], c226 = cube[226], c227 = cube[227],
             c228 = cube[228], c229 = cube[229], c230 = cube[230], c233 = cube[233],
             c234 = cube[234], c235 = cube[235], c236 = cube[236], c237 = cube[237];
        cube[205] = c237;
        cube[206] = c236;
        cube[207] = c235;
        cube[208] = c234;
        cube[209] = c233;
        cube[212] = c230;
        cube[213] = c229;
        cube[214] = c228;
        cube[215] = c227;
        cube[216] = c226;
        cube[219] = c223;
        cube[220] = c222;
        cube[222] = c220;
        cube[223] = c219;
        cube[226] = c216;
        cube[227] = c215;
        cube[228] = c214;
        cube[229] = c213;
        cube[230] = c212;
        cube[233] = c209;
        cube[234] = c208;
        cube[235] = c207;
        cube[236] = c206;
        cube[237] = c205;
        break;
    }

    case Bw: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c58 = cube[58], c65 = cube[65], c72 = cube[72],
             c79 = cube[79], c86 = cube[86], c160 = cube[160], c167 = cube[167],
             c174 = cube[174], c181 = cube[181], c188 = cube[188], c205 = cube[205],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209],
             c212 = cube[212], c213 = cube[213], c214 = cube[214], c215 = cube[215],
             c216 = cube[216], c219 = cube[219], c220 = cube[220], c222 = cube[222],
             c223 = cube[223], c226 = cube[226], c227 = cube[227], c228 = cube[228],
             c229 = cube[229], c230 = cube[230], c233 = cube[233], c234 = cube[234],
             c235 = cube[235], c236 = cube[236], c237 = cube[237], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[9] = c160;
        cube[10] = c167;
        cube[11] = c174;
        cube[12] = c181;
        cube[13] = c188;
        cube[58] = c13;
        cube[65] = c12;
        cube[72] = c11;
        cube[79] = c10;
        cube[86] = c9;
        cube[160] = c286;
        cube[167] = c285;
        cube[174] = c284;
        cube[181] = c283;
        cube[188] = c282;
        cube[205] = c233;
        cube[206] = c226;
        cube[207] = c219;
        cube[208] = c212;
        cube[209] = c205;
        cube[212] = c234;
        cube[213] = c227;
        cube[214] = c220;
        cube[215] = c213;
        cube[216] = c206;
        cube[219] = c235;
        cube[220] = c228;
        cube[222] = c214;
        cube[223] = c207;
        cube[226] = c236;
        cube[227] = c229;
        cube[228] = c222;
        cube[229] = c215;
        cube[230] = c208;
        cube[233] = c237;
        cube[234] = c230;
        cube[235] = c223;
        cube[236] = c216;
        cube[237] = c209;
        cube[282] = c58;
        cube[283] = c65;
        cube[284] = c72;
        cube[285] = c79;
        cube[286] = c86;
        break;
    }

    case Bw_PRIME: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c58 = cube[58], c65 = cube[65], c72 = cube[72],
             c79 = cube[79], c86 = cube[86], c160 = cube[160], c167 = cube[167],
             c174 = cube[174], c181 = cube[181], c188 = cube[188], c205 = cube[205],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209],
             c212 = cube[212], c213 = cube[213], c214 = cube[214], c215 = cube[215],
             c216 = cube[216], c219 = cube[219], c220 = cube[220], c222 = cube[222],
             c223 = cube[223], c226 = cube[226], c227 = cube[227], c228 = cube[228],
             c229 = cube[229], c230 = cube[230], c233 = cube[233], c234 = cube[234],
             c235 = cube[235], c236 = cube[236], c237 = cube[237], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[9] = c86;
        cube[10] = c79;
        cube[11] = c72;
        cube[12] = c65;
        cube[13] = c58;
        cube[58] = c282;
        cube[65] = c283;
        cube[72] = c284;
        cube[79] = c285;
        cube[86] = c286;
        cube[160] = c9;
        cube[167] = c10;
        cube[174] = c11;
        cube[181] = c12;
        cube[188] = c13;
        cube[205] = c209;
        cube[206] = c216;
        cube[207] = c223;
        cube[208] = c230;
        cube[209] = c237;
        cube[212] = c208;
        cube[213] = c215;
        cube[214] = c222;
        cube[215] = c229;
        cube[216] = c236;
        cube[219] = c207;
        cube[220] = c214;
        cube[222] = c228;
        cube[223] = c235;
        cube[226] = c206;
        cube[227] = c213;
        cube[228] = c220;
        cube[229] = c227;
        cube[230] = c234;
        cube[233] = c205;
        cube[234] = c212;
        cube[235] = c219;
        cube[236] = c226;
        cube[237] = c233;
        cube[282] = c188;
        cube[283] = c181;
        cube[284] = c174;
        cube[285] = c167;
        cube[286] = c160;
        break;
    }

    case Bw2: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c58 = cube[58], c65 = cube[65], c72 = cube[72],
             c79 = cube[79], c86 = cube[86], c160 = cube[160], c167 = cube[167],
             c174 = cube[174], c181 = cube[181], c188 = cube[188], c205 = cube[205],
             c206 = cube[206], c207 = cube[207], c208 = cube[208], c209 = cube[209],
             c212 = cube[212], c213 = cube[213], c214 = cube[214], c215 = cube[215],
             c216 = cube[216], c219 = cube[219], c220 = cube[220], c222 = cube[222],
             c223 = cube[223], c226 = cube[226], c227 = cube[227], c228 = cube[228],
             c229 = cube[229], c230 = cube[230], c233 = cube[233], c234 = cube[234],
             c235 = cube[235], c236 = cube[236], c237 = cube[237], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[9] = c286;
        cube[10] = c285;
        cube[11] = c284;
        cube[12] = c283;
        cube[13] = c282;
        cube[58] = c188;
        cube[65] = c181;
        cube[72] = c174;
        cube[79] = c167;
        cube[86] = c160;
        cube[160] = c86;
        cube[167] = c79;
        cube[174] = c72;
        cube[181] = c65;
        cube[188] = c58;
        cube[205] = c237;
        cube[206] = c236;
        cube[207] = c235;
        cube[208] = c234;
        cube[209] = c233;
        cube[212] = c230;
        cube[213] = c229;
        cube[214] = c228;
        cube[215] = c227;
        cube[216] = c226;
        cube[219] = c223;
        cube[220] = c222;
        cube[222] = c220;
        cube[223] = c219;
        cube[226] = c216;
        cube[227] = c215;
        cube[228] = c214;
        cube[229] = c213;
        cube[230] = c212;
        cube[233] = c209;
        cube[234] = c208;
        cube[235] = c207;
        cube[236] = c206;
        cube[237] = c205;
        cube[282] = c13;
        cube[283] = c12;
        cube[284] = c11;
        cube[285] = c10;
        cube[286] = c9;
        break;
    }

    case threeBw: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c58 = cube[58], c59 = cube[59],
             c65 = cube[65], c66 = cube[66], c72 = cube[72], c73 = cube[73],
             c79 = cube[79], c80 = cube[80], c86 = cube[86], c87 = cube[87],
             c159 = cube[159], c160 = cube[160], c166 = cube[166], c167 = cube[167],
             c173 = cube[173], c174 = cube[174], c180 = cube[180], c181 = cube[181],
             c187 = cube[187], c188 = cube[188], c205 = cube[205], c206 = cube[206],
             c207 = cube[207], c208 = cube[208], c209 = cube[209], c212 = cube[212],
             c213 = cube[213], c214 = cube[214], c215 = cube[215], c216 = cube[216],
             c219 = cube[219], c220 = cube[220], c222 = cube[222], c223 = cube[223],
             c226 = cube[226], c227 = cube[227], c228 = cube[228], c229 = cube[229],
             c230 = cube[230], c233 = cube[233], c234 = cube[234], c235 = cube[235],
             c236 = cube[236], c237 = cube[237], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[9] = c160;
        cube[10] = c167;
        cube[11] = c174;
        cube[12] = c181;
        cube[13] = c188;
        cube[16] = c159;
        cube[17] = c166;
        cube[18] = c173;
        cube[19] = c180;
        cube[20] = c187;
        cube[58] = c13;
        cube[59] = c20;
        cube[65] = c12;
        cube[66] = c19;
        cube[72] = c11;
        cube[73] = c18;
        cube[79] = c10;
        cube[80] = c17;
        cube[86] = c9;
        cube[87] = c16;
        cube[159] = c279;
        cube[160] = c286;
        cube[166] = c278;
        cube[167] = c285;
        cube[173] = c277;
        cube[174] = c284;
        cube[180] = c276;
        cube[181] = c283;
        cube[187] = c275;
        cube[188] = c282;
        cube[205] = c233;
        cube[206] = c226;
        cube[207] = c219;
        cube[208] = c212;
        cube[209] = c205;
        cube[212] = c234;
        cube[213] = c227;
        cube[214] = c220;
        cube[215] = c213;
        cube[216] = c206;
        cube[219] = c235;
        cube[220] = c228;
        cube[222] = c214;
        cube[223] = c207;
        cube[226] = c236;
        cube[227] = c229;
        cube[228] = c222;
        cube[229] = c215;
        cube[230] = c208;
        cube[233] = c237;
        cube[234] = c230;
        cube[235] = c223;
        cube[236] = c216;
        cube[237] = c209;
        cube[275] = c59;
        cube[276] = c66;
        cube[277] = c73;
        cube[278] = c80;
        cube[279] = c87;
        cube[282] = c58;
        cube[283] = c65;
        cube[284] = c72;
        cube[285] = c79;
        cube[286] = c86;
        break;
    }

    case threeBw_PRIME: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c58 = cube[58], c59 = cube[59],
             c65 = cube[65], c66 = cube[66], c72 = cube[72], c73 = cube[73],
             c79 = cube[79], c80 = cube[80], c86 = cube[86], c87 = cube[87],
             c159 = cube[159], c160 = cube[160], c166 = cube[166], c167 = cube[167],
             c173 = cube[173], c174 = cube[174], c180 = cube[180], c181 = cube[181],
             c187 = cube[187], c188 = cube[188], c205 = cube[205], c206 = cube[206],
             c207 = cube[207], c208 = cube[208], c209 = cube[209], c212 = cube[212],
             c213 = cube[213], c214 = cube[214], c215 = cube[215], c216 = cube[216],
             c219 = cube[219], c220 = cube[220], c222 = cube[222], c223 = cube[223],
             c226 = cube[226], c227 = cube[227], c228 = cube[228], c229 = cube[229],
             c230 = cube[230], c233 = cube[233], c234 = cube[234], c235 = cube[235],
             c236 = cube[236], c237 = cube[237], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[9] = c86;
        cube[10] = c79;
        cube[11] = c72;
        cube[12] = c65;
        cube[13] = c58;
        cube[16] = c87;
        cube[17] = c80;
        cube[18] = c73;
        cube[19] = c66;
        cube[20] = c59;
        cube[58] = c282;
        cube[59] = c275;
        cube[65] = c283;
        cube[66] = c276;
        cube[72] = c284;
        cube[73] = c277;
        cube[79] = c285;
        cube[80] = c278;
        cube[86] = c286;
        cube[87] = c279;
        cube[159] = c16;
        cube[160] = c9;
        cube[166] = c17;
        cube[167] = c10;
        cube[173] = c18;
        cube[174] = c11;
        cube[180] = c19;
        cube[181] = c12;
        cube[187] = c20;
        cube[188] = c13;
        cube[205] = c209;
        cube[206] = c216;
        cube[207] = c223;
        cube[208] = c230;
        cube[209] = c237;
        cube[212] = c208;
        cube[213] = c215;
        cube[214] = c222;
        cube[215] = c229;
        cube[216] = c236;
        cube[219] = c207;
        cube[220] = c214;
        cube[222] = c228;
        cube[223] = c235;
        cube[226] = c206;
        cube[227] = c213;
        cube[228] = c220;
        cube[229] = c227;
        cube[230] = c234;
        cube[233] = c205;
        cube[234] = c212;
        cube[235] = c219;
        cube[236] = c226;
        cube[237] = c233;
        cube[275] = c187;
        cube[276] = c180;
        cube[277] = c173;
        cube[278] = c166;
        cube[279] = c159;
        cube[282] = c188;
        cube[283] = c181;
        cube[284] = c174;
        cube[285] = c167;
        cube[286] = c160;
        break;
    }

    case threeBw2: {
        char c9 = cube[9], c10 = cube[10], c11 = cube[11], c12 = cube[12],
             c13 = cube[13], c16 = cube[16], c17 = cube[17], c18 = cube[18],
             c19 = cube[19], c20 = cube[20], c58 = cube[58], c59 = cube[59],
             c65 = cube[65], c66 = cube[66], c72 = cube[72], c73 = cube[73],
             c79 = cube[79], c80 = cube[80], c86 = cube[86], c87 = cube[87],
             c159 = cube[159], c160 = cube[160], c166 = cube[166], c167 = cube[167],
             c173 = cube[173], c174 = cube[174], c180 = cube[180], c181 = cube[181],
             c187 = cube[187], c188 = cube[188], c205 = cube[205], c206 = cube[206],
             c207 = cube[207], c208 = cube[208], c209 = cube[209], c212 = cube[212],
             c213 = cube[213], c214 = cube[214], c215 = cube[215], c216 = cube[216],
             c219 = cube[219], c220 = cube[220], c222 = cube[222], c223 = cube[223],
             c226 = cube[226], c227 = cube[227], c228 = cube[228], c229 = cube[229],
             c230 = cube[230], c233 = cube[233], c234 = cube[234], c235 = cube[235],
             c236 = cube[236], c237 = cube[237], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[9] = c286;
        cube[10] = c285;
        cube[11] = c284;
        cube[12] = c283;
        cube[13] = c282;
        cube[16] = c279;
        cube[17] = c278;
        cube[18] = c277;
        cube[19] = c276;
        cube[20] = c275;
        cube[58] = c188;
        cube[59] = c187;
        cube[65] = c181;
        cube[66] = c180;
        cube[72] = c174;
        cube[73] = c173;
        cube[79] = c167;
        cube[80] = c166;
        cube[86] = c160;
        cube[87] = c159;
        cube[159] = c87;
        cube[160] = c86;
        cube[166] = c80;
        cube[167] = c79;
        cube[173] = c73;
        cube[174] = c72;
        cube[180] = c66;
        cube[181] = c65;
        cube[187] = c59;
        cube[188] = c58;
        cube[205] = c237;
        cube[206] = c236;
        cube[207] = c235;
        cube[208] = c234;
        cube[209] = c233;
        cube[212] = c230;
        cube[213] = c229;
        cube[214] = c228;
        cube[215] = c227;
        cube[216] = c226;
        cube[219] = c223;
        cube[220] = c222;
        cube[222] = c220;
        cube[223] = c219;
        cube[226] = c216;
        cube[227] = c215;
        cube[228] = c214;
        cube[229] = c213;
        cube[230] = c212;
        cube[233] = c209;
        cube[234] = c208;
        cube[235] = c207;
        cube[236] = c206;
        cube[237] = c205;
        cube[275] = c20;
        cube[276] = c19;
        cube[277] = c18;
        cube[278] = c17;
        cube[279] = c16;
        cube[282] = c13;
        cube[283] = c12;
        cube[284] = c11;
        cube[285] = c10;
        cube[286] = c9;
        break;
    }

    case D: {
        char c254 = cube[254], c255 = cube[255], c256 = cube[256], c257 = cube[257],
             c258 = cube[258], c261 = cube[261], c262 = cube[262], c263 = cube[263],
             c264 = cube[264], c265 = cube[265], c268 = cube[268], c269 = cube[269],
             c271 = cube[271], c272 = cube[272], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[254] = c282;
        cube[255] = c275;
        cube[256] = c268;
        cube[257] = c261;
        cube[258] = c254;
        cube[261] = c283;
        cube[262] = c276;
        cube[263] = c269;
        cube[264] = c262;
        cube[265] = c255;
        cube[268] = c284;
        cube[269] = c277;
        cube[271] = c263;
        cube[272] = c256;
        cube[275] = c285;
        cube[276] = c278;
        cube[277] = c271;
        cube[278] = c264;
        cube[279] = c257;
        cube[282] = c286;
        cube[283] = c279;
        cube[284] = c272;
        cube[285] = c265;
        cube[286] = c258;
        break;
    }

    case D_PRIME: {
        char c254 = cube[254], c255 = cube[255], c256 = cube[256], c257 = cube[257],
             c258 = cube[258], c261 = cube[261], c262 = cube[262], c263 = cube[263],
             c264 = cube[264], c265 = cube[265], c268 = cube[268], c269 = cube[269],
             c271 = cube[271], c272 = cube[272], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[254] = c258;
        cube[255] = c265;
        cube[256] = c272;
        cube[257] = c279;
        cube[258] = c286;
        cube[261] = c257;
        cube[262] = c264;
        cube[263] = c271;
        cube[264] = c278;
        cube[265] = c285;
        cube[268] = c256;
        cube[269] = c263;
        cube[271] = c277;
        cube[272] = c284;
        cube[275] = c255;
        cube[276] = c262;
        cube[277] = c269;
        cube[278] = c276;
        cube[279] = c283;
        cube[282] = c254;
        cube[283] = c261;
        cube[284] = c268;
        cube[285] = c275;
        cube[286] = c282;
        break;
    }

    case D2: {
        char c254 = cube[254], c255 = cube[255], c256 = cube[256], c257 = cube[257],
             c258 = cube[258], c261 = cube[261], c262 = cube[262], c263 = cube[263],
             c264 = cube[264], c265 = cube[265], c268 = cube[268], c269 = cube[269],
             c271 = cube[271], c272 = cube[272], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[254] = c286;
        cube[255] = c285;
        cube[256] = c284;
        cube[257] = c283;
        cube[258] = c282;
        cube[261] = c279;
        cube[262] = c278;
        cube[263] = c277;
        cube[264] = c276;
        cube[265] = c275;
        cube[268] = c272;
        cube[269] = c271;
        cube[271] = c269;
        cube[272] = c268;
        cube[275] = c265;
        cube[276] = c264;
        cube[277] = c263;
        cube[278] = c262;
        cube[279] = c261;
        cube[282] = c258;
        cube[283] = c257;
        cube[284] = c256;
        cube[285] = c255;
        cube[286] = c254;
        break;
    }

    case Dw: {
        char c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c90 = cube[90], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c138 = cube[138], c139 = cube[139], c184 = cube[184], c185 = cube[185],
             c186 = cube[186], c187 = cube[187], c188 = cube[188], c233 = cube[233],
             c234 = cube[234], c235 = cube[235], c236 = cube[236], c237 = cube[237],
             c254 = cube[254], c255 = cube[255], c256 = cube[256], c257 = cube[257],
             c258 = cube[258], c261 = cube[261], c262 = cube[262], c263 = cube[263],
             c264 = cube[264], c265 = cube[265], c268 = cube[268], c269 = cube[269],
             c271 = cube[271], c272 = cube[272], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[86] = c233;
        cube[87] = c234;
        cube[88] = c235;
        cube[89] = c236;
        cube[90] = c237;
        cube[135] = c86;
        cube[136] = c87;
        cube[137] = c88;
        cube[138] = c89;
        cube[139] = c90;
        cube[184] = c135;
        cube[185] = c136;
        cube[186] = c137;
        cube[187] = c138;
        cube[188] = c139;
        cube[233] = c184;
        cube[234] = c185;
        cube[235] = c186;
        cube[236] = c187;
        cube[237] = c188;
        cube[254] = c282;
        cube[255] = c275;
        cube[256] = c268;
        cube[257] = c261;
        cube[258] = c254;
        cube[261] = c283;
        cube[262] = c276;
        cube[263] = c269;
        cube[264] = c262;
        cube[265] = c255;
        cube[268] = c284;
        cube[269] = c277;
        cube[271] = c263;
        cube[272] = c256;
        cube[275] = c285;
        cube[276] = c278;
        cube[277] = c271;
        cube[278] = c264;
        cube[279] = c257;
        cube[282] = c286;
        cube[283] = c279;
        cube[284] = c272;
        cube[285] = c265;
        cube[286] = c258;
        break;
    }

    case Dw_PRIME: {
        char c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c90 = cube[90], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c138 = cube[138], c139 = cube[139], c184 = cube[184], c185 = cube[185],
             c186 = cube[186], c187 = cube[187], c188 = cube[188], c233 = cube[233],
             c234 = cube[234], c235 = cube[235], c236 = cube[236], c237 = cube[237],
             c254 = cube[254], c255 = cube[255], c256 = cube[256], c257 = cube[257],
             c258 = cube[258], c261 = cube[261], c262 = cube[262], c263 = cube[263],
             c264 = cube[264], c265 = cube[265], c268 = cube[268], c269 = cube[269],
             c271 = cube[271], c272 = cube[272], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[86] = c135;
        cube[87] = c136;
        cube[88] = c137;
        cube[89] = c138;
        cube[90] = c139;
        cube[135] = c184;
        cube[136] = c185;
        cube[137] = c186;
        cube[138] = c187;
        cube[139] = c188;
        cube[184] = c233;
        cube[185] = c234;
        cube[186] = c235;
        cube[187] = c236;
        cube[188] = c237;
        cube[233] = c86;
        cube[234] = c87;
        cube[235] = c88;
        cube[236] = c89;
        cube[237] = c90;
        cube[254] = c258;
        cube[255] = c265;
        cube[256] = c272;
        cube[257] = c279;
        cube[258] = c286;
        cube[261] = c257;
        cube[262] = c264;
        cube[263] = c271;
        cube[264] = c278;
        cube[265] = c285;
        cube[268] = c256;
        cube[269] = c263;
        cube[271] = c277;
        cube[272] = c284;
        cube[275] = c255;
        cube[276] = c262;
        cube[277] = c269;
        cube[278] = c276;
        cube[279] = c283;
        cube[282] = c254;
        cube[283] = c261;
        cube[284] = c268;
        cube[285] = c275;
        cube[286] = c282;
        break;
    }

    case Dw2: {
        char c86 = cube[86], c87 = cube[87], c88 = cube[88], c89 = cube[89],
             c90 = cube[90], c135 = cube[135], c136 = cube[136], c137 = cube[137],
             c138 = cube[138], c139 = cube[139], c184 = cube[184], c185 = cube[185],
             c186 = cube[186], c187 = cube[187], c188 = cube[188], c233 = cube[233],
             c234 = cube[234], c235 = cube[235], c236 = cube[236], c237 = cube[237],
             c254 = cube[254], c255 = cube[255], c256 = cube[256], c257 = cube[257],
             c258 = cube[258], c261 = cube[261], c262 = cube[262], c263 = cube[263],
             c264 = cube[264], c265 = cube[265], c268 = cube[268], c269 = cube[269],
             c271 = cube[271], c272 = cube[272], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[86] = c184;
        cube[87] = c185;
        cube[88] = c186;
        cube[89] = c187;
        cube[90] = c188;
        cube[135] = c233;
        cube[136] = c234;
        cube[137] = c235;
        cube[138] = c236;
        cube[139] = c237;
        cube[184] = c86;
        cube[185] = c87;
        cube[186] = c88;
        cube[187] = c89;
        cube[188] = c90;
        cube[233] = c135;
        cube[234] = c136;
        cube[235] = c137;
        cube[236] = c138;
        cube[237] = c139;
        cube[254] = c286;
        cube[255] = c285;
        cube[256] = c284;
        cube[257] = c283;
        cube[258] = c282;
        cube[261] = c279;
        cube[262] = c278;
        cube[263] = c277;
        cube[264] = c276;
        cube[265] = c275;
        cube[268] = c272;
        cube[269] = c271;
        cube[271] = c269;
        cube[272] = c268;
        cube[275] = c265;
        cube[276] = c264;
        cube[277] = c263;
        cube[278] = c262;
        cube[279] = c261;
        cube[282] = c258;
        cube[283] = c257;
        cube[284] = c256;
        cube[285] = c255;
        cube[286] = c254;
        break;
    }

    case threeDw: {
        char c79 = cube[79], c80 = cube[80], c81 = cube[81], c82 = cube[82],
             c83 = cube[83], c86 = cube[86], c87 = cube[87], c88 = cube[88],
             c89 = cube[89], c90 = cube[90], c128 = cube[128], c129 = cube[129],
             c130 = cube[130], c131 = cube[131], c132 = cube[132], c135 = cube[135],
             c136 = cube[136], c137 = cube[137], c138 = cube[138], c139 = cube[139],
             c177 = cube[177], c178 = cube[178], c179 = cube[179], c180 = cube[180],
             c181 = cube[181], c184 = cube[184], c185 = cube[185], c186 = cube[186],
             c187 = cube[187], c188 = cube[188], c226 = cube[226], c227 = cube[227],
             c228 = cube[228], c229 = cube[229], c230 = cube[230], c233 = cube[233],
             c234 = cube[234], c235 = cube[235], c236 = cube[236], c237 = cube[237],
             c254 = cube[254], c255 = cube[255], c256 = cube[256], c257 = cube[257],
             c258 = cube[258], c261 = cube[261], c262 = cube[262], c263 = cube[263],
             c264 = cube[264], c265 = cube[265], c268 = cube[268], c269 = cube[269],
             c271 = cube[271], c272 = cube[272], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[79] = c226;
        cube[80] = c227;
        cube[81] = c228;
        cube[82] = c229;
        cube[83] = c230;
        cube[86] = c233;
        cube[87] = c234;
        cube[88] = c235;
        cube[89] = c236;
        cube[90] = c237;
        cube[128] = c79;
        cube[129] = c80;
        cube[130] = c81;
        cube[131] = c82;
        cube[132] = c83;
        cube[135] = c86;
        cube[136] = c87;
        cube[137] = c88;
        cube[138] = c89;
        cube[139] = c90;
        cube[177] = c128;
        cube[178] = c129;
        cube[179] = c130;
        cube[180] = c131;
        cube[181] = c132;
        cube[184] = c135;
        cube[185] = c136;
        cube[186] = c137;
        cube[187] = c138;
        cube[188] = c139;
        cube[226] = c177;
        cube[227] = c178;
        cube[228] = c179;
        cube[229] = c180;
        cube[230] = c181;
        cube[233] = c184;
        cube[234] = c185;
        cube[235] = c186;
        cube[236] = c187;
        cube[237] = c188;
        cube[254] = c282;
        cube[255] = c275;
        cube[256] = c268;
        cube[257] = c261;
        cube[258] = c254;
        cube[261] = c283;
        cube[262] = c276;
        cube[263] = c269;
        cube[264] = c262;
        cube[265] = c255;
        cube[268] = c284;
        cube[269] = c277;
        cube[271] = c263;
        cube[272] = c256;
        cube[275] = c285;
        cube[276] = c278;
        cube[277] = c271;
        cube[278] = c264;
        cube[279] = c257;
        cube[282] = c286;
        cube[283] = c279;
        cube[284] = c272;
        cube[285] = c265;
        cube[286] = c258;
        break;
    }

    case threeDw_PRIME: {
        char c79 = cube[79], c80 = cube[80], c81 = cube[81], c82 = cube[82],
             c83 = cube[83], c86 = cube[86], c87 = cube[87], c88 = cube[88],
             c89 = cube[89], c90 = cube[90], c128 = cube[128], c129 = cube[129],
             c130 = cube[130], c131 = cube[131], c132 = cube[132], c135 = cube[135],
             c136 = cube[136], c137 = cube[137], c138 = cube[138], c139 = cube[139],
             c177 = cube[177], c178 = cube[178], c179 = cube[179], c180 = cube[180],
             c181 = cube[181], c184 = cube[184], c185 = cube[185], c186 = cube[186],
             c187 = cube[187], c188 = cube[188], c226 = cube[226], c227 = cube[227],
             c228 = cube[228], c229 = cube[229], c230 = cube[230], c233 = cube[233],
             c234 = cube[234], c235 = cube[235], c236 = cube[236], c237 = cube[237],
             c254 = cube[254], c255 = cube[255], c256 = cube[256], c257 = cube[257],
             c258 = cube[258], c261 = cube[261], c262 = cube[262], c263 = cube[263],
             c264 = cube[264], c265 = cube[265], c268 = cube[268], c269 = cube[269],
             c271 = cube[271], c272 = cube[272], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[79] = c128;
        cube[80] = c129;
        cube[81] = c130;
        cube[82] = c131;
        cube[83] = c132;
        cube[86] = c135;
        cube[87] = c136;
        cube[88] = c137;
        cube[89] = c138;
        cube[90] = c139;
        cube[128] = c177;
        cube[129] = c178;
        cube[130] = c179;
        cube[131] = c180;
        cube[132] = c181;
        cube[135] = c184;
        cube[136] = c185;
        cube[137] = c186;
        cube[138] = c187;
        cube[139] = c188;
        cube[177] = c226;
        cube[178] = c227;
        cube[179] = c228;
        cube[180] = c229;
        cube[181] = c230;
        cube[184] = c233;
        cube[185] = c234;
        cube[186] = c235;
        cube[187] = c236;
        cube[188] = c237;
        cube[226] = c79;
        cube[227] = c80;
        cube[228] = c81;
        cube[229] = c82;
        cube[230] = c83;
        cube[233] = c86;
        cube[234] = c87;
        cube[235] = c88;
        cube[236] = c89;
        cube[237] = c90;
        cube[254] = c258;
        cube[255] = c265;
        cube[256] = c272;
        cube[257] = c279;
        cube[258] = c286;
        cube[261] = c257;
        cube[262] = c264;
        cube[263] = c271;
        cube[264] = c278;
        cube[265] = c285;
        cube[268] = c256;
        cube[269] = c263;
        cube[271] = c277;
        cube[272] = c284;
        cube[275] = c255;
        cube[276] = c262;
        cube[277] = c269;
        cube[278] = c276;
        cube[279] = c283;
        cube[282] = c254;
        cube[283] = c261;
        cube[284] = c268;
        cube[285] = c275;
        cube[286] = c282;
        break;
    }

    case threeDw2: {
        char c79 = cube[79], c80 = cube[80], c81 = cube[81], c82 = cube[82],
             c83 = cube[83], c86 = cube[86], c87 = cube[87], c88 = cube[88],
             c89 = cube[89], c90 = cube[90], c128 = cube[128], c129 = cube[129],
             c130 = cube[130], c131 = cube[131], c132 = cube[132], c135 = cube[135],
             c136 = cube[136], c137 = cube[137], c138 = cube[138], c139 = cube[139],
             c177 = cube[177], c178 = cube[178], c179 = cube[179], c180 = cube[180],
             c181 = cube[181], c184 = cube[184], c185 = cube[185], c186 = cube[186],
             c187 = cube[187], c188 = cube[188], c226 = cube[226], c227 = cube[227],
             c228 = cube[228], c229 = cube[229], c230 = cube[230], c233 = cube[233],
             c234 = cube[234], c235 = cube[235], c236 = cube[236], c237 = cube[237],
             c254 = cube[254], c255 = cube[255], c256 = cube[256], c257 = cube[257],
             c258 = cube[258], c261 = cube[261], c262 = cube[262], c263 = cube[263],
             c264 = cube[264], c265 = cube[265], c268 = cube[268], c269 = cube[269],
             c271 = cube[271], c272 = cube[272], c275 = cube[275], c276 = cube[276],
             c277 = cube[277], c278 = cube[278], c279 = cube[279], c282 = cube[282],
             c283 = cube[283], c284 = cube[284], c285 = cube[285], c286 = cube[286];
        cube[79] = c177;
        cube[80] = c178;
        cube[81] = c179;
        cube[82] = c180;
        cube[83] = c181;
        cube[86] = c184;
        cube[87] = c185;
        cube[88] = c186;
        cube[89] = c187;
        cube[90] = c188;
        cube[128] = c226;
        cube[129] = c227;
        cube[130] = c228;
        cube[131] = c229;
        cube[132] = c230;
        cube[135] = c233;
        cube[136] = c234;
        cube[137] = c235;
        cube[138] = c236;
        cube[139] = c237;
        cube[177] = c79;
        cube[178] = c80;
        cube[179] = c81;
        cube[180] = c82;
        cube[181] = c83;
        cube[184] = c86;
        cube[185] = c87;
        cube[186] = c88;
        cube[187] = c89;
        cube[188] = c90;
        cube[226] = c128;
        cube[227] = c129;
        cube[228] = c130;
        cube[229] = c131;
        cube[230] = c132;
        cube[233] = c135;
        cube[234] = c136;
        cube[235] = c137;
        cube[236] = c138;
        cube[237] = c139;
        cube[254] = c286;
        cube[255] = c285;
        cube[256] = c284;
        cube[257] = c283;
        cube[258] = c282;
        cube[261] = c279;
        cube[262] = c278;
        cube[263] = c277;
        cube[264] = c276;
        cube[265] = c275;
        cube[268] = c272;
        cube[269] = c271;
        cube[271] = c269;
        cube[272] = c268;
        cube[275] = c265;
        cube[276] = c264;
        cube[277] = c263;
        cube[278] = c262;
        cube[279] = c261;
        cube[282] = c258;
        cube[283] = c257;
        cube[284] = c256;
        cube[285] = c255;
        cube[286] = c254;
        break;
    }


    default:
        printf("ERROR: invalid move %d\n", move);
        exit(1);
    }
}
            
