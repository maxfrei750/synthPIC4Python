#!/usr/bin/python

import sys
import getopt
import os
from setup_synthpic import get_blender_executable_path, download_blender, install_dependencies
from utilities import execute_and_print


def print_help():
    print("Usage:")
    print("render.py -s <scenefile> -r <recipefile>")
    print("render.py --scene <scenefile> --recipe <recipefile>")
    sys.exit(2)


def render(scene_path, recipe_path):
    recipe_path = os.path.abspath(recipe_path)
    scene_path = os.path.abspath(scene_path)

    assert os.path.exists(recipe_path), "Could not find recipe file {}".format(recipe_path)
    assert os.path.exists(scene_path), "Could not find scene file {}".format(scene_path)

    assert recipe_path.endswith(".py"), "Expected recipe file to be a .py file."
    assert scene_path.endswith(".blend"), "Expected scene file to be a .blend file."

    print("Rendering")
    print("Scene: {}".format(scene_path))
    print("Recipe: {}\n".format(recipe_path))

    blender_executable_path = get_blender_executable_path()

    if not os.path.isfile(blender_executable_path):
        print("Warning: Could not find blender in \n    {}\n".format(blender_executable_path))

        while True:
            answer = input("Do you want to download and set up blender automatically? [y/n]\n")

            if answer == "y":
                download_blender()
                install_dependencies()
                break
            elif answer == "n":
                print("Aborting.")
                sys.exit()

    execute_and_print(
        [blender_executable_path, scene_path, "--background", "--factory-startup", "--python", recipe_path])


def main(argv):
    recipe_path = None
    scene_path = None

    try:
        opts, args = getopt.getopt(argv, "hr:s:", ["help", "recipe=", "scene="])
    except getopt.GetoptError as err:
        print(err)
        print_help()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt in ("-r", "--recipe"):
            recipe_path = arg
        elif opt in ("-s", "--scene"):
            scene_path = arg

    assert recipe_path is not None, "No recipe path was specified. Type 'python render.py -h' for help."
    assert scene_path is not None, "No scene path was specified. Type 'python render.py -h' for help."

    render(scene_path, recipe_path)


if __name__ == "__main__":
    main(sys.argv[1:])
