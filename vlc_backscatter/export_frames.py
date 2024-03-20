import cv2
import numpy as np
import os
import argparse
from concurrent.futures import ThreadPoolExecutor
from metavision_core.event_io import EventsIterator
from metavision_sdk_core import PeriodicFrameGenerationAlgorithm
from metavision_sdk_ui import Window, EventLoop

def process_events(evs, frame_gen, window):
    frame_gen.process_events(evs)  # Feed events to the frame generator
    EventLoop.poll_and_dispatch()  # Dispatch system events to the window

def convert_raw_to_avi(input_path, output_path):
    mv_iterator = EventsIterator(input_path=input_path, delta_t=1e3)
    height, width = mv_iterator.get_size()

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))

    with Window("Conversion", width, height, Window.RenderMode.BGR) as window:
        def periodic_cb(ts, frame):
            cv2.putText(frame, "Timestamp: " + str(ts), (0, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0))
            out.write(frame)
            window.show(frame)

        periodic_gen = PeriodicFrameGenerationAlgorithm(width, height, accumulation_time_us=10000, fps=50)
        periodic_gen.set_output_callback(periodic_cb)

        with ThreadPoolExecutor(max_workers=1) as executor:
            for evs in mv_iterator:
                executor.submit(process_events, evs, periodic_gen, window)
                if window.should_close():
                    break

    out.release()

def main(input_dir, output_dir):
    # Check for existing .avi files in output directory
    existing_avis = {file.replace('.avi', '') for file in os.listdir(output_dir) if file.endswith('.avi')}

    # Process .raw files that haven't been converted
    for file in os.listdir(input_dir):
        if file.endswith('.raw') and file.replace('.raw', '') not in existing_avis:
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file.replace('.raw', '.avi'))
            print(f"Converting {file} to AVI...")
            convert_raw_to_avi(input_path, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .raw files to .avi format.")
    parser.add_argument('--input_dir', type=str, help="Directory containing .raw files.")
    parser.add_argument('--output_dir', type=str, help="Directory to save .avi files.")

    args = parser.parse_args()

    main(args.input_dir, args.output_dir)
