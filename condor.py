import os
import argparse
import subprocess
import time
from radioactivedecay.nuclide import Nuclide

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate GEANT4 macros.")
    parser.add_argument("--macros_folder", required=True, help="Path to the folder to save the generated macros.")
    parser.add_argument("--isotope", required=True, help="Isotope name.")
    parser.add_argument("--position", required=True, help="Position string.")
    parser.add_argument("--confine", required=True, help="Confinement name.")
    parser.add_argument("--num_events", type=int, required=True, help="Number of events.")
    parser.add_argument("--times", type=int, default=1, help="Number of times to submit the macro.")
    return parser.parse_args()

def generate_seeds():
    # Get current time in milliseconds
    current_time_ms = int(time.time() * 1000)

    # Introduce a short delay to allow the current time to change
    time.sleep(0.001)  # Sleep for 1 millisecond

    # Use current time as seeds
    seed1 = current_time_ms % 4294967295  # Maximum value for a 32-bit unsigned integer
    seed2 = (current_time_ms // 2) % 4294967295  # Avoid potential correlation with seed1

    return seed1, seed2

    return seed1, seed2

def get_metastable_energy(isotope, metastable_state):
    # Dictionary mapping isotopes to their known metastable energies
    metastable_energies = {
        "Ag108m": {
            'm': 109.466  # Energy in keV for Cs-137 metastable state m
        },
        # Add more isotopes and their metastable energies as needed
    }

    # Check if the isotope is in the dictionary
    if isotope in metastable_energies:
        # Check if the metastable state is known for the isotope
        if metastable_state in metastable_energies[isotope]:
            return metastable_energies[isotope][metastable_state]
        else:
            print(f"Metastable state {metastable_state} not found for isotope {isotope}.")
    else:
        print(f"Isotope {isotope} not found in metastable energy database.")

    return None

def generate_geant4_macros(macros_folder, isotope, position, confine, seed1, seed2, num_events, timestamp):
    # Ensure the macros folder exists
    os.makedirs(macros_folder, exist_ok=True)

    # Create a Nuclide instance
    nuclide = Nuclide(isotope)

    # Extract Z, A, and energy state from the Nuclide instance
    Z = nuclide.Z
    A = nuclide.A
    state = nuclide.state

    # Initialize excitation energy to 0 as default
    excitation_energy_keV = 0

    # If the isotope is in a metastable state
    if state == 'm':
        # Retrieve the excitation energy of the metastable state (in keV)
        excitation_energy_keV = get_metastable_energy(isotope, state)

    # Parse position into halfx, halfy, halfz
    halfx, halfy, halfz = position.split()

    # Define the output file name with timestamp
    output_file = f"{isotope}_{confine}_{timestamp}.root"

    # Define the content of the GEANT4 macro
    macro_content = f"""
# GENERATION OF RADIOACTIVE PARTICLES

/run/initialize

# define particle or ion
/gps/particle ion
/gps/ion {Z} {A} 0 {excitation_energy_keV} keV  # Setting properties of the ion with excitation energy

# define energy (set 0 for radioactive decaying nuclei)
/gps/energy 0. keV
/gps/pos/shape Para
/gps/pos/centre 0. 97. 0. cm
/gps/pos/halfx {halfx} m
/gps/pos/halfy {halfy} m
/gps/pos/halfz {halfz} m
#
/gps/pos/type Volume
/gps/pos/confine {confine}
#
#Save only events that pass that have hits in the sensitive gas
/CYGNO/cutoutfile 1
/CYGNO/save_hits_branches 0
/CYGNO/registeron 0
#
#change these for debug
/run/verbose 0
/event/verbose 0
/tracking/verbose 0
/CYGNO/reportingfrequency 100000
#Output file name
/CYGNO/outfile {output_file}
/random/setSeeds {seed1} {seed2}
#/process/em/deexcitationIgnoreCut true

# define number of events to be generated
/run/beamOn {num_events}
"""

    # Write the macro content to a file
    with open(os.path.join(macros_folder, f"{isotope}_{confine}_{timestamp}.mac"), "w") as f:
        f.write(macro_content)

def generate_condor_submit(submit_folder, isotope, confine, timestamp):
    # Ensure the submit folder exists
    os.makedirs(submit_folder, exist_ok=True)

    # Define the content of the Condor submit file
    submit_content = f"""
universe   = vanilla
executable = /jupyter-workspace/private/CYGNO_04/CYGNO-MC-build/run_simulation.sh
arguments  = {isotope}_{confine}_{timestamp}.mac

log        = {isotope}_{confine}_{timestamp}.log
output     = {isotope}_{confine}_{timestamp}.out
error      = {isotope}_{confine}_{timestamp}.error

getenv = True
transfer_input_files = /jupyter-workspace/private/CYGNO_04/CYGNO-MC-build/CYGNO, /jupyter-workspace/private/CYGNO_04/CYGNO-MC-build/macros, /jupyter-workspace/private/CYGNO_04/geometry, /usr/local/lib/libcadmesh.so
transfer_output_files  = {isotope}_{confine}_{timestamp}.root

+CygnoUser = "$ENV(USERNAME)"
+OWNER = "condor"

queue
"""

    # Write the submit content to a file
    with open(os.path.join(submit_folder, f"{isotope}_{confine}_{timestamp}.submit"), "w") as f:
        f.write(submit_content)

def submit_condor_job(submit_folder, isotope, confine, timestamp):
    # Path to the Condor submit file
    submit_file = os.path.join(submit_folder, f"{isotope}_{confine}_{timestamp}.submit")

    # Execute condor_submit command with spooling and capture output
    try:
        output = subprocess.check_output(["condor_submit", "-spool", submit_file], text=True)
        # Extract job ID from the output
        job_id = output.split()[-1]
        print(f"Submitted job {job_id}")

        # Delete the Condor submit file
        os.remove(submit_file)

        return job_id
    except subprocess.CalledProcessError as e:
        print(f"Error submitting job: {e}")
        return None
    
def check_jobs(job_ids_file):
    try:
        # Read job IDs and macro file names from the job IDs file
        with open(job_ids_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            job_id, macro_file = line.strip().split('\t')
            # Run condor_q command to check job status
            result = subprocess.run(["condor_q", job_id], capture_output=True, text=True)
            if "not found" in result.stdout:
                print(f"Job {job_id} associated with {macro_file} is not found.")
            else:
                print(f"Job {job_id} associated with {macro_file} is still running.")

                # Check if the job has finished
                if "not found" not in result.stdout:
                    # Run condor_transfer_data to retrieve output files
                    subprocess.run(["condor_transfer_data", job_id])
                    # Remove the job from the Condor queue
                    subprocess.run(["condor_rm", job_id])
                    print(f"Job {job_id} associated with {macro_file} has finished.")

    except FileNotFoundError:
        print(f"Job IDs file {job_ids_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

