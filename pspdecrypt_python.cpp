/*
 * Python bindings for pspdecrypt using pybind11
 * Exposes C++ decryption functions to Python
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <cstring>

extern "C" {
#include "libkirk/kirk_engine.h"
}

#include "CommonTypes.h"
#include "pspdecrypt_lib.h"
#include "PrxDecrypter.h"
#include "PsarDecrypter.h"

namespace py = pybind11;

// Helper function to decrypt PRX from bytes
py::bytes decrypt_prx(py::bytes data, py::object secure_id_obj = py::none(), bool verbose = false) {
    // Initialize KIRK engine
    static bool kirk_initialized = false;
    if (!kirk_initialized) {
        kirk_init();
        kirk_initialized = true;
    }

    // Convert Python bytes to C++ buffer
    std::string input_str = data;
    const u8* input_data = reinterpret_cast<const u8*>(input_str.data());
    u32 input_size = input_str.size();

    if (input_size < PSP_HEADER_SIZE) {
        throw std::runtime_error("Input data is too small (< 0x150 bytes)");
    }

    // Parse secure ID if provided
    u8 secure_id[16] = {0};
    const u8* secure_id_ptr = nullptr;
    
    if (!secure_id_obj.is_none()) {
        py::bytes secure_id_bytes = secure_id_obj.cast<py::bytes>();
        std::string secure_id_str = secure_id_bytes;
        if (secure_id_str.size() != 16) {
            throw std::runtime_error("Secure ID must be exactly 16 bytes");
        }
        memcpy(secure_id, secure_id_str.data(), 16);
        secure_id_ptr = secure_id;
    }

    // Get output buffer size
    u32 psp_size = pspGetPspSize(input_data);
    u32 elf_size = pspGetElfSize(input_data);
    u32 output_capacity = std::max(psp_size, elf_size);
    output_capacity = ((output_capacity + 15) / 16) * 16; // Align to 16 bytes

    // Allocate output buffer
    std::vector<u8> output_buffer(output_capacity);

    // Decrypt the PRX
    int output_size = pspDecryptPRX(input_data, output_buffer.data(), input_size, secure_id_ptr, verbose);
    
    if (output_size < 0) {
        throw std::runtime_error("PRX decryption failed");
    }

    // Check if data is compressed and decompress if needed
    if (output_size >= 4 && pspIsCompressed(output_buffer.data())) {
        std::string log_str;
        std::vector<u8> temp_buffer(elf_size);
        int decompressed_size = pspDecompress(output_buffer.data(), output_size, 
                                               temp_buffer.data(), elf_size, log_str);
        
        if (decompressed_size == elf_size) {
            output_size = decompressed_size;
            output_buffer = std::move(temp_buffer);
            if (verbose) {
                py::print("Decompression successful:", log_str.substr(1));
            }
        } else if (verbose) {
            py::print("Decompression failed:", log_str.substr(1));
        }
    }

    // Return as Python bytes
    return py::bytes(reinterpret_cast<const char*>(output_buffer.data()), output_size);
}

// Helper function to decrypt PRX from file
py::bytes decrypt_prx_file(const std::string& filename, py::object secure_id_obj = py::none(), bool verbose = false) {
    // Read file
    FILE* f = fopen(filename.c_str(), "rb");
    if (!f) {
        throw std::runtime_error("Could not open file: " + filename);
    }

    // Get file size
    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (file_size < 0) {
        fclose(f);
        throw std::runtime_error("Could not determine file size");
    }

    // Read file data
    std::vector<u8> file_data(file_size);
    size_t bytes_read = fread(file_data.data(), 1, file_size, f);
    fclose(f);

    if (bytes_read != static_cast<size_t>(file_size)) {
        throw std::runtime_error("Could not read entire file");
    }

    // Convert to Python bytes and call decrypt_prx
    py::bytes data = py::bytes(reinterpret_cast<const char*>(file_data.data()), file_size);
    return decrypt_prx(data, secure_id_obj, verbose);
}

// Helper function to get PRX info
py::dict get_prx_info(py::bytes data) {
    std::string input_str = data;
    const u8* input_data = reinterpret_cast<const u8*>(input_str.data());
    
    if (input_str.size() < PSP_HEADER_SIZE) {
        throw std::runtime_error("Input data is too small (< 0x150 bytes)");
    }

    py::dict info;
    info["tag"] = pspGetTagVal(input_data);
    info["elf_size"] = pspGetElfSize(input_data);
    info["psp_size"] = pspGetPspSize(input_data);
    info["comp_size"] = pspGetCompSize(input_data);
    info["is_compressed"] = pspIsCompressed(input_data) != 0;
    
    return info;
}

// Helper function to decrypt IPL stage 1
py::bytes decrypt_ipl1(py::bytes data, bool verbose = false) {
    // Initialize KIRK engine
    static bool kirk_initialized = false;
    if (!kirk_initialized) {
        kirk_init();
        kirk_initialized = true;
    }

    std::string input_str = data;
    const u8* input_data = reinterpret_cast<const u8*>(input_str.data());
    u32 input_size = input_str.size();

    std::vector<u8> output_buffer(input_size);
    std::string log_str;
    
    int output_size = pspDecryptIPL1(input_data, output_buffer.data(), input_size, log_str);
    
    if (output_size <= 0) {
        throw std::runtime_error("IPL stage 1 decryption failed");
    }

    if (verbose && !log_str.empty()) {
        py::print("IPL1 decryption:", log_str.substr(1));
    }

    return py::bytes(reinterpret_cast<const char*>(output_buffer.data()), output_size);
}

// Helper function to linearize IPL stage 2
py::tuple linearize_ipl2(py::bytes data) {
    std::string input_str = data;
    const u8* input_data = reinterpret_cast<const u8*>(input_str.data());
    u32 input_size = input_str.size();

    std::vector<u8> output_buffer(input_size);
    u32 start_addr = 0;
    
    int output_size = pspLinearizeIPL2(input_data, output_buffer.data(), input_size, &start_addr);
    
    if (output_size <= 0) {
        throw std::runtime_error("IPL stage 2 linearization failed");
    }

    py::bytes result = py::bytes(reinterpret_cast<const char*>(output_buffer.data()), output_size);
    return py::make_tuple(result, start_addr);
}

// Helper function to decrypt IPL stage 3
py::bytes decrypt_ipl3(py::bytes data) {
    std::string input_str = data;
    const u8* input_data = reinterpret_cast<const u8*>(input_str.data());
    u32 input_size = input_str.size();

    std::vector<u8> output_buffer(input_size);
    
    int output_size = pspDecryptIPL3(input_data, output_buffer.data(), input_size);
    
    if (output_size <= 0) {
        throw std::runtime_error("IPL stage 3 decryption failed");
    }

    return py::bytes(reinterpret_cast<const char*>(output_buffer.data()), output_size);
}

// Helper function to decompress data
py::bytes decompress(py::bytes data, int max_size = -1, bool verbose = false) {
    std::string input_str = data;
    u32 input_size = input_str.size();

    // Copy to mutable buffer since pspDecompress may modify the input
    std::vector<u8> input_buffer(input_size);
    memcpy(input_buffer.data(), input_str.data(), input_size);

    if (!pspIsCompressed(input_buffer.data())) {
        throw std::runtime_error("Input data is not compressed");
    }

    // Use max_size or a reasonable default
    u32 output_capacity = (max_size > 0) ? max_size : (input_size * 10);
    std::vector<u8> output_buffer(output_capacity);
    std::string log_str;
    
    int output_size = pspDecompress(input_buffer.data(), input_size, 
                                     output_buffer.data(), output_capacity, log_str);
    
    if (output_size < 0) {
        throw std::runtime_error("Decompression failed: " + log_str);
    }

    if (verbose && !log_str.empty()) {
        py::print("Decompression:", log_str.substr(1));
    }

    return py::bytes(reinterpret_cast<const char*>(output_buffer.data()), output_size);
}

// Module definition
PYBIND11_MODULE(pspdecrypt, m) {
    m.doc() = "Python bindings for PSP decryption library";

    // PRX decryption functions
    m.def("decrypt_prx", &decrypt_prx, 
          "Decrypt a PSP PRX/executable from bytes",
          py::arg("data"),
          py::arg("secure_id") = py::none(),
          py::arg("verbose") = false);
    
    m.def("decrypt_prx_file", &decrypt_prx_file,
          "Decrypt a PSP PRX/executable from file",
          py::arg("filename"),
          py::arg("secure_id") = py::none(),
          py::arg("verbose") = false);
    
    m.def("get_prx_info", &get_prx_info,
          "Get information about a PRX file",
          py::arg("data"));

    // IPL decryption functions
    m.def("decrypt_ipl1", &decrypt_ipl1,
          "Decrypt IPL stage 1",
          py::arg("data"),
          py::arg("verbose") = false);
    
    m.def("linearize_ipl2", &linearize_ipl2,
          "Linearize IPL stage 2, returns (data, start_address)",
          py::arg("data"));
    
    m.def("decrypt_ipl3", &decrypt_ipl3,
          "Decrypt IPL stage 3",
          py::arg("data"));

    // Compression/decompression
    m.def("decompress", &decompress,
          "Decompress GZIP/KL4E/KL3E/2RLZ compressed data",
          py::arg("data"),
          py::arg("max_size") = -1,
          py::arg("verbose") = false);

    // Version information
    m.attr("__version__") = "1.0.0";
}
