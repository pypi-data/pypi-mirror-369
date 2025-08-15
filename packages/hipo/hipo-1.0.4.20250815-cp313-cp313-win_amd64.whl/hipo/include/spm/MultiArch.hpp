#pragma once

#include "utils/Config.hpp"

#if defined(__CUDACC__) || defined(__HIPCC__)
#define SPM_ATTRIBUTE __host__ __device__
//#warning device host are all supported
#else
#define SPM_ATTRIBUTE
#endif




