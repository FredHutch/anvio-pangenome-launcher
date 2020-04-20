#!/usr/bin/env python3

from tkinter import *
from tkinter import filedialog, Tk, messagebox

import argparse
import atexit
import docker
import logging
import os
import sys
from time import sleep, time
import webbrowser


def find_anvio_db_files(root):
    """Ask the user to find the anvi'o DB input files."""
    root.filename =  filedialog.askopenfilename(
        initialdir = os.getcwd(),
        title = "Select anvi'o output file",
        filetypes = (
            ("db files","*.db"),
            ("all files", "*.*")
        )
    )
    # We're looking for two files, one ends with
    # -GENOMES.db, and the other ends with
    # -PAN.db
    is_genome_db = root.filename.endswith("-GENOMES.db")
    is_pan_db = root.filename.endswith("-PAN.db")
    if is_genome_db is False and is_pan_db is False:
        msg = "Expected a file ending with either -GENOMES.db or -PAN.db"
        messagebox.showinfo(
            "Error", 
            msg
        )
        assert False, msg

    elif is_genome_db:
        genome_db_fp = root.filename
        pan_db_fp = genome_db_fp.replace("-GENOMES.db", "-PAN.db")

        if os.path.exists(pan_db_fp) is False:
            msg = "Expected to find a file in the same folder ending with -PAN.db"
            messagebox.showinfo(
                "Error",
                msg
            )
            assert False, msg

    else:
        pan_db_fp = root.filename
        genome_db_fp = pan_db_fp.replace("-PAN.db", "-GENOMES.db")

        if os.path.exists(genome_db_fp) is False:
            msg = "Expected to find a file in the same folder ending with -GENOMES.db"
            messagebox.showinfo(
                "Error",
                msg
            )
            assert False, msg

    return genome_db_fp, pan_db_fp


def clean_up_containers(client, pause=5):
    """Remove any running containers."""

    # Get the list of running containers
    for container in client.containers.list():

        if container.status == "running":

            logging.info("Stopping running container: {} ({})".format(
                container.image,
                container.short_id
            ))

            # Issue the kill command
            container.kill()

            # Wait to let the container stop
            sleep(pause)


def check_for_docker_image(client, docker_image="meren/anvio:5.5"):
    """Make sure the appropriate Docker image is present."""

    # Pull the appropriate image
    client.images.pull(docker_image)


def launch_image(client, image, genome_db_fp, pan_db_fp):
    """Launch the image running anvi'o."""

    # Get the folder that the db files are in
    db_folder = os.path.dirname(genome_db_fp)

    # Get just the filename for both db files
    genome_db = os.path.basename(genome_db_fp)
    pan_db = os.path.basename(pan_db_fp)

    return client.containers.run(
        image,
        "anvi-display-pan -g /share/{} -p /share/{}".format(
            genome_db,
            pan_db
        ),
        auto_remove = True,
        detach = True,
        volumes = {
            db_folder: {
                'bind': '/share/', 
                'mode': 'rw'
            }
        },
        ports = {
            "8080/tcp": ("127.0.0.1", "80")
        }
    )


def wait_for_database(container, pause = 1, max_time = 600):
    """Wait for the anvi'o database to load inside the running container."""
    start_time = time()
    while (time() - start_time) < max_time:
        if "Gene clusters are initialized for all" in str(container.logs()):
            for _ in range(10):
                print(".", end="", flush=True)
                sleep(pause)
            print("")
            logging.info("Server is ready")
            return
        else:
            sleep(pause)
            print(".", end="", flush=True)
    msg = "Timed out after waiting {} seconds for the server to load".format(max_time)
    assert False, msg


def launch_browser():
    """Launch the web browser for anvi'o."""
    webbrowser.open('http://127.0.0.1:80', new=2)


if __name__ == "__main__":
    """Launch anvi'o in a browser for the user."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--image", 
        default = "meren/anvio:5.5",
        help = "Docker image to run"
    )
    args = parser.parse_args()

    # Set up the window system
    root = Tk()

    # Set up logging
    logFormatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s [Launch anvi'o] %(message)s"
    )
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    # Write to STDOUT
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    # Find the files to launch
    logging.info("Finding input files")

    try:
        genome_db_fp, pan_db_fp = find_anvio_db_files(root)
    except Exception as inst:
        logging.info("ANVIO LAUNCHER ENCOUNTERED AN ERROR")
        logging.info("----")
        logging.info("ERROR MESSAGE BELOW")
        logging.info("----")
        logging.info(inst)
        logging.info("----")
        input("Press Enter to close window...")
        exit()


    # Set up the Docker client
    try:
        docker_client = docker.from_env()
    except Exception as inst:
        logging.info("ANVIO LAUNCHER ENCOUNTERED AN ERROR")
        logging.info("----")
        logging.info("ERROR MESSAGE BELOW")
        logging.info("----")
        logging.info(inst)
        logging.info("----")
        input("Press Enter to close window...")
        exit()

    # Clean up any running containers using the port we need
    logging.info("Removing any running containers")
    try:
        clean_up_containers(docker_client)
    except Exception as inst:
        logging.info("ANVIO LAUNCHER ENCOUNTERED AN ERROR")
        logging.info("----")
        logging.info("ERROR MESSAGE BELOW")
        logging.info("----")
        logging.info(inst)
        logging.info("----")
        input("Press Enter to close window...")
        exit()

    # Make sure that we have the Docker image
    logging.info("Checking for Docker image")
    try:
        check_for_docker_image(
            docker_client, 
            docker_image = args.image
        )
    except Exception as inst:
        logging.info("ANVIO LAUNCHER ENCOUNTERED AN ERROR")
        logging.info("----")
        logging.info("ERROR MESSAGE BELOW")
        logging.info("----")
        logging.info(inst)
        logging.info("----")
        input("Press Enter to close window...")
        exit()

    logging.info("Launching Docker image")
    try:
        container = launch_image(
            docker_client, 
            args.image,
            genome_db_fp, 
            pan_db_fp
        )
    except Exception as inst:
        logging.info("ANVIO LAUNCHER ENCOUNTERED AN ERROR")
        logging.info("----")
        logging.info("ERROR MESSAGE BELOW")
        logging.info("----")
        logging.info(inst)
        logging.info("----")
        input("Press Enter to close window...")
        exit()

    # Make sure to kill the container when this task ends
    try:
        atexit.register(container.kill)
    except Exception as inst:
        logging.info("ANVIO LAUNCHER ENCOUNTERED AN ERROR")
        logging.info("----")
        logging.info("ERROR MESSAGE BELOW")
        logging.info("----")
        logging.info(inst)
        logging.info("----")
        input("Press Enter to close window...")
        exit()

    logging.info("Waiting for database to load")
    try:
        wait_for_database(container)
    except Exception as inst:
        logging.info("ANVIO LAUNCHER ENCOUNTERED AN ERROR")
        logging.info("----")
        logging.info("ERROR MESSAGE BELOW")
        logging.info("----")
        logging.info(inst)
        logging.info("----")
        input("Press Enter to close window...")
        exit()

    logging.info("Launching the browser")
    try:
        launch_browser()
    except Exception as inst:
        logging.info("ANVIO LAUNCHER ENCOUNTERED AN ERROR")
        logging.info("----")
        logging.info("ERROR MESSAGE BELOW")
        logging.info("----")
        logging.info(inst)
        logging.info("----")
        input("Press Enter to close window...")
        exit()

    logging.info("Close this window to shut down the server")

    # Print all of the output to the terminal
    for stdout in container.attach(stream = True):
        for line in stdout.decode('ascii').split("\r"):
            if len(line) > 0:
                logging.info(line)
