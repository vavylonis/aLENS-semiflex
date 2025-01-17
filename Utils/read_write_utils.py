"""@package docstring
File: read_write_utils.py
Author: Adam Lamson
Email: alamson@flatironinstitute.org
Description: Commonly used functions to read in and out aLENS files
"""
from copy import deepcopy
import numpy as np


def get_file_number(path):
    name = path.stem
    num = name.split("_")[-1]
    return int(num)


def gen_id(i=0):
    """Generates sequence of ids that are only used once
    @param i Starting id to use
    @return: Generator for ids that always increase by one


    """
    while True:
        yield i
        i += 1


class Sylinder():

    def __init__(self, line):
        data = line.split()
        self.type = data[0]
        if self.type == 'L':
            return Link
        self.gid = data[1]
        dat = np.asarray(data[2:], dtype=np.double)
        self.radius = dat[0]
        self.start_pos = dat[1:4]
        self.end_pos = dat[4:7]
        self.grp_id = data[-1]

        self.vec = self.end_pos - self.start_pos

    def get_str_to_write(self):
        return '{0} {1} {2} {3:0.6f} {4:0.6f} {5:0.6f} {6:0.6f} {7:0.6f} {8:0.6f} {9}\n'.format(
            self.type, self.gid, self.radius,
            self.start_pos[0], self.start_pos[1], self.start_pos[2],
            self.end_pos[0], self.end_pos[1], self.end_pos[2],
            self.grp_id)

    def get_com(self):
        return .5 * (self.end_pos + self.start_pos)


class Particle(Sylinder):

    """Stores information about each filament segment including position, gid,
    filament group, and connecting segments. """

    def __init__(self, start_pos, director, length, radius, grp_id, gid,
                 seg_type='C'):
        self.start_pos = deepcopy(start_pos)
        self.director = deepcopy(director)
        self.director /= np.linalg.norm(self.director)
        self.length = length
        self.radius = radius
        self.end_pos = length * self.director + start_pos
        self.grp_id = grp_id
        self.gid = gid
        self.type = seg_type


class Protein():

    """Docstring for Protein. """

    def __init__(self, gid, ptype, end0_pos, end1_pos, end0_gid, end1_gid):
        """Stores information about each protein.

        @param

        """
        self.gid = gid
        self.ptype = ptype
        self.end0_pos = end0_pos
        self.end1_pos = end1_pos
        self.end0_gid = end0_gid
        self.end1_gid = end1_gid

    def get_str_to_write(self):
        return 'P {0} {1} {2:0.6f} {3:0.6f} {4:0.6f} {5:0.6f} {6:0.6f} {7:0.6f} {8} {9}\n'.format(
            self.gid, self.ptype,
            self.end0_pos[0], self.end0_pos[1], self.end0_pos[2],
            self.end1_pos[0], self.end1_pos[1], self.end1_pos[2],
            self.end0_gid, self.end1_gid)


class ProteinAscii(Protein):

    """Docstring for ProteinAscii. """

    def __init__(self, line):
        """Stores information about each protein.

        @param line TODO

        """
        data = line.split()
        Protein.__init__(self, int(data[1]), int(data[2]),
                         list(map(float, data[3:6])),
                         list(map(float, data[6:9])),
                         int(data[9]), int(data[10]))


class Force():

    def __init__(self, line):
        data = line.split()
        self.pos = np.asarray(data[0:3])
        self.force = np.asarray(data[3:6])
        self.radius = data[-1]


class Link():

    """Spring-like link between filament"""

    def __init__(self, line):
        """Initialize with the ids of the two objects to connect

        @param prev_id First object to connect
        @param next_id Second object to connect

        """
        data = line.split()

        self._prev_id = int(data[1])
        self._next_id = int(data[2])

    def get_str_to_write(self):
        """Return string that defines link"""
        return f'L {self._prev_id} {self._next_id}\n'


def read_sylinder_ascii_file(fpath):
    with fpath.open('r') as file1:
        filecontent = file1.readlines()
        # Delete the first two lines because they dont have any data
        filecontent[0:2] = []
        # Create list of particles
        particles = sorted([Sylinder(line)
                            for line in filecontent
                            if line.split()[0] != 'L'],
                           key=lambda x: int(x.gid))
    return particles


def read_protein_ascii_file(fpath):
    with fpath.open('r') as file1:
        filecontent = file1.readlines()
        # Delete the first two lines because they dont have any data
        filecontent[0:2] = []
        # Create list of particles
        particles = sorted([ProteinAscii(line)
                            for line in filecontent],
                           key=lambda x: int(x.gid))
    return particles


def read_links_ascii_file(fpath):
    with fpath.open('r') as file1:
        filecontent = file1.readlines()
        # Delete the first two lines because they dont have any data
        filecontent[0:2] = []
        # Create list of links
        links = [Link(line) for line in filecontent if line.split()[0] == 'L']
    return links


def read_force_file(fpath):
    with fpath.open('r') as file1:
        filecontent = file1.readlines()
        # Delete the first two lines because they dont have any data
        filecontent[0:2] = []
        # Create list of forces
        forces = [Force(line) for line in filecontent]

    return forces


def get_sorted_dat_paths(
        result_dir, particle_type='SylinderAscii', file_type='dat'):
    return sorted(result_dir.glob(f"**/{particle_type}*.{file_type}"),
                  key=get_file_number)
