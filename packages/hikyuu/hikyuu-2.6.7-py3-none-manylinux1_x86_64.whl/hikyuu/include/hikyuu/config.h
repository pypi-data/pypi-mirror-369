#pragma once
#ifndef HIKYUU_CONFIG_H_
#define HIKYUU_CONFIG_H_

// clang-format off

// Debug 模式
#define HKU_DEBUG_MODE 0

// support serialization
#define HKU_SUPPORT_SERIALIZATION  1

#if HKU_SUPPORT_SERIALIZATION
#define HKU_SUPPORT_TEXT_ARCHIVE   0
#define HKU_SUPPORT_XML_ARCHIVE    1  //must 1 for python
#define HKU_SUPPORT_BINARY_ARCHIVE 1  //must 1 for python
#endif /* HKU_SUPPORT_SERIALIZATION*/

// 检查下标越界
#define CHECK_ACCESS_BOUND 1

// 启用MSVC内存泄漏检查
#define ENABLE_MSVC_LEAK_DETECT 0

// 启用内存泄漏检测，用于 linux 系统
#define HKU_ENABLE_LEAK_DETECT 0

// 启用发送用户使用信息
#define HKU_ENABLE_SEND_FEEDBACK 1

// 启用 hdf5 K线数据引擎
#define HKU_ENABLE_HDF5_KDATA 1

// 启用 MySQL K线数据引擎
#define HKU_ENABLE_MYSQL_KDATA 1

// 启用 SQLite K线数据引擎
#define HKU_ENABLE_SQLITE_KDATA 1

// 启用通达信本地 K线数据引擎
#define HKU_ENABLE_TDX_KDATA 1

// 使用低精度版本，Indicator 使用 float 类型进行计算
#define HKU_USE_LOW_PRECISION 0

// 使用 TA-Lib
#define HKU_ENABLE_TA_LIB 1

// clang-format on

#endif /* HIKYUU_CONFIG_H_ */