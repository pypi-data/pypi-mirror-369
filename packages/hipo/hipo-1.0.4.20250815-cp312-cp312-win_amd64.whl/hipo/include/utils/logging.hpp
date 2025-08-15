#pragma once

#include "utils/Config.hpp"


#include <iostream>

namespace hipo {


class LogMessage {
    std::ostream* stream_ = 0;
    bool checker_  = false;
    int level_ = 0;
    int condition_;
    std::string file_;
    int line_;
public:
    std::ostream& stream() {
        return *stream_;
    }
    LogMessage(bool checker, int lvl, int cond, const std::string& file_, int line_, std::ostream* os = 0);
    ~LogMessage();
};


}

#ifdef HIPO_ENABLE_GLOG

#include <glog/logging.h>



#else


#define LOG(lvl) hipo::LogMessage(false, lvl, 1, __FILE__, __LINE__).stream()
#define LOG_IF(lvl, cond) hipo::LogMessage(false, lvl, cond, __FILE__, __LINE__).stream()
#define CHECK(cond) hipo::LogMessage(true, INFO, cond, __FILE__, __LINE__).stream()
#define CHECK_LE(a, b) hipo::LogMessage(true, INFO, (a) <= (b), __FILE__, __LINE__).stream()
#define CHECK_LT(a, b) hipo::LogMessage(true, INFO, (a) <  (b), __FILE__, __LINE__).stream()
#define CHECK_GE(a, b) hipo::LogMessage(true, INFO, (a) >= (b), __FILE__, __LINE__).stream()
#define CHECK_GT(a, b) hipo::LogMessage(true, INFO, (a) >  (b), __FILE__, __LINE__).stream()
#define CHECK_EQ(a, b) hipo::LogMessage(true, INFO, (a) == (b), __FILE__, __LINE__).stream()
#define FATAL 0
#define ERROR 1
#define WARNING 2
#define INFO 3


#endif



