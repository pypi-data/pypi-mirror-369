# MediLink_Down.py
import os, shutil, sys

# Add paths
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
current_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Use core utilities for imports
try:
    from MediCafe.core_utils import get_shared_config_loader, extract_medilink_config
    MediLink_ConfigLoader = get_shared_config_loader()
    if MediLink_ConfigLoader is not None:
        log = MediLink_ConfigLoader.log
        load_configuration = MediLink_ConfigLoader.load_configuration
    else:
        raise ImportError("MediLink_ConfigLoader not available")
except ImportError:
    # Fallback for when core_utils is not available
    def log(message, level="INFO"):
        print("[{}] {}".format(level, message))
    def load_configuration():
        return {}, {}

try:
    from MediLink_Decoder import process_decoded_file, display_consolidated_records, write_records_to_csv
except ImportError:
    # Fallback if decoder not available
    process_decoded_file = None
    display_consolidated_records = None
    write_records_to_csv = None

try:
    from MediLink_DataMgmt import operate_winscp
except ImportError:
    operate_winscp = None

try:
    from tqdm import tqdm
except ImportError:
    # Fallback for when tqdm is not available
    def tqdm(iterable, **kwargs):
        return iterable

try:
    from MediCafe.submission_index import append_submission_record as _append_submission_record, ensure_submission_index as _ensure_submission_index, append_ack_event as _append_ack_event
except ImportError:
    # Fallback if submission_index not available
    _append_submission_record = None
    _ensure_submission_index = None
    _append_ack_event = None


def handle_files(local_storage_path, downloaded_files):
    """
    Moves downloaded files to the appropriate directory and translates them to CSV format.
    """
    log("Starting to handle downloaded files.")
    
    # Set the local response directory
    local_response_directory = os.path.join(local_storage_path, "responses")
    os.makedirs(local_response_directory, exist_ok=True)
    
    # Supported file extensions (enable ERA/277/999; keep EBT)
    file_extensions = ['.era', '.277', '.277ibr', '.277ebr', '.999', '.dpt', '.ebt', '.ibt', '.txt']
    
    files_moved = []
    
    for file in downloaded_files:
        lower = file.lower()
        if any(lower.endswith(ext) for ext in file_extensions):  # Case-insensitive match
            source_path = os.path.join(local_storage_path, file)
            destination_path = os.path.join(local_response_directory, os.path.basename(file))
            
            try:
                shutil.move(source_path, destination_path)
                log("Moved '{}' to '{}'".format(file, local_response_directory))
                files_moved.append(destination_path)
            except Exception as e:
                log("Error moving file '{}' to '{}': {}".format(file, destination_path, e), level="ERROR")
        else:
            log("Skipping unsupported file '{}'.".format(file), level="DEBUG")
    
    if not files_moved:
        log("No files were moved. Ensure that files with supported extensions exist in the download directory.", level="WARNING")
    
    # Translate the files
    consolidated_records, translated_files = translate_files(files_moved, local_response_directory)
    
    return consolidated_records, translated_files

def translate_files(files, output_directory):
    """
    Translates given files into CSV format and returns the list of translated files and consolidated records.
    """
    log("Translating files: {}".format(files), level="DEBUG")

    if not files:
        log("No files provided for translation. Exiting translate_files.", level="WARNING")
        return [], []

    translated_files = []
    consolidated_records = []
    
    # Enable processing for ERA, 277 family, 999, and EBT
    file_type_selector = {
        '.era': True,
        '.277': True,
        '.277ibr': True,
        '.277ebr': True,
        '.999': True,
        '.dpt': False,
        '.ebt': True,
        '.ibt': False,
        '.txt': False
    }

    file_counts = {ext: 0 for ext in file_type_selector.keys()}

    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if file_type_selector.get(ext, False):  # Check if the file type is selected
            file_counts[ext] += 1

            try:
                src_path = os.path.join(output_directory, os.path.basename(file))
                records = process_decoded_file(src_path, output_directory, return_records=True)
                # Annotate records with source metadata for downstream persistence
                try:
                    mtime = os.path.getmtime(src_path)
                except Exception:
                    mtime = None
                for r in records:
                    try:
                        setattr(r, 'source_file', src_path)
                        setattr(r, 'source_mtime', mtime)
                    except Exception:
                        pass
                consolidated_records.extend(records)
                csv_file_path = os.path.join(output_directory, os.path.basename(file) + '_decoded.csv')
                translated_files.append(csv_file_path)
                log("Translated file to CSV: {}".format(csv_file_path), level="INFO")
            except ValueError:
                log("Unsupported file type: {}".format(file), level="WARNING")
            except Exception as e:
                log("Error processing file {}: {}".format(file, e), level="ERROR")
        else:
            log("Skipping unselected file type for '{}'.".format(file), level="DEBUG")

    log("Detected and processed file counts by type:")
    for ext, count in file_counts.items():
        log("{}: {} files detected".format(ext, count), level="INFO")

    # Simple, elegant summary for console UI
    try:
        if consolidated_records:
            total = len(consolidated_records)
            num_rejected = 0
            num_accepted = 0
            for r in consolidated_records:
                status = getattr(r, 'status', '') if hasattr(r, 'status') else r.get('Status', '')
                if status:
                    if ('Reject' in status) or (':' in status and status.upper().startswith('R')):
                        num_rejected += 1
                    elif ('Accept' in status) or (':' in status and status.upper().startswith('A')):
                        num_accepted += 1
            print("\nAcknowledgements Summary:")
            print("  Total records: {}".format(total))
            print("  Accepted: {}".format(num_accepted))
            print("  Rejected: {}".format(num_rejected))
            print("")
    except Exception:
        pass

    return consolidated_records, translated_files

def prompt_csv_export(records, output_directory):
    """
    Prompts the user to export consolidated records to a CSV file.
    """
    if records:
        # Persist lightweight ack events into receipts index (optional, best-effort)
        try:
            config, _ = load_configuration()
            medi = extract_medilink_config(config)
            receipts_root = medi.get('local_claims_path', None)
            if receipts_root and _ensure_submission_index and _append_ack_event:
                _ensure_submission_index(receipts_root)
                for rec in records:
                    try:
                        # rec may be UnifiedRecord; convert
                        if hasattr(rec, 'to_dict'):
                            d = rec.to_dict()
                        else:
                            d = rec
                        claim_no = d.get('Claim #', '')
                        status_text = d.get('Status', '')
                        # infer ack_type by presence of fields
                        ack_type = ''
                        if d.get('Paid', '') != '' or d.get('Allowed', '') != '':
                            ack_type = 'ERA'
                        elif status_text and ':' in status_text:
                            ack_type = '277'
                        else:
                            ack_type = 'EBT'  # default for text notifications
                        # Use file metadata when available
                        file_name = os.path.basename(getattr(rec, 'source_file', '')) if hasattr(rec, 'source_file') else 'responses'
                        ts = getattr(rec, 'source_mtime', None)
                        control_ids = {}
                        if claim_no:
                            _append_ack_event(
                                receipts_root,
                                '',  # claim_key unknown here
                                status_text,
                                ack_type,
                                file_name,
                                control_ids,
                                'download_ack',
                                int(ts) if isinstance(ts, (int, float)) else None
                            )
                    except Exception:
                        continue
        except Exception:
            pass
        
        user_input = input("Do you want to export the consolidated records to a CSV file? (y/n): ")
        if user_input.lower() == 'y':
            output_file_path = os.path.join(output_directory, "Consolidated_Records.csv")
            write_records_to_csv(records, output_file_path)
            log("Consolidated CSV file created at: {}".format(output_file_path), level="INFO")
        else:
            log("CSV export skipped by user.", level="INFO")

def main(desired_endpoint=None):
    """
    Main function for running MediLink_Down as a standalone script. 
    Simplified to handle only CLI operations and delegate the actual processing to the high-level function.
    """
    log("Running MediLink_Down.main with desired_endpoint={}".format(desired_endpoint))

    if not desired_endpoint:
        log("No specific endpoint provided. Aborting operation.", level="ERROR")
        return None, None
    
    try:
        config, _ = load_configuration()
        medi = extract_medilink_config(config)
        endpoint_config = medi.get('endpoints', {}).get(desired_endpoint)
        if not endpoint_config or 'remote_directory_down' not in endpoint_config:
            log("Configuration for endpoint '{}' is incomplete or missing 'remote_directory_down'.".format(desired_endpoint), level="ERROR")
            return None, None

        local_storage_path = medi.get('local_storage_path', '.')
        log("Local storage path set to {}".format(local_storage_path))
        
        downloaded_files = operate_winscp("download", None, endpoint_config, local_storage_path, config)
        
        if downloaded_files:
            log("From main(), WinSCP Downloaded the following files: \n{}".format(downloaded_files))
            consolidated_records, translated_files = handle_files(local_storage_path, downloaded_files)
            
            # Convert UnifiedRecord instances to dictionaries before displaying
            dict_consolidated_records = [record.to_dict() for record in consolidated_records]
            display_consolidated_records(dict_consolidated_records)

            # Prompt for CSV export
            prompt_csv_export(consolidated_records, local_storage_path)
            
            return consolidated_records, translated_files
        else:
            log("No files were downloaded for endpoint: {}. Exiting...".format(desired_endpoint), level="WARNING")
            return None, None
    
    except Exception as e:
        log("An error occurred in MediLink_Down.main: {}".format(e), level="ERROR")
        return None, None


def check_for_new_remittances(config=None):
    """
    Function to check for new remittance files across all configured endpoints.
    Loads the configuration, validates it, and processes each endpoint to download and handle files.
    Accumulates results from all endpoints and processes them together at the end.
    """
    # Start the process and log the initiation
    log("Starting check_for_new_remittances function")
    print("\nChecking for new files across all endpoints...")
    log("Checking for new files across all endpoints...")

    # Step 1: Load and validate the configuration
    if config is None:
        config, _ = load_configuration()

    medi = extract_medilink_config(config)
    if not medi or 'endpoints' not in medi:
        log("Error: Config is missing necessary sections. Aborting...", level="ERROR")
        return

    endpoints = medi.get('endpoints')
    if not isinstance(endpoints, dict):
        log("Error: 'endpoints' is not a dictionary. Aborting...", level="ERROR")
        return

    # Lists to accumulate all consolidated records and translated files across all endpoints
    all_consolidated_records = []
    all_translated_files = []

    # Step 2: Process each endpoint and accumulate results
    for endpoint_key, endpoint_info in tqdm(endpoints.items(), desc="Processing endpoints"):
        # Validate endpoint structure
        if not endpoint_info or not isinstance(endpoint_info, dict):
            log("Error: Invalid endpoint structure for {}. Skipping...".format(endpoint_key), level="ERROR")
            continue

        if 'remote_directory_down' in endpoint_info:
            # Process the endpoint and handle the files
            log("Processing endpoint: {}".format(endpoint_key))
            consolidated_records, translated_files = process_endpoint(endpoint_key, endpoint_info, config)
            
            # Accumulate the results for later processing
            if consolidated_records:
                all_consolidated_records.extend(consolidated_records)
            if translated_files:
                all_translated_files.extend(translated_files)
        else:
            log("Skipping endpoint '{}'. 'remote_directory_down' not configured.".format(endpoint_info.get('name', 'Unknown')), level="WARNING")

    # Step 3: After processing all endpoints, handle the accumulated results
    if all_consolidated_records:
        display_consolidated_records(all_consolidated_records)  # Ensure this is called only once
        prompt_csv_export(all_consolidated_records, medi.get('local_storage_path', '.'))
    else:
        log("No records to display after processing all endpoints.", level="WARNING")
        print("No records to display after processing all endpoints.")


def process_endpoint(endpoint_key, endpoint_info, config):
    """
    Helper function to process a single endpoint.
    Downloads files from the endpoint, processes them, and returns the consolidated records and translated files.
    """
    try:
        # Process the files for the given endpoint
        medi = extract_medilink_config(config)
        local_storage_path = medi.get('local_storage_path', '.')
        log("[Process Endpoint] Local storage path set to {}".format(local_storage_path))
        downloaded_files = operate_winscp("download", None, endpoint_info, local_storage_path, config)
        
        if downloaded_files:
            log("[Process Endpoint] WinSCP Downloaded the following files: \n{}".format(downloaded_files))
            return handle_files(local_storage_path, downloaded_files)
        else:
            log("[Process Endpoint]No files were downloaded for endpoint: {}.".format(endpoint_key), level="WARNING")
            return [], []

    except Exception as e:
        # Handle any exceptions that occur during the processing
        log("Error processing endpoint {}: {}".format(endpoint_key, e), level="ERROR")
        return [], []

if __name__ == "__main__":
    main()