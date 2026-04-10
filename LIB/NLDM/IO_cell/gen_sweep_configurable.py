import argparse
import os

def generate_spectre_sweep(corner, netlist, cell_name):
    # --- 1. ASAP7 .lib Indices ---
    input_slews = [5.0e-12, 10.0e-12, 20.0e-12, 40.0e-12, 80.0e-12, 160.0e-12, 320.0e-12] 
    load_caps = [5.76e-15, 11.52e-15, 23.04e-15, 46.08e-15, 92.16e-15, 184.32e-15, 368.64e-15]      

    # --- 2. Corner Configurations ---
    corner_configs = {
        "FF": {"voltage": 0.77, "temp": 0,   "model": "7nm_FF_160803.pm"},
        "SS": {"voltage": 0.63, "temp": 100, "model": "7nm_SS_160803.pm"},
        "TT": {"voltage": 0.70, "temp": 25,  "model": "7nm_TT_160803.pm"}
    }

    corner = corner.upper()
    if corner not in corner_configs:
        print(f"Error: Invalid corner '{corner}'. Choose TT, FF, or SS.")
        return

    config = corner_configs[corner]
    vdd = config["voltage"]
    
    # --- 3. Dynamic Threshold Calculation (Crucial for Multi-Corner) ---
    slew_lower_v = round(0.10 * vdd, 4)
    delay_v      = round(0.50 * vdd, 4)
    slew_upper_v = round(0.90 * vdd, 4)

    out_filename = f"char_sweep_{corner}_{cell_name}.scs"

    # --- 4. Generate the char_sweep.scs file ---
    with open(out_filename, "w") as f:
        f.write(f'// Auto-generated 7x7 Characterization Sweep\n')
        f.write(f'// Corner: {corner} | VDD: {vdd}V | Temp: {config["temp"]}C\n')
        f.write(f'include "{config["model"]}"\n')
        
        # Include your specific netlist
        f.write(f'include "{netlist}"\n\n')
        
        f.write(f'simulatorOptions options temp={config["temp"]}\n\n')
        f.write('parameters my_slew=10p my_cap=1f\n\n')

        # Power Setup
        f.write(f'Vvdd (vdd 0) vsource dc={vdd}\n')
        f.write('Vvss (vss 0) vsource dc=0\n\n')
        
        # Stimulus (Amplitude matches corner VDD)
        f.write(f'Vin (in 0) vsource type=pulse val0=0 val1={vdd} delay=100p rise=my_slew/0.8 fall=my_slew/0.8 width=4n period=8n\n\n')

        # DUT Instantiation (Uses the cell name passed in via command line)
        if cell_name == "IOCELLBUFANTENNAOUT":
            # Matches: VSS VDD in out w1 w3 w2
            f.write(f'X1 (vss vdd in out w1 w3 w2) {cell_name}\n')
        elif cell_name == "IOCELLBUFANTENNAIN":
            # Matches the original IN layout terminals
            f.write(f'X1 (vdd vss in w2 out) {cell_name}\n')
        else:
            print(f"Warning: Unknown cell {cell_name}, defaulting to 5 pins.")
            f.write(f'X1 (vdd vss in w2 out) {cell_name}\n')
            
        f.write('Cload (out 0) capacitor c=my_cap\n\n')

        f.write('simulator lang=spice\n')
        
        # Transition Measurements 
        f.write(f'.measure tran fall_transition trig v(out) val={slew_upper_v} fall=1 targ v(out) val={slew_lower_v} fall=1\n')
        f.write(f'.measure tran rise_transition trig v(out) val={slew_lower_v} rise=1 targ v(out) val={slew_upper_v} rise=1\n')
        
        # Delay Measurements
        f.write(f'.measure tran cell_rise trig v(in) val={delay_v} rise=1 targ v(out) val={delay_v} rise=1\n')
        f.write(f'.measure tran cell_fall trig v(in) val={delay_v} fall=1 targ v(out) val={delay_v} fall=1\n')
        
        # C_in Measurement
        f.write('.measure tran q_in integ i(Vin) from=90p to=1n\n')
        f.write(f'.measure tran c_in param=\'(-1 * q_in) / {vdd}\'\n')
        
        f.write('simulator lang=spectre\n\n')

        # Nested Sweeps
        f.write('sweep_cap sweep param=my_cap values=[')
        f.write(' '.join(map(str, load_caps)))
        f.write('] {\n')

        f.write('  sweep_slew sweep param=my_slew values=[')
        f.write(' '.join(map(str, input_slews)))
        f.write('] {\n')

        f.write('    tran_sim tran stop=10n\n')
        f.write('  }\n')
        f.write('}\n')

    print(f"Successfully generated: {out_filename}")
    print(f" -> VDD: {vdd}V | 10%: {slew_lower_v}V | 50%: {delay_v}V | 90%: {slew_upper_v}V")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate full 7x7 Spectre sweeps for specific corners.")
    parser.add_argument("-c", "--corner", required=True, choices=['TT', 'FF', 'SS', 'tt', 'ff', 'ss'], 
                        help="Process corner (TT, FF, SS)")
    parser.add_argument("-n", "--netlist", required=True, 
                        help="Path to the netlist file (e.g., lay.net)")
    parser.add_argument("-cell", "--cellname", required=True, 
                        help="Name of the subcircuit to instantiate (e.g., IOCELLBUFANTENNAIN)")
    
    args = parser.parse_args()
    generate_spectre_sweep(args.corner, args.netlist, args.cellname)