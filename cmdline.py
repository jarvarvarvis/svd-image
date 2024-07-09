import sys

def print_expected():
    print(f"Expected arguments: {sys.argv[0]} PATH [sv_percentage/sv_count] [SV_VALUE] [PRECISION] [aligned] [color/grayscale] OUT_PATH")

def get_command_line_args():
    # Check if the number of arguments is correct
    if len(sys.argv) < 7:
        print_expected()
        sys.exit(-1)

    args = {}
    args["path"] = sys.argv[1]

    args["sv_mode"] = sys.argv[2]
    if args["sv_mode"] != "sv_percentage" and args["sv_mode"] != "sv_count":
        print("Unexpected sv_mode:", args["sv_mode"])
        print_expected()
        sys.exit(-1)

    args["sv_value"] = float(sys.argv[3]) if args["sv_mode"] == "sv_percentage" else int(sys.argv[3])

    args["precision"] = int(sys.argv[4])
    args["bit_mode"] = sys.argv[5]
    if args["bit_mode"] != "aligned":
        print("Unexpected bit_mode:", args["bit_mode"])
        print_expected()
        sys.exit(-1)

    args["color_mode"] = sys.argv[6]
    if args["color_mode"] != "color" and args["color_mode"] != "grayscale":
        print("Unexpected color_mode:", args["color_mode"])
        print_expected()
        sys.exit(-1)

    args["out_path"] = sys.argv[7] if len(sys.argv) >= 8 else "svd-image.out"

    return args
