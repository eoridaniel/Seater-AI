# Copyright 2021-2022 NVIDIA Corporation.  All rights reserved.
#
# Please refer to the NVIDIA end user license agreement (EULA) associated
# with this source code for terms and conditions that govern your use of
# this software. Any use, reproduction, disclosure, or distribution of
# this software and related documentation outside the terms of the EULA
# is strictly prohibited.
cimport cuda._lib.dlfcn as dlfcn

cdef bint __cuPythonInit = False
cdef void *__nvrtcGetErrorString = NULL
cdef void *__nvrtcVersion = NULL
cdef void *__nvrtcGetNumSupportedArchs = NULL
cdef void *__nvrtcGetSupportedArchs = NULL
cdef void *__nvrtcCreateProgram = NULL
cdef void *__nvrtcDestroyProgram = NULL
cdef void *__nvrtcCompileProgram = NULL
cdef void *__nvrtcGetPTXSize = NULL
cdef void *__nvrtcGetPTX = NULL
cdef void *__nvrtcGetCUBINSize = NULL
cdef void *__nvrtcGetCUBIN = NULL
cdef void *__nvrtcGetNVVMSize = NULL
cdef void *__nvrtcGetNVVM = NULL
cdef void *__nvrtcGetProgramLogSize = NULL
cdef void *__nvrtcGetProgramLog = NULL
cdef void *__nvrtcAddNameExpression = NULL
cdef void *__nvrtcGetLoweredName = NULL

cdef int cuPythonInit() nogil except -1:
    global __cuPythonInit
    if __cuPythonInit:
        return 0
    __cuPythonInit = True

    # Load library
    handle = NULL
    if handle == NULL:
        handle = dlfcn.dlopen('libnvrtc.so.11.2', dlfcn.RTLD_NOW)
    if handle == NULL:
        handle = dlfcn.dlopen('libnvrtc.so.11.1', dlfcn.RTLD_NOW)
    if handle == NULL:
        handle = dlfcn.dlopen('libnvrtc.so.11.0', dlfcn.RTLD_NOW)
    if handle == NULL:
        with gil:
            raise RuntimeError('Failed to dlopen libnvrtc.so.11.2, or libnvrtc.so.11.1, or libnvrtc.so.11.0')


    # Load function
    global __nvrtcGetErrorString
    __nvrtcGetErrorString = dlfcn.dlsym(handle, 'nvrtcGetErrorString')
    global __nvrtcVersion
    __nvrtcVersion = dlfcn.dlsym(handle, 'nvrtcVersion')
    global __nvrtcGetNumSupportedArchs
    __nvrtcGetNumSupportedArchs = dlfcn.dlsym(handle, 'nvrtcGetNumSupportedArchs')
    global __nvrtcGetSupportedArchs
    __nvrtcGetSupportedArchs = dlfcn.dlsym(handle, 'nvrtcGetSupportedArchs')
    global __nvrtcCreateProgram
    __nvrtcCreateProgram = dlfcn.dlsym(handle, 'nvrtcCreateProgram')
    global __nvrtcDestroyProgram
    __nvrtcDestroyProgram = dlfcn.dlsym(handle, 'nvrtcDestroyProgram')
    global __nvrtcCompileProgram
    __nvrtcCompileProgram = dlfcn.dlsym(handle, 'nvrtcCompileProgram')
    global __nvrtcGetPTXSize
    __nvrtcGetPTXSize = dlfcn.dlsym(handle, 'nvrtcGetPTXSize')
    global __nvrtcGetPTX
    __nvrtcGetPTX = dlfcn.dlsym(handle, 'nvrtcGetPTX')
    global __nvrtcGetCUBINSize
    __nvrtcGetCUBINSize = dlfcn.dlsym(handle, 'nvrtcGetCUBINSize')
    global __nvrtcGetCUBIN
    __nvrtcGetCUBIN = dlfcn.dlsym(handle, 'nvrtcGetCUBIN')
    global __nvrtcGetNVVMSize
    __nvrtcGetNVVMSize = dlfcn.dlsym(handle, 'nvrtcGetNVVMSize')
    global __nvrtcGetNVVM
    __nvrtcGetNVVM = dlfcn.dlsym(handle, 'nvrtcGetNVVM')
    global __nvrtcGetProgramLogSize
    __nvrtcGetProgramLogSize = dlfcn.dlsym(handle, 'nvrtcGetProgramLogSize')
    global __nvrtcGetProgramLog
    __nvrtcGetProgramLog = dlfcn.dlsym(handle, 'nvrtcGetProgramLog')
    global __nvrtcAddNameExpression
    __nvrtcAddNameExpression = dlfcn.dlsym(handle, 'nvrtcAddNameExpression')
    global __nvrtcGetLoweredName
    __nvrtcGetLoweredName = dlfcn.dlsym(handle, 'nvrtcGetLoweredName')

cdef const char* _nvrtcGetErrorString(nvrtcResult result) nogil except ?NULL:
    global __nvrtcGetErrorString
    cuPythonInit()
    if __nvrtcGetErrorString == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetErrorString" not found')
    err = (<const char* (*)(nvrtcResult) nogil> __nvrtcGetErrorString)(result)
    return err

cdef nvrtcResult _nvrtcVersion(int* major, int* minor) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcVersion
    cuPythonInit()
    if __nvrtcVersion == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcVersion" not found')
    err = (<nvrtcResult (*)(int*, int*) nogil> __nvrtcVersion)(major, minor)
    return err

cdef nvrtcResult _nvrtcGetNumSupportedArchs(int* numArchs) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetNumSupportedArchs
    cuPythonInit()
    if __nvrtcGetNumSupportedArchs == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetNumSupportedArchs" not found')
    err = (<nvrtcResult (*)(int*) nogil> __nvrtcGetNumSupportedArchs)(numArchs)
    return err

cdef nvrtcResult _nvrtcGetSupportedArchs(int* supportedArchs) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetSupportedArchs
    cuPythonInit()
    if __nvrtcGetSupportedArchs == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetSupportedArchs" not found')
    err = (<nvrtcResult (*)(int*) nogil> __nvrtcGetSupportedArchs)(supportedArchs)
    return err

cdef nvrtcResult _nvrtcCreateProgram(nvrtcProgram* prog, const char* src, const char* name, int numHeaders, const char** headers, const char** includeNames) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcCreateProgram
    cuPythonInit()
    if __nvrtcCreateProgram == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcCreateProgram" not found')
    err = (<nvrtcResult (*)(nvrtcProgram*, const char*, const char*, int, const char**, const char**) nogil> __nvrtcCreateProgram)(prog, src, name, numHeaders, headers, includeNames)
    return err

cdef nvrtcResult _nvrtcDestroyProgram(nvrtcProgram* prog) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcDestroyProgram
    cuPythonInit()
    if __nvrtcDestroyProgram == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcDestroyProgram" not found')
    err = (<nvrtcResult (*)(nvrtcProgram*) nogil> __nvrtcDestroyProgram)(prog)
    return err

cdef nvrtcResult _nvrtcCompileProgram(nvrtcProgram prog, int numOptions, const char** options) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcCompileProgram
    cuPythonInit()
    if __nvrtcCompileProgram == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcCompileProgram" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, int, const char**) nogil> __nvrtcCompileProgram)(prog, numOptions, options)
    return err

cdef nvrtcResult _nvrtcGetPTXSize(nvrtcProgram prog, size_t* ptxSizeRet) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetPTXSize
    cuPythonInit()
    if __nvrtcGetPTXSize == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetPTXSize" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, size_t*) nogil> __nvrtcGetPTXSize)(prog, ptxSizeRet)
    return err

cdef nvrtcResult _nvrtcGetPTX(nvrtcProgram prog, char* ptx) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetPTX
    cuPythonInit()
    if __nvrtcGetPTX == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetPTX" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, char*) nogil> __nvrtcGetPTX)(prog, ptx)
    return err

cdef nvrtcResult _nvrtcGetCUBINSize(nvrtcProgram prog, size_t* cubinSizeRet) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetCUBINSize
    cuPythonInit()
    if __nvrtcGetCUBINSize == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetCUBINSize" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, size_t*) nogil> __nvrtcGetCUBINSize)(prog, cubinSizeRet)
    return err

cdef nvrtcResult _nvrtcGetCUBIN(nvrtcProgram prog, char* cubin) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetCUBIN
    cuPythonInit()
    if __nvrtcGetCUBIN == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetCUBIN" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, char*) nogil> __nvrtcGetCUBIN)(prog, cubin)
    return err

cdef nvrtcResult _nvrtcGetNVVMSize(nvrtcProgram prog, size_t* nvvmSizeRet) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetNVVMSize
    cuPythonInit()
    if __nvrtcGetNVVMSize == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetNVVMSize" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, size_t*) nogil> __nvrtcGetNVVMSize)(prog, nvvmSizeRet)
    return err

cdef nvrtcResult _nvrtcGetNVVM(nvrtcProgram prog, char* nvvm) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetNVVM
    cuPythonInit()
    if __nvrtcGetNVVM == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetNVVM" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, char*) nogil> __nvrtcGetNVVM)(prog, nvvm)
    return err

cdef nvrtcResult _nvrtcGetProgramLogSize(nvrtcProgram prog, size_t* logSizeRet) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetProgramLogSize
    cuPythonInit()
    if __nvrtcGetProgramLogSize == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetProgramLogSize" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, size_t*) nogil> __nvrtcGetProgramLogSize)(prog, logSizeRet)
    return err

cdef nvrtcResult _nvrtcGetProgramLog(nvrtcProgram prog, char* log) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetProgramLog
    cuPythonInit()
    if __nvrtcGetProgramLog == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetProgramLog" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, char*) nogil> __nvrtcGetProgramLog)(prog, log)
    return err

cdef nvrtcResult _nvrtcAddNameExpression(nvrtcProgram prog, const char* name_expression) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcAddNameExpression
    cuPythonInit()
    if __nvrtcAddNameExpression == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcAddNameExpression" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, const char*) nogil> __nvrtcAddNameExpression)(prog, name_expression)
    return err

cdef nvrtcResult _nvrtcGetLoweredName(nvrtcProgram prog, const char* name_expression, const char** lowered_name) nogil except ?NVRTC_ERROR_INVALID_INPUT:
    global __nvrtcGetLoweredName
    cuPythonInit()
    if __nvrtcGetLoweredName == NULL:
        with gil:
            raise RuntimeError('Function "nvrtcGetLoweredName" not found')
    err = (<nvrtcResult (*)(nvrtcProgram, const char*, const char**) nogil> __nvrtcGetLoweredName)(prog, name_expression, lowered_name)
    return err
