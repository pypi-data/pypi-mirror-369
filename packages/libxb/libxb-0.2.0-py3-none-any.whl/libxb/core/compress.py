from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntFlag, auto
from typing import override

from .exceptions import ArgumentError, DecompressionError
from .streams import BufferStream, OpenMode, SeekDir, Stream


class CompressionStrategy(ABC):
    """Data compression/decompression algorithm"""

    @classmethod
    @abstractmethod
    def compress(cls, strm: Stream) -> BufferStream:
        """Compresses the input data. The output data is prefixed with the
        compression header (decomp size, compress size)

        Args:
            strm (Stream): Stream to decompressed data

        Returns:
            BufferStream: Stream to compressed data
        """
        pass

    @classmethod
    @abstractmethod
    def decompress(
        cls, strm: Stream, expand_size: int = None, compress_size: int = None
    ) -> BufferStream:
        """Decompresses the input data. If it is not provided, the input data is expected
        to be prefixed with the compression header (expanded size, compressed size)

        Args:
            strm (Stream): Stream to compressed data
            expand_size (int, optional): Size of the decompressed data.
                                         Defaults to 'None' (read from the stream).
            compress_size (int, optional): Size of the compressed data.
                                           Defaults to 'None' (read from the stream).

        Returns:
            BufferStream: Stream to decompressed data
        """
        pass


class ClapHanzLZS(CompressionStrategy):
    """ClapHanz's implementation of LZS data compression"""

    MIN_RUN = 3

    class ChunkFlag(IntFlag):
        """Compression chunk flags"""

        LITERAL = 0
        SHORTRUN = auto()
        LONGRUN = auto()
        MASK = SHORTRUN | LONGRUN

    @classmethod
    @override
    def compress(cls, strm: Stream) -> BufferStream:
        """Compresses the input data. The output data is prefixed with the
        compression header (decomp size, compress size)

        Args:
            strm (Stream): Stream to decompressed data

        Returns:
            BufferStream: Stream to compressed data
        """
        raise NotImplementedError()

    @classmethod
    @override
    def decompress(
        cls, strm: Stream, expand_size: int = None, compress_size: int = None
    ) -> BufferStream:
        """Decompresses the input data. If it is not provided, the input data is expected
        to be prefixed with the compression header (expanded size, compressed size)

        Args:
            strm (Stream): Stream to compressed data
            expand_size (int, optional): Size of the decompressed data.
                                         Defaults to 'None' (read from the stream).
            compress_size (int, optional): Size of the compressed data.
                                           Defaults to 'None' (read from the stream).

        Returns:
            BufferStream: Stream to decompressed data

        Raises
            ArgumentError: Invalid argument(s) provided
            DecompressionError: Decompression cannot be completed
        """
        if expand_size is None:
            expand_size = strm.read_u32()
        if compress_size is None:
            compress_size = strm.read_u32()

        if expand_size == 0:
            raise ArgumentError("Invalid decompressed size")

        # File was marked for compression but wasn't actually compressed.
        # Seems like the ClapHanz tools omit compression if it would have wasted space.
        if compress_size == 0:
            return BufferStream(
                OpenMode.RW, strm.endian, strm.read(expand_size)
            )

        # Cache loop invariant attributes
        c_mask = cls.ChunkFlag.MASK.value
        c_literal = cls.ChunkFlag.LITERAL.value
        c_shortrun = cls.ChunkFlag.SHORTRUN.value
        min_run = cls.MIN_RUN
        read_u8 = strm.read_u8
        read = strm.read

        output = bytearray()

        try:
            while len(output) < expand_size:
                code = read_u8()

                # Literal copy
                if (code & c_mask) == c_literal:
                    copy_len = (code >> 2) + 1
                    output += read(copy_len)

                # Run decode
                else:
                    run_offset = 0
                    run_len = 0

                    # Short-distance run
                    if code & c_shortrun:
                        b0 = read_u8()
                        value = b0 << 8 | code

                        run_len = ((value & 0b1110) >> 1) + min_run
                        run_offset = value >> 4
                    # Long-distance run
                    else:
                        b0 = read_u8()
                        b1 = read_u8()
                        value = b1 << 16 | b0 << 8 | code

                        run_len = ((value & 0b111111111100) >> 2) + min_run
                        run_offset = value >> 12

                    run_idx = len(output) - run_offset

                    # No overlap: Copy by slice
                    if run_offset >= run_len:
                        output += output[run_idx : run_idx + run_len]
                    # Overlap: must go byte-by-byte
                    else:
                        for _ in range(run_len):
                            output.append(output[run_idx])
                            run_idx += 1

        except IndexError:
            raise DecompressionError("Compressed data is malformed")
        except EOFError:
            raise DecompressionError("Hit the end-of-file while decompressing")

        return BufferStream(OpenMode.RW, strm.endian, output)


class ClapHanzHuffman(CompressionStrategy):
    """ClapHanz's implementation of Huffman data compression"""

    MAX_DEPTH = 10
    TABLE_SIZE = pow(2, MAX_DEPTH)

    @dataclass
    class Symbol:
        """Flat Huffman decode table entry"""

        length: int
        symbol: int

    @classmethod
    @override
    def compress(cls, strm: Stream) -> BufferStream:
        """Compresses the input data. The output data is prefixed with the
        compression header (decomp size, compress size)

        Args:
            strm (Stream): Stream to decompressed data

        Returns:
            BufferStream: Stream to compressed data
        """
        raise NotImplementedError()

    @classmethod
    @override
    def decompress(
        cls, strm: Stream, expand_size: int = None, compress_size: int = None
    ) -> BufferStream:
        """Decompresses the input data. If it is not provided, the input data is expected
        to be prefixed with the compression header (expanded size, compressed size)

        Args:
            strm (Stream): Stream to compressed data
            expand_size (int, optional): Size of the decompressed data.
                                         Defaults to 'None' (read from the stream).
            compress_size (int, optional): Size of the compressed data.
                                           Defaults to 'None' (read from the stream).

        Returns:
            BufferStream: Stream to decompressed data

        Raises
            ArgumentError: Invalid argument(s) provided
            DecompressionError: Decompression cannot be completed
        """
        if expand_size is None:
            expand_size = strm.read_u32()
        if compress_size is None:
            compress_size = strm.read_u32()

        if expand_size == 0:
            raise ArgumentError("Invalid decompressed size")

        # File was marked for compression but wasn't actually compressed.
        # Seems like the ClapHanz tools omit compression if it would have wasted space.
        if compress_size == 0:
            return BufferStream(
                OpenMode.RW, strm.endian, strm.read(expand_size)
            )

        # Build the Huffman decoding table
        try:
            table = cls._rebuild_huffman_table(strm)
        except (IndexError, EOFError):
            raise DecompressionError("Failed to create Huffman table")

        output = bytearray(expand_size)

        bit_num = 0
        bit_strm = 0

        # Cache loop invariant attributes
        read_u16 = strm.read_u16
        max_depth = cls.MAX_DEPTH
        table_size = cls.TABLE_SIZE

        try:
            for i in range(expand_size):
                # Read Huffman code and find the table entry
                if bit_num < max_depth:
                    # ClapHanz's decompression code will read out-of-bounds in some cases.
                    #
                    # In practice, memory is zeroed out past the end of the buffer, so
                    # the data is unimportant.
                    try:
                        bit_strm |= read_u16() << bit_num
                    except EOFError:
                        pass

                    bit_num += 16

                index = bit_strm & (table_size - 1)
                entry = table[index]

                # Huffman symbol
                if entry.length <= max_depth:
                    # Consume bits based on the symbol length
                    output[i] = entry.symbol & 0xFF

                    bit_strm >>= entry.length
                    bit_num -= entry.length
                # Literal byte
                else:
                    bit_strm >>= max_depth
                    bit_num -= max_depth

                    # Refresh stream if needed
                    if bit_num < 16:
                        # ClapHanz's decompression code will read out-of-bounds in some cases.
                        #
                        # In practice, memory is zeroed out past the end of the buffer, so
                        # the data is unimportant.
                        try:
                            bit_strm |= read_u16() << bit_num
                        except EOFError:
                            pass

                        bit_num += 16

                    # Consume one byte (8 bits)
                    output[i] = bit_strm & 0xFF

                    bit_strm >>= 8
                    bit_num -= 8

        except IndexError:
            raise DecompressionError("Compressed data is malformed")
        except EOFError:
            raise DecompressionError("Hit the end-of-file while decompressing")

        return BufferStream(OpenMode.RW, strm.endian, output)

    @classmethod
    def _rebuild_huffman_table(cls, strm: Stream) -> list[Symbol]:
        """Reconstructs a flat Huffman decoding table from input code data

        Args:
            strm (Stream): Stream to Huffman code data

        Raises
            ArgumentError: Invalid argument(s) provided
            DecompressionError: Decompression cannot be completed

        Returns:
            list[Symbol]: List of Huffman symbols
        """
        # Cache loop invariant attributes
        read_u8 = strm.read_u8
        max_depth = cls.MAX_DEPTH
        table_size = cls.TABLE_SIZE
        symbol_cls = cls.Symbol

        # Table has a fixed size
        table = [None] * table_size

        max_length = read_u8()
        if max_length == 0:
            raise DecompressionError("Huffman code data is malformed")

        code = 0
        length = 1

        try:
            while length <= max_length:
                code_num = read_u8()

                # Read all codes of the current length
                for _ in range(code_num):
                    code_bits = code
                    index = 0

                    # Build the table index
                    for _ in range(length):
                        index = index << 1 | (code_bits & 0b1)
                        code_bits >>= 1

                    symbol = read_u8()

                    # Duplicate symbols which match the prefix?
                    while index < table_size:
                        table[index] = symbol_cls(length, symbol)
                        index += 1 << length

                    if length <= max_depth:
                        code += 1

                length += 1
                code <<= 1
        except IndexError:
            raise DecompressionError("Compressed data is malformed")
        except EOFError:
            raise DecompressionError("Hit the end-of-file while decompressing")

        # Data is aligned to two byte boundary
        if strm.tell() % 2 != 0:
            strm.seek(SeekDir.CURRENT, 1)

        return table


class ClapHanzDeflate(CompressionStrategy):
    """ClapHanz's implementation of Deflate data compression (LZS + Huffman)"""

    @classmethod
    @override
    def compress(cls, strm: Stream) -> BufferStream:
        """Compresses the input data. The output data is prefixed with the
        compression header (decomp size, compress size)

        Args:
            strm (Stream): Stream to decompressed data

        Returns:
            BufferStream: Stream to compressed data
        """
        lz_strm = ClapHanzLZS.compress(strm)
        return ClapHanzHuffman.compress(lz_strm)

    @classmethod
    @override
    def decompress(
        cls, strm: Stream, expand_size: int = None, compress_size: int = None
    ) -> BufferStream:
        """Decompresses the input data. If it is not provided, the input data is expected
        to be prefixed with the compression header (expanded size, compressed size)

        Args:
            strm (Stream): Stream to compressed data

        Returns:
            BufferStream: Stream to decompressed data
        """
        lz_strm = ClapHanzHuffman.decompress(strm, expand_size, compress_size)
        return ClapHanzLZS.decompress(lz_strm)
