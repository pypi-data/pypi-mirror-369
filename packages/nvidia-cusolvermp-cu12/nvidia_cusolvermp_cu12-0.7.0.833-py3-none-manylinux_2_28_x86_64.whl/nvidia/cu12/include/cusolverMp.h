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

#include <stdio.h>

#include "nccl.h"
#include "cusolverDn.h"

#define CUSOLVERMP_VER_MAJOR 0
#define CUSOLVERMP_VER_MINOR 7
#define CUSOLVERMP_VER_PATCH 0
#define CUSOLVERMP_VER_BUILD 0
#define CUSOLVERMP_VERSION   (CUSOLVERMP_VER_MAJOR * 1000 + CUSOLVERMP_VER_MINOR * 100 + CUSOLVERMP_VER_PATCH)

#if defined(__cplusplus)
extern "C"
{
#endif /* __cplusplus */

    typedef enum
    {
        CUSOLVERMP_GRID_MAPPING_ROW_MAJOR = 1,
        CUSOLVERMP_GRID_MAPPING_COL_MAJOR = 0
    } cusolverMpGridMapping_t;

    /* Opaque structure of the distributed grid */
    struct cusolverMpGrid;
    typedef struct cusolverMpGrid* cusolverMpGrid_t;

    struct cusolverMpMatrixDescriptor;
    typedef struct cusolverMpMatrixDescriptor* cusolverMpMatrixDescriptor_t;

    struct cusolverMpHandle;
    typedef struct cusolverMpHandle* cusolverMpHandle_t;

    /*
     * REMARK: should come from cudaLibMg
     *
     * Each global data object is described by an associated description
     * vector.  This vector stores the information required to establish
     * the mapping between an object element and its corresponding process
     * and memory location.
     *
     * Let A be a generic term for any 2D block cyclicly distributed array.
     * Such a global array has an associated description vector DESCA.
     * In the following comments, the character _ should be read as
     * "of the global array".
     *
     * grid     : Equivalent to CTXT_A in ScaLAPACK
     * dataType : Data type
     * M_A      : The number of rows in the distributed matrix
     * N_A      : The number of cols in the distributed matrix
     * MB_A     : The blocking factor used to distribute the rows
     *            of the matrix
     * NB_A     : The blocking factor used to distribute the columns of
     *            the matrix
     * RSRC_A   : The process row over which the first row of the matrix
     *            is distributed. Base-0.
     * CSRC_A   : The process column over which the first row of the matrix
     *            is distributed. Base-0.
     * LLD_A    : The leading dimension of the local array storing the local
     *            blocks of the distributed matrix A.
     *            LLD_A >= MAX(1,LOCr(M_A)).
     */

    cusolverStatus_t CUSOLVERAPI cusolverMpCreate(cusolverMpHandle_t* handle, int deviceId, cudaStream_t stream);

    cusolverStatus_t CUSOLVERAPI cusolverMpDestroy(cusolverMpHandle_t handle);

    cusolverStatus_t CUSOLVERAPI cusolverMpGetStream(cusolverMpHandle_t handle, cudaStream_t* stream);

    cusolverStatus_t CUSOLVERAPI cusolverMpGetVersion(cusolverMpHandle_t handle, int* version);

    cusolverStatus_t CUSOLVERAPI cusolverMpCreateDeviceGrid(cusolverMpHandle_t            handle,
                                                            cusolverMpGrid_t*             grid,
                                                            const ncclComm_t              comm,
                                                            int32_t                       numRowDevices,
                                                            int32_t                       numColDevices,
                                                            const cusolverMpGridMapping_t mapping);

    cusolverStatus_t CUSOLVERAPI cusolverMpDestroyGrid(cusolverMpGrid_t grid);

    cusolverStatus_t CUSOLVERAPI cusolverMpCreateMatrixDesc(cusolverMpMatrixDescriptor_t* desc,
                                                            cusolverMpGrid_t              grid,
                                                            cudaDataType                  dataType,
                                                            int64_t                       M_A,
                                                            int64_t                       N_A,
                                                            int64_t                       MB_A,
                                                            int64_t                       NB_A,
                                                            uint32_t                      RSRC_A,
                                                            uint32_t                      CSRC_A,
                                                            int64_t                       LLD_A);

    cusolverStatus_t CUSOLVERAPI cusolverMpDestroyMatrixDesc(cusolverMpMatrixDescriptor_t descr);


    /*  Purpose
     *  =======
     *
     *  NUMROC computes the NUMber of Rows Or Columns of a distributed
     *  matrix owned by the process indicated by IPROC.
     *
     *  Arguments
     *  =========
     *
     *  N         (global input) INTEGER
     *            The number of rows/columns in distributed matrix.
     *
     *  NB        (global input) INTEGER
     *            Block size, size of the blocks the distributed matrix is
     *            split into.
     *
     *  IPROC     (local input) INTEGER
     *            The coordinate of the process whose local array row or
     *            column is to be determined.
     *
     *  ISRCPROC  (global input) INTEGER
     *            The coordinate of the process that possesses the first
     *            row or column of the distributed matrix.
     *            0 <= IRSRC < NPROW.
     *
     *  NPROCS    (global input) INTEGER
     *            The total number processes over which the matrix is
     *            distributed.
     */
    __host__ __device__ int64_t CUSOLVERAPI
    cusolverMpNUMROC(int64_t n, int64_t nb, uint32_t iproc, uint32_t isrcproc, uint32_t nprocs);

    /*
     * REMARK : this routine will NOT be part of the official release,
     *          is only shipped fo EA.
     *
     * Internal routine: distributes a host-side matrix on rank rankId
     * to a distributed matrix according to the information in the
     * matrix descriptor descr.
     */
    cusolverStatus_t CUSOLVERAPI cusolverMpMatrixScatterH2D(cusolverMpHandle_t           handle,
                                                            int64_t                      M,
                                                            int64_t                      N,
                                                            void*                        d_A,
                                                            int64_t                      IA,
                                                            int64_t                      JA,
                                                            cusolverMpMatrixDescriptor_t descrA,
                                                            int                          root,
                                                            const void*                  h_src,
                                                            int64_t                      h_ldsrc);

    /*
     * REMARK : this routine will NOT be part of the official release, it
     *          is only shipped fo EA.
     *
     * Internal routine: gathers a distributed matrix (on device memory)
     * to a host pointer on rank rankId
     */
    cusolverStatus_t CUSOLVERAPI cusolverMpMatrixGatherD2H(cusolverMpHandle_t           handle,
                                                           int64_t                      M,
                                                           int64_t                      N,
                                                           const void*                  d_A,
                                                           int64_t                      IA,
                                                           int64_t                      JA,
                                                           cusolverMpMatrixDescriptor_t descrA,
                                                           int                          root,
                                                           void*                        h_dst,
                                                           int64_t                      h_lddst);


    /* Computes workspace requirements for cusolverMpGetrf */
    cusolverStatus_t CUSOLVERAPI cusolverMpGetrf_bufferSize(cusolverMpHandle_t           handle,
                                                            int64_t                      M,
                                                            int64_t                      N,
                                                            void*                        d_A,
                                                            int64_t                      IA,
                                                            int64_t                      JA,
                                                            cusolverMpMatrixDescriptor_t descrA,
                                                            int64_t*                     d_ipiv,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    /* Computes LU factorization of a general matrix with or without pivoting */
    cusolverStatus_t CUSOLVERAPI cusolverMpGetrf(cusolverMpHandle_t           handle,
                                                 int64_t                      M,
                                                 int64_t                      N,
                                                 void*                        d_A,
                                                 int64_t                      IA,
                                                 int64_t                      JA,
                                                 cusolverMpMatrixDescriptor_t descrA,
                                                 int64_t*                     d_ipiv,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         info);

    cusolverStatus_t CUSOLVERAPI cusolverMpGetrs_bufferSize(cusolverMpHandle_t           handle,
                                                            cublasOperation_t            trans,
                                                            int64_t                      N,
                                                            int64_t                      NRHS,
                                                            const void*                  d_A,
                                                            int64_t                      IA,
                                                            int64_t                      JA,
                                                            cusolverMpMatrixDescriptor_t descrA,
                                                            const int64_t*               d_ipiv,
                                                            void*                        d_B,
                                                            int64_t                      IB,
                                                            int64_t                      JB,
                                                            cusolverMpMatrixDescriptor_t descrB,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    cusolverStatus_t CUSOLVERAPI cusolverMpGetrs(cusolverMpHandle_t           handle,
                                                 cublasOperation_t            trans,
                                                 int64_t                      N,
                                                 int64_t                      NRHS,
                                                 const void*                  d_A,
                                                 int64_t                      IA,
                                                 int64_t                      JA,
                                                 cusolverMpMatrixDescriptor_t descrA,
                                                 const int64_t*               d_ipiv,
                                                 void*                        d_B,
                                                 int64_t                      IB,
                                                 int64_t                      JB,
                                                 cusolverMpMatrixDescriptor_t descrB,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         d_info);

    cusolverStatus_t CUSOLVERAPI cusolverMpPotrf_bufferSize(cusolverMpHandle_t           handle,
                                                            cublasFillMode_t             uplo,
                                                            int64_t                      n,
                                                            const void*                  a,
                                                            int64_t                      ia,
                                                            int64_t                      ja,
                                                            cusolverMpMatrixDescriptor_t descA,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    cusolverStatus_t CUSOLVERAPI cusolverMpPotrf(cusolverMpHandle_t           handle,
                                                 cublasFillMode_t             uplo,
                                                 int64_t                      n,
                                                 void*                        a,
                                                 int64_t                      ia,
                                                 int64_t                      ja,
                                                 cusolverMpMatrixDescriptor_t descA,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         info);

    cusolverStatus_t CUSOLVERAPI cusolverMpPotrs_bufferSize(cusolverMpHandle_t           handle,
                                                            cublasFillMode_t             uplo,
                                                            int64_t                      n,
                                                            int64_t                      nrhs,
                                                            const void*                  a,
                                                            int64_t                      ia,
                                                            int64_t                      ja,
                                                            cusolverMpMatrixDescriptor_t descA,
                                                            const void*                  b,
                                                            int64_t                      ib,
                                                            int64_t                      jb,
                                                            cusolverMpMatrixDescriptor_t descB,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    cusolverStatus_t CUSOLVERAPI cusolverMpPotrs(cusolverMpHandle_t           handle,
                                                 cublasFillMode_t             uplo,
                                                 int64_t                      n,
                                                 int64_t                      nrhs,
                                                 const void*                  a,
                                                 int64_t                      ia,
                                                 int64_t                      ja,
                                                 cusolverMpMatrixDescriptor_t descA,
                                                 void*                        b,
                                                 int64_t                      ib,
                                                 int64_t                      jb,
                                                 cusolverMpMatrixDescriptor_t descB,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         info);

    cusolverStatus_t CUSOLVERAPI cusolverMpOrmqr_bufferSize(cusolverMpHandle_t           handle,
                                                            cublasSideMode_t             side,
                                                            cublasOperation_t            trans,
                                                            int64_t                      m,
                                                            int64_t                      n,
                                                            int64_t                      k,
                                                            const void*                  a,
                                                            int64_t                      ia,
                                                            int64_t                      ja,
                                                            cusolverMpMatrixDescriptor_t descA,
                                                            const void*                  tau,
                                                            void*                        c,
                                                            int64_t                      ic,
                                                            int64_t                      jc,
                                                            cusolverMpMatrixDescriptor_t descC,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    cusolverStatus_t CUSOLVERAPI cusolverMpOrmqr(cusolverMpHandle_t           handle,
                                                 cublasSideMode_t             side,
                                                 cublasOperation_t            trans,
                                                 int64_t                      m,
                                                 int64_t                      n,
                                                 int64_t                      k,
                                                 const void*                  a,
                                                 int64_t                      ia,
                                                 int64_t                      ja,
                                                 cusolverMpMatrixDescriptor_t descA,
                                                 const void*                  tau,
                                                 void*                        c,
                                                 int64_t                      ic,
                                                 int64_t                      jc,
                                                 cusolverMpMatrixDescriptor_t descC,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         info);

    cusolverStatus_t CUSOLVERAPI cusolverMpOrmtr_bufferSize(cusolverMpHandle_t           handle,
                                                            cublasSideMode_t             side,
                                                            cublasFillMode_t             uplo,
                                                            cublasOperation_t            trans,
                                                            int64_t                      m,
                                                            int64_t                      n,
                                                            const void*                  a,
                                                            int64_t                      ia,
                                                            int64_t                      ja,
                                                            cusolverMpMatrixDescriptor_t descA,
                                                            const void*                  tau,
                                                            void*                        c,
                                                            int64_t                      ic,
                                                            int64_t                      jc,
                                                            cusolverMpMatrixDescriptor_t descC,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    cusolverStatus_t CUSOLVERAPI cusolverMpOrmtr(cusolverMpHandle_t           handle,
                                                 cublasSideMode_t             side,
                                                 cublasFillMode_t             uplo,
                                                 cublasOperation_t            trans,
                                                 int64_t                      m,
                                                 int64_t                      n,
                                                 const void*                  a,
                                                 int64_t                      ia,
                                                 int64_t                      ja,
                                                 cusolverMpMatrixDescriptor_t descA,
                                                 const void*                  tau,
                                                 void*                        c,
                                                 int64_t                      ic,
                                                 int64_t                      jc,
                                                 cusolverMpMatrixDescriptor_t descC,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         info);

    cusolverStatus_t CUSOLVERAPI cusolverMpGels_bufferSize(cusolverMpHandle_t           handle,
                                                           cublasOperation_t            trans,
                                                           int64_t                      m,
                                                           int64_t                      n,
                                                           int64_t                      nrhs,
                                                           void*                        a,
                                                           int64_t                      ia,
                                                           int64_t                      ja,
                                                           cusolverMpMatrixDescriptor_t descA,
                                                           void*                        b,
                                                           int64_t                      ib,
                                                           int64_t                      jb,
                                                           cusolverMpMatrixDescriptor_t descB,
                                                           cudaDataType_t               computeType,
                                                           size_t*                      workspaceInBytesOnDevice,
                                                           size_t*                      workspaceInBytesOnHost);

    cusolverStatus_t CUSOLVERAPI cusolverMpGels(cusolverMpHandle_t           handle,
                                                cublasOperation_t            trans,
                                                int64_t                      m,
                                                int64_t                      n,
                                                int64_t                      nrhs,
                                                void*                        a,
                                                int64_t                      ia,
                                                int64_t                      ja,
                                                cusolverMpMatrixDescriptor_t descA,
                                                void*                        b,
                                                int64_t                      ib,
                                                int64_t                      jb,
                                                cusolverMpMatrixDescriptor_t descB,
                                                cudaDataType_t               computeType,
                                                void*                        d_work,
                                                size_t                       workspaceInBytesOnDevice,
                                                void*                        h_work,
                                                size_t                       workspaceInBytesOnHost,
                                                int*                         info);

    /* Computes workspace requirements for cusolverMpStedc */
    cusolverStatus_t CUSOLVERAPI cusolverMpStedc_bufferSize(cusolverMpHandle_t           handle,
                                                            char*                        compz,
                                                            int64_t                      N,
                                                            void*                        d_D,
                                                            void*                        d_E,
                                                            void*                        d_Q,
                                                            int64_t                      IQ,
                                                            int64_t                      JQ,
                                                            cusolverMpMatrixDescriptor_t descrQ,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost,
                                                            int*                         iwork);

    /* Computes all eigenvalues and eigenvectors of a symmetric tridiagonal matrix */
    cusolverStatus_t CUSOLVERAPI cusolverMpStedc(cusolverMpHandle_t           handle,
                                                 char*                        compz,
                                                 int64_t                      N,
                                                 void*                        d_D,
                                                 void*                        d_E,
                                                 void*                        d_Q,
                                                 int64_t                      IQ,
                                                 int64_t                      JQ,
                                                 cusolverMpMatrixDescriptor_t descrQ,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         info);

    /* Computes workspace requirements for cusolverMpGeqrf */
    cusolverStatus_t CUSOLVERAPI cusolverMpGeqrf_bufferSize(cusolverMpHandle_t           handle,
                                                            int64_t                      M,
                                                            int64_t                      N,
                                                            void*                        d_A,
                                                            int64_t                      IA,
                                                            int64_t                      JA,
                                                            cusolverMpMatrixDescriptor_t descrA,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    /* Computes QR factorization of a general matrix */
    cusolverStatus_t CUSOLVERAPI cusolverMpGeqrf(cusolverMpHandle_t           handle,
                                                 int64_t                      M,
                                                 int64_t                      N,
                                                 void*                        d_A,
                                                 int64_t                      IA,
                                                 int64_t                      JA,
                                                 cusolverMpMatrixDescriptor_t descrA,
                                                 void*                        d_tau,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         info);

    /* Computes workspace requirements for cusolverMpSytrd */
    cusolverStatus_t CUSOLVERAPI cusolverMpSytrd_bufferSize(cusolverMpHandle_t           handle,
                                                            cublasFillMode_t             uplo,
                                                            int64_t                      N,
                                                            void*                        d_A,
                                                            int64_t                      IA,
                                                            int64_t                      JA,
                                                            cusolverMpMatrixDescriptor_t descrA,
                                                            void*                        d_D,
                                                            void*                        d_E,
                                                            void*                        d_TAU,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    /* Computes tridiagonal form */
    cusolverStatus_t CUSOLVERAPI cusolverMpSytrd(cusolverMpHandle_t           handle,
                                                 cublasFillMode_t             uplo,
                                                 int64_t                      N,
                                                 void*                        d_A,
                                                 int64_t                      IA,
                                                 int64_t                      JA,
                                                 cusolverMpMatrixDescriptor_t descrA,
                                                 void*                        d_D,
                                                 void*                        d_E,
                                                 void*                        d_TAU,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         info);

    /* Computes workspace requirements for cusolverMpSyevd */
    cusolverStatus_t CUSOLVERAPI cusolverMpSyevd_bufferSize(cusolverMpHandle_t           handle,
                                                            char*                        compz,
                                                            cublasFillMode_t             uplo,
                                                            int64_t                      N,
                                                            void*                        d_A,
                                                            int64_t                      IA,
                                                            int64_t                      JA,
                                                            cusolverMpMatrixDescriptor_t descrA,
                                                            void*                        d_D,
                                                            void*                        d_Q,
                                                            int64_t                      IQ,
                                                            int64_t                      JQ,
                                                            cusolverMpMatrixDescriptor_t descrQ,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    /* Computes all eigenvalues and eigenvectors of a symmetric matrix */
    cusolverStatus_t CUSOLVERAPI cusolverMpSyevd(cusolverMpHandle_t           handle,
                                                 char*                        compz,
                                                 cublasFillMode_t             uplo,
                                                 int64_t                      N,
                                                 void*                        d_A,
                                                 int64_t                      IA,
                                                 int64_t                      JA,
                                                 cusolverMpMatrixDescriptor_t descrA,
                                                 void*                        d_D,
                                                 void*                        d_Q,
                                                 int64_t                      IQ,
                                                 int64_t                      JQ,
                                                 cusolverMpMatrixDescriptor_t descrQ,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         d_info);

    /* Reduce a generalized hermitian eigen problem to a standard form */
    cusolverStatus_t CUSOLVERAPI cusolverMpSygst_bufferSize(cusolverMpHandle_t           handle,
                                                            cusolverEigType_t            ibtype,
                                                            cublasFillMode_t             uplo,
                                                            int64_t                      m,
                                                            int64_t                      ia,
                                                            int64_t                      ja,
                                                            cusolverMpMatrixDescriptor_t descA,
                                                            int64_t                      ib,
                                                            int64_t                      jb,
                                                            cusolverMpMatrixDescriptor_t descB,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    /* Reduce a generalized hermitian eigen problem to a standard form */
    cusolverStatus_t CUSOLVERAPI cusolverMpSygst(cusolverMpHandle_t           handle,
                                                 cusolverEigType_t            ibtype,
                                                 cublasFillMode_t             uplo,
                                                 int64_t                      m,
                                                 void*                        a,
                                                 int64_t                      ia,
                                                 int64_t                      ja,
                                                 cusolverMpMatrixDescriptor_t descA,
                                                 const void*                  b,
                                                 int64_t                      ib,
                                                 int64_t                      jb,
                                                 cusolverMpMatrixDescriptor_t descB,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         info);

    /* Generalized Hermitian eigen solver */
    cusolverStatus_t CUSOLVERAPI cusolverMpSygvd_bufferSize(cusolverMpHandle_t           handle,
                                                            cusolverEigType_t            ibtype,
                                                            cusolverEigMode_t            jobz,
                                                            cublasFillMode_t             uplo,
                                                            int64_t                      m,
                                                            int64_t                      ia,
                                                            int64_t                      ja,
                                                            cusolverMpMatrixDescriptor_t descA,
                                                            int64_t                      ib,
                                                            int64_t                      jb,
                                                            cusolverMpMatrixDescriptor_t descB,
                                                            int64_t                      iz,
                                                            int64_t                      jz,
                                                            cusolverMpMatrixDescriptor_t descZ,
                                                            cudaDataType_t               computeType,
                                                            size_t*                      workspaceInBytesOnDevice,
                                                            size_t*                      workspaceInBytesOnHost);

    /* Generalized Hermitian eigen solver */
    cusolverStatus_t CUSOLVERAPI cusolverMpSygvd(cusolverMpHandle_t           handle,
                                                 cusolverEigType_t            ibtype,
                                                 cusolverEigMode_t            jobz,
                                                 cublasFillMode_t             uplo,
                                                 int64_t                      m,
                                                 void*                        a,
                                                 int64_t                      ia,
                                                 int64_t                      ja,
                                                 cusolverMpMatrixDescriptor_t descA,
                                                 void*                        b,
                                                 int64_t                      ib,
                                                 int64_t                      jb,
                                                 cusolverMpMatrixDescriptor_t descB,
                                                 void*                        w,
                                                 void*                        z,
                                                 int64_t                      iz,
                                                 int64_t                      jz,
                                                 cusolverMpMatrixDescriptor_t descZ,
                                                 cudaDataType_t               computeType,
                                                 void*                        d_work,
                                                 size_t                       workspaceInBytesOnDevice,
                                                 void*                        h_work,
                                                 size_t                       workspaceInBytesOnHost,
                                                 int*                         info);

    typedef void (*cusolverMpLoggerCallback_t)(int logLevel, const char* functionName, const char* message);

    cusolverStatus_t CUSOLVERAPI cusolverMpLoggerSetCallback(cusolverMpLoggerCallback_t callback);

    cusolverStatus_t CUSOLVERAPI cusolverMpLoggerSetFile(FILE* file);

    cusolverStatus_t CUSOLVERAPI cusolverMpLoggerOpenFile(const char* logFile);

    cusolverStatus_t CUSOLVERAPI cusolverMpLoggerSetLevel(int level);

    cusolverStatus_t CUSOLVERAPI cusolverMpLoggerSetMask(int mask);

    cusolverStatus_t CUSOLVERAPI cusolverMpLoggerForceDisable();

#if CUSOLVER_VERSION >= 12000
    cusolverStatus_t CUSOLVERAPI cusolverMpSetMathMode(cusolverMpHandle_t handle, cusolverMathMode_t mode);
    cusolverStatus_t CUSOLVERAPI cusolverMpGetMathMode(cusolverMpHandle_t handle, cusolverMathMode_t* mode);

    cusolverStatus_t CUSOLVERAPI cusolverMpSetEmulationStrategy(cusolverMpHandle_t      handle,
                                                                cudaEmulationStrategy_t strategy);

    cusolverStatus_t CUSOLVERAPI cusolverMpGetEmulationStrategy(cusolverMpHandle_t       handle,
                                                                cudaEmulationStrategy_t* strategy);
#endif

#if defined(__cplusplus)
}
#endif /* __cplusplus */
