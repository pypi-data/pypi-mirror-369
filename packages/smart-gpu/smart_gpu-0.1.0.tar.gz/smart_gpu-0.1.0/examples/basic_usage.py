#!/usr/bin/env python3
"""
Basic usage example for smart-gpu package.

This example demonstrates how to use the smart-gpu package for automatic
GPU/CPU mode switching.
"""

from smart_gpu import (
    gpu_utils, 
    array, 
    DataFrame, 
    to_cpu, 
    synchronize,
    get_gpu_mode,
    set_gpu_mode
)

# Import np and pd directly from gpu_utils for automatic GPU/CPU switching
np = gpu_utils.np
pd = gpu_utils.pd


def main():
    """Main example function."""
    print("=== Smart GPU Basic Usage Example ===\n")
    
    # Check current GPU mode
    print(f"Current GPU mode: {'GPU' if get_gpu_mode() else 'CPU'}")
    print(f"GPU mode active: {gpu_utils.is_gpu_mode}")
    print()
    
    # Note: np and pd are imported from gpu_utils for automatic GPU/CPU switching
    print(f"Using NumPy from: {np.__name__}")
    print(f"Using Pandas from: {pd.__name__}")
    print()
    
    # Create arrays using the smart utilities
    print("Creating arrays...")
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Method 1: Using convenience functions
    arr1 = array(data)
    print(f"Array 1 type: {type(arr1)}")
    print(f"Array 1: {arr1}")
    
    # Method 2: Using gpu_utils instance
    arr2 = gpu_utils.array(data)
    print(f"Array 2 type: {type(arr2)}")
    print(f"Array 2: {arr2}")
    
    # Method 3: Using np property
    arr3 = gpu_utils.np.array(data)
    print(f"Array 3 type: {type(arr3)}")
    print(f"Array 3: {arr3}")
    
    # Method 4: Using imported np (automatic GPU/CPU switching)
    arr4 = np.array(data)
    print(f"Array 4 type: {type(arr4)}")
    print(f"Array 4: {arr4}")
    print()
    
    # Create DataFrames using the smart utilities
    print("Creating DataFrames...")
    df_data = {
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50],
        'C': ['a', 'b', 'c', 'd', 'e']
    }
    
    # Method 1: Using convenience functions
    df1 = DataFrame(df_data)
    print(f"DataFrame 1 type: {type(df1)}")
    print(f"DataFrame 1:\n{df1}")
    
    # Method 2: Using gpu_utils instance
    df2 = gpu_utils.DataFrame(df_data)
    print(f"DataFrame 2 type: {type(df2)}")
    print(f"DataFrame 2:\n{df2}")
    
    # Method 3: Using pd property
    df3 = gpu_utils.pd.DataFrame(df_data)
    print(f"DataFrame 3 type: {type(df3)}")
    print(f"DataFrame 3:\n{df3}")
    
    # Method 4: Using imported pd (automatic GPU/CPU switching)
    df4 = pd.DataFrame(df_data)
    print(f"DataFrame 4 type: {type(df4)}")
    print(f"DataFrame 4:\n{df4}")
    print()
    
    # Perform some operations
    print("Performing operations...")
    
    # Array operations using imported np
    arr_squared = np.square(arr1)
    arr_sum = np.sum(arr1)
    arr_mean = np.mean(arr1)
    print(f"Array squared: {arr_squared}")
    print(f"Array sum: {arr_sum}")
    print(f"Array mean: {arr_mean}")
    
    # DataFrame operations using imported pd
    df_sum = df1.sum(numeric_only=True)
    df_mean = df1.mean(numeric_only=True)
    print(f"DataFrame sum:\n{df_sum}")
    print(f"DataFrame mean:\n{df_mean}")
    print()
    
    # Convert to CPU if needed
    print("Converting to CPU format...")
    cpu_arr = to_cpu(arr1)
    cpu_df = to_cpu(df1)
    print(f"CPU array type: {type(cpu_arr)}")
    print(f"CPU DataFrame type: {type(cpu_df)}")
    print()
    
    # Synchronize GPU operations
    print("Synchronizing GPU operations...")
    synchronize()
    print("Synchronization complete!")
    print()
    
    # Demonstrate mode switching
    print("=== Mode Switching Demo ===")
    
    # Force CPU mode
    print("Forcing CPU mode...")
    set_gpu_mode(False)
    print(f"GPU mode after forcing CPU: {get_gpu_mode()}")
    
    cpu_arr_forced = array([1, 2, 3, 4, 5])
    print(f"Array created in forced CPU mode: {type(cpu_arr_forced)}")
    
    # Try to force GPU mode (will fall back to CPU if not available)
    print("Attempting to force GPU mode...")
    set_gpu_mode(True)
    print(f"GPU mode after forcing GPU: {get_gpu_mode()}")
    
    gpu_arr_attempted = array([1, 2, 3, 4, 5])
    print(f"Array created in attempted GPU mode: {type(gpu_arr_attempted)}")
    print()
    
    print("=== Example Complete ===")


if __name__ == "__main__":
    main()
