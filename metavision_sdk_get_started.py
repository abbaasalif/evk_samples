from metavision_core.event_io import EventsIterator
def parse_args():
    import argparse
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Metavision SDK get started example.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-i', '--input-raw-file', dest='input_path', default="",
        help="Path to input RAW file. If not specified, the live stream of the first available camera is used. "
        "If it's a camera serial number, it will try to open that camera instead.")
    args=parser.parse_args()
    return args

def main():
    """Main function of the example."""
    args = parse_args()

    mv_iterator = EventsIterator(args.input_path, delta_t=1000)

    for evs in mv_iterator:
        print("Got {} events".format(len(evs)))
    
if __name__ == "__main__":
    main()

