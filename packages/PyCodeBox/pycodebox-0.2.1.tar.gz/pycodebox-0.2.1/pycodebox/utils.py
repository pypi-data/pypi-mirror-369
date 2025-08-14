#!/bin/env python
# -*- coding: utf-8 -*-


# ----------------------------------------------------------------#
# Other Utilities                                                 #
# ----------------------------------------------------------------#
# These functions are used for performing various actions not     #
# readily available in base python or other packages.             #
# ----------------------------------------------------------------#


def read_tab_delim_file_to_dict(filename):
  """
  Read a tab-delimited file and return a dictionary where:
  - Key: first field of each line
  - Value: list of remaining fields (excluding empty fields)

  Parameters
  ----------
  filename : str
      Path to the tab-delimited file.

  Returns
  -------
  dict
      Dictionary with first field as key and remaining fields as list values
  """
  data_dict = {}

  try:
    with open(filename, "r", encoding="utf-8") as file:
      for line_num, line in enumerate(file, 1):
        # Strip whitespace and skip empty lines
        line = line.strip()
        if not line:
          continue

        # Split by tab
        fields = line.split("\t")

        # Skip lines with less than 2 fields (i.e., no values to key)
        if len(fields) < 2:
          print(f"Warning: Line {line_num} has less than 2 fields, skipping...")
          continue

        # First field is the key
        key = fields[0]

        # Remaining fields are the values (filter out empty strings)
        values = [field for field in fields[1:] if field.strip()]

        # Add to dictionary
        data_dict[key] = values

  except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    return {}
  except Exception as e:
    print(f"Error reading file: {e}")
    return {}

  return data_dict
