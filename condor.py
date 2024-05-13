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

def generate_geant4_gamma_bkg(macros_folder, num_events, seed1, seed2, timestamp):
    # Ensure the macros folder exists
    os.makedirs(macros_folder, exist_ok=True)
    
    # Define the output file name for the gamma background macro
    output_file = f"gamma_bkg_{timestamp}"

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
/gps/hist/point 0.044762924   1.16346931261
/gps/hist/point 0.065288852   2.53419075174
/gps/hist/point 0.08581478   3.66807847112
/gps/hist/point 0.106340708   3.74716766106
/gps/hist/point 0.126866636   3.50027681576
/gps/hist/point 0.147392564   3.0053457398
/gps/hist/point 0.167918492   2.5934756305
/gps/hist/point 0.18844442   2.22045926614
/gps/hist/point 0.208970348   1.96201003324
/gps/hist/point 0.229496276   1.73335939029
/gps/hist/point 0.250022204   1.54671467937
/gps/hist/point 0.270548132   1.3429621908
/gps/hist/point 0.29107406   1.17565485344
/gps/hist/point 0.311599988   1.06176331611
/gps/hist/point 0.332125916   0.993175163725
/gps/hist/point 0.352651844   0.910398539939
/gps/hist/point 0.373177772   0.738639197742
/gps/hist/point 0.3937037   0.576301610433
/gps/hist/point 0.414229628   0.476402371708
/gps/hist/point 0.434755556   0.434709985142
/gps/hist/point 0.455281484   0.395203286008
/gps/hist/point 0.475807412   0.369293883804
/gps/hist/point 0.49633334   0.351926215148
/gps/hist/point 0.516859268   0.363792345843
/gps/hist/point 0.537385196   0.361403461156
/gps/hist/point 0.557911124   0.409275520283
/gps/hist/point 0.578437052   0.454530760283
/gps/hist/point 0.59896298   0.471570345397
/gps/hist/point 0.619488908   0.428740821399
/gps/hist/point 0.640014836   0.358978092148
/gps/hist/point 0.660540764   0.251812749608
/gps/hist/point 0.681066692   0.202896927534
/gps/hist/point 0.70159262   0.173362589983
/gps/hist/point 0.722118548   0.169933068474
/gps/hist/point 0.742644476   0.171339686976
/gps/hist/point 0.763170404   0.165835722179
/gps/hist/point 0.783696332   0.168225397019
/gps/hist/point 0.80422226   0.159107616102
/gps/hist/point 0.824748188   0.150151746154
/gps/hist/point 0.845274116   0.145974403065
/gps/hist/point 0.865800044   0.143814938934
/gps/hist/point 0.886325972   0.142540073192
/gps/hist/point 0.9068519   0.14344359798
/gps/hist/point 0.927377828   0.140168409182
/gps/hist/point 0.947903756   0.128299860233
/gps/hist/point 0.968429684   0.117507311505
/gps/hist/point 0.988955612   0.10468031298
/gps/hist/point 1.00948154   0.101218009031
/gps/hist/point 1.030007468   0.102608194116
/gps/hist/point 1.050533396   0.100699784189
/gps/hist/point 1.071059324   0.115606584067
/gps/hist/point 1.091585252   0.123331457919
/gps/hist/point 1.11211118   0.135182201253
/gps/hist/point 1.132637108   0.126356440611
/gps/hist/point 1.153163036   0.120217840115
/gps/hist/point 1.173688964   0.118725069837
/gps/hist/point 1.194214892   0.104176484339
/gps/hist/point 1.21474082   0.102057507576
/gps/hist/point 1.235266748   0.0934214515671
/gps/hist/point 1.255792676   0.0832727955587
/gps/hist/point 1.276318604   0.0803718576792
/gps/hist/point 1.296844532   0.0760484896764
/gps/hist/point 1.31737046   0.0665157624599
/gps/hist/point 1.337896388   0.0745067600499
/gps/hist/point 1.358422316   0.0858400855464
/gps/hist/point 1.378948244   0.109615123397
/gps/hist/point 1.399474172   0.116908493191
/gps/hist/point 1.4200001   0.142798051022
/gps/hist/point 1.440526028   0.157313364759
/gps/hist/point 1.461051956   0.15103393223
/gps/hist/point 1.481577884   0.143850679883
/gps/hist/point 1.502103812   0.120780588657
/gps/hist/point 1.52262974   0.0946666853485
/gps/hist/point 1.543155668   0.0691588085715
/gps/hist/point 1.563681596   0.0537521187891
/gps/hist/point 1.584207524   0.0437403951457
/gps/hist/point 1.604733452   0.0364763936031
/gps/hist/point 1.62525938   0.0320658609018
/gps/hist/point 1.645785308   0.0327453960063
/gps/hist/point 1.666311236   0.0409415947329
/gps/hist/point 1.686837164   0.0420502091726
/gps/hist/point 1.707363092   0.0500444853794
/gps/hist/point 1.72788902   0.0543595923717
/gps/hist/point 1.748414948   0.0594816382721
/gps/hist/point 1.768940876   0.0570266451508
/gps/hist/point 1.789466804   0.0526039264534
/gps/hist/point 1.809992732   0.0488696322063
/gps/hist/point 1.83051866   0.0371220568436
/gps/hist/point 1.851044588   0.0329140181089
/gps/hist/point 1.871570516   0.0276733246664
/gps/hist/point 1.892096444   0.0193131930049
/gps/hist/point 1.912622372   0.0166664913188
/gps/hist/point 1.9331483   0.0146262661956
/gps/hist/point 1.953674228   0.0124753806466
/gps/hist/point 1.974200156   0.0123255153096
/gps/hist/point 1.994726084   0.0106532765635
/gps/hist/point 2.015252012   0.0103731483466
/gps/hist/point 2.03577794   0.0123401252676
/gps/hist/point 2.056303868   0.0145168437638
/gps/hist/point 2.076829796   0.0144715774864
/gps/hist/point 2.097355724   0.0159068233514
/gps/hist/point 2.117881652   0.0167747975648
/gps/hist/point 2.13840758   0.0187427463765
/gps/hist/point 2.158933508   0.0201935921262
/gps/hist/point 2.179459436   0.020248191723
/gps/hist/point 2.199985364   0.0211720756747
/gps/hist/point 2.220511292   0.0190436361013
/gps/hist/point 2.24103722   0.0172738676219
/gps/hist/point 2.261563148   0.0154480022411
/gps/hist/point 2.282089076   0.0120061821786
/gps/hist/point 2.302615004   0.0111606719771
/gps/hist/point 2.323140932   0.00976536163943
/gps/hist/point 2.34366686   0.00931140676905
/gps/hist/point 2.364192788   0.0073739090747
/gps/hist/point 2.384718716   0.00715807006388
/gps/hist/point 2.405244644   0.0074127216236
/gps/hist/point 2.425770572   0.00804925694138
/gps/hist/point 2.4462965   0.00769969593137
/gps/hist/point 2.466822428   0.00829910316793
/gps/hist/point 2.487348356   0.00827014935526
/gps/hist/point 2.507874284   0.0107853389267
/gps/hist/point 2.528400212   0.0122642635805
/gps/hist/point 2.54892614   0.0150196278053
/gps/hist/point 2.569452068   0.0178797602166
/gps/hist/point 2.589977996   0.0190074393928
/gps/hist/point 2.610503924   0.0189051043263
/gps/hist/point 2.631029852   0.0192959110052
/gps/hist/point 2.65155578   0.0168765666994
/gps/hist/point 2.672081708   0.0145764674866
/gps/hist/point 2.692607636   0.0109263602858
/gps/hist/point 2.713133564   0.00829841542242
/gps/hist/point 2.733659492   0.00596636778765
/gps/hist/point 2.75418542   0.00339414549949
/gps/hist/point 2.774711348   0.00206847315419
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
    with open(os.path.join(macros_folder, f"gamma_background_{timestamp}.mac"), "w") as f:
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

def submit_condor_job(submit_folder, timestamp, isotope=None, confine=None):
    # Construct the submit file name based on provided arguments
    submit_file_name = f"{isotope}_" if isotope else ""
    submit_file_name += f"{confine}_" if confine else ""
    submit_file_name += f"{timestamp}.submit"
    
    # Path to the Condor submit file
    submit_file = os.path.join(submit_folder, submit_file_name)

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

