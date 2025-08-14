#ifndef OPENCL_WRAPPER_H
#define OPENCL_WRAPPER_H

#define CL_TARGET_OPENCL_VERSION 100
#include <CL/cl.h>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

#define CL_CHECK(err)                                                          \
  checkError(err,                                                              \
             std::string(__FILE__) + ":" + std::to_string(__LINE__) + ": ");

class OpenCLWrapper {
public:
  OpenCLWrapper() {
    blockSize = std::vector<Size>{1, 8, 8};

    cl_int err;
    cl_uint platformCount;
    clGetPlatformIDs(0, NULL, &platformCount);
    ASSERT(platformCount > 0);

    std::vector<cl_platform_id> platforms(platformCount);
    clGetPlatformIDs(platformCount, platforms.data(), NULL);

    // try to find a GPU
    for (auto platform : platforms) {
      cl_uint deviceCount;
      clGetDeviceIDs(platform, CL_DEVICE_TYPE_GPU, 0, NULL, &deviceCount);
      if (deviceCount > 0) {
        clGetDeviceIDs(platform, CL_DEVICE_TYPE_GPU, 1, &device, NULL);
        context = clCreateContext(NULL, 1, &device, NULL, NULL, &err);
        if (err == CL_SUCCESS) {
          queue = clCreateCommandQueue(context, device, 0, &err);
          if (err == CL_SUCCESS) {
            return;
          }
          clReleaseContext(context);
        }
      }
    }

    // fall back to CPU
    for (auto platform : platforms) {
      cl_uint deviceCount;
      clGetDeviceIDs(platform, CL_DEVICE_TYPE_CPU, 0, NULL, &deviceCount);
      if (deviceCount > 0) {
        clGetDeviceIDs(platform, CL_DEVICE_TYPE_CPU, 1, &device, NULL);
        context = clCreateContext(NULL, 1, &device, NULL, NULL, &err);
        if (err == CL_SUCCESS) {
          queue = clCreateCommandQueue(context, device, 0, &err);
          if (err == CL_SUCCESS) {
            return;
          }
          clReleaseContext(context);
        }
      }
    }

    throw std::runtime_error("No suitable GPU or CPU found for OpenCL.");
  }

  cl_program compile(const std::string &code) {
    cl_int err;

    const char *_code = code.c_str();
    Size codeSize = code.size();
    cl_program program =
        clCreateProgramWithSource(context, 1, &_code, &codeSize, &err);
    CL_CHECK(err);

    err = clBuildProgram(program, 1, &device, NULL, NULL, NULL);

    Size logSize;
    clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG, 0, NULL,
                          &logSize);
    if ((err != CL_SUCCESS) or (logSize > 2)) {
      std::vector<char> buildLog(logSize);
      clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG, logSize,
                            buildLog.data(), NULL);
      std::cerr << buildLog.data() << std::endl;
      CL_CHECK(err);
    }
    programs.push_back(program);
    findKernels(program);
    return program;
  }

  void findKernels(cl_program program) {
    cl_int err;
    cl_uint num_kernels;
    err = clCreateKernelsInProgram(program, 0, NULL, &num_kernels);
    CL_CHECK(err);

    cl_kernel *_kernels = (cl_kernel *)malloc(num_kernels * sizeof(cl_kernel));
    ASSERT(_kernels != NULL);

    err = clCreateKernelsInProgram(program, num_kernels, _kernels, NULL);
    CL_CHECK(err);

    for (cl_uint i = 0; i < num_kernels; i++) {
      char name[256];
      Size name_size;
      err = clGetKernelInfo(_kernels[i], CL_KERNEL_FUNCTION_NAME, sizeof(name),
                            name, &name_size);
      kernels[name] = _kernels[i];
      CL_CHECK(err);
    }
  }

  std::vector<Size> getBlockSize() const { return blockSize; }

  void setBlockSize(const std::vector<Size> &blockSize) {
    this->blockSize = blockSize;
  }

  template <typename... Args>
  void execute(const std::string &kernelName, const std::vector<Size> &workSize,
               Args... args) {
    Size dim = workSize.size();
    Size localWorkSize[dim];
    Size globalWorkSize[dim];
    for (Size d = 0; d < dim; d++) {
      const Size L = d < blockSize.size() ? blockSize[d] : 1;
      localWorkSize[d] = L;
      globalWorkSize[d] = ((workSize[d] + L - 1) / L) * L;
    }

    auto it = kernels.find(kernelName);
    ASSERT(it != kernels.end());

    cl_kernel kernel = it->second;
    setKernelArg(kernel, 0, args...);

    cl_int err = clEnqueueNDRangeKernel(
        queue, kernel, dim, NULL, globalWorkSize, localWorkSize, 0, NULL, NULL);
    CL_CHECK(err);

    clFinish(queue);
  }

  cl_mem buffer(Size size, void *data, cl_int flags = CL_MEM_READ_WRITE) {
    cl_int err;
    cl_mem buffer = clCreateBuffer(context, flags, size, data, &err);
    CL_CHECK(err);
    return buffer;
  }

  cl_mem bufferR(Size size, void *data) {
    return buffer(size, data, CL_MEM_READ_ONLY | CL_MEM_COPY_HOST_PTR);
  }

  cl_mem bufferW(Size size, void *data = NULL) {
    return buffer(size, data, CL_MEM_WRITE_ONLY);
  }

  void copyBufferData(Size size, cl_mem buffer, void *data) {
    cl_int err = clEnqueueReadBuffer(queue, buffer, CL_TRUE, 0, size, data, 0,
                                     NULL, NULL);
    CL_CHECK(err);
  }

  void free(cl_mem buffer) {
    cl_int err = clReleaseMemObject(buffer);
    CL_CHECK(err);
  }

  ~OpenCLWrapper() {
    for (auto &kernel : kernels) {
      clReleaseKernel(kernel.second);
    }

    for (auto &program : programs) {
      clReleaseProgram(program);
    }

    clReleaseCommandQueue(queue);
    clReleaseContext(context);
  }

  cl_int checkError(cl_int error, const std::string message = "") {
    if (error != CL_SUCCESS) {
      throw std::runtime_error(message + getErrorString(error));
    }
    return error;
  }

  const char *getErrorString(cl_int error) {
    // Source: https://stackoverflow.com/posts/24336429/
    switch (error) {
    // run-time and JIT compiler errors
    case 0:
      return "CL_SUCCESS";
    case -1:
      return "CL_DEVICE_NOT_FOUND";
    case -2:
      return "CL_DEVICE_NOT_AVAILABLE";
    case -3:
      return "CL_COMPILER_NOT_AVAILABLE";
    case -4:
      return "CL_MEM_OBJECT_ALLOCATION_FAILURE";
    case -5:
      return "CL_OUT_OF_RESOURCES";
    case -6:
      return "CL_OUT_OF_HOST_MEMORY";
    case -7:
      return "CL_PROFILING_INFO_NOT_AVAILABLE";
    case -8:
      return "CL_MEM_COPY_OVERLAP";
    case -9:
      return "CL_IMAGE_FORMAT_MISMATCH";
    case -10:
      return "CL_IMAGE_FORMAT_NOT_SUPPORTED";
    case -11:
      return "CL_BUILD_PROGRAM_FAILURE";
    case -12:
      return "CL_MAP_FAILURE";
    case -13:
      return "CL_MISALIGNED_SUB_BUFFER_OFFSET";
    case -14:
      return "CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST";
    case -15:
      return "CL_COMPILE_PROGRAM_FAILURE";
    case -16:
      return "CL_LINKER_NOT_AVAILABLE";
    case -17:
      return "CL_LINK_PROGRAM_FAILURE";
    case -18:
      return "CL_DEVICE_PARTITION_FAILED";
    case -19:
      return "CL_KERNEL_ARG_INFO_NOT_AVAILABLE";

    // compile-time errors
    case -30:
      return "CL_INVALID_VALUE";
    case -31:
      return "CL_INVALID_DEVICE_TYPE";
    case -32:
      return "CL_INVALID_PLATFORM";
    case -33:
      return "CL_INVALID_DEVICE";
    case -34:
      return "CL_INVALID_CONTEXT";
    case -35:
      return "CL_INVALID_QUEUE_PROPERTIES";
    case -36:
      return "CL_INVALID_COMMAND_QUEUE";
    case -37:
      return "CL_INVALID_HOST_PTR";
    case -38:
      return "CL_INVALID_MEM_OBJECT";
    case -39:
      return "CL_INVALID_IMAGE_FORMAT_DESCRIPTOR";
    case -40:
      return "CL_INVALID_IMAGE_SIZE";
    case -41:
      return "CL_INVALID_SAMPLER";
    case -42:
      return "CL_INVALID_BINARY";
    case -43:
      return "CL_INVALID_BUILD_OPTIONS";
    case -44:
      return "CL_INVALID_PROGRAM";
    case -45:
      return "CL_INVALID_PROGRAM_EXECUTABLE";
    case -46:
      return "CL_INVALID_KERNEL_NAME";
    case -47:
      return "CL_INVALID_KERNEL_DEFINITION";
    case -48:
      return "CL_INVALID_KERNEL";
    case -49:
      return "CL_INVALID_ARG_INDEX";
    case -50:
      return "CL_INVALID_ARG_VALUE";
    case -51:
      return "CL_INVALID_ARG_SIZE";
    case -52:
      return "CL_INVALID_KERNEL_ARGS";
    case -53:
      return "CL_INVALID_WORK_DIMENSION";
    case -54:
      return "CL_INVALID_WORK_GROUP_SIZE";
    case -55:
      return "CL_INVALID_WORK_ITEM_SIZE";
    case -56:
      return "CL_INVALID_GLOBAL_OFFSET";
    case -57:
      return "CL_INVALID_EVENT_WAIT_LIST";
    case -58:
      return "CL_INVALID_EVENT";
    case -59:
      return "CL_INVALID_OPERATION";
    case -60:
      return "CL_INVALID_GL_OBJECT";
    case -61:
      return "CL_INVALID_BUFFER_SIZE";
    case -62:
      return "CL_INVALID_MIP_LEVEL";
    case -63:
      return "CL_INVALID_GLOBAL_WORK_SIZE";
    case -64:
      return "CL_INVALID_PROPERTY";
    case -65:
      return "CL_INVALID_IMAGE_DESCRIPTOR";
    case -66:
      return "CL_INVALID_COMPILER_OPTIONS";
    case -67:
      return "CL_INVALID_LINKER_OPTIONS";
    case -68:
      return "CL_INVALID_DEVICE_PARTITION_COUNT";

    // extension errors
    case -1000:
      return "CL_INVALID_GL_SHAREGROUP_REFERENCE_KHR";
    case -1001:
      return "CL_PLATFORM_NOT_FOUND_KHR";
    case -1002:
      return "CL_INVALID_D3D10_DEVICE_KHR";
    case -1003:
      return "CL_INVALID_D3D10_RESOURCE_KHR";
    case -1004:
      return "CL_D3D10_RESOURCE_ALREADY_ACQUIRED_KHR";
    case -1005:
      return "CL_D3D10_RESOURCE_NOT_ACQUIRED_KHR";
    default:
      return "Unknown OpenCL error";
    }
  }

private:
  template <typename T, typename... Args>
  void setKernelArg(cl_kernel kernel, cl_uint index, T firstArg,
                    Args... remainingArgs) {
    cl_int err = clSetKernelArg(kernel, index, sizeof(T), &firstArg);
    CL_CHECK(err);
    setKernelArg(kernel, index + 1, remainingArgs...);
  }
  void setKernelArg(cl_kernel, cl_uint) {}

  cl_context context = NULL;
  cl_command_queue queue = NULL;
  cl_device_id device = NULL;
  std::map<std::string, cl_kernel> kernels;
  std::vector<cl_program> programs;
  std::vector<Size> blockSize;
};

#endif // OPENCL_WRAPPER_H
