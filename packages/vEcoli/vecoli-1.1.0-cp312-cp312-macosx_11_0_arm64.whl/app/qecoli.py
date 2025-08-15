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
    return LoadSimData, Path, SimulationDataEcoli, mo, orjson, pl


@app.cell
def _(LoadSimData, Path, SimulationDataEcoli, orjson):
    def read_parameter_mapping(config_id):
        fp = Path("parameters") / f"{config_id}.json"
        with open(fp, 'rb') as f:
            return orjson.loads(f.read())

    def load_state(t: int = 2527):
        fp = Path(f"/Users/alexanderpatrie/Desktop/repos/ecoli/sms/vEcoli/data/vivecoli_t{t}.json")
        with open(fp, 'rb') as f:
            return orjson.loads(f.read())['agents']['0']

    def get_simdata_path(experiment_id: str) -> str:
            outdir = (Path(__file__).parent.parent / "out").absolute()
            return str(outdir / f"{experiment_id}/parca/kb/simData.cPickle")

    def load_simdata(experiment_id: str) -> SimulationDataEcoli:
        simdata_path = get_simdata_path(experiment_id)
        return LoadSimData(simdata_path).sim_data

    param_map = read_parameter_mapping("api_wf")
    state = load_state(2527)
    return


@app.cell
def _(Path, pl):
    import dataclasses as dc 
    from pennylane import qchem 
    import numpy as np

    @dc.dataclass
    class Formula:
        value: str

        @property
        def parts(self):
            import re
            return re.findall(r'[A-Z][a-z]?\d*', self.value)

    @dc.dataclass
    class Compound:
        id: str 
        formula: Formula 
        charge: int
        smiles: str
        xyz_dir: Path = Path("assets/compounds")

        @property
        def xyz_path(self):
            return (self.xyz_dir / f"{self.id}.xyz").absolute()

        def export(self):
            with open(self.xyz_path, 'w') as fil:
                fil.write(self.xyz)

        @property
        def xyz(self) -> "xyz":
            from rdkit import Chem
            from rdkit.Chem import AllChem

            name = self.id
            smiles = self.smiles
            mol = Chem.MolFromSmiles(smiles)
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol)
            AllChem.UFFOptimizeMolecule(mol)

            atoms = mol.GetAtoms()
            conf = mol.GetConformer()

            lines = [str(len(atoms)), name]
            a = []
            for atom in atoms:
                pos = conf.GetAtomPosition(atom.GetIdx())
                # a.append(f"")
                lines.append(f"{atom.GetSymbol()} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}")
            xyz = "\n".join(lines)
            return xyz

        def load_structure(self) -> tuple[list[str], np.ndarray[float]]:
            if not self.xyz_path.exists():
                self.export()

            xyz_path = str(self.xyz_path)
            return qchem.read_structure(xyz_path)

    def get_row(compound_id, df):
        for row in df.iter_rows():
            cid, formula, charge, smiles = row 
            if compound_id == cid:
                return Compound(id=cid, formula=Formula(value=formula), charge=charge, smiles=smiles)

    def get_compounds(fp: Path | None = None, export: bool = True):
        fp = fp or Path('reconstruction/ecoli/flat/metabolites.tsv')
        with open(fp, 'r', encoding='utf-8') as f:
            lines = [line for line in f if not line.startswith("#")]

        from io import StringIO
        import pandas as pd
        data_str = "".join(lines)
        dff = pd.read_csv(StringIO(data_str), sep="\t", quotechar='"')
        df = dff.loc[dff['chemical_formula'].notna(), ['id', 'chemical_formula', 'molecular_charge', '_smiles']]

        if export:
            df.to_csv("assets/compounds.tsv", sep='\t', index=False)
        return pl.DataFrame(df.to_dict())

    def load_compounds(fp: Path | None = None):
        fp = fp or Path("assets/compounds.tsv")
        if not fp.exists():
            return get_compounds(fp, export=True)
        return pl.read_csv(fp, separator='\t')

    return Compound, get_row, load_compounds, np, qchem


@app.cell
def _(get_row, load_compounds):
    compounds = load_compounds()
    compound_id = '--TRANS-ACENAPHTHENE-12-DIOL'
    compound_i = get_row(compound_id, compounds)
    return (compound_i,)


@app.cell
def _(Compound, qchem):
    import pickle 

    def load_molecule(compound: Compound):
        symbols, coordinates = compound.load_structure()
        return qchem.Molecule(symbols, coordinates, charge=compound.charge,  name=compound.id, unit='angstrom')

    class MolecularHamiltonian:
        __slots__ = ("molecule", "_remaining_electrons", "_H", "qubits", "_v")

        def __init__(self, source: qchem.Molecule | Compound):
            if isinstance(source, Compound):
                self.molecule = load_molecule(source)
            else:
                self.molecule = source 

            self._remaining_electrons = self.molecule.n_electrons

            self._H: bytes = None 
            self.qubits = None 

        def calculate(
            self, 
            active_orbitals: int | None = None, 
            active_electrons: int | None = None,
            solver: str = "pyscf"
        ) -> tuple:
            if active_orbitals and not active_electrons:
                active_electrons = 2 * active_orbitals

            if active_electrons is not None:
                self._remaining_electrons -= active_electrons

            if self._remaining_electrons < 0:
                print('There are no remaining electrons to be simulated!')
                return 

            self.H, self.qubits = qchem.molecular_hamiltonian(
                self.molecule, method=solver, active_orbitals=active_orbitals, active_electrons=active_electrons
            )

        @property 
        def H(self):
            if self._H is not None:
                return pickle.loads(self._H)
            return self._H

        @H.setter
        def H(self, H):
            self._H = pickle.dumps(H)


    def get_hamiltonian(compound: Compound, n_active_orbitals: int | None = None, n_active_electrons: int | None = None, initialize: bool = True) -> MolecularHamiltonian:
        H_m = MolecularHamiltonian(compound)
        if initialize:
            H_m.calculate(active_orbitals=n_active_orbitals, active_electrons=n_active_electrons)
        return H_m
    return MolecularHamiltonian, get_hamiltonian


@app.cell
def _(compound_i, get_hamiltonian):
    # 40 core electrons for 20 doubly-occupied orbitals
    n_core_orbitals = 20

    # 98 total electrons - 40 core = 58 electrons remaining
    # Perhaps we can start with a very small set of e/orbs?
    n_active_electrons = 8
    n_active_orbitals = 8

    H_i = get_hamiltonian(compound=compound_i, n_active_orbitals=n_active_orbitals, n_active_electrons=n_active_electrons)
    H = H_i.H
    qubits = H_i.qubits
    return H, H_i, n_active_orbitals, qubits


@app.cell
def _(H):
    dir(H)
    return


@app.cell
def _(H):
    dir(H.pauli_rep)
    return


@app.cell
def _(np, qml):
    class QuantumOscillator(qml.data.Dataset, data_name="quantum_oscillator", identifiers=["mass", "force_constant"]):
        """Dataset describing a quantum oscillator."""

        mass: float = qml.data.field(doc = "The mass of the particle")
        force_constant: float = qml.data.field(doc = "The force constant of the oscillator")
        hamiltonian: qml.Hamiltonian = qml.data.field(doc = "The hamiltonian of the particle")
        energy_levels: np.ndarray = qml.data.field(doc = "The first 1000 energy levels of the system")
    return


@app.cell
def _(MolecularHamiltonian, n_active_orbitals, np):
    import pennylane as qml 

    def create_dataset(H_m: MolecularHamiltonian, n_orbitals: int | None = None):
        H = H_m.H
        eigvals, eigvecs = np.linalg.eigh(qml.matrix(H))
        return qml.data.Dataset(
            data_name=f"{H_m.molecule.id}_{n_orbitals or n_active_orbitals}o",
            hamiltonian=H,
            energies=eigvals
        )
    return (qml,)


@app.cell
def _():
    # dataset_i = create_dataset(H_i, n_active_orbitals)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Generative Quantum Eigensolver (training)

    References:
    https://arxiv.org/abs/2401.09253
    https://pennylane.ai/qml/demos/gqe_training
    """
    )
    return


@app.cell
def _(np, qml):
    def generate_molecule_data(molecules="H2"):
        datasets = qml.data.load("qchem", molname=molecules)

        # Get the time set T
        op_times = np.sort(np.array([-2**k for k in range(1, 5)] + [2**k for k in range(1, 5)]) / 160)

        # Build operator set P for each molecule
        molecule_data = dict()
        for dataset in datasets:
            molecule = dataset.molecule
            num_electrons, num_qubits = molecule.n_electrons, 2 * molecule.n_orbitals
            singles, doubles = qml.qchem.excitations(num_electrons, num_qubits)
            double_excs = [qml.DoubleExcitation(time, wires=double) for double in doubles for time in op_times]
            single_excs = [qml.SingleExcitation(time, wires=single) for single in singles for time in op_times]
            identity_ops = [qml.exp(qml.I(range(num_qubits)), 1j*time) for time in op_times] # For Identity
            operator_pool = double_excs + single_excs + identity_ops
            molecule_data[dataset.molname] = {
                "op_pool": np.array(operator_pool),
                "num_qubits": num_qubits,
                "hf_state": dataset.hf_state,
                "hamiltonian": dataset.hamiltonian,
                "expected_ground_state_E": dataset.fci_energy
            }
        return molecule_data

    # molecule_data = generate_molecule_data("H2")
    # h2_data = molecule_data["H2"]
    # op_pool = h2_data["op_pool"]
    # num_qubits = h2_data["num_qubits"]
    # init_state = h2_data["hf_state"]
    # hamiltonian = h2_data["hamiltonian"]
    # grd_E = h2_data["expected_ground_state_E"]
    # op_pool_size = len(op_pool)


    return


@app.cell
def _():
    from pennylane import fermi 

    dir(fermi)
    return


@app.cell
def _(H_i):
    H_i.molecule.coordinates
    return


@app.cell
def _(H_i, qchem):
    h_fermi = qchem.fermionic_hamiltonian(H_i.molecule)()
    return


@app.cell
def _(H_i):
    H_i.molecule.symbols, H_i.molecule.coordinates.shape
    return


@app.cell
def _(H_i):
    H_i.molecule.coordinates.shape
    return


@app.cell
def _(qchem):
    dir(qchem.molecule)
    return


@app.cell
def _(H_i, qchem, qml, qubits):
    mol = H_i.molecule 
    wires = list(range(qubits))
    dev = qml.device("default.qubit", wires=qubits)

    # create all possible excitations in H3+
    singles, doubles = qchem.excitations(2, qubits)
    excitations = singles + doubles
    return dev, excitations, mol, wires


@app.cell
def _(H2mol, dev, excitations, qml, wf_hf, wires):
    @qml.qnode(dev)
    def circuit_VQE(theta, initial_state):
        qml.StatePrep(initial_state, wires=wires)
        for i, excitation in enumerate(excitations):
            if len(excitation) == 4:
                qml.DoubleExcitation(theta[i], wires=excitation)
            else:
                qml.SingleExcitation(theta[i], wires=excitation)
        return qml.expval(H2mol)


    def cost_fn(param):
        return circuit_VQE(param, initial_state=wf_hf)
    return (cost_fn,)


@app.cell
def _(mol, qml):
    from pennylane.qchem import import_state
    from pyscf import gto, scf, ci
    myhf = scf.UHF(mol).run()
    myci = ci.UCISD(myhf).run()
    wf_hf = qml.qchem.import_state(myci, tol=1e-1)
    return gto, wf_hf


@app.cell
def _(cost_fn, excitations):
    import optax
    import jax
    from jax import numpy as jnp
    jax.config.update("jax_enable_x64", True)

    opt = optax.sgd(learning_rate=0.4)  # sgd stands for StochasticGradientDescent
    theta = jnp.array(jnp.zeros(len(excitations)))
    delta_E, iteration = 10, 0
    results_hf = []
    opt_state = opt.init(theta)
    prev_energy = cost_fn(theta)

    # run the VQE optimization loop until convergence threshold is reached
    while abs(delta_E) > 1e-5:
        gradient = jax.grad(cost_fn)(theta)
        updates, opt_state = opt.update(gradient, opt_state)
        theta = optax.apply_updates(theta, updates)
        new_energy = cost_fn(theta)
        delta_E = new_energy - prev_energy
        prev_energy = new_energy
        results_hf.append(new_energy)
        if len(results_hf) % 5 == 0:
            print(f"Step = {len(results_hf)},  Energy = {new_energy:.6f} Ha")
    print(f"Starting with HF state took {len(results_hf)} iterations until convergence.")
    return


@app.cell
def _(gto):
    gto.M()

    return


@app.cell
def _(compound_i, gto):
    molec = gto.M(atom=str(compound_i.xyz_path))
    return


@app.cell
def _():
    # molec.build()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
