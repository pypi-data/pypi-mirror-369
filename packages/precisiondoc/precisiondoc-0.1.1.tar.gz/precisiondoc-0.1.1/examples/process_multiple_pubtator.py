#!/usr/bin/env python3
import os
import sys
import glob
import shutil
import subprocess
import argparse
from pathlib import Path

def create_modified_script(original_script_path, tmp_script_path, input_file, output_file):
    """
    Create a modified version of the original script with updated input and output file paths
    """
    with open(original_script_path, 'r') as f:
        script_content = f.read()
    
    # Replace the input and output file paths
    script_content = script_content.replace('in_pubtator_file="input.pubtator"', f'in_pubtator_file="{input_file}"')
    script_content = script_content.replace('out_pubtator_file="predict.pubtator"', f'out_pubtator_file="{output_file}"')
    
    # Write the modified script to a temporary file
    with open(tmp_script_path, 'w') as f:
        f.write(script_content)
    
    # Make the temporary script executable
    os.chmod(tmp_script_path, 0o755)

def main():
    parser = argparse.ArgumentParser(description='Process multiple PubTator files using BioREx')
    parser.add_argument('--biorex_dir', required=True, help='Path to BioREx directory')
    parser.add_argument('--input_dir', required=True, help='Directory containing PubTator files')
    parser.add_argument('--output_dir', required=True, help='Directory for output files')
    parser.add_argument('--gpu_ids', default='0,1', help='GPU IDs to use (default: 0,1)')
    parser.add_argument('--file_pattern', default='*.pubtator', help='Pattern to match PubTator files (default: *.pubtator)')
    
    args = parser.parse_args()
    
    # Ensure paths are absolute
    biorex_dir = os.path.abspath(args.biorex_dir)
    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)
    
    # Path to the original script
    original_script = os.path.join(biorex_dir, 'scripts', 'run_test_pred.sh')
    
    # Check if the original script exists
    if not os.path.isfile(original_script):
        print(f"Error: Original script not found at {original_script}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a temporary directory for modified scripts
    tmp_dir = os.path.join('./tmp', f'biorex_scripts_{os.getpid()}')
    os.makedirs(tmp_dir, exist_ok=True)
    
    print(f"Looking for PubTator files in {input_dir} with pattern {args.file_pattern}")
    
    # Find all PubTator files in the input directory
    pubtator_files = glob.glob(os.path.join(input_dir, args.file_pattern))
    
    if not pubtator_files:
        print(f"No PubTator files found in {input_dir} with pattern {args.file_pattern}")
        sys.exit(1)
    
    print(f"Found {len(pubtator_files)} PubTator files to process")
    
    # Process each PubTator file
    for input_file in pubtator_files:
        filename = os.path.basename(input_file)
        output_file = os.path.join(output_dir, filename)
        
        print(f"\nProcessing {filename}...")
        
        # Create a temporary script for this file
        tmp_script = os.path.join(tmp_dir, f"run_pred_{filename}.sh")
        
        # Create modified script
        create_modified_script(original_script, tmp_script, input_file, output_file)
        
        # Execute the temporary script
        try:
            # Change to the BioREx directory before executing the script
            original_dir = os.getcwd()
            os.chdir(biorex_dir)
            
            # Execute the script
            print(f"Executing: bash {tmp_script} {args.gpu_ids}")
            subprocess.run(['bash', tmp_script, args.gpu_ids], check=True)
            
            # Change back to the original directory
            os.chdir(original_dir)
            
            print(f"Successfully processed {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing {filename}: {e}")
        except Exception as e:
            print(f"Unexpected error processing {filename}: {e}")
    
    # Clean up temporary directory
    shutil.rmtree(tmp_dir)
    
    print(f"\nAll files processed. Results are in {output_dir}")

if __name__ == "__main__":
    main()
