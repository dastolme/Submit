import time
import os
import argparse
from condor import generate_geant4_gamma_bkg, generate_seeds, generate_condor_submit_gamma_background, submit_condor_job

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate GEANT4 macros.")
    parser.add_argument("--macros_folder", required=True, help="Path to the folder to save the generated macros.")
    parser.add_argument("--num_events", type=int, required=True, help="Number of events.")
    parser.add_argument("--times", type=int, default=1, help="Number of times to submit the macro.")
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Ensure the macros folder exists
    os.makedirs(args.macros_folder, exist_ok=True)
    
    # Define the submit folder                                                                                         
    submit_folder = "."

    # Generate log file path
    log_file = f"macro_generation.log"
    log_path = os.path.join(submit_folder, log_file)

    # Open log file to save seeds and macro generation info
    with open(log_path, "w") as log:
        log.write("Seed1\tSeed2\tNum Events\tMacro Generation Info\tJob ID\n")

        # Iterate 'times' and generate macros
        for i in range(args.times):
            # Generate timestamp
            timestamp = int(time.time())

            # Generate seeds
            seed1, seed2 = generate_seeds()

            # Call the function to generate macros
            generate_geant4_gamma_bkg(args.macros_folder, args.num_events, seed1, seed2, timestamp)

            # Generate Condor submit file
            generate_condor_submit_gamma_background(submit_folder, timestamp)

            # Submit Condor job and save job ID
            job_id = submit_condor_job(submit_folder, timestamp)
            if job_id:
                log.write(f"{seed1}\t{seed2}\t{args.num_events}\tMacro {i+1}/{args.times}\t{job_id}\n")
                print(f"Condor job {job_id} submitted successfully.")
            else:
                log.write(f"{seed1}\t{seed2}\t{args.num_events}\tMacro {i+1}/{args.times}\tFailed to submit job\n")
                print("Failed to submit Condor job.")

            # Introduce a one-second delay
            time.sleep(1)

# Execute the main function if the script is run directly
if __name__ == "__main__":
    main()