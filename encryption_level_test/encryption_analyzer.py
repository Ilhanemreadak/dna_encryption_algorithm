import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def analyze_encrypted_file(filename):
    """Perform statistical analysis on encrypted data."""
    with open(filename, "rb") as f:
        data = f.read()
    
    # Convert to numpy array for analysis
    byte_array = np.frombuffer(data, dtype=np.uint8)
    
    # Basic statistics
    print(f"File size: {len(byte_array)} bytes")
    print(f"Mean byte value: {byte_array.mean()}")
    print(f"Standard deviation: {byte_array.std()}")
    
    # Chi-square test (should be close to random for good encryption)
    observed_freq = np.bincount(byte_array, minlength=256)
    expected_freq = np.ones(256) * (len(byte_array)/256)
    chi2, p_value = stats.chisquare(observed_freq, expected_freq)
    print(f"Chi-square test p-value: {p_value}")
    print(f"Chi-square value: {chi2}")
    
    # Entropy calculation (should be close to 8 for truly random bytes)
    _, counts = np.unique(byte_array, return_counts=True)
    probabilities = counts / len(byte_array)
    entropy = -np.sum(probabilities * np.log2(probabilities))
    print(f"Shannon entropy: {entropy} bits (max 8 bits)")
    
    # Autocorrelation (should be near zero for good encryption)
    autocorr = np.correlate(byte_array, byte_array, mode='same')
    center = len(autocorr) // 2
    autocorr = autocorr / autocorr[center]
    plt.figure(figsize=(10, 6))
    plt.plot(autocorr[center-50:center+50])
    plt.title("Autocorrelation (should be spike at center only)")
    plt.savefig("autocorrelation.png")
    plt.show()
    
    # Byte frequency histogram
    plt.figure(figsize=(15, 5))
    plt.bar(range(256), observed_freq)
    plt.title("Byte Frequency (should be uniform)")
    plt.xlabel("Byte value")
    plt.ylabel("Frequency")
    plt.savefig("byte_frequency.png")
    plt.show()

analyze_encrypted_file("sifreli_data.bin")