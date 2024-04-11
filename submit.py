import time
from condor import parse_arguments, os, generate_geant4_macros, generate_seeds, generate_condor_submit

# Define the main function
def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Ensure the macros folder exists
    os.makedirs(args.macros_folder, exist_ok=True)
    os.makedirs(args.submit_folder, exist_ok=True)

    # Generate log file path
    log_file = f"macro_generation_{args.isotope}.log"
    log_path = os.path.join(args.submit_folder, log_file)

    # Open log file to save seeds and macro generation info
    with open(log_path, "w") as log:
        log.write("Seed1\tSeed2\tMacro Generation Info\tJob ID\n")

        # Iterate 'times' and generate macros
        for i in range(args.times):
            # Generate timestamp
            timestamp = int(time.time())

            # Generate seeds
            seed1, seed2 = generate_seeds()

            # Call the function to generate macros
            generate_geant4_macros(args.macros_folder, args.isotope, args.position, args.confine, seed1, seed2, args.num_events, timestamp)

            # Generate Condor submit file
            generate_condor_submit(args.submit_folder, args.isotope, args.confine, timestamp)

            # Submit Condor job and save job ID
            job_id = submit_condor_job(args.submit_folder, args.isotope, args.confine, timestamp, log_path, f"{args.isotope}_{args.confine}_{timestamp}.mac")
            if job_id:
                log.write(f"{seed1}\t{seed2}\tMacro {i+1}/{args.times}\t{job_id}\n")
                print(f"Condor job {job_id} submitted successfully.")
            else:
                log.write(f"{seed1}\t{seed2}\tMacro {i+1}/{args.times}\tFailed to submit job\n")
                print("Failed to submit Condor job.")

            # Introduce a one-second delay
            time.sleep(1)

# Execute the main function if the script is run directly
if __name__ == "__main__":
    main()



