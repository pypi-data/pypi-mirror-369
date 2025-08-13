// Copyright (c) 2024-2025, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

// libmathdx's API is subject to change.
// Please contact Math-Libs-Feedback@nvidia.com for usage feedback.

#ifndef MATHDX_LIBCOMMONDX_H
#define MATHDX_LIBCOMMONDX_H

#include <stddef.h>

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

#ifndef LIBMATHDX_API
#if __GNUC__ >= 4
#define LIBMATHDX_API __attribute__((visibility("default")))
#else
#define LIBMATHDX_API
#endif
#endif

#ifndef LIBMATHDX_CALL
#ifdef _WIN32
#define LIBMATHDX_CALL __stdcall
#else
#define LIBMATHDX_CALL
#endif
#endif

#ifdef __cplusplus
#ifndef LIBMATHDX_API_NOEXCEPT
#define LIBMATHDX_API_NOEXCEPT noexcept
#endif
#else
#define LIBMATHDX_API_NOEXCEPT
#endif

/**
 * @brief A handle to some compiled code.
 *
 * Compiled code generally contains one or more device function, and is specified by
 * the code type (e.g. SASS, PTX, LTO - \ref commondxCodeContainer_t) and the compute capability
 * (in the form of an integer, e.g. 800 for CC 8.0).
 *
 * Compiled code can be genrated by a call to \ref cublasdxFinalizeCode,
 * \ref cufftdxFinalizeCode or \ref cusolverdxFinalizeCode.
 */
typedef long long int commondxCode;

/**
 * @brief The set of value types supported by the library.
 *
 * Note that, for complex numbers, this combines real and imaginary part,
 * and that all complex numbers are overaligned on their size.
 */
typedef enum commondxValueType_t {
    /** Equivalent to __nv_fp8_e5m2. Size: 1B, alignment: 1B */
    COMMONDX_R_8F_E5M2 = 0,
    /** Equivalent to 2x__nv_fp8_e5m2. Size: 2B, alignment: 2B (overaligned) */
    COMMONDX_C_8F_E5M2 = 1,
    /** Equivalent to __nv_fp8_e4m3. Size: 1B, alignment: 1B */
    COMMONDX_R_8F_E4M3 = 2,
    /** Equivalent to 2x__nv_fp8_e4m3. Size: 2B, alignment: 2B (overaligned) */
    COMMONDX_C_8F_E4M3 = 3,
    /** Equivalent to __nv_bfloat16. Size: 2B, alignment: 2B */
    COMMONDX_R_16BF = 4,
    /** Equivalent to 2x__nv_bfloat16. Size: 4B, alignment: 4B (overaligned) */
    COMMONDX_C_16BF = 5,
    /** Equivalent to __half2. Size: 4B, alignment: 4B */
    COMMONDX_R_16F2 = 6,
    /** Equivalent to __half. Size: 2B, alignment: 2B */
    COMMONDX_R_16F = 7,
    /** Equivalent to 2x__half. Size: 4B, alignment: 4B (overaligned) */
    COMMONDX_C_16F = 8,
    /** Equivalent to 2x__half2. Size: 8B, alignment: 8B (overaligned) */
    COMMONDX_C_16F2 = 9,
    /** Equivalent to tf32. Size: 4B, alignment: 4B */
    COMMONDX_R_32TF = 10,
    /** Equivalent to 2xtf32. Size: 8B, alignment: 8B (overaligned) */
    COMMONDX_C_32TF = 11,
    /** Equivalent to float. Size: 4B, alignment: 4B */
    COMMONDX_R_32F = 12,
    /** Equivalent to 2xfloat. Size: 8B, alignment: 8B (overaligned) */
    COMMONDX_C_32F = 13,
    /** Equivalent to double. Size: 8B, alignment: 8B */
    COMMONDX_R_64F = 14,
    /** Equivalent to 2xdouble. Size: 16B, alignment: 16B (overaligned) */
    COMMONDX_C_64F = 15,
    /** Equivalent to int8_t. Size 1B, alignment: 1B */
    COMMONDX_R_8I = 16,
    /** Equivalent to 2xint8_t. Size 2B, alignment: 2B (overaligned) */
    COMMONDX_C_8I = 17,
    /** Equivalent to int16_t. Size 2B, alignment: 2B */
    COMMONDX_R_16I = 18,
    /** Equivalent to 2xint16_t. Size 4B, alignment: 4B (overaligned) */
    COMMONDX_C_16I = 19,
    /** Equivalent to int32_t. Size 4B, alignment: 4B */
    COMMONDX_R_32I = 20,
    /** Equivalent to 2xint32_t. Size 8B, alignment: 8B (overaligned)*/
    COMMONDX_C_32I = 21,
    /** Equivalent to int64_t. Size 8B, alignment: 8B */
    COMMONDX_R_64I = 22,
    /** Equivalent to 2xint64_t. Size 16B, alignment: 16B (overaligned) */
    COMMONDX_C_64I = 23,
    /** Equivalent to uint8_t. Size 1B, alignment: 1B */
    COMMONDX_R_8UI = 24,
    /** Equivalent to 2xuint8_t. Size 2B, alignment: 2B (overaligned) */
    COMMONDX_C_8UI = 25,
    /** Equivalent to uint16_t. Size 2B, alignment: 2B */
    COMMONDX_R_16UI = 26,
    /** Equivalent to 2xuint16_t. Size 4B, alignment: 4B (overaligned) */
    COMMONDX_C_16UI = 27,
    /** Equivalent to uint32_t. Size 4B, alignment: 4B */
    COMMONDX_R_32UI = 28,
    /** Equivalent to 2xuint32_t. Size 8B, alignment: 8B (overaligned)*/
    COMMONDX_C_32UI = 29,
    /** Equivalent to uint64_t. Size 8B, alignment: 8B */
    COMMONDX_R_64UI = 30,
    /** Equivalent to 2xuint64_t. Size 16B, alignment: 16B (overaligned) */
    COMMONDX_C_64UI = 31,
} commondxValueType;

/**
 * @brief The set of status values that can be returned by APIs defined in the library
 */
typedef enum commondxStatusType_t {
    /** Success */
    COMMONDX_SUCCESS = 0,
    /** One of the input values is not in the allowed range or is otherwise invalid */
    COMMONDX_INVALID_VALUE = 1,
    /** Library internal error */
    COMMONDX_INTERNAL_ERROR = 2,
    /** Compilation did not complete successfully */
    COMMONDX_COMPILATION_ERROR = 3,
    /** Library dependency error */
    COMMONDX_CUFFT_ERROR = 4,
} commondxStatusType;

/**
 * @brief The set of precisions supported by the library
 *
 * For the actual input and output value types, see \ref commondxValueType_t
 */
typedef enum commondxPrecision_t {
    /** Equivalent to __nv_fp8_e5m2 */
    COMMONDX_PRECISION_F8_E5M2 = 0,
    /** Equivalent to __nv_fp8_e4m3 */
    COMMONDX_PRECISION_F8_E4M3 = 1,
    /** Equivalent to __nv_bfloat16 */
    COMMONDX_PRECISION_BF16 = 2,
    /** Equivalent to __half */
    COMMONDX_PRECISION_F16 = 3,
    /** Equivalent to tfloat32 */
    COMMONDX_PRECISION_TF32 = 4,
    /** Equivalent to float */
    COMMONDX_PRECISION_F32 = 5,
    /** Equivalent to double */
    COMMONDX_PRECISION_F64 = 6,
    /** Equivalent to int8_t */
    COMMONDX_PRECISION_I8 = 7,
    /** Equivalent to int16_t */
    COMMONDX_PRECISION_I16 = 8,
    /** Equivalent to int32_t */
    COMMONDX_PRECISION_I32 = 9,
    /** Equivalent to int64_t */
    COMMONDX_PRECISION_I64 = 10,
    /** Equivalent to uint8_t */
    COMMONDX_PRECISION_UI8 = 11,
    /** Equivalent to uint16_t */
    COMMONDX_PRECISION_UI16 = 12,
    /** Equivalent to uint32_t */
    COMMONDX_PRECISION_UI32 = 13,
    /** Equivalent to uint64_t */
    COMMONDX_PRECISION_UI64 = 14,
} commondxPrecision;

/**
 * @brief Options to tweak code generation
 */
typedef enum commondxOption_t {
    /**
     * Symbol to wrap the device function in (default is autogenerated).
     * Associated value must be A C-string.
     */
    COMMONDX_OPTION_SYMBOL_NAME = 0,
    /**
     * Target SM.
     * Associated value must be an integer, e.g. 800 for SM80.
     * See \ref commondxSetCodeOptionInt64
     */
    COMMONDX_OPTION_TARGET_SM = 1,
    /**
     * Code container type (e.g. PTX, LTO, Cubin (SASS), FATBIN).
     * Associated value must be a value of \ref commondxCodeContainer_t
     */
    COMMONDX_OPTION_CODE_CONTAINER = 2,
    /**
     * Code ISA (e.g. 12.3 for LTO).
     * Associated value must be an integer, e.g. 12030 for 12.3
     */
    COMMONDX_OPTION_CODE_ISA = 3,
    /**
     * Extra arguments passed to NVRTC.
     * Must be one or more C-string. See \ref commondxSetCodeOptionStr
     * and \ref commondxSetCodeOptionStrs .
     */
     COMMONDX_OPTION_EXTRA_NVTRC_ARGS = 4,
} commondxOption;

/**
 * @brief The set of execution modes supported by the library
 */
typedef enum commondxExecution_t {
    /**
     * Thread APIs.
     * All threads are independant, divergent control flow is allowed.
     */
    COMMONDX_EXECUTION_THREAD = 0,
    /**
     * Block APIs.
     * All threads in the block cooperate, and all must call the device function.
     */
    COMMONDX_EXECUTION_BLOCK = 1,
} commondxExecution;

/**
 * @brief The set of device code container types supported by the library.
 * See \ref commondxOption_t::COMMONDX_OPTION_CODE_CONTAINER
 */
typedef enum commondxCodeContainer_t {
    /**
     * `.ltoir`, aka `-dlto -ltoir` with NVCC and NVRTC
     */
    COMMONDX_CODE_CONTAINER_LTOIR = 0,
    /**
     * `.fatbin`, aka `-fatbin` with NVCC
     */
    COMMONDX_CODE_CONTAINER_FATBIN = 1,
} commondxCodeContainer;

/**
 * @brief Creates a code handle.
 *
 * @param[out] code A pointer to the output code handle.
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxCreateCode(commondxCode* code) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Set an option on a code handle
 *
 * @param[in] code A code handle from \ref commondxCreateCode
 * @param[in] option The option to set the code to
 * @param[in] value A corresponding value for the selected option
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxSetCodeOptionInt64(commondxCode code,
                                                                           commondxOption option,
                                                                           long long int value) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Set a C-string option on a code handle.
 *
 * @param[in] code A code handle from \ref commondxCreateCode.
 * @param[in] option The option to set the code to.
 * @param[in] value A C-string. Cannot be `NULL`.
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxSetCodeOptionStr(commondxCode code,
                                                                         commondxOption option,
                                                                         const char* value) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Set one or more C-string option on a code handle.
 *
 * @param[in] code A code handle from \ref commondxCreateCode.
 * @param[in] option The option to set the code to.
 * @param[in] count The number of C-strings to set.
 * @param[in] values A pointer to an array of `count` C-strings.
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxSetCodeOptionStrs(commondxCode code,
                                                                          commondxOption option,
                                                                          size_t count,
                                                                          const char** values) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Get option from a code handle
 *
 * @param[in] code A code handle from \ref commondxCreateCode
 * @param[in] option The option to get
 * @param[out] value The option value.
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxGetCodeOptionInt64(commondxCode code,
                                                                           commondxOption option,
                                                                           long long int* value) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Get options (as an array) from a code handle, with one option per output code
 *
 * @param[in] code A code handle from \ref commondxCreateCode
 * @param[in] option The option to get
 * @param[in] size The array size, as result from \ref commondxGetCodeNumLTOIRs
 * @param[out] array A pointer to the beginning of the output array. Must be a pointer to a buffer of at least `size`
 * elements.
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL
commondxGetCodeOptionsInt64s(commondxCode code, commondxOption option, size_t size, long long int* array)
    LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Extract the LTOIR size, in bytes.
 *
 * @param[in] code A code handle from \ref commondxCreateCode
 * @param[out] size The LTOIR size, in bytes.
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxGetCodeLTOIRSize(commondxCode code,
                                                                         size_t* size) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Extract the LTOIR.
 *
 * @param[in] code A code handle from \ref commondxCreateCode
 * @param[in] size The LTOIR size, as returned by \ref commondxGetCodeLTOIRSize
 * @param[out] out The LTOIR. Must be a pointer to a buffer of at least size byte.
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxGetCodeLTOIR(commondxCode code,
                                                                     size_t size,
                                                                     void* out) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Returns the number the LTOIR chunks.
 *
 * Some code produce more than one LTOIR.
 * In this case, this function must be used to retreive the number of LTOIR's.
 *
 * @param[in] code A code handle from \ref commondxCreateCode
 * @param[out] size The number of LTOIR chunks.
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxGetCodeNumLTOIRs(commondxCode code,
                                                                         size_t* size) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Returns the size of all LTOIR chunks.
 *
 * @param[in] code A code handle from \ref commondxCreateCode
 * @param[in] size The number of LTOIR chunks, as returned by \ref commondxGetCodeNumLTOIRs
 * @param[out] out On output, `out[i]` is the size, in byte, of the ith LTOIR chunk.
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxGetCodeLTOIRSizes(commondxCode code,
                                                                          size_t size,
                                                                          size_t* out) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Returns all LTOIR chunks.
 *
 * @param[in] code A code handle from \ref commondxCreateCode
 * @param[in] size The number of LTOIR chunks, as returned by \ref commondxGetCodeNumLTOIRs
 * @param[out] out On output, `out[i]` is filled with the ith LTOIR chunk. `out[i]` must point to a buffer
 * of at least `size[i]` bytes, with `size` the output of \ref commondxGetCodeLTOIRSizes
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxGetCodeLTOIRs(commondxCode code,
                                                                      size_t size,
                                                                      void** out) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Destroys a code handle.
 *
 * @param[in] code A code handle from \ref commondxCreateCode
 * @return `COMMONDX_SUCCESS` on success, or an error.
 */
LIBMATHDX_API commondxStatusType LIBMATHDX_CALL commondxDestroyCode(commondxCode code) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a status enum to a human readable C-string
 *
 * @param[in] status The status enum to convert
 * @return A short C-string describing the enum. This C-string should be not free'ed by the caller.
 */
LIBMATHDX_API const char* LIBMATHDX_CALL commondxStatusToStr(commondxStatusType status) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a precision enum to a human readable C-string
 *
 * @param[in] precision The precision enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL commondxPrecisionToStr(commondxPrecision precision) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a value type enum to a human readable C-string
 *
 * @param[in] value_type The value type enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL commondxValueTypeToStr(commondxValueType value_type) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert an option enum to a human readable C-string
 *
 * @param[in] option The option enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL commondxOptionToStr(commondxOption option) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert an execution enum to a human readable C-string
 *
 * @param[in] execution The execution enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL commondxExecutionToStr(commondxExecution execution) LIBMATHDX_API_NOEXCEPT;

/**
 * @brief Convert a code container type enum to a human readable C-string
 *
 * @param[in] container The code container type enum to convert
 * @return The C-string
 */
LIBMATHDX_API const char* LIBMATHDX_CALL commondxCodeContainerToStr(commondxCodeContainer container)
    LIBMATHDX_API_NOEXCEPT;

#if defined(__cplusplus)
} // extern "C"
#endif /* __cplusplus */

#endif // MATHDX_LIBCOMMONDX_H
