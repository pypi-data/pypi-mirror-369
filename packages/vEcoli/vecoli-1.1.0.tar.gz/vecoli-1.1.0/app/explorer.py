import marimo

__generated_with = "0.14.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import json 
    from pathlib import Path 
    from typing import Callable
    import shutil

    import marimo as mo
    import polars as pl
    import duckdb as ddb
    import zipfile
    import orjson 
    return Callable, Path, json, mo, pl, shutil


@app.cell
def _():
    # distribution:

    # 1. map = get_mapping({objects: [processes_that_use_this_object]})
    # 2. for each object in map.keys(), run new process
    # 3. collect results
    return


@app.cell
def _(Path, shutil):
    output_dir = Path("out")
    user_output_dir = Path("simulation_outputs")
    for path in output_dir.iterdir():
        fname = path.name
        if 'kb' not in fname:
            shutil.copytree(src=path, dst=user_output_dir / fname, dirs_exist_ok=True)
        
    
    return (user_output_dir,)


@app.cell
def _(mo, user_output_dir):
    mo.vstack([mo.ui.file_browser(user_output_dir, label="Available simulation data")])
    return


@app.cell
def _(Callable, pl):
    # -- "API" --

    def get_simulation_output(
        experiment_id: str,
        observables: list[str] | None = None, 
        timepoints: tuple[int, int] | None = None,
        post_processor: Callable | None = None,
        variant_idx: int = 0,
        lineage_seed: int = 0,
        generation_idx: int = 1,
        agent_id: int = 0
    ) -> pl.DataFrame:
        experiment_dir = _get_experiment_dir(experiment_id=experiment_id)
        chunks_dir = _get_chunks_dir(experiment_dir, variant_idx, lineage_seed, generation_idx, agent_id)
        lf = _read_chunks(chunks_dir)
        return _get_data(lf=lf, observables=observables, timepoints=timepoints, post_processor=post_processor)
    return


@app.cell
def _(Callable, Path, json, pl):
    # -- Service -- 

    def _get_output_dir(config_fp: Path | None = None) -> Path:
        """Returns the absolute path of the output directory sepecified for the emitter arg in the associated
            simulation config.json file. Defaults to vEcoli/out.
        """
        if config_fp:
            with open(config_fp, 'r') as f:
                return Path(json.load(f)['emitter_arg']['out_dir']).absolute()
        return Path("out").absolute()

    def _get_experiment_dir(experiment_id: str, config_fp: Path | None = None) -> Path:
        """Simply returns out(outdir from config file)/<experiment_id>"""
        return _get_output_dir(config_fp) / experiment_id

    def _get_chunks_dir(
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
            / f"experiment_id={experiment_id}/" \
            / f"variant={variant_idx}" \
            / f"lineage_seed={lineage_seed}" \
            / f"generation={generation_idx}" \
            / f"agent_id={agent_id}"
        )

    def _read_chunks(chunks_dir: Path) -> pl.LazyFrame:
        """Returns a lazy polars dataframe representing a concatenation of all available simulation 
            parquet files.
        """
        return pl.scan_parquet(chunks_dir)

    def _get_data(
        lf: pl.LazyFrame, 
        observables: list[str] | None = None, 
        timepoints: tuple[int, int] | None = None,
        post_processor: Callable | None = None,
        **processor_kwargs
    ) -> pl.DataFrame:
        """Returns the result of lf.collect() for a given simulation output dataframe.

        :param lf: polars lazyframe created by scaning the hiveparitioned output dir.
        :param observables: list of observables (column names) to include within the in memory df. If this
            val is not none, pl.LazyFrame.select(*observables) will be called prior to collection.
        :param timepoints: timepoints by which to slice the df rows.
        :param post_processor: function to be run prior to collection.
        """
        cols = observables or ['*']
        rows = timepoints or (0, None)

        # TODO: if post_processor, do analysis on lf

        return lf.select(cols).slice(*rows).collect()




    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
