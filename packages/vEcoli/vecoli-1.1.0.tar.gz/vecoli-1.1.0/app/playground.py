import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import orjson
    import json
    import os
    from pathlib import Path 

    import requests
    import ijson
    import marimo as mo
    import polars as pl 
    import ray 
    from pydantic_settings import BaseSettings, SettingsConfigDict

    from ecoli.library.sim_data import LoadSimData
    from reconstruction.ecoli.simulation_data import SimulationDataEcoli
    return (
        BaseSettings,
        LoadSimData,
        Path,
        SettingsConfigDict,
        SimulationDataEcoli,
        json,
        mo,
        orjson,
        ray,
    )


@app.cell
def _(BaseSettings, Path, SettingsConfigDict, mo):
    # -- ui state hooks, env, and constraints -- 
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file='assets/.env', env_file_encoding='utf-8')
        biocyc_email: str = ""
        biocyc_password: str = ""

    def get_settings():
        return Settings()

    states_dir = Path("data").absolute()
    config_dir = Path("configs").absolute()
    output_dir = Path("out").absolute()

    get_selected_experiment, set_selected_experiment = mo.state(None)
    get_selected_state, set_selected_state = mo.state(None)
    return (
        config_dir,
        output_dir,
        set_selected_experiment,
        set_selected_state,
        states_dir,
    )


@app.cell
def _(
    Path,
    json,
    mo,
    output_dir,
    set_selected_experiment,
    set_selected_state,
    states_dir,
):
    # -- ui file selection and file utils --

    def get_available_experiments(output_dir: Path) -> list[str]:
        paths = []
        ids = []
        for fpath in output_dir.iterdir():
            if not fpath.name.startswith('kb') and fpath.is_dir():
                paths.append(fpath)
                ids.append(fpath.name)
        return dict(zip(ids, paths))

    def get_output_dir(config_fp: Path | None = None) -> Path:
        """Returns the absolute path of the output directory sepecified for the emitter arg in the associated
            simulation config.json file. Defaults to vEcoli/out.
        """
        if config_fp:
            with open(config_fp, 'r') as f:
                return Path(json.load(f)['emitter_arg']['out_dir']).absolute()
        return output_dir

    def get_experiment_dir(experiment_id: str, config_fp: Path | None = None) -> Path:
        """Simply returns out(outdir from config file)/<experiment_id>"""
        return get_output_dir(config_fp) / experiment_id

    def get_chunks_dir(
        experiment_dir: Path,
        variant_idx: int = 0,
        lineage_seed: int = 0,
        generation_idx: int = 1,
        agent_id: int = 0
    ) -> Path:
        """Returns the hive parition-formmated dirpath containing single simulation parquet files."""
        experiment_id = experiment_dir.parts[-1]
        return (
            experiment_dir \
            / "history" \
            / f"experiment_id={experiment_id}/" \
            / f"variant={variant_idx}" \
            / f"lineage_seed={lineage_seed}" \
            / f"generation={generation_idx}" \
            / f"agent_id={agent_id}"
        )

    def get_parquet_dir(expid: str) -> Path:
        pqdir = get_chunks_dir(get_experiment_dir(experiment_id=expid))
        if not pqdir.exists():
            raise FileNotFoundError(f"{pqdir.name} does not exist at: {pqdir.absolute()}")
        return pqdir.absolute()

    def on_select_experiment(selection: list[dict]):
        if len(selection):
            experiment_dir = selection[0]['value']
            chunks_dir = get_chunks_dir(experiment_dir)
            if not chunks_dir.exists():
                print(f'{chunks_dir} not existing...')
            set_selected_experiment(chunks_dir)
        else:
            set_selected_experiment(None)

    def get_available_states(states_dir: Path):
        states = {}
        for fpath in states_dir.iterdir():
            fname = fpath.name
            if fname.startswith('vivecoli') and fname.endswith('.json'):
                timestep_id = str(fname.split("_")[-1].replace('.json', '').replace('t', ''))
                states[timestep_id] = fpath 
        return states 

    def on_select_state(selection: list[dict]):
        if len(selection):
            set_selected_state(selection[0]['value'])
        else:
            set_selected_state(None)

    experiments_table = mo.ui.table(get_available_experiments(output_dir), on_change=lambda selection: on_select_experiment(selection))
    experiments_stack = mo.vstack([mo.md("#### Available Parquet Outputs (`/out`)"), experiments_table])

    states_table = mo.ui.table(get_available_states(states_dir), on_change=lambda selection: on_select_state(selection), show_column_summaries=False, show_data_types=False)
    states_stack = mo.vstack([mo.md("#### Available States (`/data`)"), states_table])
    return get_experiment_dir, get_parquet_dir


@app.cell
def _():
    # from pprint import pformat 

    # selections = {'experiment': get_selected_experiment(), 'state': get_selected_state()}
    # mo.vstack([mo.ui.text_area(f'Selections:\n{pformat(selections)}', disabled=True), experiments_stack, states_stack])
    return


@app.cell
def _(orjson, states_dir):
    # -- molecular hamiltonian encoding -- 

    def get_state(t: int) -> dict:
        state_fp = states_dir / f"vivecoli_t{t}.json"
        with open(state_fp, "rb") as f:  # must read as bytes
            data = orjson.loads(f.read())
        return data

    def flatten_keys(d, parent_key=''):
        keys = []
        for k, v in d.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                keys.extend(flatten_keys(v, full_key))
            else:
                keys.append(full_key)
        return keys

    def get_param_paths(d, parent_key=''):
        params = {}
        for k, v in d.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                # keys.extend()
                flatten_keys(v, full_key)
            else:
                params[full_key] = v
        return params


    def test_flatten_keys():
        x = {'a': 11.11, 'b': {'c': 22}, 'd': {'e': {'f': 3}}}
        keys = flatten_keys(x)
        assert keys == ['a', 'b.c', 'd.e.f']
    return


@app.cell
def _(
    LoadSimData,
    Path,
    SimulationDataEcoli,
    get_experiment_dir,
    get_parquet_dir,
    ray,
):
    # -- data service: dist and io -- 
    from contextlib import contextmanager

    from pyarrow import fs

    def get_excluded_outdirs(experiment_id: str) -> list[Path]:
        return [
            fpath for fpath in get_experiment_dir(experiment_id).iterdir() \
            if fpath.parts[-1] not in ["parca", "history"]
        ]

    def initialize_ray(experiment_id: str, **init_kwargs) -> "BaseContext":
        experiment_dir = get_experiment_dir(experiment_id=experiment_id)
        pq_dir = get_parquet_dir(expid=experiment_id)
        return ray.init(
            runtime_env={
                "working_dir": pq_dir,
                "excludes": get_excluded_outdirs(experiment_id)
            }
        )

    @contextmanager
    def rayinit(experiment_id: str, **init_kwargs):
        try:
            yield initialize_ray(experiment_id, **init_kwargs)
        finally:
            ray.shutdown()
            print('Ray has shutdown')

    def get_experiment_fs(experiment_id: str) -> tuple[fs.LocalFileSystem, Path]:
        chunks_dir = get_parquet_dir(experiment_id)
        filesys, pq_dir = fs.LocalFileSystem.from_uri(f"file://{chunks_dir}")
        return filesys, Path(pq_dir)

    def get_simdata_path(experiment_id: str) -> str:
        outdir = (Path(__file__).parent.parent / "out").absolute()
        return str(outdir / f"{experiment_id}/parca/kb/simData.cPickle")

    def load_simdata(experiment_id: str) -> SimulationDataEcoli:
        @ray.remote
        def _load_simdata(experiment_id: str) -> SimulationDataEcoli:
            # sim_data_path = f"/Users/alexanderpatrie/Desktop/repos/ecoli/sms/vEcoli/out/{experiment_id}/parca/kb/simData.cPickle"
            simdata_path = get_simdata_path(experiment_id)
            return LoadSimData(simdata_path).sim_data

        future = _load_simdata.remote(experiment_id)
        return ray.get(future)

    def load_results_dataset(
        experiment_id: str, 
        cols: list[str] | None = None, 
        concurrency: int | None = None,
        outfile_format: str = "pq"
    ) -> ray.data.Dataset:
        # get dedicated fs and pq dir
        experiment_fs, parquet_dir = get_experiment_fs(experiment_id)
        return ray.data.read_parquet(
            paths=[f"local://{f}" for f in parquet_dir.iterdir()], 
            file_extensions=[outfile_format], 
            concurrency=concurrency or 22, 
            columns=cols,
            filesystem=experiment_fs
        )

    def load_experimental_parameters(parameter_ids: list[str]):
        # loads actual ideal values from experiments for the ideal parameters
        # represents `s_exp`
        pass

    def get_initial_parameters(parameter_ids: list[str] = None):
        if parameter_ids:
            return load_experimental_parameters(parameter_ids)

        import numpy as np
        return {"p_a": float(np.random.random())}
    return load_simdata, rayinit


@app.cell
def _(Path, jnp, simulate):
    # -- forward-mode automatic differentiation solver -- 

    # ideally, you've performed sensitivity analysis and know the parameters you wish to optimize
    import typing
    import dataclasses as dc 
    from datetime import datetime 


    def timestamp() -> str:
        return str(datetime.now())


    # @ray.remote
    class Parameter:
        name: str
        last_updated: str | None = None
        _state: typing.Any | None = None

        def __init__(self, name: str, state: typing.Any | None = None):
            self.name = name
            if state is not None:
                self.set_state(state)

            self.last_updated = timestamp() 

        @classmethod
        def from_file(cls, reader: typing.Callable[[Path], None], *args):
            initial_state = reader(*args)
            cls.set_state(initial_state)

        def get_state(self):
            return self.state

        def set_state(self, s):
            self._state = s
            self.last_updated = timestamp()

        @property
        def state(self):
            return self._state

        @state.setter
        def state(self, s):
            raise Exception("Do not set this directly, rather via self.set_state(s)")

        def to_dict(self):
            return {
                'name': self.name,
                'state': self.get_state(),
                'last_updated': self.last_updated
            }

        def __repr__(self):
            return f"{self.to_dict()}"


    class Dual:
        """a + (b * e) where:
        a: real number 
        b: dual part (derivative)
        e: infintessimal such that e^2 = 0
        """
        def __init__(self, real, dual):
            self.real = real 
            self.dual = dual 

        def __add__(self, other):
            if (isinstance(other, Dual)):
                real = self.real + other.real
                dual = self.dual + other.dual 
                return Dual(real, dual)
            return Dual(self.real + other, self.dual)

        __radd__ = __add__

        def __mul__(self, other):
            if (isinstance(other, Dual)):
                real = self.real * other.real
                dual = self.dual * other.real + self.real * other.dual 
                return Dual(real, dual)
            return Dual(self.real * other, self.dual * other)

        __rmul__ = __mul__


    def apply_gradient(x_i, grad_i, lr=0.01):
        return x_i - lr * grad_i


    def oracle(x_i, desired_results):
        # params can be a vector of any length
        params_i = x_i
        results_i = simulate(*params_i)  # or however simulate expects them
        return jnp.sum((results_i - desired_results)**2)


    def diff(f: typing.Callable, x):
        """We need the following pieces of information to effectively use this outside of a ML context:

        A. x:
            A single simulation parameter (or set of parameters) that serves as a simulation input which, when correctly tuned, 
                yield some sort of desired outcome/state/behavior/geometry/trait, etc

        B. f(x, desired) -> Score:
            A function that takes sim parameters at iteration i, as well as the desired outcome/value for x, and serves to provide some heuristic/score/rating which describes how close in similarity
                the desired outcome from lab (state_exp) is from the simulated outcome (P_sim, which inherently ends up being
                a measure of the simulation/model quality.) Consider the following loss/objective function for this value: 

                def oracle(x_i, desired_results):
                    # params can be a vector of any length
                    params_i = x_i
                    results_i = simulate(*params_i)  # or however simulate expects them
                    return jnp.sum((results_i - desired_results)**2)

        C. desired_results:
            A final "state" which can be directly (1:1) compared to simulation results that in practice, can be reproduced 
                in lab guided directly from simulation outputs.
                Either:
                    1. A single simulation parameter (or set of parameters) which, when correctly tuned, 
                      yield some sort of desired outcome/state/behavior/geometry/trait, etc
                   Or(harder):
                    2. A desired outcome/state/behavior/geometry/trait that is observable/experience-able for which 
                      there are unknown linked/relevant parameters. You must determine the actively contributing parameters
                      mapped to this desired outcome, THEN simply feed it into #1.

        D. x_i:
            effectively, x

        E. apply_gradient(grad_i, x_i) -> x_next:
            A function whose inputs are (the output of this function (diff), params_i) and that applies the small, vectorized gradient to the actual param value which will serve as the passed value for the next iteration, essentially perturbing it in a particular direction. Consider the following:

                def apply_gradient(x_i, grad_i, lr=0.01):
                    return x_i - lr * grad_i

        """
        return f(Dual(x, 1)).dual

    return (Parameter,)


@app.cell
def _():
    # -- main: data inference and parallelization -- 

    experiment_id = "api_wf_20250729-184929"
    selected_observables = ["listeners__rnap_data__headon_collision_coordinates"]
    timestep_id = 2527
    return (experiment_id,)


@app.cell
def _(ray):
    ray.shutdown()
    return


@app.cell
def _(experiment_id, load_simdata, rayinit):
    # TODO: make ray ds out of the following parca outputs:
    # initialize_ray(experiment_id=experiment_id)
    # simdata = load_simdata(experiment_id)

    with rayinit(experiment_id=experiment_id) as init:
        simdata = load_simdata(experiment_id=experiment_id)
    return (simdata,)


@app.cell
def _(simdata):
    view_simdata = lambda: [attr for attr in dir(simdata) if not attr.startswith("_")]
    return


@app.cell
def _(simdata):
    simdata.doubling_time
    return


@app.cell
def _(Parameter, SimulationDataEcoli, simdata):
    x_conditions = simdata.conditions
    x_molecule_ids = simdata.molecule_ids
    x_growth_rate = simdata.growth_rate_parameters
    x_molecule_groups = simdata.molecule_groups
    x_rnap_per_cell = x_growth_rate.RNAP_per_cell

    def load_parameters(param_paths: list[str], sim_data: SimulationDataEcoli) -> dict[str, Parameter]:
        """
        :param param_paths: list of '.'-delimited paths in which the delimiting represents the 
            nesting structure as it pertains to accessing that parameter from simdata. For example, 
            the parameter 'RNAP_per_cell' would be represented as 'growth_rate_parameters.RNAP_per_cell'
        """
        import copy 

        selected = {}
        for path in param_paths:
            parts = path.split(".")
            param_name = parts[0]
            param_val = getattr(sim_data, param_name)
            parts.remove(param_name)
            if len(parts) > 1:
                for part in parts:
                    print(f'Extra part for {path}: {part}')
                    param_val = getattr(param_val, part)
                    param_name = part
            selected[path] = Parameter(name=param_name, state=param_val)
        return selected 
    return (load_parameters,)


@app.cell
def _(load_parameters, simdata):
    selected_param_paths = ["doubling_time", "growth_rate_parameters.RNAP_per_cell"]
    selected_params = load_parameters(selected_param_paths, simdata)
    selected_params
    return


@app.cell
def _():
    def get_dataclass_ids(simdata_dict):
        data_classes = []
        for k, v in simdata_dict.items():
            if hasattr(v, '__module__') and "doubling_time" not in k:
                data_classes.append(k)

        return set(data_classes)

    def dataclasses_to_dict(data_classes: set, simdata_dict: dict):
        for cls in data_classes:
            data_class = simdata_dict[cls].__dict__ 
            simdata_dict[cls] = data_class

    def serialize_simdata(simdata):
        simdata_dict = simdata.__dict__
        dcs = get_dataclass_ids(simdata_dict)
        dataclasses_to_dict(dcs, simdata_dict)
        print(simdata_dict.keys())
        return simdata_dict
    return


@app.cell
def _(Path, config_dir, json, orjson):
    from dataclasses import dataclass, make_dataclass, asdict
    import types 

    from ecoli.experiments.ecoli_master_sim import EcoliSim
        
                
    def get_config(config_id: str) -> dict:
        with open(config_dir / f"{config_id}.json", 'r') as fp:
            return json.load(fp)
        
    def get_process_parameters(config_id, simdata_path=None):
        config = get_config(config_id)
        sdpath = config.get('sim_data_path')
        if sdpath is None:
            assert simdata_path is not None, "You must provide a sim_data_path if passing a config that contains none."
            config['sim_data_path'] = simdata_path
        
        simulation = EcoliSim(config=config)
        simulation.build_ecoli()
        param_mapping = {}
        for pname, pdef in simulation.processes.items():
            param_mapping[pname] = pdef.defaults
        return param_mapping

    def invert(x: dict) -> dict:
        result = {}
        callables = []
        for outer_key, inner_dict in x.items():
            for inner_key in inner_dict:
                outer = x[outer_key]
                for k in outer.keys():
                    if isinstance(outer[k], types.LambdaType):
                        callables.append(k)
                result.setdefault(inner_key, []).append(outer_key)

        callable_params = set(callables)
        return result, callable_params

    def get_parameter_mapping(configid: str, sdatapath = "out/kb/simData.cPickle", export: bool = False):
        mapping, callables = invert(get_process_parameters(configid, sdatapath))
    
        param_map = {}
        for param_id, procs in mapping.items():
            processes = mapping[param_id]
            if param_id in callables:
                procs = []
                for process in processes:
                    procs.append(f'{process}(callable)')
                processes = procs
            param_map[param_id] = processes
        
        ppath = Path("parameters") / f"{configid}.json"
        if not ppath.exists() and export:
            with open(ppath, 'w') as fp:
                json.dump(param_map, fp, indent=4)
        return param_map

    class ParameterMapBase:
        def export(self, fp):
            with open(fp, 'wb') as f:
                f.write(orjson.dumps(self.to_dict()))

        def to_bytes(self):
            return orjson.dumps(self.to_dict())

        def to_dict(self):
            return asdict(self)

        def to_json(self):
            return self.to_bytes().decode()

    def parameter_mapping(config_id: str, use_slots: bool = True) -> 'ParameterMapping':
        name = 'ParameterMapping'
        field_dict = get_parameter_mapping(config_id)
        fields = [(key, type(value)) for key, value in field_dict.items()]
        cls = make_dataclass(name, fields, bases=(ParameterMapBase,), slots=use_slots)
        return cls(**field_dict)
    return (parameter_mapping,)


@app.cell
def _(parameter_mapping):
    configid = "api_wf"
    parameter_map = parameter_mapping(configid)
    return configid, parameter_map


@app.cell
def _(Path, configid, parameter_map):
    parameter_map.export(Path("parameters") / f"{configid}.json")
    return


@app.cell
def _(parameter_map):
    map_data = parameter_map.to_dict()
    rows = list(map_data.keys())
    cols = set()
    for param_id, processes in map_data.items():
        for proc in processes:
            cols.add(proc)
    return cols, rows


@app.cell
def _(cols, rows):
    dfdata = {col: [0 for row in set(rows)] for col in cols}
    dfdata
        
    return (dfdata,)


@app.cell
def _(dfdata, rows):
    import pandas as pd 
    pd.DataFrame(dfdata, index=list(set(rows)))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
