import os
import subprocess
import time
from radioactivedecay.nuclide import Nuclide

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
    output_file = f"{isotope}_{confine}_{timestamp}"

    # Define the content of the GEANT4 macro
    macro_content = f"""
# GENERATION OF RADIOACTIVE PARTICLES

/run/initialize

"""

    # Add nucleusLimits for U238
    if isotope == "U238":
        macro_content += "/grdm/nucleusLimits 230 238 90 92\n"

    # Append the rest of the macro content
    macro_content += f"""

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

def generate_geant4_gamma_bkg(macros_folder, num_events, seed1, seed2):
    # Ensure the macros folder exists
    os.makedirs(macros_folder, exist_ok=True)
    
    # Define the output file name for the gamma background macro
    output_file = "gamma_bkg"

    # Define the content of the GEANT4 gamma background macro
    macro_content = f"""
/run/initialize

# GENERATION OF GAMMAS
/gps/particle gamma
/gps/pos/type Surface
/gps/pos/shape Sphere
/gps/pos/centre 0. 0. 0. m
/gps/pos/radius 3.3 m
/gps/ang/type iso

# FIXME : check normalization
#########       energy [MeV]   counts/keV/sec in Hall C @LNGS  
/gps/hist/point 0.003711068   0.239576347412
/gps/hist/point 0.024236996   0.567445723826
... (truncated for brevity)
/gps/hist/point 2.795237276   0.00120586576321
/gps/hist/point 2.815763204   0.000902168592194
/gps/hist/point 2.836289132   0.000638594111615

# DEBUG OPTIONS
/run/verbose 0
/event/verbose 0
/tracking/verbose 0
/CYGNO/reportingfrequency 100000
#Output file name
/CYGNO/outfile {output_file}
/random/setSeeds {seed1} {seed2}

# define number of events to be generated
/run/beamOn {num_events}
"""

    # Write the macro content to a file
    with open(os.path.join(macros_folder, f"gamma_background.mac"), "w") as f:
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

def generate_condor_submit_gamma_background(submit_folder, timestamp):
    # Ensure the submit folder exists
    os.makedirs(submit_folder, exist_ok=True)

    # Define the content of the Condor submit file for gamma background
    submit_content = f"""
universe   = vanilla
executable = /path/to/gamma_background_executable
arguments  = --macros_folder /path/to/macros_folder --num_events 1000000 --times 1

log        = gamma_background_{timestamp}.log
output     = gamma_background_{timestamp}.out
error      = gamma_background_{timestamp}.error

getenv = True
transfer_input_files = /path/to/gamma_background_files
transfer_output_files  = gamma_background_{timestamp}.root

queue
"""

    # Write the submit content to a file
    with open(os.path.join(submit_folder, f"submit_gamma_background_{timestamp}.submit"), "w") as f:
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
    
def check_jobs(log_files):
    for log_file in log_files:
        try:
            # Read job IDs and macro file names from the log file
            with open(log_file, 'r') as f:
                lines = f.readlines()

            for line in lines:
                # Split the line by tabs to extract job ID and macro file name
                job_info = line.strip().split('\t')
                job_id = job_info[-1]  # Last element is the job ID
                macro_file = job_info[-2]  # Second to last element is the macro file name
                
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
            print(f"Log file {log_file} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

