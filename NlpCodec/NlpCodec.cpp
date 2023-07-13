#include <zlib.h>
#include <cstdio>
#include <cstdint>
#include <cinttypes>
#include <filesystem>
#include <string>
#include <fstream>
#include <memory>

namespace NlpCodec {

    constexpr const uint8_t g_XorArray[] {
        0x2C, 0xA8, 0x56, 0xF9, 0xBD, 0xA6, 0x8D, 0x15, 0x25, 0x38, 0x1A, 0xD4, 0x65, 0x58, 0x28, 0x37,
        0xFA, 0x6B, 0xB5, 0xA1, 0x2C, 0x96, 0x13, 0xA2, 0xAB, 0x4F, 0xC5, 0xA1, 0x3E, 0xA7, 0x91, 0x8D,
        0x2C, 0xDF, 0x78, 0x6D, 0x3C, 0xFC, 0x92, 0x1F, 0x1A, 0x62, 0xA7, 0x9C, 0x92, 0x29, 0x44, 0x6D,
        0x3D, 0xA9, 0x2B, 0xE1, 0x91, 0xAD, 0x49, 0x3C, 0xE2, 0x33, 0xD2, 0x1A, 0x55, 0x92, 0xE7, 0x95,
        0x8C, 0xDA, 0xD2, 0xCD, 0xA2, 0xCF, 0x92, 0x9A, 0xE1, 0xF9, 0x3A, 0x26, 0xFA, 0xC4, 0xA9, 0x23,
        0xA9, 0x4D, 0x1A, 0x2C, 0x3C, 0x2A, 0xAC, 0x62, 0xA3, 0x92, 0xAC, 0x1F, 0x3E, 0xA6, 0xC9, 0xC8,
        0x63, 0xCA, 0x52, 0xF9, 0xFB, 0x3A, 0x9C, 0x2A, 0xB2, 0x1A, 0x8D, 0x9A, 0x8C, 0x2A, 0x9C, 0x32,
        0xAA, 0xC3, 0xA2, 0x97, 0x34, 0x92, 0xFA, 0x71, 0xBE, 0x3F, 0xAC, 0x28, 0x22, 0x9F, 0xAC, 0xE8
    };
    constexpr const size_t g_XorArrayLen = sizeof(g_XorArray) / sizeof(uint8_t);
    constexpr const uint32_t MAGIC_DWORD = 0xF956A82Cu;
    constexpr const size_t TAIL_SIZE = sizeof(uint32_t) * 2u;

    void GeneralXorOperation(void* data, size_t datalen) {
        uint8_t* ptr = reinterpret_cast<uint8_t*>(data);
        for (size_t i = 0u; i < datalen; ++i) {
            ptr[i] ^= g_XorArray[i & 0x7Fu];
        }
    }

    uint32_t GetFileLength(std::ifstream& fin) {
        // backup
        uint64_t curpos = static_cast<uint64_t>(fin.tellg());
        // get tail
        fin.seekg(0, std::ios_base::end);
        uint32_t tail = static_cast<uint32_t>(fin.tellg());
        // restore
        fin.seekg(static_cast<std::ifstream::off_type>(curpos), std::ios_base::beg);

        return tail;
    }

    bool EncodeNlp(std::ifstream& fin, std::ofstream& fout) {
        // get file length and decide zlib boundary
        uint32_t rawsize = GetFileLength(fin);
        uint32_t compboundary = static_cast<uint32_t>(compressBound(static_cast<uLong>(rawsize)));

        // create buffer first
        std::unique_ptr<char[]> inbuf(new(std::nothrow) char[rawsize]);
        std::unique_ptr<char[]> outbuf(new(std::nothrow) char[compboundary]);
        if (inbuf == nullptr || outbuf == nullptr) {
            fputs("[ERR] Fail to allocate memory.\n", stdout);
            return false;
        }

        // read data from file
        fin.read(inbuf.get(), rawsize);
        if (!fin.good() || fin.gcount() != rawsize) {
            fputs("[ERR] Fail to read data into buffer.\n", stdout);
            return false;
        }

        // do xor operation
        GeneralXorOperation(inbuf.get(), rawsize);

        // do compress and get the size of compressed data
        uLongf _destLen = static_cast<uLongf>(compboundary);
        int ret = compress2(
            reinterpret_cast<Bytef*>(outbuf.get()), &_destLen,
            reinterpret_cast<Bytef*>(inbuf.get()), rawsize,
            Z_BEST_COMPRESSION
        );
        if (ret != Z_OK) {
            fputs("[ERR] Zlib compress() failed.\n", stdout);
            return false;
        }
        uint32_t compsize = static_cast<uint32_t>(_destLen);

        // produce checksum
        uint32_t checksum = static_cast<uint32_t>(adler32(0u, reinterpret_cast<Bytef*>(outbuf.get()), static_cast<uInt>(compsize)));

        // write compressed data into file
        fout.write(outbuf.get(), compsize);
        if (!fout.good()) {
            fputs("[ERR] Fail to write data into file.\n", stdout);
            return false;
        }

        // raw size and checksum need some extra operation before writting
        rawsize = static_cast<uint32_t>(-(static_cast<int32_t>(rawsize) + 1)) ^ MAGIC_DWORD;
        checksum = checksum + 1072u;

        // write raw size and checksum
        fout.write(reinterpret_cast<char*>(&rawsize), sizeof(uint32_t));
        if (!fout.good()) {
            fputs("[ERR] Fail to write raw size into file.\n", stdout);
            return false;
        }
        fout.write(reinterpret_cast<char*>(&checksum), sizeof(uint32_t));
        if (!fout.good()) {
            fputs("[ERR] Fail to write checksum into file.\n", stdout);
            return false;
        }

        return true;
    }

    bool DecodeNlp(std::ifstream& fin, std::ofstream& fout) {
        // seek to tail to get essential data
        uint32_t compsize = GetFileLength(fin);
        if (compsize < TAIL_SIZE) {
            fputs("[ERR] Invalid file.\n", stdout);
            return false;
        }
        compsize -= TAIL_SIZE;
        fin.seekg(compsize, std::ios_base::beg);
        uint32_t expected_rawlen = 0u, expected_checksum = 0u;
        fin.read(reinterpret_cast<char*>(&expected_rawlen), sizeof(uint32_t));
        fin.read(reinterpret_cast<char*>(&expected_checksum), sizeof(uint32_t));
        fin.seekg(0, std::ios_base::beg);

        // these tail data need to do some processes
        expected_rawlen = static_cast<uint32_t>(-1 - static_cast<int32_t>(MAGIC_DWORD ^ expected_rawlen));
        expected_checksum = expected_checksum - 1072u;

        // allocate memory to store data
        std::unique_ptr<char[]> inbuf(new(std::nothrow) char[compsize]);
        std::unique_ptr<char[]> outbuf(new(std::nothrow) char[expected_rawlen]);
        if (inbuf == nullptr || outbuf == nullptr) {
            fputs("[ERR] Fail to allocate memory.\n", stdout);
            return false;
        }

        // read into buffer
        fin.read(inbuf.get(), compsize);
        if (!fin.good() || fin.gcount() != compsize) {
            fputs("[ERR] Fail to read data into buffer.\n", stdout);
            return false;
        }

        // test checksum
        uint32_t checksum = static_cast<uint32_t>(adler32(0u, reinterpret_cast<Bytef*>(inbuf.get()), static_cast<uInt>(compsize)));
        if (checksum != expected_checksum) {
            fprintf(stdout, "[ERR] Fail to match crc32. Expect 0x%" PRIx32 " got 0x%" PRIx32 ".\n",
                expected_checksum, checksum
            );
            return false;
        }

        // do uncompress
        uLongf _destLen = static_cast<uLongf>(expected_rawlen);
        int ret = uncompress(
            reinterpret_cast<Bytef*>(outbuf.get()), &_destLen,
            reinterpret_cast<Bytef*>(inbuf.get()), static_cast<uLong>(compsize)
        );
        if (ret != Z_OK) {
            fputs("[ERR] Zlib uncompress() failed.\n", stdout);
            return false;
        }

        // do xor operation
        GeneralXorOperation(outbuf.get(), expected_rawlen);

        // write into file
        fout.write(outbuf.get(), expected_rawlen);
        if (!fout.good()) {
            fputs("[ERR] Fail to write data into file.\n", stdout);
            return false;
        }

        return true;
    }

}

static void PrintHelp(void) {
    fputs("NlpCodec Usage\n", stdout);
    fputs("\n", stdout);
    fputs("NlpCodec [encode | decode] <src> <dest>\n", stdout);
    fputs("encode - encode text file into nlp file.\n", stdout);
    fputs("decode - decompress nlp file into text file.\n", stdout);
    fputs("<src> - the source file. text file in compress mode. nlp file in uncompress mode.\n", stdout);
    fputs("<dest> - the destination file. nlp file in compress mode. text file in uncompress mode.\n", stdout);
}

int main(int argc, char* argv[]) {

    // check arguments
    if (argc != 4) {
        fputs("[ERR] Invalid arguments!\n", stdout);
        PrintHelp();
        return 1;
    }

    std::string mode(argv[1]);
    if (mode != "encode" && mode != "decode") {
        fputs("[ERR] Unknow operation!\n", stdout);
        PrintHelp();
        return 1;
    }

    // try initializing files
    std::ifstream infile;
    infile.open(std::filesystem::path(argv[2]), std::ios_base::in | std::ios_base::binary);
    std::ofstream outfile;
    outfile.open(std::filesystem::path(argv[3]), std::ios_base::out | std::ios_base::binary);

    if (!infile.is_open() || !outfile.is_open()) {
        fputs("[ERR] Fail to open file!\n", stdout);
        return 1;
    }

    // do real work
    bool result = true;
    if (mode == "encode") {
        result = NlpCodec::EncodeNlp(infile, outfile);
    } else {
        result = NlpCodec::DecodeNlp(infile, outfile);
    }

    // free resources and report
    infile.close();
    outfile.close();

    if (!result) {
        fputs("[ERR] Encoder failed!\n", stdout);
        return 1;
    }

    return 0;
}
