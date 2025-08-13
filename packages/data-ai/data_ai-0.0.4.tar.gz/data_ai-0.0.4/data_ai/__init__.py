import sys
import argparse
import numpy as np
import io
from IPython import embed


# Global variables to store original file info for save function
_original_lines = None
_original_file = None
_has_header = None
_data = None


def save(filename=None):
    """
    Save numpy array data back to file, only modifying rows that have changed.
    Compares current data with parsed original lines to detect changes.
    
    Args:
        data: The numpy array to save
        filename: Output filename (defaults to original file if not specified)
    """
    global _original_lines, _original_file, _has_header, _data
    
    if _original_lines is None:
        print("Error: No original file data available. Make sure you loaded data using this tool.")
        return False
    
    output_file = filename if filename is not None else _original_file
    
    if output_file is None:
        print("Error: No output filename specified")
        return False
    
    try:
        # Start with original lines
        output_lines = _original_lines.copy()
        header_offset = 1 if _has_header else 0
        modified_count = 0
        
        # Compare each data row with the parsed original
        for row_idx in range(len(_data)):
            line_idx = row_idx + header_offset
            if line_idx >= len(_original_lines):
                continue
                
            original_line = _original_lines[line_idx]
            
            # Parse the original line to compare with current data
            try:
                original_values = original_line.split(',')
                current_row = _data[row_idx]
                
                # Check if this row has changed
                row_changed = False
                
                if _data.dtype.names is not None:
                    # Structured array - compare each field
                    if len(original_values) == len(_data.dtype.names):
                        for i, field_name in enumerate(_data.dtype.names):
                            original_val_str = original_values[i].strip()
                            current_val = current_row[field_name]
                            
                            # Try to parse original as same type as current
                            try:
                                if isinstance(current_val, (np.floating, float)):
                                    original_val = float(original_val_str)
                                    if not np.isclose(original_val, float(current_val), rtol=1e-15, atol=1e-15):
                                        row_changed = True
                                        break
                                elif isinstance(current_val, (np.integer, int)):
                                    original_val = int(float(original_val_str))  # Handle scientific notation
                                    if original_val != int(current_val):
                                        row_changed = True
                                        break
                                else:
                                    if str(original_val_str) != str(current_val):
                                        row_changed = True
                                        break
                            except (ValueError, TypeError):
                                # If parsing fails, assume changed
                                row_changed = True
                                break
                else:
                    # Regular array
                    if hasattr(current_row, '__iter__') and not isinstance(current_row, str):
                        # Multi-dimensional row
                        if len(original_values) == len(current_row):
                            for i, current_val in enumerate(current_row):
                                original_val_str = original_values[i].strip()
                                try:
                                    if isinstance(current_val, (np.floating, float)):
                                        original_val = float(original_val_str)
                                        if not np.isclose(original_val, float(current_val), rtol=1e-15, atol=1e-15):
                                            row_changed = True
                                            break
                                    elif isinstance(current_val, (np.integer, int)):
                                        original_val = int(float(original_val_str))
                                        if original_val != int(current_val):
                                            row_changed = True
                                            break
                                    else:
                                        if str(original_val_str) != str(current_val):
                                            row_changed = True
                                            break
                                except (ValueError, TypeError):
                                    row_changed = True
                                    break
                        else:
                            row_changed = True
                    else:
                        # Single value row
                        if len(original_values) == 1:
                            original_val_str = original_values[0].strip()
                            try:
                                if isinstance(current_row, (np.floating, float)):
                                    original_val = float(original_val_str)
                                    if not np.isclose(original_val, float(current_row), rtol=1e-15, atol=1e-15):
                                        row_changed = True
                                elif isinstance(current_row, (np.integer, int)):
                                    original_val = int(float(original_val_str))
                                    if original_val != int(current_row):
                                        row_changed = True
                                else:
                                    if str(original_val_str) != str(current_row):
                                        row_changed = True
                            except (ValueError, TypeError):
                                row_changed = True
                        else:
                            row_changed = True
                
                # If row changed, format and replace it
                if row_changed:
                    if _data.dtype.names is not None:
                        # Structured array
                        formatted_values = []
                        for field_name in _data.dtype.names:
                            val = current_row[field_name]
                            try:
                                num_val = float(val)
                                if abs(num_val) >= 1e15:
                                    formatted_values.append(f"{num_val:.16g}")
                                else:
                                    formatted_values.append(f"{num_val:.16g}")
                            except (ValueError, TypeError):
                                formatted_values.append(str(val))
                        new_line = ','.join(formatted_values)
                    else:
                        # Regular array
                        if hasattr(current_row, '__iter__') and not isinstance(current_row, str):
                            formatted_values = []
                            for val in current_row:
                                try:
                                    num_val = float(val)
                                    if abs(num_val) >= 1e15:
                                        formatted_values.append(f"{num_val:.16g}")
                                    else:
                                        formatted_values.append(f"{num_val:.16g}")
                                except (ValueError, TypeError):
                                    formatted_values.append(str(val))
                            new_line = ','.join(formatted_values)
                        else:
                            try:
                                num_val = float(current_row)
                                if abs(num_val) >= 1e15:
                                    new_line = f"{num_val:.16g}"
                                else:
                                    new_line = f"{num_val:.16g}"
                            except (ValueError, TypeError):
                                new_line = str(current_row)
                    
                    output_lines[line_idx] = new_line
                    modified_count += 1
                    
            except Exception as e:
                # If comparison fails, assume row changed
                print(f"Warning: Could not compare row {row_idx}, assuming changed: {e}")
                modified_count += 1
        
        # Write the file
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in output_lines:
                f.write(line + '\n')
        
        print(f"Data saved to '{output_file}' - {modified_count} row(s) modified")
        return True
        
    except Exception as e:
        print(f"Error saving file '{output_file}': {e}")
        return False


def main():
    global _original_lines, _original_file, _has_header, _data
    
    parser = argparse.ArgumentParser(description="Load CSV file and drop into a Python shell.")
    parser.add_argument('file', help='Path to the CSV file to load')
    parser.add_argument('--no-header', action='store_true', help='CSV has no header row')
    args = parser.parse_args()

    # Read CSV data from file and store original lines
    user_ns = {
        'data': None, 
        'np': np, 
        'save': save
    }
    def reload():
        global _original_lines, _original_file, _has_header, _data
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                _original_lines = [line.rstrip('\n\r') for line in f.readlines()]
            csv_content = '\n'.join(_original_lines)
            csv_buffer = io.StringIO(csv_content)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        except IOError as e:
            print(f"Error reading file '{args.file}': {e}")
            sys.exit(1)

        # Store file info globally for save function
        _original_file = args.file
        _has_header = not args.no_header

        # Use numpy.genfromtxt for structured array with column access
        _data = np.genfromtxt(
            csv_buffer,
            delimiter=",",
            names=not args.no_header,  # True if header exists, False if --no-header
            dtype=None,                # infer dtypes
            encoding="utf-8"
        )
        user_ns['data'] = _data
    reload()
    user_ns['reload'] = reload

    if args.no_header:
        banner = f"Loaded CSV data from '{args.file}' as numpy array in variable '_data'. Access columns with _data[column_index].\n\nUse save_csv(_data) to save changes back to the original file, or save(_data, 'newfile.csv') to save to a different file.\nOnly modified rows will be changed, preserving original formatting."
    else:
        banner = f"Loaded CSV data from '{args.file}' as numpy structured array in variable '_data'. Access columns with _data['column_name'].\n\nUse save(_data) to save changes back to the original file, or save(_data, 'newfile.csv') to save to a different file.\nOnly modified rows will be changed, preserving original formatting."
    
    try:
        import matplotlib.pyplot as plt
        user_ns['plt'] = plt
    except ImportError:
        pass

    embed(user_ns=user_ns, banner1=banner)