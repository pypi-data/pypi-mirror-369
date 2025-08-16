"""Cryptographic algorithms mapping"""
from cryptography.hazmat.primitives import hashes

# Mapeo de algoritmos string a objetos hash de cryptography
HASH_ALGORITHMS = {
    "sha1": hashes.SHA1,
    "sha256": hashes.SHA256,
    "sha512": hashes.SHA512,
}


def get_hash_algorithm(algorithm: str) -> hashes.HashAlgorithm:
    """
    Get cryptography hash algorithm from string name
    
    Args:
        algorithm: Algorithm name ("sha1", "sha256", "sha512")
        
    Returns:
        Hash algorithm instance
        
    Raises:
        ValueError: If algorithm is not supported
    """
    if algorithm not in HASH_ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Supported: {list(HASH_ALGORITHMS.keys())}")
    
    return HASH_ALGORITHMS[algorithm]()