from typing import Callable, Dict, Optional, List, Any
from functools import partial
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
# from multiprocessing import Pool
import subprocess
from .string_util import u_color, highlight_args


def run_cmd(cmd, verbose=False, shell=True):
    if verbose:
        # dbg(cmd, head="Run $")
        print(f"Run $ {cmd}")
    process = subprocess.Popen(cmd, shell=shell)
    process.wait()


def multi_wrapper(cmd_list, choice="thread", n=2, **kwargs):
    run_cmd_wrapper = partial(run_cmd, **kwargs)

    if choice in ["thread", "t", "th", "T", "threads"]:
        with ThreadPoolExecutor(max_workers=n) as executor:
            futures = [executor.submit(run_cmd_wrapper, cmd) for cmd in cmd_list]
            for future in futures:
                future.result()
    elif choice in ["process", "p", "pro", "P", "processes"]:
        with ProcessPoolExecutor(max_workers=n) as executor:
            futures = [executor.submit(run_cmd_wrapper, cmd) for cmd in cmd_list]
            for future in futures:
                future.result()
    # elif choice in ["pool", "po", "poo", "Pool"]:
    #     with Pool(processes=n) as pool:
    #         pool.map(run_cmd_wrapper, cmd_list)
    else:
        raise ValueError("Invalid choice")


def run_cmd_list(cmd_list: List[str], n: int = 1, choice="thread", confirm=None, **kwargs):
    if not cmd_list:
        print("Empty command list, nothing to execute")
        return
    if not confirm:
        print(f"\n{u_color('=== Command List Preview ===', 'bright_cyan')}")
        for i, cmd in enumerate(cmd_list):
            print(f"{str(i + 1) + '.'}", end=" ")
            print(highlight_args(cmd))

        print(f"\n{u_color('=== Statistics ===', 'cyan')}")
        print(f"{'Total commands:'} {str(len(cmd_list))}")

        mode_text = f"{'Batch (threads: ' + str(n) + ')' if n > 1 else 'Stream'}"
        print(f"{'Execution mode:'} {mode_text}")

        print(f"\n{'Execute these commands? (y/n):'} ", end="")
        confirmation = input().strip().lower()
        if confirmation not in ['y', 'yes', 'yep']:
            print("Execution canceled")
            return

    if n == 1:
        for cmd in cmd_list:
            print(f"Stream $ {cmd}")
            run_cmd(cmd, **kwargs)
    else:
        for cmd in cmd_list:
            print(f"Batch $ {cmd}")
        multi_wrapper(cmd_list=cmd_list, n=n, choice=choice, **kwargs)


def split_sequence(sequence, n=1):
    length = len(sequence)
    if n <= 0:
        return []
    if n == 1:
        return [sequence]
    if n >= length:
        return [[item] for item in sequence] + [[] for _ in range(n - length)]

    base_size = length // n
    remainder = length % n

    result = []
    start = 0
    for i in range(n):
        end = start + base_size + (1 if i < remainder else 0)
        result.append(sequence[start:end])
        start = end
    return result


def split_dict(dictionary, n=1):
    items = list(dictionary.items())
    length = len(items)

    if n <= 0:
        return []
    if n == 1:
        return [dictionary.copy()]
    if n >= length:
        result = [{k: v} for k, v in items]
        result.extend([{} for _ in range(n - length)])
        return result

    base_size = length // n
    remainder = length % n

    result = []
    start = 0
    for i in range(n):
        end = start + base_size + (1 if i < remainder else 0)
        part_dict = dict(items[start:end])
        result.append(part_dict)
        start = end
    return result


def make_args(arg_dict):
    args = []
    kwargs = {}
    pos_para = {}
    for key, value in arg_dict.items():
        if key.startswith("_") and key[1:].isdigit():
            index = int(key[1:])
            pos_para[index] = value
        else:
            kwargs[key] = value
    indices = sorted(pos_para.keys())
    for index in indices:
        args.append(pos_para[index])
    return args, kwargs


# outside executor
def _execute_function(serialized_func, args, kwargs):
    import cloudpickle
    func = cloudpickle.loads(serialized_func)
    result = func(*args, **kwargs)
    return result


def run_func(_func, choice="thread", n=1, paras=[], desc=">--RUN-FUNC--<"):
    from tqdm import tqdm
    tasks = [make_args(para) for para in paras]

    results = [None] * len(tasks)

    if choice in ["thread", "t", "th", "T", "threads"]:
        with ThreadPoolExecutor(max_workers=n) as executor:
            # futures = []
            # for args, kwargs in tasks:
            #     futures.append(executor.submit(_func, *args, **kwargs))
            # for future in futures:
            #     future.result()
            future2id = {executor.submit(_func, *args, **kwargs): i for i, (args, kwargs) in enumerate(tasks)}
            for future in tqdm(as_completed(future2id), total=len(tasks), desc=desc):
                task_id = future2id[future]
                results[task_id] = future.result()

    elif choice in ["process", "p", "pro", "P", "processes"]:
        import cloudpickle
        serialized_func = cloudpickle.dumps(_func)
        with ProcessPoolExecutor(max_workers=n) as executor:
            # futures = []
            # for args, kwargs in tasks:
            #     futures.append(executor.submit(_execute_function, serialized_func, args, kwargs))
            # for future in futures:
            #     future.result()

            future2id = {executor.submit(_execute_function, serialized_func, args, kwargs): i for i, (args, kwargs) in enumerate(tasks)}
            for future in tqdm(as_completed(future2id), total=len(tasks), desc=desc):
                task_id = future2id[future]
                results[task_id] = future.result()

    else:
        raise ValueError("Invalid choice")

    return results


# utils for CmdGen
def extract_value_split(cmd, key, mode):
    parts = cmd.split()
    key = mode + key
    if key in parts:
        return parts[parts.index(key) + 1]
    return ""


def sort_cmd_list(sort=None, cmd_list=None, mode=None):
    if isinstance(sort, list) or isinstance(sort, tuple):
        for item in sort:
            cmd_list.sort(key=lambda cmd: extract_value_split(cmd, item, mode))

    elif isinstance(sort, str):
        cmd_list.sort(key=lambda cmd: extract_value_split(cmd, sort, mode))


class CmdGen:
    def __init__(self, script="python run.py", mode="--", **kwargs):
        self.mode = mode
        self.script = script
        zip_params = {k: list(v) for k, v in kwargs.items() if isinstance(v, zip)}
        normal_params = {k: v for k, v in kwargs.items() if not isinstance(v, zip)}

        self._original_kwargs = {"normal_params": normal_params, "zip_params": zip_params}
        self._filter_conditions = {k: None for params_dict in self._original_kwargs.values() for k in params_dict}
        self.config_list = self._gen_config_list(self._original_kwargs)

    def _handle_normal_params(self, params) -> List[Dict]:
        if not params:
            return [{}]
        # items = sorted([(k, params[k] if isinstance(params[k], (list, tuple)) else [params[k]]) for k in params.keys()])
        # keys = [item[0] for item in items]
        # values = [item[1] for item in items]

        items = [(k, params[k] if isinstance(params[k], (list, tuple)) else [params[k]])
                 for k in params.keys()]
        keys = [item[0] for item in items]
        values = [item[1] for item in items]

        # Generate all combinations with parameters in alphabetical order
        configs = []
        from itertools import product
        for values_combo in product(*values):
            configs.append({k: v for k, v in zip(keys, values_combo)})

        return configs

    def _merge_zip_params(self, base_configs: List[Dict], zip_params: Dict) -> List[Dict]:
        if not zip_params:
            return base_configs
        zip_len = len(next(iter(zip_params.values())))
        if not base_configs:
            base_configs = [{}]

        # sorted_keys = sorted(zip_params.keys())
        keys = list(zip_params.keys())
        return [{**base, **{k: zip_params[k][i][0] for k in keys}}
                for base in base_configs
                for i in range(zip_len)]

    def _gen_config_list(self, kwargs) -> List[Dict]:
        normal_params = kwargs["normal_params"]
        zip_params = kwargs["zip_params"]

        config_list = self._handle_normal_params(normal_params)
        if zip_params:
            config_list = self._merge_zip_params(config_list, zip_params)
        return config_list

    def filter(self, **kwargs) -> 'CmdGen':
        for key, value in kwargs.items():
            if key not in self._filter_conditions:
                raise KeyError(f"Filter key '{key}' not found")
            self._filter_conditions[key] = (value if callable(value) or value is None
                                            else ([value] if not isinstance(value, (list, tuple))
                                                  else value))
        return self

    def _apply_filters(self, config: Dict[str, Any]) -> bool:
        for key, condition in self._filter_conditions.items():
            if condition is None or key not in config:
                continue
            value = config[key]
            if callable(condition):
                try:
                    if not condition(value):
                        return False
                except Exception as e:
                    raise ValueError(f"Filter function error for '{key}': {e}")
            elif value not in condition:
                return False
        return True

    def _format_cmd(self, config):
        cmd = self.script
        for k, v in config.items():
            if self.mode == "v":
                cmd += f" {v}"
            elif self.mode == "cli":
                k = k.replace("_", "-")
                cmd += f" {k} {v}"
            else:
                if isinstance(v, bool):
                    cmd += f" {self.mode}{k}" if v else ""
                else:
                    if isinstance(v, str):
                        cmd += f" {self.mode}{k} \"{v}\""
                    else:
                        cmd += f" {self.mode}{k} {v}"
        return cmd.strip()

    def add(self, **kwargs) -> 'CmdGen':
        for k, v in kwargs.items():
            if isinstance(v, zip):
                self._original_kwargs["zip_params"][k] = list(v)
            else:
                self._original_kwargs["normal_params"][k] = v
            self._filter_conditions.update({k: None for k in kwargs})
        self.config_list = self._gen_config_list(self._original_kwargs)
        return self

    def rm(self, *keys) -> 'CmdGen':
        for k in keys:
            if k in self._original_kwargs["normal_params"]:
                self._original_kwargs["normal_params"].pop(k, None)
            elif k in self._original_kwargs["zip_params"]:
                self._original_kwargs["zip_params"].pop(k, None)
            self._filter_conditions.pop(k, None)
        self.config_list = self._gen_config_list(self._original_kwargs)
        return self

    def reset(self) -> 'CmdGen':
        self._filter_conditions = {k: None for k in self._original_kwargs}
        return self

    def gen(self) -> List[str]:
        return [self._format_cmd(config)
                for config in self.config_list
                if self._apply_filters(config)]

    def cat(self, *genes: 'CmdGen', sep=" && ", sort=None) -> List[str]:
        self_list, self_mode = self.gen(), self.mode
        if sort: sort_cmd_list(sort, self_list, self_mode)
        if genes is None: return self_list

        other_lists, other_modes = [gene.gen() for gene in genes], [gene.mode for gene in genes]
        if sort: [sort_cmd_list(sort, cmd_list, mode) for cmd_list, mode in zip(other_lists, other_modes)]
        return [sep.join(z_cmd) for z_cmd in zip(self_list, *other_lists)]

    @classmethod
    def concat(cls, *genes: 'CmdGen', sep=" && ", sort=None) -> list[str]:
        cmd_lists = [gene.gen() for gene in genes]
        modes = [gene.mode for gene in genes]
        if sort: [sort_cmd_list(sort, cmd_list, mode) for cmd_list, mode in zip(cmd_lists, modes)]
        return [sep.join(z_cmd) for z_cmd in zip(*cmd_lists)]
