import networkx as nx
from fullerenedatapraser.molecular.fullerene import FullereneFamily
from ase.io import read
import os
from ase.atoms import Atoms




class Cage():
    def __init__(self, pristine_path, workbase, add_num: int=None):
        self.pristine_path = pristine_path
        self.name, fmt = os.path.splitext(os.path.basename(pristine_path))
        self.workbase = os.path.join(workbase, self.name)
        os.makedirs(self.workbase, exist_ok=True)
        # parameter for standard name
        self.atoms = read(pristine_path, format=fmt[1:])
        self.centre = self.atoms.get_positions().mean(axis=0)
        self.size = len(self.atoms)
        self.max_add_36_size = len(to_36_base(int('1'*self.size, 2)))
        # graph6str
        self._get_graph6str()

    def _get_graph6str(self):
        f = FullereneFamily(spiral=0, atoms=self.atoms)
        self.graph6str = nx.to_graph6_bytes(f.graph, header=False).decode().split()[0]
        if os.name == 'posix':
            self.graph6str = self.graph6str.replace('`', '\\`')

    def set_add_num(self, add_num: int=None):
        self.add_num = add_num
        self.addon_path = os.path.join(self.workbase, f'{self.add_num}addons')
        os.makedirs(name=self.addon_path, exist_ok=True)
        os.chdir(self.addon_path)


def to_36_base(num):
  return ((num == 0) and "0") or (to_36_base(num // 36).lstrip("0") + "0123456789abcdefghijklmnopqrstuvwxyz"[num % 36])


def name2seq(name: str, cage_size: int):
    seq = str()
    addon_set = set()
    bin_str = format(int(name, 36), 'b')
    bin_str = '0' * (cage_size - len(bin_str)) + bin_str
    for idx, a_position in enumerate(bin_str):
        if a_position == '1':
            seq += str(idx) + ' '
            addon_set.add(idx)
    return seq, addon_set


def seq2name(seq: str, cage: Cage):
    addon_list = []
    bin_name = ['0'] * cage.size
    for i in seq.split():
        bin_name[int(i)] = '1'
        addon_list.append(int(i))
    bin_name_str = ''.join(bin_name)
    base_36_name = to_36_base(int(bin_name_str, 2))
    for i in range(cage.max_add_36_size - len(base_36_name)):
        base_36_name = '0' + base_36_name
    addon_set = set(addon_list)
    return base_36_name, addon_set
