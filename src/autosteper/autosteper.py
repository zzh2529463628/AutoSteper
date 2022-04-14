import os
import shutil
import pandas as pd
from autosteper.cage import Cage, name2seq
from autosteper.checker import Checker
from autosteper.generator import Generator
from autosteper.optimizers import *
from autosteper.tools import get_yes_info
from autosteper.path_parser import Path_Parser


class AutoSteper():
    def __init__(self, para: dict):
        self.cage = Cage(pristine_path=para['pristine_cage'], workbase=para['workbase'])
        self.generator = Generator(para['gen_para'])
        self.checker = Checker(chk_skin=self.generator.skin, group=self.generator.group, cage_size=self.cage.size)
        if para['opt_mode'] == 'xtb':
            self.optimizer = XTB_Optimizer(para['opt_para'], checker=self.checker, cage= self.cage)
        elif para['opt_mode'] == 'ase':
            self.optimizer = ASE_Optimizer(para['opt_para'], checker=self.checker, cage= self.cage)

        self.start = para['run_para']['start']
        self.stop = para['run_para']['stop']
        self.step = para['run_para']['step']
        self.cutoff_mode = para['run_para']['cutoff_mode']
        self.cutoff_rank = para['run_para']['cutoff_rank']
        self.cutoff_value = para['run_para']['cutoff_value']
        self.path_parser = Path_Parser(path_para=para['path_para'], step=self.step, workbase=para['workbase'], q_cage=self.cage, optimizer=self.optimizer)

    def _first_step(self):
        self.cage.set_add_num(self.start)
        gen_out_path = f'{self.cage.name}_{self.cage.add_num}_addons.out'
        self.generator.gen_seq(cage=self.cage,
                               gen_out_path=gen_out_path,
                               mode='base')
        self.optimizer.set_init_folders()
        self.generator.build(is_first=True,
                             gen_out_path=gen_out_path,
                             dump_folder=self.optimizer.path_raw_init,
                             cage=self.cage,
                             prev_xyz_path=self.cage.pristine_path)


        step_status = self.optimizer.opt()
        if step_status == 0:
            return 0
        else:
            self.prev_deep_yes = get_yes_info(opt_mode=self.optimizer.mode)
        return step_status

    def _take_a_step(self):
        def _step_unit():
            prev_xyz_path = prev_deep_yes['xyz_path'][idx]
            prev_name = prev_deep_yes['name'][idx]
            prev_seq, prev_addon_set = name2seq(name=prev_name, cage_size=self.cage.size)
            sub_nauty_o = os.path.join(sub_nauty_path, f'{prev_name}.out')
            self.generator.gen_seq(mode='step', cage=self.cage, gen_out_path=sub_nauty_o, prev_seq=prev_seq)
            self.all_parent_info = self.generator.build(is_first=False,
                                                        gen_out_path=sub_nauty_o,
                                                        dump_folder=self.optimizer.path_raw_init,
                                                        cage=self.cage,
                                                        prev_xyz_path=prev_xyz_path,
                                                        parent_info=self.all_parent_info,
                                                        prev_addon_set=prev_addon_set,
                                                        parent_name=prev_name
                                                        )

        self.cage.set_add_num(self.new_add_num)
        self.optimizer.set_init_folders()
        self.all_parent_info = {}
        sub_nauty_path = 'sub_nauty'
        os.makedirs(sub_nauty_path, exist_ok=True)

        prev_deep_yes = pd.read_pickle(self.prev_deep_yes)
        if self.cutoff_mode == 'rank':
            for idx in range(self.cutoff_rank):
                _step_unit()
        elif self.cutoff_mode == 'value_rank':
            lowest_e = prev_deep_yes['energy'][0]
            tracker = 0
            for idx, a_prev_energy in enumerate(prev_deep_yes['energy']):
                if a_prev_energy > lowest_e + self.cutoff_value:
                    break
                _step_unit()
                tracker += 1
                if tracker == self.cutoff_rank:
                    break
        elif self.cutoff_mode == 'value':
            lowest_e = prev_deep_yes['energy'][0]
            for a_prev_energy in prev_deep_yes['energy']:
                if a_prev_energy > lowest_e + self.cutoff_value:
                    break
                _step_unit()
        else:
            raise RuntimeError(f'The cutoff mode {self.cutoff_mode} is not supported in this program.')

        all_parent_info_df = pd.DataFrame(self.all_parent_info)
        all_parent_info_df.to_pickle('all_parent_info.pickle')

        step_status = self.optimizer.opt()
        self.prev_deep_yes = get_yes_info(opt_mode=self.optimizer.mode, all_parent_info=self.all_parent_info)
        return step_status

    def run(self):
        step_status = self._first_step()
        if step_status == 0:
            print("AutoSteper failed on first step.")
        else:
            while step_status != 0:
                self.new_add_num = self.cage.add_num + self.step
                if self.stop != None:
                    if self.new_add_num > self.stop:
                        print("Normal Termination of AutoSteper.")
                        break
                step_status = self._take_a_step()
                if step_status == 0:
                    print(f"AutoSteper failed after optimizing {self.cage.add_num} addon system.")
                    break





