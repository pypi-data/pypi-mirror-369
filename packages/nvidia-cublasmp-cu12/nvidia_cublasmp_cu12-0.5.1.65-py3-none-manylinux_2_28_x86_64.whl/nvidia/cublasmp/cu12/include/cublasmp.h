/*
 * Copyright 2025 NVIDIA Corporation.  All rights reserved.
 *
 * NOTICE TO LICENSEE:
 *
 * This source code and/or documentation ("Licensed Deliverables") are
 * subject to NVIDIA intellectual property rights under U.S. and
 * international Copyright laws.
 *
 * These Licensed Deliverables contained herein is PROPRIETARY and
 * CONFIDENTIAL to NVIDIA and is being provided under the terms and
 * conditions of a form of NVIDIA software license agreement by and
 * between NVIDIA and Licensee ("License Agreement") or electronically
 * accepted by Licensee.  Notwithstanding any terms or conditions to
 * the contrary in the License Agreement, reproduction or disclosure
 * of the Licensed Deliverables to any third party without the express
 * written consent of NVIDIA is prohibited.
 *
 * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
 * LICENSE AGREEMENT, NVIDIA MAKES NO REPRESENTATION ABOUT THE
 * SUITABILITY OF THESE LICENSED DELIVERABLES FOR ANY PURPOSE.  IT IS
 * PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
 * NVIDIA DISCLAIMS ALL WARRANTIES WITH REGARD TO THESE LICENSED
 * DELIVERABLES, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
 * NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
 * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
 * LICENSE AGREEMENT, IN NO EVENT SHALL NVIDIA BE LIABLE FOR ANY
 * SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
 * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
 * WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
 * ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
 * OF THESE LICENSED DELIVERABLES.
 *
 * U.S. Government End Users.  These Licensed Deliverables are a
 * "commercial item" as that term is defined at 48 C.F.R. 2.101 (OCT
 * 1995), consisting of "commercial computer software" and "commercial
 * computer software documentation" as such terms are used in 48
 * C.F.R. 12.212 (SEPT 1995) and is provided to the U.S. Government
 * only as a commercial end item.  Consistent with 48 C.F.R.12.212 and
 * 48 C.F.R. 227.7202-1 through 227.7202-4 (JUNE 1995), all
 * U.S. Government End Users acquire the Licensed Deliverables with
 * only those rights set forth herein.
 *
 * Any use of the Licensed Deliverables in individual and commercial
 * software must include, in the user documentation and internal
 * comments to the code, the above Disclaimer and U.S. Government End
 * Users Notice.
 */

#pragma once

#include <cublas_v2.h>
#include <inttypes.h>
#include <nccl.h>
#include <stdio.h>

#define CUBLASMP_VER_MAJOR 0
#define CUBLASMP_VER_MINOR 5
#define CUBLASMP_VER_PATCH 1
#define CUBLASMP_VERSION (CUBLASMP_VER_MAJOR * 1000 + CUBLASMP_VER_MINOR * 100 + CUBLASMP_VER_PATCH)

#ifdef __cplusplus
extern "C"
{
#endif

typedef enum
{
    CUBLASMP_STATUS_SUCCESS = 0,
    CUBLASMP_STATUS_NOT_INITIALIZED = 1,
    CUBLASMP_STATUS_ALLOCATION_FAILED = 2,
    CUBLASMP_STATUS_INVALID_VALUE = 3,
    CUBLASMP_STATUS_ARCHITECTURE_MISMATCH = 4,
    CUBLASMP_STATUS_EXECUTION_FAILED = 5,
    CUBLASMP_STATUS_INTERNAL_ERROR = 6,
    CUBLASMP_STATUS_NOT_SUPPORTED = 7,
} cublasMpStatus_t;

typedef enum
{
    CUBLASMP_GRID_LAYOUT_COL_MAJOR = 0,
    CUBLASMP_GRID_LAYOUT_ROW_MAJOR = 1
} cublasMpGridLayout_t;

typedef enum
{
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_TRANSA = 0,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_TRANSB = 1,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_COMPUTE_TYPE = 2,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_ALGO_TYPE = 3,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_COMMUNICATION_SM_COUNT = 4,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_EPILOGUE = 5,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_BIAS_POINTER = 6,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_BIAS_BATCH_STRIDE = 7,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_BIAS_DATA_TYPE = 8,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_EPILOGUE_AUX_POINTER = 9,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_EPILOGUE_AUX_LD = 10,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_EPILOGUE_AUX_BATCH_STRIDE = 11,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_EPILOGUE_AUX_DATA_TYPE = 12,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_EPILOGUE_AUX_SCALE_POINTER = 13,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_EPILOGUE_AUX_AMAX_POINTER = 14,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_EPILOGUE_AUX_SCALE_MODE = 15,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_A_SCALE_POINTER = 16,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_A_SCALE_MODE = 17,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_B_SCALE_POINTER = 18,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_B_SCALE_MODE = 19,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_C_SCALE_POINTER = 20,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_C_SCALE_MODE = 21,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_D_SCALE_POINTER = 22,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_D_SCALE_MODE = 23,
    CUBLASMP_MATMUL_DESCRIPTOR_ATTRIBUTE_AMAX_D_POINTER = 24
} cublasMpMatmulDescriptorAttribute_t;

typedef enum
{
    CUBLASMP_MATMUL_ALGO_TYPE_DEFAULT = 0,
    CUBLASMP_MATMUL_ALGO_TYPE_SPLIT_P2P = 1,
    CUBLASMP_MATMUL_ALGO_TYPE_SPLIT_MULTICAST = 2,
    CUBLASMP_MATMUL_ALGO_TYPE_ATOMIC_P2P = 3,
    CUBLASMP_MATMUL_ALGO_TYPE_ATOMIC_MULTICAST = 4
} cublasMpMatmulAlgoType_t;

typedef enum
{
    CUBLASMP_MATMUL_EPILOGUE_DEFAULT = 0,
    CUBLASMP_MATMUL_EPILOGUE_ALLREDUCE = 1,
    CUBLASMP_MATMUL_EPILOGUE_RELU = 2,
    CUBLASMP_MATMUL_EPILOGUE_RELU_AUX = (CUBLASMP_MATMUL_EPILOGUE_RELU | 128),
    CUBLASMP_MATMUL_EPILOGUE_BIAS = 4,
    CUBLASMP_MATMUL_EPILOGUE_RELU_BIAS = (CUBLASMP_MATMUL_EPILOGUE_RELU | CUBLASMP_MATMUL_EPILOGUE_BIAS),
    CUBLASMP_MATMUL_EPILOGUE_RELU_AUX_BIAS = (CUBLASMP_MATMUL_EPILOGUE_RELU_AUX | CUBLASMP_MATMUL_EPILOGUE_BIAS),
    CUBLASMP_MATMUL_EPILOGUE_DRELU = (8 | 128),
    CUBLASMP_MATMUL_EPILOGUE_DRELU_BGRAD = (CUBLASMP_MATMUL_EPILOGUE_DRELU | 16),
    CUBLASMP_MATMUL_EPILOGUE_GELU = 32,
    CUBLASMP_MATMUL_EPILOGUE_GELU_AUX = (CUBLASMP_MATMUL_EPILOGUE_GELU | 128),
    CUBLASMP_MATMUL_EPILOGUE_GELU_BIAS = (CUBLASMP_MATMUL_EPILOGUE_GELU | CUBLASMP_MATMUL_EPILOGUE_BIAS),
    CUBLASMP_MATMUL_EPILOGUE_GELU_AUX_BIAS = (CUBLASMP_MATMUL_EPILOGUE_GELU_AUX | CUBLASMP_MATMUL_EPILOGUE_BIAS),
    CUBLASMP_MATMUL_EPILOGUE_DGELU = (64 | 128),
    CUBLASMP_MATMUL_EPILOGUE_DGELU_BGRAD = (CUBLASMP_MATMUL_EPILOGUE_DGELU | 16),
    CUBLASMP_MATMUL_EPILOGUE_BGRADA = 256,
    CUBLASMP_MATMUL_EPILOGUE_BGRADB = 512
} cublasMpMatmulEpilogue_t;

typedef enum
{
    CUBLASMP_MATMUL_MATRIX_SCALE_SCALAR_FP32 = 0
} cublasMpMatmulMatrixScale_t;

struct cublasMpHandle;
typedef struct cublasMpHandle* cublasMpHandle_t;

struct cublasMpGrid;
typedef struct cublasMpGrid* cublasMpGrid_t;

struct cublasMpMatrixDescriptor;
typedef struct cublasMpMatrixDescriptor* cublasMpMatrixDescriptor_t;

struct cublasMpMatmulDescriptor;
typedef struct cublasMpMatmulDescriptor* cublasMpMatmulDescriptor_t;

cublasMpStatus_t cublasMpCreate(cublasMpHandle_t* handle, cudaStream_t stream);

cublasMpStatus_t cublasMpDestroy(cublasMpHandle_t handle);

cublasMpStatus_t cublasMpStreamSet(cublasMpHandle_t handle, cudaStream_t stream);

cublasMpStatus_t cublasMpStreamGet(cublasMpHandle_t handle, cudaStream_t* stream);

cublasMpStatus_t cublasMpGetVersion(int* version);

cublasMpStatus_t cublasMpGridCreate(
    int64_t nprow,
    int64_t npcol,
    cublasMpGridLayout_t layout,
    ncclComm_t comm,
    cublasMpGrid_t* grid);

cublasMpStatus_t cublasMpGridDestroy(cublasMpGrid_t grid);

cublasMpStatus_t cublasMpMatrixDescriptorCreate(
    int64_t m,
    int64_t n,
    int64_t mb,
    int64_t nb,
    int64_t rsrc,
    int64_t csrc,
    int64_t lld,
    cudaDataType_t type,
    cublasMpGrid_t grid,
    cublasMpMatrixDescriptor_t* desc);

cublasMpStatus_t cublasMpMatrixDescriptorDestroy(cublasMpMatrixDescriptor_t desc);

cublasMpStatus_t cublasMpMatrixDescriptorInit(
    int64_t m,
    int64_t n,
    int64_t mb,
    int64_t nb,
    int64_t rsrc,
    int64_t csrc,
    int64_t lld,
    cudaDataType_t type,
    cublasMpGrid_t grid,
    cublasMpMatrixDescriptor_t desc);

cublasMpStatus_t cublasMpMatmulDescriptorCreate(
    cublasMpMatmulDescriptor_t* matmulDesc,
    cublasComputeType_t computeType);

cublasMpStatus_t cublasMpMatmulDescriptorDestroy(cublasMpMatmulDescriptor_t matmulDesc);

cublasMpStatus_t cublasMpMatmulDescriptorInit(cublasMpMatmulDescriptor_t matmulDesc, cublasComputeType_t computeType);

cublasMpStatus_t cublasMpMatmulDescriptorAttributeSet(
    cublasMpMatmulDescriptor_t matmulDesc,
    cublasMpMatmulDescriptorAttribute_t attr,
    const void* buf,
    size_t sizeInBytes);

cublasMpStatus_t cublasMpMatmulDescriptorAttributeGet(
    cublasMpMatmulDescriptor_t matmulDesc,
    cublasMpMatmulDescriptorAttribute_t attr,
    void* buf,
    size_t sizeInBytes,
    size_t* sizeWritten);

cublasMpStatus_t cublasMpTrsm_bufferSize(
    cublasMpHandle_t handle,
    cublasSideMode_t side,
    cublasFillMode_t uplo,
    cublasOperation_t trans,
    cublasDiagType_t diag,
    int64_t m,
    int64_t n,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    void* b,
    int64_t ib,
    int64_t jb,
    cublasMpMatrixDescriptor_t descB,
    cublasComputeType_t computeType,
    size_t* workspaceSizeInBytesOnDevice,
    size_t* workspaceSizeInBytesOnHost);

cublasMpStatus_t cublasMpTrsm(
    cublasMpHandle_t handle,
    cublasSideMode_t side,
    cublasFillMode_t uplo,
    cublasOperation_t trans,
    cublasDiagType_t diag,
    int64_t m,
    int64_t n,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    void* b,
    int64_t ib,
    int64_t jb,
    cublasMpMatrixDescriptor_t descB,
    cublasComputeType_t computeType,
    void* d_work,
    size_t workspaceSizeInBytesOnDevice,
    void* h_work,
    size_t workspaceSizeInBytesOnHost);

cublasMpStatus_t cublasMpGemm_bufferSize(
    cublasMpHandle_t handle,
    cublasOperation_t transA,
    cublasOperation_t transB,
    int64_t m,
    int64_t n,
    int64_t k,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    const void* b,
    int64_t ib,
    int64_t jb,
    cublasMpMatrixDescriptor_t descB,
    const void* beta,
    void* c,
    int64_t ic,
    int64_t jc,
    cublasMpMatrixDescriptor_t descC,
    cublasComputeType_t computeType,
    size_t* workspaceSizeInBytesOnDevice,
    size_t* workspaceSizeInBytesOnHost);

cublasMpStatus_t cublasMpGemm(
    cublasMpHandle_t handle,
    cublasOperation_t transA,
    cublasOperation_t transB,
    int64_t m,
    int64_t n,
    int64_t k,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    const void* b,
    int64_t ib,
    int64_t jb,
    cublasMpMatrixDescriptor_t descB,
    const void* beta,
    void* c,
    int64_t ic,
    int64_t jc,
    cublasMpMatrixDescriptor_t descC,
    cublasComputeType_t computeType,
    void* d_work,
    size_t workspaceSizeInBytesOnDevice,
    void* h_work,
    size_t workspaceSizeInBytesOnHost);

cublasMpStatus_t cublasMpMatmul_bufferSize(
    cublasMpHandle_t handle,
    cublasMpMatmulDescriptor_t matmulDesc,
    int64_t m,
    int64_t n,
    int64_t k,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    const void* b,
    int64_t ib,
    int64_t jb,
    cublasMpMatrixDescriptor_t descB,
    const void* beta,
    const void* c,
    int64_t ic,
    int64_t jc,
    cublasMpMatrixDescriptor_t descC,
    void* d,
    int64_t id,
    int64_t jd,
    cublasMpMatrixDescriptor_t descD,
    size_t* workspaceSizeInBytesOnDevice,
    size_t* workspaceSizeInBytesOnHost);

cublasMpStatus_t cublasMpMatmul(
    cublasMpHandle_t handle,
    cublasMpMatmulDescriptor_t matmulDesc,
    int64_t m,
    int64_t n,
    int64_t k,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    const void* b,
    int64_t ib,
    int64_t jb,
    cublasMpMatrixDescriptor_t descB,
    const void* beta,
    const void* c,
    int64_t ic,
    int64_t jc,
    cublasMpMatrixDescriptor_t descC,
    void* d,
    int64_t id,
    int64_t jd,
    cublasMpMatrixDescriptor_t descD,
    void* d_work,
    size_t workspaceSizeInBytesOnDevice,
    void* h_work,
    size_t workspaceSizeInBytesOnHost);

cublasMpStatus_t cublasMpSyrk_bufferSize(
    cublasMpHandle_t handle,
    cublasFillMode_t uplo,
    cublasOperation_t trans,
    int64_t n,
    int64_t k,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    const void* beta,
    void* c,
    int64_t ic,
    int64_t jc,
    cublasMpMatrixDescriptor_t descC,
    cublasComputeType_t computeType,
    size_t* workspaceSizeInBytesOnDevice,
    size_t* workspaceSizeInBytesOnHost);

cublasMpStatus_t cublasMpSyrk(
    cublasMpHandle_t handle,
    cublasFillMode_t uplo,
    cublasOperation_t trans,
    int64_t n,
    int64_t k,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    const void* beta,
    void* c,
    int64_t ic,
    int64_t jc,
    cublasMpMatrixDescriptor_t descC,
    cublasComputeType_t computeType,
    void* d_work,
    size_t workspaceSizeInBytesOnDevice,
    void* h_work,
    size_t workspaceSizeInBytesOnHost);

int64_t cublasMpNumroc(int64_t n, int64_t nb, uint32_t iproc, uint32_t isrcproc, uint32_t nprocs);

cublasMpStatus_t cublasMpGemr2D_bufferSize(
    cublasMpHandle_t handle,
    int64_t m,
    int64_t n,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    void* b,
    int64_t ib,
    int64_t jb,
    cublasMpMatrixDescriptor_t descB,
    size_t* workspaceSizeInBytesOnDevice,
    size_t* workspaceSizeInBytesOnHost,
    ncclComm_t global_comm);

cublasMpStatus_t cublasMpGemr2D(
    cublasMpHandle_t handle,
    int64_t m,
    int64_t n,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    void* b,
    int64_t ib,
    int64_t jb,
    cublasMpMatrixDescriptor_t descB,
    void* d_work,
    size_t workspaceSizeInBytesOnDevice,
    void* h_work,
    size_t workspaceSizeInBytesOnHost,
    ncclComm_t global_comm);

cublasMpStatus_t cublasMpTrmr2D_bufferSize(
    cublasMpHandle_t handle,
    cublasFillMode_t uplo,
    cublasDiagType_t diag,
    int64_t m,
    int64_t n,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    void* b,
    int64_t ib,
    int64_t jb,
    cublasMpMatrixDescriptor_t descB,
    size_t* workspaceSizeInBytesOnDevice,
    size_t* workspaceSizeInBytesOnHost,
    ncclComm_t global_comm);

cublasMpStatus_t cublasMpTrmr2D(
    cublasMpHandle_t handle,
    cublasFillMode_t uplo,
    cublasDiagType_t diag,
    int64_t m,
    int64_t n,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    void* b,
    int64_t ib,
    int64_t jb,
    cublasMpMatrixDescriptor_t descB,
    void* d_work,
    size_t workspaceSizeInBytesOnDevice,
    void* h_work,
    size_t workspaceSizeInBytesOnHost,
    ncclComm_t global_comm);

cublasMpStatus_t cublasMpGeadd_bufferSize(
    cublasMpHandle_t handle,
    cublasOperation_t trans,
    int64_t m,
    int64_t n,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    const void* beta,
    void* c,
    int64_t ic,
    int64_t jc,
    cublasMpMatrixDescriptor_t descC,
    size_t* workspaceSizeInBytesOnDevice,
    size_t* workspaceSizeInBytesOnHost);

cublasMpStatus_t cublasMpGeadd(
    cublasMpHandle_t handle,
    cublasOperation_t trans,
    int64_t m,
    int64_t n,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    const void* beta,
    void* c,
    int64_t ic,
    int64_t jc,
    cublasMpMatrixDescriptor_t descC,
    void* d_work,
    size_t workspaceSizeInBytesOnDevice,
    void* h_work,
    size_t workspaceSizeInBytesOnHost);

cublasMpStatus_t cublasMpTradd_bufferSize(
    cublasMpHandle_t handle,
    cublasFillMode_t uplo,
    cublasOperation_t trans,
    int64_t m,
    int64_t n,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    const void* beta,
    void* c,
    int64_t ic,
    int64_t jc,
    cublasMpMatrixDescriptor_t descC,
    size_t* workspaceSizeInBytesOnDevice,
    size_t* workspaceSizeInBytesOnHost);

cublasMpStatus_t cublasMpTradd(
    cublasMpHandle_t handle,
    cublasFillMode_t uplo,
    cublasOperation_t trans,
    int64_t m,
    int64_t n,
    const void* alpha,
    const void* a,
    int64_t ia,
    int64_t ja,
    cublasMpMatrixDescriptor_t descA,
    const void* beta,
    void* c,
    int64_t ic,
    int64_t jc,
    cublasMpMatrixDescriptor_t descC,
    void* d_work,
    size_t workspaceSizeInBytesOnDevice,
    void* h_work,
    size_t workspaceSizeInBytesOnHost);

typedef void (*cublasMpLoggerCallback_t)(int logLevel, const char* functionName, const char* message);

cublasMpStatus_t cublasMpLoggerSetCallback(cublasMpLoggerCallback_t callback);

cublasMpStatus_t cublasMpLoggerSetFile(FILE* file);

cublasMpStatus_t cublasMpLoggerOpenFile(const char* logFile);

cublasMpStatus_t cublasMpLoggerSetLevel(int level);

cublasMpStatus_t cublasMpLoggerSetMask(int mask);

cublasMpStatus_t cublasMpLoggerForceDisable();

#ifdef __cplusplus
}
#endif
