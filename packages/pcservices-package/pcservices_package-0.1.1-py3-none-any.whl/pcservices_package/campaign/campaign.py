import hashlib
import random

# def get_group_number(email):
#     if not email or email=='' or not isinstance(email, str):
#         return -1
#     # Use a 64-bit hash, similar to FarmHash in spirit
#     hash_value = int(hashlib.md5(email.lower().encode('utf-8')).hexdigest(), 16)
#     return hash_value % 100


def get_consistent_customer_number(email_address):
    """
    Generates a deterministic integer between 0 and 99 for a customer email.
    The email is normalized before hashing to ensure consistency.
    """
    if not email_address or email_address=='' or not isinstance(email_address, str):
        return -1
    # Step 1: Normalize the email address
    normalized_email = email_address.lower()
    
    # Step 2: Hash the normalized email using SHA-256
    sha256_hash = hashlib.sha256(normalized_email.encode('utf-8'))
    hex_digest = sha256_hash.hexdigest()
    
    # Step 3: Truncate the hex string and convert it to an integer
    truncated_hex = hex_digest[:15]
    hash_as_int = int(truncated_hex, 16)
    
    # Step 4: Apply the modulo operator to get a number from 0 to 99
    final_number = hash_as_int % 100
    
    return final_number


def generate_random_numbers(n, seed=None):
    """
    Generate N random numbers between 0 and 99.

    Parameters:
    - n (int): The number of random numbers to generate.
    - seed (int, optional): The seed for the random number generator. Default is None.

    Returns:
    - list: A list containing N random numbers between 0 and 99.
    """
    
    # Set the seed if provided
    if seed is not None:
        random.seed(seed)
    
    # Generate N random numbers between 0 and 99
    random_numbers = [random.randint(0, 99) for _ in range(n)]
    
    return random_numbers