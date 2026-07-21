import os
import csv
import pandas as pd
import time

def thesis_performance_logger(grid_metadata, times_dict, report_metrics):
    """
    Dedicated scaling performance logger for Master's Thesis data tables.
    Tracks structural grid parameters against isolated runtime execution tiers.
    """
    log_file = "results/thesis_scaling_results.csv"
    
    # Assemble the comprehensive thesis results row
    results_row = {
        # Grid Structural Topology Parameters
        "num_nodes_V": int(grid_metadata["n_nodes"]),
        "num_lines_E": int(grid_metadata["n_lines"]),  # Added physical edges count
        "mesh_ratio_alpha": float(grid_metadata["mesh_ratio"]),
        "sensor_density_p": float(grid_metadata["sensor_density"]),
        "total_measurements_M": int(grid_metadata["total_measurements"]),  # Added total sensors count
        "redundant_pool_size_R": int(grid_metadata["r_pool_size"]),
        
        # Isolated Execution Tiers (Rounded to 6 decimals for microsecond precision)
        "tier1_setup_preprocess_sec": round(times_dict["setup"], 6),
        "tier1_augment_expansion_sec": round(times_dict["augment"], 6),
        "tier2_island_sanitization_sec": round(times_dict["sanitize"], 6),
        "tier1_greedy_admittance_sec": round(times_dict["greedy"], 6),
        "tier3_total_pipeline_sec": round(times_dict["total"], 6),
        
        # Convergence & Topological Integrity Metrics
        "post_opt_island_count": int(report_metrics["num_islands"]),
        "unobservable_island_count": int(report_metrics["unobs_islands"]),
        "final_observability_status": str(report_metrics["status"]),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    should_write = True

    # Duplicate Protection Guard: Modified to check both nodes and lines
    if os.path.exists(log_file):
        try:
            existing_df = pd.read_csv(log_file)
            duplicate = existing_df[
                (existing_df['num_nodes_V'] == results_row['num_nodes_V']) & 
                (existing_df['num_lines_E'] == results_row['num_lines_E']) & 
                (existing_df['redundant_pool_size_R'] == results_row['redundant_pool_size_R'])
            ]
            
            # if not duplicate.empty:
            #     print(f"[Skip Logger] A benchmark record for V={results_row['num_nodes_V']}, E={results_row['num_lines_E']}, R={results_row['redundant_pool_size_R']} already exists.")
            #     should_write = False
        except Exception as e:
            print(f"Note: Log read-check skipped ({e}), safe writing anyway.")

    # Stream cleanly to the target CSV file
    if should_write:
        file_exists = os.path.isfile(log_file)
        with open(log_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results_row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(results_row)
        print(f"[Logger Success] Scaling data point cleanly exported to {log_file}")