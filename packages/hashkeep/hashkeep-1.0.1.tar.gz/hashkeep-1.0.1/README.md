Caching File Hasher
===================

Simple utility to hash the contents of files and store hashes in a cache for quick repeat hashing.


Installing
----------

    pip install hashkeep


Basic Usage
-----------
    
    from pathlib import Path
    from hashlib import md5

    from hashkeep import CachingFileHasher

    hasher = CachingFileHasher(hasher=m5d, cache_path=Path('.cache'))
    hasher.get_file_hash('file.dat') == '9dd4e461268c8034f5c8564e155c67a6'


Command Line Usage
------------------

    usage: hashkeep [-h]
                    [--hasher {blake2b,blake2s,md5,md5-sha1,ripemd160,sha1,sha224,sha256,sha384,sha3_224,sha3_256,
                               sha3_384,sha3_512,sha512,sha512_224,sha512_256,shake_128,shake_256,sm3}]
                    [--hash-only] [--cache-path CACHE_PATH]
                    [--cache-for CACHE_FOR]
                    paths [paths ...]

    Perform file hash and cache results
    
    positional arguments:
      paths                 File to hash
    
    options:
      -h, --help            show this help message and exit
      --hasher {blake2b,blake2s,md5,md5-sha1,ripemd160,sha1,sha224,sha256,sha384,sha3_224,sha3_256,
                sha3_384,sha3_512,sha512,sha512_224,sha512_256,shake_128,shake_256,sm3}
                            Which hashing algorithm to use
      --hash-only           Only print file hash
      --cache-path CACHE_PATH
                            Where to cache computed file hashes
      --cache-for CACHE_FOR
                            Seconds to cache hashes for (default 365 days)
