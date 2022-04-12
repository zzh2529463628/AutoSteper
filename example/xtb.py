from autosteper.autosteper import AutoSteper


para = {
    'mode': 'xtb',
    'workbase': r'F:\autosteper\AutoSteper\example',
    'pristine_cage': r'F:\autosteper\AutoSteper\example\c50.xyz',

    'gen_para': {
        'gen_core_path': r"I:\new_nauty\my_v\usenauty\bin\cagesearch.exe",
        'geom_mode': 'pre_defined',
        'group': 'Cl',
        'skin': 0.15
    },
    'opt_para': {
        'xtb_path':  r'/home/mkliu/anaconda3/envs/env001/bin/xtb',
        'cmd_list': ['--opt', 'tight'],
        'out_list': ['xtbopt.xyz', 'xtbopt.log'],
        'is_Opt_Twice': True,
        'init_cycle': 15,
        'final_cycle': 100,
        'deal_wrong_mode': 'complete',
        'mach_para': {
            'batch_type': "Torque",
            'context_type': "SSHContext",
            'remote_root': '/home/mkliu/test_dpdispatcher/',
            'remote_profile': {
                "hostname": "219.245.39.76",
                "username": "mkliu",
                "password": "mkliu123",
                "port": 22,
                "timeout": 10
            }
        },
        'resrc_para': {
            'number_node': 2,
            'cpu_per_node': 8,
            'gpu_per_node': 0,
            'group_size': 1,
            'queue_name': "batch",
            'envs': {
                "OMP_STACKSIZE": "4G",
                "OMP_NUM_THREADS": "3,1",
                "OMP_MAX_ACTIVE_LEVELS": "1",
                "MKL_NUM_THREADS": "3"
            }
        },
        'sub_batch_size': 30
    },
    'run_para': {
        'start': 1,
        'step': 1,
        'stop': None,
        'cutoff_mode': 'value_rank',
        'cutoff_value': 0.037,
        'cutoff_rank': 200
    }

}


auto = AutoSteper(para)
auto.run()
