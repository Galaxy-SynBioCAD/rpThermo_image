#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Extract the sink from an SBML into RP2 friendly format

"""
import argparse
import tempfile
import os
import logging
import shutil
import docker


##
#
#
def main(inputfile, input_format, pathway_id, output):
    docker_client = docker.from_env()
    image_str = 'brsynth/rpthermo-standalone:dev'
    try:
        image = docker_client.images.get(image_str)
    except docker.errors.ImageNotFound:
        logging.warning('Could not find the image, trying to pull it')
        try:
            docker_client.images.pull(image_str)
            image = docker_client.images.get(image_str)
        except docker.errors.ImageNotFound:
            logging.error('Cannot pull image: '+str(image_str))
            exit(1)
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        shutil.copy(inputfile, tmpOutputFolder+'/input.dat')
        command = ['/home/tool_rpThermo.py',
                   '-input',
                   '/home/tmp_output/input.dat',
                   '-input_format',
                   str(input_format),
                   '-pathway_id',
                   str(pathway_id),
                   '-output',
                   '/home/tmp_output/output.dat']
        docker_client.containers.run(image_str, 
                command, 
                auto_remove=True, 
                detach=False, 
                volumes={tmpOutputFolder+'/': {'bind': '/home/tmp_output', 'mode': 'rw'}})
        shutil.copy(tmpOutputFolder+'/output.dat', output)


##
#
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Python wrapper to add cofactors to generate rpSBML collection')
    parser.add_argument('-input', type=str)
    parser.add_argument('-pathway_id', type=str, default='rp_pathway')
    parser.add_argument('-output', type=str)
    parser.add_argument('-input_format', type=str)
    params = parser.parse_args()
    main(params.input, params.input_format, params.pathway_id, params.output)