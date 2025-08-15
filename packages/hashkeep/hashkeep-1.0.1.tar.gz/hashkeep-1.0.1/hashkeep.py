#!/usr/bin/env python3
import argparse
import os
from datetime import timedelta
from pathlib import Path
import hashlib

import diskcache


class CachingFileHasher:
    """File hasher and hash cache"""

    DEFAULT_CACHE_PATH = Path.home() / ".hashkeep"
    DEFAULT_HASHER = hashlib.md5
    DEFAULT_EXPIRE = timedelta(days=365)

    def __init__(self, cache_path: Path, hasher = DEFAULT_HASHER, cache_for: timedelta = DEFAULT_EXPIRE):

        self.cache_path = Path(cache_path)
        if not cache_path.exists():
            try:
                self.cache_path.mkdir()
            except Exception as e:
                raise ValueError(f"Failed to create cache folder {self.cache_path}: {e.__class__.__name__}: {e}")
        elif not self.cache_path.is_dir():
            raise ValueError(f"Cache path must be a directory: {self.cache_path}")

        self.expire = cache_for.total_seconds()
        self.cache = diskcache.Cache(self.cache_path)
        self.hasher = hasher


    @property
    def hasher_name(self):
        return self.hasher.__name__


    def path_cache_key(self, path: Path) -> str:

        # Normalize path
        cache_key = str(path.absolute()).replace('\\', '/')

        # not required, but keeps actual paths out of cache
        cache_key = self.DEFAULT_HASHER(cache_key.encode()).hexdigest().lower()

        return cache_key


    def compute_file_hash(self, path: Path) -> str:
        """Compute file has from file"""

        hasher = self.hasher()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()


    def get_file_hash(self, path: Path):
        """Get the hash of the file from cache, or compute if needed"""

        if not path.is_file():
            raise ValueError(f"{path} is not a file")

        cache_key = self.path_cache_key(path)
        mtime = int(path.stat().st_mtime)

        # Return from cache
        try:
            cached = self.cache[cache_key]
            if cached and cached['mtime'] == mtime:
                return cached[self.hasher_name]
        except KeyError:
            pass

        # Compute hash from disk
        entry = {
            'mtime': mtime,
            self.hasher_name: self.compute_file_hash(path),
        }

        # Cache hash
        self.cache.set(cache_key, entry, expire=self.expire)

        return entry[self.hasher_name]


    def __getitem__(self, path: Path):
        """Get or compute file hash"""
        return self.get_file_hash(path)

    def __contains__(self, path: Path):
        """Peak to see if the path is in the cache"""
        cache_key = self.path_cache_key(path)
        mtime = int(path.stat().st_mtime)
        entry = self.cache.get(cache_key)
        return (entry and entry['mtime'] == mtime)


class CommandLine:
    """Commandline execution namespace"""

    @staticmethod
    def existing_file(path: str) -> Path:
        path = Path(path)
        if not path.exists():
            raise argparse.ArgumentTypeError(f"{path}: Does not exist")
        if not path.is_file():
            raise argparse.ArgumentTypeError(f"{path}: Is not a file")
        return path

    @staticmethod
    def hasher_by_name(name: str):
        if name not in hashlib.algorithms_available:
            raise argparse.ArgumentTypeError(f"Unknown hasher algorithm: {name}")
        try:
            return getattr(hashlib, name)
        except AttributeError:
            raise argparse.ArgumentTypeError(f"Unknown hasher algorithm: {name}")

    @staticmethod
    def parser() -> argparse.ArgumentParser:

        parser = argparse.ArgumentParser(
            prog='hashkeep',
            description='Perform file hash and cache results'
        )

        parser.add_argument('paths', type=CommandLine.existing_file, nargs='+',
                            help="File to hash")

        parser.add_argument('--hasher', type=CommandLine.hasher_by_name,
                            choices=list(sorted(hashlib.algorithms_available)),
                            default=CachingFileHasher.DEFAULT_HASHER().name,
                            help="Which hashing algorithm to use")

        try:
            default_cache_path = Path(os.environ['HASHKEEP_CACHE_PATH'])
        except KeyError:
            default_cache_path = CachingFileHasher.DEFAULT_CACHE_PATH

        parser.add_argument('--hash-only', action='store_true',
                            help="Only print file hash")

        parser.add_argument('--cache-path', type=Path,
                            default=default_cache_path,
                            help="Where to cache computed file hashes")

        parser.add_argument('--cache-for', type=int,
                            default=CachingFileHasher.DEFAULT_EXPIRE.total_seconds(),
                            help=f"Seconds to cache hashes for (default {CachingFileHasher.DEFAULT_EXPIRE})")

        return parser

    @staticmethod
    def main():
        parser = CommandLine.parser()
        args = parser.parse_args()
        hasher = CachingFileHasher(
            cache_path=args.cache_path,
            hasher=args.hasher,
            cache_for=timedelta(seconds=args.cache_for),
        )
        for path in args.paths:
            if args.hash_only:
                print(hasher.get_file_hash(path))
            else:
                print(f"{path}: {hasher.get_file_hash(path)}")


def main():
    CommandLine.main()


if __name__ == '__main__':
    CommandLine.main()
