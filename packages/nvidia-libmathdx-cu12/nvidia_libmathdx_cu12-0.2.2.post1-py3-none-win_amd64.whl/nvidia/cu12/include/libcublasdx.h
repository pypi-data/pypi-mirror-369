// Copyright (c) 2024-2025, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

// libmathdx's API is subject to change.
// Please contact Math-Libs-Feedback@nvidia.com for usage feedback.

#ifndef MATHDX_LIBCUBLASDX_H
#define MATHDX_LIBCUBLASDX_H

#include <stddef.h>

#include "libcommondx.h"

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

/**
 * @brief A handle to a cuBLASDx descriptor.
 *
 * Equivalent to `using GEMM = ...` in cuBLASDx CUDA C++.
 */
typedef long long int cublasdxDescriptor;

/**
 * @brief A handle to an opaque device tensor.
 */
typedef long long int cublasdxTensor;

/**
 * @brief A handle to a device function.
 * A device function operators on tensors described by \ref cublasdxTensor
 */
typedef long long int cublasdxDeviceFunction;

/**
 * @brief Type of cublasDx API
 *
 * Handling problems with default or custom/dynamic leading dimensions.
 * Check cublasdx::LeadingDimension operator documentation for more details
 * (https://docs.nvidia.com/cuda/cublasdx/api/operators.html#leadingdimension-operator)
 */
typedef enum cublasdxApi_t {
    /**
     * Use API for problems with default leading dimensions.
     * Function API is defined by its signature:
     * `void (value_type_c* alpha, value_type_a* smem_a, value_type_b* smem_b, value_type_c* beta, value_type_c*
     * smem_c)` where
     *     - `smem_a`, `smem_b` and `smem_c` are pointers to value of type given by the \ref CUBLASDX_TRAIT_VALUE_TYPE
     * a, b, and c trait. `smem_a`, `smem_b` and `smem_c` must be shared memory pointers.
     *     - `alpha` and `beta` are pointers to value of type \ref CUBLASDX_TRAIT_VALUE_TYPE c.
     *
     * Note that complex numbers must be over-aligned.
     *
     * The function is `extern "C"` and the symbol name can be queried using \ref CUBLASDX_TRAIT_SYMBOL_NAME.
     * See https://docs.nvidia.com/cuda/cublasdx/api/methods.html#shared-memory-api and in
     * particular the `Pointer API` section.
     */
    CUBLASDX_API_SMEM = 0,
    /** Use API for problems with custom / dynamic leading dimensions.
     * Function API is defined by its signature:
     * `void (value_type_c alpha, value_type_a* smem_a, unsigned* lda, value_type_b *smem_b, unsigned* ldb,
     * value_type_c* beta, value_type_c* smem_c, unsigned *ldc)` where
     *     - `smem_a`, `smem_b` and `smem_c` are pointers to value of type given by the \ref CUBLASDX_TRAIT_VALUE_TYPE
     * a, b, and c trait. `smem_a`, `smem_b` and `smem_c` must be shared memory pointers.
     *     - `alpha` and `beta` are pointers to value of type \ref CUBLASDX_TRAIT_VALUE_TYPE c trait.
     *     - `lda`, `ldb` and `ldc` are pointers to unsigned 32 bits integer (`unsigned`)
     *
     * Note that complex numbers must be over-aligned.
     *
     * The function is `extern "C"` and the symbol name can be queried using \ref CUBLASDX_TRAIT_SYMBOL_NAME.
     * See https://docs.nvidia.com/cuda/cublasdx/api/methods.html#shared-memory-api and in
     * particular the `Pointer API, which allows providing runtime/dynamic leading dimensions for matrices A, B,
     * and C` section.
     */
    CUBLASDX_API_SMEM_DYNAMIC_LD = 1,
    /** Use Tensor API.
     * Function API is defined by the input and output tensors specified
     * when calling \ref cublasdxBindDeviceFunction
     * The device functions are not `extern "C"`. The name and argument types must be mangled. Tensors
     * are trivial and passed by value. Scalars are `void*`.
     */
    CUBLASDX_API_TENSORS = 2,
} cublasdxApi;

/**
 * @brief Type of computation data
 *
 * Check cubladx::Type operator documentation for more details
 * (https://docs.nvidia.com/cuda/cublasdx/api/operators.html#type-operator)
 */
typedef enum cublasdxType_t {
    /** Use for real matmuls */
    CUBLASDX_TYPE_REAL = 0,
    /** Use for complex matmuls */
    CUBLASDX_TYPE_COMPLEX = 1,
} cublasdxType;

/**
 * @brief Tensor transpose mode
 *
 * The transpose mode depends on cubladx::TransposeMode operator
 * which is deprecated since cublasDx 0.2.0 and might be removed in future
 * versions of mathDx libraries
 *
 * Check cubladx::TransposeMode operator documentation for more details
 * (https://docs.nvidia.com/cuda/cublasdx/api/operators.html#transposemode-operator)
 */
typedef enum cublasdxTransposeMode_t {
    /** Use matrix as-is in the matmul */
    CUBLASDX_TRANSPOSE_MODE_NON_TRANSPOSED = 0,
    /** Use transposed matrix in the matmul */
    CUBLASDX_TRANSPOSE_MODE_TRANSPOSED = 1,
    /** Use transposed and conjugate matrix in the matmul */
    CUBLASDX_TRANSPOSE_MODE_CONJ_TRANSPOSED = 2,
} cublasdxTransposeMode;

/**
 * @brief Data arrangement mode
 *
 * Defines data arrangements in tensors' taking part in the calculation.
 *
 * Check cubladx::TransposeMode operator documentation for more details
 * (https://docs.nvidia.com/cuda/cublasdx/api/operators.html#arrangement-operator)
 */
typedef enum cublasdxArrangement_t {
    /** Data is considered column-major */
    CUBLASDX_ARRANGEMENT_COL_MAJOR = 0,
    /** Data is considered row-major */
    CUBLASDX_ARRANGEMENT_ROW_MAJOR = 1,
} cublasdxArrangement;

/**
 * @brief BLAS function
 *
 * Sets the BLAS function that will be executed.
 *
 * Check cubladx::Function operator documentation for more details
 * (https://docs.nvidia.com/cuda/cublasdx/api/operators.html#function-operator)
 */
typedef enum cublasdxFunction_t {
    /** Matrix-multiply */
    CUBLASDX_FUNCTION_MM = 0,
} cublasdxFunction;

/**
 * @brief cublasDx operators
 *
 * The set of supported cublasDx operators.
 *
 * Check cublaDx description operator documentation for more details
 * (https://docs.nvidia.com/cuda/cublasdx/api/operators.html#function-operator)
 *
 * Check cublasDx execution operator documentation for more details
 * (https://docs.nvidia.com/cuda/cublasdx/api/operators.html#execution-operators)
 */
typedef enum cublasdxOperatorType_t {
    /** Operator data type: \ref cublasdxFunction_t.
     * Operator definition: required */
    CUBLASDX_OPERATOR_FUNCTION = 0,
    /** Operator data type: long long int * 3.
     * Expected content: `<M, N, K>` problem sizes.
     * Operator definition: required */
    CUBLASDX_OPERATOR_SIZE = 1,
    /** Operator data type: \ref cublasdxType_t.
     * Operator definition: optional */
    CUBLASDX_OPERATOR_TYPE = 2,
    /** Operator data type: \ref commondxPrecision_t * 3.
     * Expected content: `<A, B, C>` precisions.
     * Operator definition: required */
    CUBLASDX_OPERATOR_PRECISION = 3,
    /** Operator data type: long long int.
     * Expected content: 700 (Volta), 800 (Ampere), ....
     * Operator definition: required */
    CUBLASDX_OPERATOR_SM = 4,
    /** Operator data type: \ref commondxExecution_t.
     * Operator definition: required */
    CUBLASDX_OPERATOR_EXECUTION = 5,
    /** Operator data type: long long int * 3.
     * Expected content: <x, y, z> block dimensions.
     * Operator definition: optional */
    CUBLASDX_OPERATOR_BLOCK_DIM = 6,
    /** Operator data type: long long int * 3.
     * Expected content: <LDA, LDB, LDC> leading dimensions.
     * Operator definition: optional */
    CUBLASDX_OPERATOR_LEADING_DIMENSION = 7,
    /** Operator data type: \ref cublasdxTransposeMode_t * 2.
     * Expected content: <A, B> transpose modes.
     * Operator definition: optional */
    CUBLASDX_OPERATOR_TRANSPOSE_MODE = 8,
    /** Operator data type: \ref cublasdxApi_t.
     * Operator definition: required */
    CUBLASDX_OPERATOR_API = 9,
    /** Operator data type: \ref cublasdxArrangement_t * 3.
     * Expected content: <A, B, C> data arrangements.
     * Operator definition: optional */
    CUBLASDX_OPERATOR_ARRANGEMENT = 10,
    /** Operator data type: long long int * 3.
     * Expected content: <AAlign, BAlign, CAlign> tensors' alignments.
     * Operator definition: optional */
    CUBLASDX_OPERATOR_ALIGNMENT = 11,
    /** Operator data type: long long int.
     * Expected content: 1, to enable cublasdx::experimental::StaticBlockDim.
     * Operator definition: optional */
    CUBLASDX_OPERATOR_STATIC_BLOCK_DIM = 12,
} cublasdxOperatorType;

/**
 * @brief cublasDx traits
 *
 * The set of supported types of traits that can be accessed from finalized sources
 * that use cublasDx.
 *
 * Check cublasDx Execution Block Traits documentation for more details
 * (https://docs.nvidia.com/cuda/cublasdx/api/traits.html#block-traits)
 */
typedef enum cublasdxTraitType_t {
    /** Trait data type: \ref commondxValueType_t * 3.
     * Expected content: <A, B, C> types.
     */
    CUBLASDX_TRAIT_VALUE_TYPE = 0,
    /** Trait data type: long long int * 3.
     * Expected content: <M, N, K> problem sizes.
     */
    CUBLASDX_TRAIT_SIZE = 1,
    /** Trait data type: long long int.
     * Expected content: multiplication result of block dimensions (x * y * z).
     */
    CUBLASDX_TRAIT_BLOCK_SIZE = 2,
    /** Trait data type: long long int * 3.
     * Expected content: <x, y, z> block dimension.
     */
    CUBLASDX_TRAIT_BLOCK_DIM = 3,
    /** Trait data type: long long int * 3.
     * Expected content: <LDA, LDB, LDC> leading dimensions.
     */
    CUBLASDX_TRAIT_LEADING_DIMENSION = 4,
    /** Trait data type: C-string
     */
    CUBLASDX_TRAIT_SYMBOL_NAME = 5,
    /** Trait data type: \ref cublasdxArrangement_t * 3.
     * Expected content: <A, B, C> data arrangements.
     */
    CUBLASDX_TRAIT_ARRANGEMENT = 6,
    /** Trait data type: long long int * 3.
     * Expected content: <AAlign, BAlign, CAlign> tensors' alignments, in bytes.
     */
    CUBLASDX_TRAIT_ALIGNMENT = 7,
    /** Trait data type: long long int * 3.
     * Expected content: <LDA, LDB, LDC>.
     */
    CUBLASDX_TRAIT_SUGGESTED_LEADING_DIMENSION = 8,
    /** Trait data type: long long int * 3.
     * Expected content: <X, Y, Z>.
     */
    CUBLASDX_TRAIT_SUGGESTED_BLOCK_DIM = 9,
    /** Trait data type: long long int.
     * Expected content: the product of three elements in block dimension.
     */
    CUBLASDX_TRAIT_MAX_THREADS_PER_BLOCK = 10
} cublasdxTraitType;

/**
 * @brief cuBLASDx desired tensor type
 *
 * Tensor types are opaque (layout is unspecified), non-owning, and defined by
 * - Memory space (global, shared or register memory)
 * - Size & alignment (in bytes)
 *
 * Tensor's representation in memory depends on their memory space.
 * Shared & register tensors are defined as
 *
 * \code
 * struct tensor {
 *   void* ptr;
 * }
 * \endcode
 *
 * Global memory tensors have an associated runtime leading dimension (64b signed integer), and their
 * representation is
 *
 * \code
 * struct tensor {
 *   void* ptr;
 *   long long ld;
 * }
 * \endcode
 *
 * In either case, `ptr` must point to some storage (with appropriate size and alignment,
 * see below) and is not owning. The user is expected to keep memory allocated beyond
 * any use of the tensor. `ld` is a signed, 64bit integer (`long long`) equal to the leading dimension of the
 * global memory tensor. The leading dimension is the number of *elements* between two successive rows or
 * columns, depending on the context.
 *
 * All tensor APIs take their argument by value (not by pointer) and expect the struct to be passed
 * as-is on the stack.
 *
 * Each opaque tensor type is uniquely identified by a unique ID and name, see \ref cublasdxTensorTrait_t .
 */
typedef enum cublasdxTensorType_t {
    /**
     * A shared memory tensor for `A`, in simple row or column layout
     * In memory representation: `struct { void* ptr; }`.
     * Corresponds to cuBLASDx `make_tensor(..., get_layout_smem_a());`
     **/
    CUBLASDX_TENSOR_SMEM_A = 0,
    /**
     * A shared memory tensor for `B`, in simple row or column layout.
     * In memory representation: `struct { void* ptr; }`.
     * Corresponds to cuBLASDx `make_tensor(..., get_layout_smem_b());`
     **/
    CUBLASDX_TENSOR_SMEM_B = 1,
    /**
     * A shared memory tensor for `C`, in simple row or column layout.
     * In memory representation: `struct { void* ptr; }`.
     * Corresponds to cuBLASDx `make_tensor(..., get_layout_smem_c());`
     **/
    CUBLASDX_TENSOR_SMEM_C = 2,
    /**
     * A shared memory tensor for `A`, in unspecified layout.
     * In memory representation: `struct { void* ptr; }`.
     * Corresponds to cuBLASDx `make_tensor(..., suggest_layout_smem_a());`
     **/
    CUBLASDX_TENSOR_SUGGESTED_SMEM_A = 3,
    /**
     * A shared memory tensor for `B`, in unspecified layout.
     * In memory representation: `struct { void* ptr; }`.
     * Corresponds to cuBLASDx `make_tensor(..., suggest_layout_smem_b());`
     **/
    CUBLASDX_TENSOR_SUGGESTED_SMEM_B = 4,
    /**
     * A shared memory tensor for `C`, in unspecified layout.
     * In memory representation: `struct { void* ptr; }`.
     * Corresponds to cuBLASDx `make_tensor(..., suggest_layout_smem_c());`
     **/
    CUBLASDX_TENSOR_SUGGESTED_SMEM_C = 5,
    /**
     * A register tensor for `C`, in unspecified layout.
     * In memory representation: `struct { void* ptr; }`.
     * Corresponds to cuBLASDx `suggest_partitioner().make_accumulator_fragment();`
     **/
    CUBLASDX_TENSOR_SUGGESTED_RMEM_C = 6,
    /**
     * A global memory view for `A` (typically a tile of a larger matrix)
     * in row or column major format, with a runtime leading dimension (`lda`).
     * In memory representation: `struct { void* ptr; long long int ld; }`.
     * Corresponds to cuBLASDx `make_tensor(a, get_layout_gmem_a(lda));`
     **/
    CUBLASDX_TENSOR_GMEM_A = 7,
    /**
     * A global memory view for `B` (typically a tile of a larger matrix)
     * in row or column major format, with a runtime leading dimension (`ldb`).
     * In memory representation: `struct { void* ptr; long long int ld; }`.
     * Corresponds to cuBLASDx `make_tensor(a, get_layout_gmem_b(ldb));`
     **/
    CUBLASDX_TENSOR_GMEM_B = 8,
    /**
     * A global memory view for `C` (typically a tile of a larger matrix)
     * in row or column major format, with a runtime leading dimension (`ldc`).
     * In memory representation: `struct { void* ptr; long long int ld; }`.
     * Corresponds to cuBLASDx `make_tensor(a, get_layout_gmem_c(ldc));`
     **/
    CUBLASDX_TENSOR_GMEM_C = 9,
} cublasdxTensorType;

/**
 * @brief Tensor options
 *
 */
typedef enum cublasdxTensorOption_t {
    /**
     * The alignment of the underlying storage, in bytes.
     * Trait data type: long long int.
     */
    CUBLASDX_TENSOR_OPTION_ALIGNMENT_BYTES = 0,
} cublasdxTensorOption;

/**
 * @brief Tensor traits, used to query informations
 */
typedef enum cublasdxTensorTrait_t {
    /**
     * The size of the underlying storage, in bytes.
     * Trait data type: long long int.
     */
    CUBLASDX_TENSOR_TRAIT_STORAGE_BYTES = 0,
    /**
     * The alignment of the underlying storage, in bytes.
     * Trait data type: long long int.
     */
    CUBLASDX_TENSOR_TRAIT_ALIGNMENT_BYTES = 1,
    /**
     * The tensor type UID. Tensor types with the same UID
     * are identical and can be passed through various cuBLASDx
     * device functions. UIDs are only well defined within a process.
     * Note: This trait has been deprecated. use `CUBLASDX_TENSOR_TRAIT_OPAQUE_NAME` instead
     * to identify device tensors.
     * Trait data type: long long int.
     */
    CUBLASDX_TENSOR_TRAIT_UID = 2,
    /**
     * A human readable C-string representing the opaque tensor type name
     * like cublasdx_tensor_<hash>. Names are stable and unique per tensor type,
     * and tensor types with the same name can be used interchangeably.
     * Trait data type: C-string.
     */
    CUBLASDX_TENSOR_TRAIT_OPAQUE_NAME = 4,
} cublasdxTensorTrait;

/**
 * @brief Device function traits, used to query informations
 */
typedef enum cublasdxDeviceFunctionTrait_t {
    /**
     * The name of the device function.
     * All device functions are templated on their
     * input type. This means the signature is, for instance,
     * `template<typename T0, typename T1, typename T2, ...> void <name>(T0, T1, T2, ...)`
     * (with or without `void*` for passing scalars)
     * and must be mangled in order to be called as-is.
     * Trait data type: C-string
     */
    CUBLASDX_DEVICE_FUNCTION_TRAIT_NAME = 0,
    /**
     * The mangled name (aka symbol) of the device function.
     * Trait data type: C-string
     */
    CUBLASDX_DEVICE_FUNCTION_TRAIT_SYMBOL = 1,
} cublasdxDeviceFunctionTrait;

/**
 * @brief Device function traits, used to query informations
 */
typedef enum cublasdxDeviceFunctionOption_t {
    /**
     * Specify an optional alignment option for copy functions, in bytes.
     * Must be a power of 2 between 1 and 16.
     * Trait data type: long long int
     */
    CUBLASDX_DEVICE_FUNCTION_OPTION_COPY_ALIGNMENT = 0,
} cublasdxDeviceFunctionOption;

/**
 * @brief Device functions supported by the library
 */
typedef enum cublasdxDeviceFunctionType_t {
    /**
     * Execute the device function (matmul).
     *
     * When the output is a register tensor, the device function API is
     * `execute(A, B, C)` which computes `C += A x B`.
     *
     * When the output is a shared memory tensor, the device function API is
     * `execute(alpha, A, B, beta, C)` which computes
     * `C = alpha A x B + beta C`.
     *
     * `A`, `B` and `C` are tensors, while alpha and beta are scalars of
     * type value_type_c (passed by `void*` pointers).
     *
     * Different `execute` generated from distinct `cublasdxDescriptor`
     * are generally different and cannot be used interchangeably, even
     * with an identical set of input and output tensors.
     *
     * \ref cublasdxBindDeviceFunction must be called with three tensors:
     *     - `A`, an instance of
     *           - `CUBLASDX_TENSOR_SUGGESTED_SMEM_A`
     *           - `CUBLASDX_TENSOR_SMEM_A`
     *     - `B`, an instance of
     *           - `CUBLASDX_TENSOR_SUGGESTED_SMEM_B`
     *           - `CUBLASDX_TENSOR_SMEM_B`
     *     - `C`, an instance of
     *           - `CUBLASDX_TENSOR_SUGGESTED_SMEM_C`
     *           - `CUBLASDX_TENSOR_SMEM_C`
     *           - `CUBLASDX_TENSOR_SUGGESTED_RMEM_C`
     *
     * The resulting function has the following device API:
     *     - `void execute(void* alpha, TA A, TB B, void* beta, TC C)` when `C` is a shared memory tensor,
     *     - `void execute(TA A, TB B, TC C)` when `C` is a register memory tensors.
     *
     * The names for `TA`, `TB` and `TC` can be retreived using \ref CUBLASDX_TENSOR_TRAIT_OPAQUE_NAME .
     *
     */
    CUBLASDX_DEVICE_FUNCTION_EXECUTE = 0,
    /**
     * Copies from one tensor to another. `copy(S, D)` copies
     * from `S` to `D`.
     *
     * Different `copy` generated from distinct `cublasdxDescriptor`
     * are in general different and cannot be used interchangeably, even
     * with identical input and output tensors.
     *
     * \ref cublasdxBindDeviceFunction must be called with two tensors:
     *     - `S`, an instance of
     *          - `CUBLASDX_TENSOR_SUGGESTED_SMEM_A`
     *          - `CUBLASDX_TENSOR_SUGGESTED_SMEM_B`
     *          - `CUBLASDX_TENSOR_SUGGESTED_SMEM_C`
     *          - `CUBLASDX_TENSOR_SUGGESTED_RMEM_C`
     *          - `CUBLASDX_TENSOR_GMEM_A`
     *          - `CUBLASDX_TENSOR_GMEM_B`
     *          - `CUBLASDX_TENSOR_GMEM_C`
     *     - `D`, an instance of
     *          - `CUBLASDX_TENSOR_SUGGESTED_SMEM_A`
     *          - `CUBLASDX_TENSOR_SUGGESTED_SMEM_B`
     *          - `CUBLASDX_TENSOR_SUGGESTED_SMEM_C`
     *          - `CUBLASDX_TENSOR_SUGGESTED_RMEM_C`
     *          - `CUBLASDX_TENSOR_GMEM_A`
     *          - `CUBLASDX_TENSOR_GMEM_B`
     *          - `CUBLASDX_TENSOR_GMEM_C`
     *
     * `S` and `D` can be in different memory spaces but must correspond to the
     * same A, B or C matrix.
     *
     * The resulting function has the following device API: `void copy(TS S, TD D)`
     *
     * The names for `TS` and `TD` can be retreived using \ref CUBLASDX_TENSOR_TRAIT_OPAQUE_NAME .
     *
     */
    CUBLASDX_DEVICE_FUNCTION_COPY = 1,
    /**
     * Wait on all previously issued copies to complete.
     * `wait_all()` waits on all previously issued copies to complete.
     *
     * Different `wait_all` from distinct `cublasdxDescriptor` are
     * identical and may used interchangeably. They will have the same
     * template names, mangled names and implementation.
     *
     * \ref cublasdxBindDeviceFunction must be called without any tensors.
     *
     * The resulting function has the following device API: `void copy_wait()`
     *
     */
    CUBLASDX_DEVICE_FUNCTION_COPY_WAIT = 2,
    /**
     * Zeroes out a tensor. `clear(C)` zeroes out `C`.
     *
     * Different `clear` generated from distinct `cublasdxDescriptor`
     * are in general different and cannot be used interchangeably, even
     * with identical input and output tensors.
     *
     * \ref cublasdxBindDeviceFunction must be called with one tensors:
     *     - `C`, an instance of
     *          - `CUBLASDX_TENSOR_SUGGESTED_RMEM_C`
     *
     * The resulting function has the following device API: `void clear(TC C)`
     *
     * The name for `TC` can be retreived using \ref CUBLASDX_TENSOR_TRAIT_OPAQUE_NAME .
     *
     */
    CUBLASDX_DEVICE_FUNCTION_CLEAR = 3,
    /**
     * Computes `D = alpha * C + beta * D`.
     *
     * Different `axpby` generated from distinct `cublasdxDescriptor`
     * are in general different and cannot be used interchangeably, even
     * with identical input and output tensors.
     *
     * \ref cublasdxBindDeviceFunction must be called with two tensors:
     *     - `C`, an instance of
     *          - `CUBLASDX_TENSOR_SUGGESTED_RMEM_C`
     *     - `D`, an instance of
     *          - `CUBLASDX_TENSOR_SUGGESTED_RMEM_C`
     *
     * The resulting function has the following device API:
     *     - `void axpby(void* alpha, TC C, void* beta, TD D)` where `C` and `D` are tensors
     *       and `alpha`, `beta` are pointers to value of type `value_type_c`.
     *
     * The name for `TC` and `TD` can be retreived using \ref CUBLASDX_TENSOR_TRAIT_OPAQUE_NAME .
     */
    CUBLASDX_DEVICE_FUNCTION_AXPBY = 4,
} cublasdxDeviceFunctionType;

/**
 * @brief Creates a cuBLASDx descriptor
 *
 * @param[out] handle A pointer to a handle
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxCreateDescriptor(cublasdxDescriptor* handle)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Sets a C-string option on a cuBLASDx descriptor.
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] option An option to set the descriptor to.
 * @param[in] value A pointer to a C-string. Cannot be `NULL`.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxSetOptionStr(cublasdxDescriptor handle,
                                                                     commondxOption option,
                                                                     const char* value) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Sets one or more C-string options on a cuBLASDx descriptor.
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] option An option to set the descriptor to.
 * @param[in] count The number of options.
 * @param[in] values A pointer to an array of `count` C-strings.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxSetOptionStrs(commondxCode code,
                                                                            commondxOption option,
                                                                            size_t count,
                                                                            const char** values) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Set an operator on a cuBLASDx descriptor to an integer value
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] op An operator to set the descriptor to.
 * @param[in] value The operator's value
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxSetOperatorInt64(cublasdxDescriptor handle,
                                                                         cublasdxOperatorType op,
                                                                         long long int value) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Set an operator on a cuBLASDx descriptor to an integer array
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] op An option to set the descriptor to.
 * @param[in] count The size of the operator array, as indicated by the \ref cublasdxOperatorType_t documentation
 * @param[in] array A pointer to an array containing the operator's value. Must point to at least `count` elements.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL
cublasdxSetOperatorInt64s(cublasdxDescriptor handle, cublasdxOperatorType op, size_t count, const long long int* array)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Binds (aka create) a tensor handle to a tensor
 * The tensor is bound to the cuBLASDx descriptor and will be freed when the cuBLASDx descriptor is
 * destroyed.
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] tensor_type The tensor type to bind to the handle
 * @param[out] tensor A valid tensor handle
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxBindTensor(cublasdxDescriptor handle,
                                                                   cublasdxTensorType tensor_type,
                                                                   cublasdxTensor* tensor) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Set an option on a tensor.
 * This must be called before the tensor is finalized.
 *
 * @param[in] tensor A cuBLASDx tensor, output of \ref cublasdxBindTensor.
 * @param[in] option The option to set on the tensor.
 * @param[in] value A value for the option.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxSetTensorOptionInt64(cublasdxTensor tensor,
                                                                             cublasdxTensorOption option,
                                                                             long long int value)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Finalize the tensors. This is required before traits can be queried.
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] count The number of tensors to finalized
 * @param[out] array The array of tensors
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL
cublasdxFinalizeTensors(cublasdxDescriptor handle, size_t count, const cublasdxTensor* array) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Query an integer trait value from a finalized tensor
 *
 * @param[in] tensor A finalized tensor handle, output of \ref cublasdxBindTensor
 * @param[in] trait The trait to query
 * @param[out] value The trait value
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxGetTensorTraitInt64(cublasdxTensor tensor,
                                                                            cublasdxTensorTrait trait,
                                                                            long long int* value)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Query an C-string trait's size from a finalized tensor
 *
 * @param[in] tensor A finalized tensor handle, output of \ref cublasdxBindTensor
 * @param[in] trait The trait to query
 * @param[out] size The C-string size (including the `\0`)
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxGetTensorTraitStrSize(cublasdxTensor tensor,
                                                                              cublasdxTensorTrait trait,
                                                                              size_t* size) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Query a C-string trait value from a finalized tensor
 *
 * @param[in] tensor A finalized tensor handle, output of \ref cublasdxBindTensor
 * @param[in] trait The trait to query
 * @param[in] size The C-string size, as returned by \ref cublasdxGetTensorTraitStrSize
 * @param[out] value The C-string trait value
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxGetTensorTraitStr(cublasdxTensor tensor,
                                                                          cublasdxTensorTrait trait,
                                                                          size_t size,
                                                                          char* value) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Binds (aka create) a device function from a set of tensor
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] device_function_type The device function to create
 * @param[in] count The number of input & output tensors to the device function
 * @param[in] array The array of input & output tensors
 * @param[out] device_function The device function
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL
cublasdxBindDeviceFunction(cublasdxDescriptor handle,
                           cublasdxDeviceFunctionType device_function_type,
                           size_t count,
                           const cublasdxTensor* array,
                           cublasdxDeviceFunction* device_function) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Finalize (aka codegen) a set of device function into a code handle
 *
 * After this, LTOIR can be extracted from `code` using \ref commondxGetCodeLTOIR
 *
 * @param[out] code A code handle, output from \ref commondxCreateCode
 * @param[in] count The number of device functions to codegen
 * @param[in] array The array of device functions
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxFinalizeDeviceFunctions(commondxCode code,
                                                                                size_t count,
                                                                                const cublasdxDeviceFunction* array)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Query a device function C-string trait value size
 *
 * @param[in] device_function A device function handle, output from \ref cublasdxFinalizeDeviceFunctions
 * @param[in] trait The trait to query the device function
 * @param[out] size The size of the trait value C-string, including the `\0`
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL
cublasdxGetDeviceFunctionTraitStrSize(cublasdxDeviceFunction device_function,
                                      cublasdxDeviceFunctionTrait trait,
                                      size_t* size) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Query a device function C-string trait value
 *
 * @param[in] device_function A device function handle, output from \ref cublasdxFinalizeDeviceFunctions
 * @param[in] trait The trait to query the device function
 * @param[in] size The size of the trait value C-string as returned by \ref cublasdxGetDeviceFunctionTraitStrSize
 * @param[out] value The trait value as a C-string. Must point to at least `size` bytes.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL
cublasdxGetDeviceFunctionTraitStr(cublasdxDeviceFunction device_function,
                                  cublasdxDeviceFunctionTrait trait,
                                  size_t size,
                                  char* value) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Returns the LTOIR size, in bytes
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[out] lto_size The size of the LTOIR.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxGetLTOIRSize(cublasdxDescriptor handle,
                                                                     size_t* lto_size) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Returns the LTOIR
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] size The size, in bytes, of the LTOIR, as returned by \ref cublasdxGetLTOIRSize
 * @param[out] lto A pointer to at least `size` bytes containing the LTOIR
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxGetLTOIR(cublasdxDescriptor handle,
                                                                 size_t size,
                                                                 void* lto) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Returns the size of a C-string trait
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] trait The trait to query the size of
 * @param[out] size The size of the C-string value, including the `\0`.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxGetTraitStrSize(cublasdxDescriptor handle,
                                                                        cublasdxTraitType trait,
                                                                        size_t* size) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Returns a C-string trait's value
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] trait The trait to query on the descriptor
 * @param[in] size The size of the C-string (including the `\0`)
 * @param[out] value The C-string trait value. Must point to at least `size` bytes.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxGetTraitStr(cublasdxDescriptor handle,
                                                                    cublasdxTraitType trait,
                                                                    size_t size,
                                                                    char* value) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Returns an integer trait's value
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] trait A trait to query the handle for
 * @param[out] value The trait value.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxGetTraitInt64(cublasdxDescriptor handle,
                                                                      cublasdxTraitType trait,
                                                                      long long int* value) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Returns an array trait's value
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] trait A trait to query handle for
 * @param[in] count The number of elements in the trait array, as indicated in the \ref cublasdxTraitType_t
 * documentation.
 * @param[out] array A pointer to at least count integers. As output, an array filled with the trait value.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxGetTraitInt64s(cublasdxDescriptor handle,
                                                                       cublasdxTraitType trait,
                                                                       size_t count,
                                                                       long long int* array) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Returns an array trait's value, when the elements are commondxValueType values
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @param[in] trait A trait to query handle for
 * @param[in] count The number of elements in the trait array, as indicated in the \ref cublasdxTraitType_t
 * documentation.
 * @param[out] array A pointer to at least count commondxValueType. As output, an array filled with the trait value.
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxGetTraitCommondxDataTypes(cublasdxDescriptor handle,
                                                                                  cublasdxTraitType trait,
                                                                                  size_t count,
                                                                                  commondxValueType* array)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert an operator enum to a human readable C-string
 *
 * @param[in] op The operator enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxOperatorTypeToStr(cublasdxOperatorType op) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a trait enum to a human readable C-string
 *
 * @param[in] trait The trait enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxTraitTypeToStr(cublasdxTraitType trait) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Fill an instance of commondxCode with the code from the cuBLASDx descriptor
 *
 * @param[out] code A commondxCode code
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxFinalizeCode(commondxCode code,
                                                                     cublasdxDescriptor handle) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Destroy a cuBLASDx descriptor
 *
 * @param[in] handle A cuBLASDx descriptor, output of \ref cublasdxCreateDescriptor
 * @return `COMMONDX_SUCCESS` on success, or an error code.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL cublasdxDestroyDescriptor(cublasdxDescriptor handle)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert an API enum to a human readable C-string
 *
 * @param[in] api The API enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxApiToStr(cublasdxApi api) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a type enum to a human readable C-string
 *
 * @param[in] type The type enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxTypeToStr(cublasdxType type) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a transpose mode enum to a human readable C-string
 *
 * @param[in] mode The transpose mode enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxTransposeModeToStr(cublasdxTransposeMode mode) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert an arrangement enum to a human readable C-string
 *
 * @param[in] arrangement The arrangement enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxArrangementToStr(cublasdxArrangement arrangement)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a function enum to a human readable C-string
 *
 * @param[in] function The function enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxFunctionToStr(cublasdxFunction function) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a tensor type enum to a human readable C-string
 *
 * @param[in] type The tensor type enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxTensorTypeToStr(cublasdxTensorType type) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a tensor option enum to a human readable C-string
 *
 * @param[in] option The tensor option enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxTensorOptionToStr(cublasdxTensorOption option) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a tensor trait enum to a human readable C-string
 *
 * @param[in] trait The tensor trait enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxTensorTraitToStr(cublasdxTensorTrait trait) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a device function trait enum to a human readable C-string
 *
 * @param[in] trait The device function trait enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxDeviceFunctionTraitToStr(cublasdxDeviceFunctionTrait trait)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a device function option enum to a human readable C-string
 *
 * @param[in] option The device function option enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxDeviceFunctionOptionToStr(cublasdxDeviceFunctionOption option)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a device function type enum to a human readable C-string
 *
 * @param[in] type The device function type enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL cublasdxDeviceFunctionTypeToStr(cublasdxDeviceFunctionType type)
    LIBMATHDX_API_NOEXCEPT;

#if defined(__cplusplus)
} // extern "C"
#endif /* __cplusplus */

#endif // MATHDX_LIBCUBLASDX_H
