import os
import csv
import pandas as pd

def logger(input_metadata, report_dur, loop_dur, validation_dur, total_dur, validation_metrics, ranked_candidates):
 
    # --- 3. LOG TO CSV ---
    log_file = "thesis_complexity_log.csv"
    file_exists = os.path.isfile(log_file)

    # --- 1. Prepare the results row ---
    avg_islands = sum(m['islands'] for m in validation_metrics) / len(validation_metrics) if validation_metrics else 0

    results_row = {
        "num_redundant_R": input_metadata["num_redundant_R"],
        "num_nodes_V": input_metadata["num_nodes_V"],
        "num_admittances": input_metadata["num_admittances"],
        "report_time": round(report_dur, 6),
        "loop_time": round(loop_dur, 6),
        "validation_time": round(validation_dur, 6),
        "total_time": round(total_dur, 6),
        "avg_islands": round(avg_islands, 2),
        "num_candidates": len(ranked_candidates),
        "timestamp": input_metadata["timestamp"]
    }

    # --- 2. Check for Duplicates before writing ---
    log_file = "thesis_complexity_log.csv"
    should_write = True

    if os.path.exists(log_file):
        try:
            existing_df = pd.read_csv(log_file)
            # Check if a row with the same R and V already exists
            duplicate = existing_df[
                (existing_df['num_redundant_R'] == results_row['num_redundant_R']) & 
                (existing_df['num_nodes_V'] == results_row['num_nodes_V'])
            ]
            
            if not duplicate.empty:
                print(f"[Skip] Results for R={results_row['num_redundant_R']}, V={results_row['num_nodes_V']} already exist in {log_file}.")
                should_write = False
        except Exception as e:
            print(f"Note: Could not read existing log file ({e}), proceeding with write.")

    # --- 3. Write to CSV if unique ---
    if should_write:
        file_exists = os.path.isfile(log_file)
        with open(log_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results_row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(results_row)
        print(f"[Performance Log] New metrics written to {log_file}")
    print(f"\n[Performance Log] All metrics written to {log_file}")


    import os
import csv
import time
import pandas as pd

def thesis_performance_logger(grid_metadata, times_dict, report_metrics):
    """
    Dedicated scaling performance logger for Master's Thesis data tables.
    Tracks structural grid parameters against isolated runtime execution tiers.
    """
    log_file = "thesis_scaling_results.csv"
    
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