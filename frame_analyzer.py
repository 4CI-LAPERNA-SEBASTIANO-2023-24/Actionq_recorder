import sys
import argparse
import csv
import os
from jetson_inference import poseNet
from jetson_utils import videoSource, videoOutput, Log

def save_csv_with_increment(base_name):
    max_index = -1
    for filename in os.listdir('.'):
        if filename.startswith(base_name) and filename.endswith('.csv'):
            try:
                index = int(filename[len(base_name)+1:-4])
                if index > max_index:
                    max_index = index
            except ValueError:
                pass
    new_index = max_index + 1
    new_filename = f"{base_name}_{new_index:03d}.csv"
    return new_filename

parser = argparse.ArgumentParser(description="Run pose estimation DNN on a video/image stream.", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=poseNet.Usage() + videoSource.Usage() + videoOutput.Usage() + Log.Usage())

parser.add_argument("input", type=str, default="", nargs='?', help="URI of the input stream (e.g. video file, camera index, etc.)")
parser.add_argument("output", type=str, default="", nargs='?', help="URI of the output stream (e.g. display, video file, etc.)")
parser.add_argument("--network", type=str, default="resnet18-body", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="links,keypoints", help="pose overlay flags (e.g. --overlay=links,keypoints)\nvalid combinations are:  'links', 'keypoints', 'boxes', 'none'")
parser.add_argument("--threshold", type=float, default=0.15, help="minimum detection threshold to use") 

try:
    args = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

net = poseNet(args.network, sys.argv, args.threshold)
input = videoSource(args.input, argv=sys.argv)
output = videoOutput(args.output, argv=sys.argv)

csv_filename = save_csv_with_increment('pose_coordinates')
csv_file = open(csv_filename, 'w', newline='')
csv_writer = csv.writer(csv_file)

keypoints = [net.GetKeypointName(i) for i in range(net.GetNumKeypoints())]
header = ['Frame'] + keypoints
csv_writer.writerow(header)

frame_idx = 0

while True:
    img = input.Capture()
    if img is None:
        continue  

    poses = net.Process(img, overlay=args.overlay)
    row = [frame_idx]
    coordinates = [ None ] * net.GetNumKeypoints()

    for j,pose in enumerate(poses):
        for i in range(len(pose.Keypoints)):
            keypoint = pose.Keypoints[i]
            if keypoint:
                if coordinates[i] is None:
                    coordinates[i] = []
                coordinates[i].append([j, keypoint.x, keypoint.y])

    row.extend(coordinates)
    csv_writer.writerow(row)

    output.Render(img)
    output.SetStatus("{:s} | Network {:.0f} FPS".format(args.network, net.GetNetworkFPS()))
    net.PrintProfilerTimes()

    frame_idx += 1

    if not input.IsStreaming() or not output.IsStreaming():
        break

csv_file.close()
