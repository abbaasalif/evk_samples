import os
import numpy as np

from metavision_core.event_io import RawReader

input_raw_file = r'data\backscatter_1sec_bias.raw'

record_raw = RawReader(input_raw_file)
print(record_raw)