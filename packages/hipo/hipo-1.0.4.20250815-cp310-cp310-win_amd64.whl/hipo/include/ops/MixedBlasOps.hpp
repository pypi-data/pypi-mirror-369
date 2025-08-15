
#pragma once


#include "utils/Complex.hpp"
#include "utils/Device.hpp"



namespace hipo {
template <class _NewValT, class _ValT, class _IdxT>
class MixedBlasOps {
public:
    static void copy(const Device& dev, _IdxT n, const _ValT * x, _NewValT * y);
}; // end of class MixedBlasOps
} // end of namespace hipo
