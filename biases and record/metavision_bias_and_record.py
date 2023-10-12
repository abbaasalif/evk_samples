# Copyright (c) Prophesee S.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""
Sample code that demonstrates how to use Metavision HAL Python API to synchronize two cameras.
"""
import sys
import time
from metavision_core.event_io.raw_reader import initiate_device
from metavision_core.event_io import EventsIterator, LiveReplayEventsIterator
from metavision_sdk_core import PeriodicFrameGenerationAlgorithm, ColorPalette
from metavision_sdk_ui import EventLoop, BaseWindow, MTWindow, UIAction, UIKeyEvent
from biases import get_biases_from_file, save_biases_to_file
import argparse


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Metavision camera synchronization sample.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-s', '--serial-number', dest='input_path', default="",
        help="Camera serial number. If not specified, the live stream of the first available camera is used.")
        
    parser.add_argument(
        '-b', '--bias-file', dest='bias_file', default="gen41_CD_standard.bias",
        help="bias file input path. If not specified, default biases used.")
        
    parser.add_argument(
        '-r', '--recording-state', dest='state', default="False",
        help="Recording path. If not specified source folder used.")

    args = parser.parse_args()
    return args

def main():
    """ Main """
    args = parse_args()

    # Creation of HAL device
    device = initiate_device(path=args.input_path)

    # Retrieves sensor version
    i_hw_identification = device.get_i_hw_identification()
    sensor_info = i_hw_identification.get_sensor_info()
    base_path = "camera" + i_hw_identification.get_serial()

    # Retrieve biases within a bias_file
    biases = {}
    bias_file = args.bias_file

    # we use the facility get_i_ll_biases to set biases
    i_ll_biases = device.get_i_ll_biases()
    if i_ll_biases is not None:
        if bias_file:
            biases = get_biases_from_file(bias_file)
            for bias_name, bias_value in biases.items():
                i_ll_biases.set(bias_name, bias_value)
        biases = i_ll_biases.get_all_biases()

    # we record stream and biases
    state = args.state
    if device.get_i_events_stream():
        if state:
            log_path = base_path + '_' + time.strftime("%y%m%d_%H%M%S", time.localtime())
            print(f'Recording to {log_path + ".raw"}')
            device.get_i_events_stream().log_raw_data(log_path + '.raw')

            # Store biases whenever available
            if device.get_i_ll_biases():
                save_biases_to_file(log_path + '.bias', device.get_i_ll_biases().get_all_biases())
        else:
            device.get_i_events_stream().stop_log_raw_data()

    # Events iterator on the device
    mv_iterator = EventsIterator.from_device(device=device)
    height, width = mv_iterator.get_size()  # Camera Geometry

    # Window - Graphical User Interface
    with MTWindow(title="Metavision set biases and record", width=width, height=height,
                  mode=BaseWindow.RenderMode.BGR) as window:
        def keyboard_cb(key, scancode, action, mods):
            if key == UIKeyEvent.KEY_ESCAPE or key == UIKeyEvent.KEY_Q:
                window.set_close_flag()

        window.set_keyboard_callback(keyboard_cb)

        # Event Frame Generator
        event_frame_gen = PeriodicFrameGenerationAlgorithm(sensor_width=width, sensor_height=height, fps=25,
                                                           palette=ColorPalette.Dark)

        def on_cd_frame_cb(ts, cd_frame):
            window.show_async(cd_frame)

        event_frame_gen.set_output_callback(on_cd_frame_cb)

        for evs in mv_iterator:
            # Dispatch system events to the window in order to catch keystrokes
            EventLoop.poll_and_dispatch()
            event_frame_gen.process_events(evs)
            if window.should_close():
                break


if __name__ == "__main__":
    main()
