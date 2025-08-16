from pathlib import Path
from string import Template
from typing import Any, Optional

from amberflow.artifacts import (
    ArtifactContainer,
    BaseBinderStructureFile,
    BaseComplexTopologyFile,
    BaseBinderTopologyFile,
    ArtifactRegistry,
    BaseTargetStructureFile,
    BaseBinderLigandStructureFile,
    BaseTargetTopologyFile,
)
from amberflow.artifacts.structure import BaseComplexStructureFile, BaseTargetStructureReferenceFile
from amberflow.artifacts.topology import LigandLib, LigandFrcmod
from amberflow.primitives import (
    filepath_t,
    dirpath_t,
    DEFAULT_RESOURCES_PATH,
    WorkNodeRunningError,
)
from amberflow.worknodes import (
    noderesource,
    worknodehelper,
    BaseSingleWorkNode,
    TleapMixin,
    check_leap_log,
    TLeapSourcesGenerator,
)

__all__ = ("GenerateTopology",)


# noinspection DuplicatedCode
@noderesource(DEFAULT_RESOURCES_PATH / "tleap")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(
        BaseComplexStructureFile,
        BaseTargetStructureFile,
        BaseBinderStructureFile,
        LigandLib,
        LigandFrcmod,
    ),
    need_all_input_artifacts=False,
    output_artifact_types=(
        BaseComplexStructureFile,
        BaseComplexTopologyFile,
        BaseBinderStructureFile,
        BaseBinderTopologyFile,
        BaseTargetStructureReferenceFile,
        BaseTargetTopologyFile,
    ),
)
class GenerateTopology(BaseSingleWorkNode, TleapMixin):
    """
    GenerateTopologyComplex
    The stages of a tleap script are:
    1. Source leaprc files
    2. Load parameters for non-standard molecules (`loadamberparams`+`loadoff`)
    3. Load the main structure (`loadpdb`)
    4. Add box (with or without solvent molecules)
    5. Neutralize
    6. Output parm7+rst7

    (1), (4) and (5) are set by the user
    (2), (3) and (6) are controlled by the WorkNode
    """

    templates: tuple[str, ...] = (
        "leaprc",
        "load_nonstandard",
        "load_pdb",
        "neutralize_ions",
        "solvateoct",
        "save_amberparm",
        "quit",
    )

    # noinspection PyUnusedLocal
    def __init__(
        self,
        wnid: str,
        *args,
        water: str = "opc",
        force_field: str = "19SB",
        atom_type: str = "gaff2",
        box_or_oct: Optional[str] = None,
        neutralize=True,
        buffer: float = 0.0,
        closeness: float = 9999.0,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.sources = TLeapSourcesGenerator(
            force_field=force_field,
            atom_type=atom_type,
            water=water,
            ions="jc",
        )
        if box_or_oct is not None:
            if box_or_oct not in ("box", "oct"):
                raise ValueError(f"Invalid box_or_oct value: {box_or_oct}. Must be 'box' or 'oct'.")
        self.box_or_oct = box_or_oct
        self.buffer = buffer
        self.closeness = closeness
        self.neutralize = neutralize

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        system_type = self.validate()
        if self._try_and_skip(sysname, system_type=system_type):
            return self.output_artifacts

        tleap_script = self.generate_tleap(
            self.input_artifacts,
            self.sources,
            sysname,
            system_type,
            box_or_oct=self.box_or_oct,
            buffer=self.buffer,
            closeness=self.closeness,
            neutralize=self.neutralize,
        )
        # Write tleap script
        tleap_script_fn = self.work_dir / f"tleap_{self.__class__.__name__}_{sysname}.in"
        with open(tleap_script_fn, "w") as outfile:
            outfile.write(tleap_script)

        self.run_tleap(self.work_dir, tleap_script_fn, sysname, system_type)
        self.output_artifacts = self.fill_output_artifacts(sysname, system_type=system_type)

        return self.output_artifacts

    def validate(self) -> str:
        """
        Validates the input artifacts
        """
        has_complex = "BaseComplexStructureFile" in self.input_artifacts
        has_frcmod = "LigandFrcmod" in self.input_artifacts
        has_lib = "LigandLib" in self.input_artifacts
        has_target = "BaseTargetStructureFile" in self.input_artifacts
        has_binder = "BaseBinderLigandStructureFile" in self.input_artifacts

        if has_complex and has_frcmod and has_lib:
            return "complex"
        elif has_target and not has_complex:
            return "target"
        elif all([has_binder, has_frcmod, has_lib]) and not (has_complex or has_target):
            return "binder"
        else:
            err_msg = """Bad `input_artifacts`. Must be  one of the following:
                   - A BaseComplexStructureFile + LigandLib, LigandFrcmod
                   - A BinderStructureFile + LigandLib, LigandFrcmod
                   - A TargetStructureFile + optional LigandLib, LigandFrcmod"""
            self.node_logger.error(err_msg)
            raise ValueError(err_msg)

    @staticmethod
    def generate_tleap(
        input_artifacts: ArtifactContainer,
        sources: TLeapSourcesGenerator,
        sysname: str,
        system_type: str,
        *,
        box_or_oct: Optional[str] = None,
        buffer: float = 0.0,
        closeness: float = 9999.0,
        neutralize: bool = True,
    ) -> str:
        """
        Generates a tleap input script

        BUG: if you send multiple artifacts of the same type, it will only load the last one.
        I'm in a hurry, so I won't fix it now.
        """
        new_lines: list[str] = []

        # Load nonstandard params first, and respect the priority
        ligand_libs = sorted(
            [
                art
                for art_type, artifacts in input_artifacts.items()
                if issubclass(ArtifactRegistry.name[art_type], LigandLib)
                for art in artifacts
            ],
            key=lambda x: x.priority,
        )
        new_lines.extend([f"loadoff {lib.filepath}" for lib in ligand_libs])

        ligand_frcmods = sorted(
            [
                art
                for art_type, artifacts in input_artifacts.items()
                if issubclass(ArtifactRegistry.name[art_type], LigandFrcmod)
                for art in artifacts
            ],
            key=lambda x: x.priority,
        )
        new_lines.extend([f"loadamberparams {frcmod.filepath}" for frcmod in ligand_frcmods])

        for art_type, artifacts in input_artifacts.items():
            if issubclass(ArtifactRegistry.name[art_type], BaseComplexStructureFile):
                for art in artifacts:
                    new_lines.append(f"mol = loadpdb {art.filepath}")
            elif issubclass(ArtifactRegistry.name[art_type], BaseTargetStructureFile):
                for art in artifacts:
                    new_lines.append(f"mol = loadpdb {art.filepath}")
            elif issubclass(ArtifactRegistry.name[art_type], BaseBinderLigandStructureFile):
                for art in artifacts:
                    new_lines.append(f"mol = loadpdb {art.filepath}")
        if box_or_oct is not None:
            new_lines.append(f"solvate{box_or_oct} mol {sources['box']} {buffer} {closeness}")
        if neutralize:
            new_lines.append("addions2 mol Na+ 0")
            new_lines.append("addions2 mol Cl- 0")

        new_lines.append(f"saveamberparm mol {system_type}_{sysname}.parm7 {system_type}_{sysname}.rst7")
        return str(sources) + "\n".join(new_lines) + "\nquit\n"

    def run_tleap(self, output_dir: dirpath_t, tleap_script: filepath_t, sysname: str, system_type: str) -> None:
        logleap = "logleap"
        self.command.run(
            ["tleap", "-f", str(tleap_script), ">", logleap],
            cwd=output_dir,
            logger=self.node_logger,
            expected=(output_dir / f"{system_type}_{sysname}.parm7", output_dir / f"{system_type}_{sysname}.rst7"),
        )
        check_leap_log(output_dir / logleap, node_logger=self.node_logger)

    def _try_and_skip(self, sysname: str, *, system_type: str) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname, system_type=system_type)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except FileNotFoundError as e:
                self.node_logger.info(f"Can't skip {self.id}. Could not find file: {e}")
        return False

    def fill_output_artifacts(self, sysname: str, *, system_type: str) -> ArtifactContainer:
        """
        awful way of doing this.
        """
        if system_type == "complex":
            return ArtifactContainer(
                sysname,
                (
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.parm7",
                        tags=self.tags[self.artifact_map["BaseComplexStructureFile"]],
                    ),
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.rst7",
                        tags=self.tags[self.artifact_map["BaseComplexStructureFile"]],
                    ),
                ),
            )
        elif system_type == "target":
            return ArtifactContainer(
                sysname,
                (
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.parm7",
                        tags=self.tags[self.artifact_map["BaseTargetStructureFile"]],
                    ),
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.rst7",
                        tags=self.tags[self.artifact_map["BaseTargetStructureFile"]],
                    ),
                ),
            )
        elif system_type == "binder":
            return ArtifactContainer(
                sysname,
                (
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.parm7",
                        tags=self.tags[self.artifact_map["BaseBinderStructureFile"]],
                    ),
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.rst7",
                        tags=self.tags[self.artifact_map["BaseBinderStructureFile"]],
                    ),
                ),
            )
        else:
            raise WorkNodeRunningError("The system type is not recognized. This should not happen.")


#
# # noinspection DuplicatedCode
# @noderesource(DEFAULT_RESOURCES_PATH / "tleap")
# @worknodehelper(
#     file_exists=True,
#     input_artifact_types=(BaseComplexStructureFile, LigandLib, LigandFrcmod),
#     output_artifact_types=(BaseComplexStructureFile, BaseComplexTopologyFile),
# )
# class GenerateTopologyComplex(BaseSingleWorkNode, TleapMixin):
#     """
#     GenerateTopologyComplex
#     The stages of a tleap script are:
#     1. Source leaprc files
#     2. Load parameters for non-standard molecules (`loadamberparams`+`loadoff`)
#     3. Load the main structure (`loadpdb`)
#     4. Add box (with or without solvent molecules)
#     5. Neutralize
#     6. Output parm7+rst7
#
#     (1), (4) and (5) are directly controlled by the user
#     (2), (3) and (6) are controlled by the WorkNode
#
#     # user source leaprc?
#     'FRCMOD': "loadamberparams $FRCMOD",
#     'LIB': "loadoff $LIB",
#     'PDB': "mol = loadpdb $PDB",
#     # user neutralize?
#     # user solvate?
#     'SAVE': lambda data: TLeapSourcesGnerator._handle_save(data)
#     'QUIT; quit",
#
#     """
#     templates: tuple[str, ...] = ("leaprc", "load_nonstandard", "load_pdb", "neutralize_ions", "solvateoct",
#                                   "save_amberparm", "quit")
#
#     # noinspection PyUnusedLocal
#     def __init__(
#             self,
#             wnid: str,
#             *args,
#             boxshape: str = "truncated_octahedron",
#             solvent: str = "opc",
#             force_field: str = "19SB",
#             atom_type: str = "gaff2",
#             templates: Optional[tuple[str, ...]] = None,
#             **kwargs,
#     ) -> None:
#         super().__init__(
#             wnid=wnid,
#             *args,
#             **kwargs,
#         )
#         super().check_supported(solvent, "water")
#         self.solvent = solvent
#
#         super().check_supported(force_field, "force_field")
#         self.force_field = force_field
#
#         super().check_supported(atom_type, "atom_type")
#         self.atom_type = atom_type
#
#         super().check_supported(boxshape, "boxshape")
#         self.boxshape = boxshape
#
#         if templates is not None:
#             self.templates = templates
#         self.final_template = Template("".join([super().load_template(archivo).template for archivo in self.templates]))
#
#     def _run(
#             self,
#             *,
#             cwd: dirpath_t,
#             sysname: str,
#             binpath: Optional[filepath_t] = None,
#             **kwargs,
#     ) -> Any:
#         if self._try_and_skip(sysname):
#             return self.output_artifacts
#
#         in_pdb = Path(self.input_artifacts["ComplexProteinLigandPDB"])
#         tleap_script = self.write_tleap(
#             self.leaprc,
#             self.load_nonstandard,
#             self.load_pdb,
#             self.neutralize_ions,
#             self.save_amberparm,
#             cwd=self.work_dir,
#             in_pdb=in_pdb,
#             lig_lib=Path(self.input_artifacts["LigandLib"]),
#             lig_frcmod=Path(self.input_artifacts["LigandFrcmod"]),
#         )
#         self.run_tleap(self.work_dir, tleap_script, sysname)
#         self.output_artifacts = self.fill_output_artifacts(self.work_dir, sysname)
#
#         return self.output_artifacts
#
#     def run_tleap(self, output_dir: dirpath_t, tleap_script: filepath_t, sysname: str) -> None:
#         logleap = "logleap"
#         self.command.run(
#             ["tleap", "-f", str(tleap_script), ">", logleap],
#             cwd=output_dir,
#             logger=self.node_logger,
#             expected=(output_dir / f"complex_{sysname}.parm7", output_dir / f"complex_{sysname}.rst7"),
#         )
#         check_leap_log(output_dir / logleap, node_logger=self.node_logger)
#
#     def fill_output_artifacts(self, output_dir: dirpath_t, sysname: str) -> ArtifactContainer:
#         return ArtifactContainer(
#             sysname,
#             (
#                 ArtifactRegistry.create_instance_by_filename(
#                     output_dir / f"complex_{sysname}.parm7",
#                     tags=self.tags[self.artifact_map["BaseComplexStructureFile"]],
#                 ),
#                 ArtifactRegistry.create_instance_by_filename(
#                     output_dir / f"complex_{sysname}.rst7",
#                     tags=self.tags[self.artifact_map["BaseComplexStructureFile"]],
#                 ),
#             ),
#         )
#
#     def write_tleap(
#             self,
#             template_leaprc: str,
#             template_load_nonstandard: str,
#             template_load_pdb: str,
#             template_neutralize: str,
#             template_save_amberparm: str,
#             *,
#             cwd: dirpath_t,
#             in_pdb: Path,
#             lig_lib: Path,
#             lig_frcmod: Path,
#     ) -> Path:
#         """
#         Generates a tleap input script based on a template and writes it to a file sitting right next to the input PDB.
#         """
#
#         leaprc = super().load_file(
#             template_leaprc, {"SOLVENT_MODEL": self.solvent, "SBFF": self.force_field, "ATOM_TYPE": self.atom_type}
#         )
#         load_nonstandard = super().load_file(template_load_nonstandard, {"LIB": lig_lib, "FRCMOD": lig_frcmod})
#         load_pdb = super().load_file(template_load_pdb, {"PDB": in_pdb})
#         neutralize = super().load_file(template_neutralize)
#         if self.boxshape == "truncated_octahedron":
#             setbox = super().load_file(
#                 "solvateoct",
#                 {
#                     "SOLVENT_BOX_TYPE": super().SOLVENT_TO_BOX[self.solvent],
#                     "BOX_BUFFER_SIZE": "0",
#                     "CLOSENESS": "999.9",
#                 },
#             )
#         else:
#             setbox = super().load_file(
#                 "solvatebox",
#                 {
#                     "SOLVENT_BOX_TYPE": super().SOLVENT_TO_BOX[self.solvent],
#                     "BOX_BUFFER_SIZE": "0",
#                     "CLOSENESS": "999.9",
#                 },
#             )
#         save_amberparm = super().load_file(template_save_amberparm, {"TOPOLOGY": in_pdb.stem, "RESTART": in_pdb.stem})
#
#         # Join all sections
#         tleap_script = "".join([leaprc, load_nonstandard, load_pdb, neutralize, setbox, save_amberparm, "quit\n"])
#
#         # Write away
#         output_path = cwd / f"tleap_{self.__class__.__name__}_{in_pdb.stem}.in"
#         with open(output_path, "w") as outfile:
#             outfile.write(tleap_script)
#
#         return output_path
#
#     def _try_and_skip(self, sysname: str) -> bool:
#         if self.skippable:
#             try:
#                 self.output_artifacts = self.fill_output_artifacts(self.work_dir, sysname)
#                 self.node_logger.info(f"Skipped {self.id} WorkNode.")
#                 return True
#             except FileNotFoundError as e:
#                 self.node_logger.info(f"Can't skip {self.id}. Could not find file: {e}")
#         return False
#
#
# # noinspection DuplicatedCode
# @noderesource(DEFAULT_RESOURCES_PATH / "tleap")
# @worknodehelper(
#     file_exists=True,
#     input_artifact_types=(BaseBinderStructureFile, LigandLib, LigandFrcmod),
#     output_artifact_types=(BaseBinderStructureFile, BaseBinderTopologyFile),
# )
# class GenerateTopologyBinder(BaseSingleWorkNode, TleapMixin):
#     def __init__(
#             self,
#             wnid: str,
#             *args,
#             boxshape: str = "truncated_octahedron",
#             solvent: str = "opc",
#             force_field: str = "19SB",
#             atom_type: str = "gaff2",
#             debug: bool = True,
#             **kwargs,
#     ) -> None:
#         super().__init__(
#             wnid=wnid,
#             *args,
#             **kwargs,
#         )
#         super().check_supported(solvent, "water")
#         self.solvent = solvent
#
#         super().check_supported(force_field, "force_field")
#         self.force_field = force_field
#
#         super().check_supported(atom_type, "atom_type")
#         self.atom_type = atom_type
#
#         super().check_supported(boxshape, "boxshape")
#         self.boxshape = boxshape
#
#         # self.solvent_selection = f"(resname {watname} or resname HOH or name Na+ Cl-)"
#         self.debug = debug
#         self.tleap = None
#
#         self.out_dirs: list[Path] = []
#         self.binders = []
#         self.complexes = []
#
#     def _run(
#             self,
#             *,
#             cwd: dirpath_t,
#             sysname: str,
#             binpath: Optional[filepath_t] = None,
#             **kwargs,
#     ) -> Any:
#         if self._try_and_skip(sysname):
#             return self.output_artifacts
#
#         in_pdb = Path(self.input_artifacts["BinderLigandPDB"])
#         tleap_script = self.write_tleap(
#             self.leaprc,
#             self.load_nonstandard,
#             self.load_pdb,
#             self.neutralize_ions,
#             self.save_amberparm,
#             cwd=self.work_dir,
#             in_pdb=in_pdb,
#             lig_lib=Path(self.input_artifacts["LigandLib"]),
#             lig_frcmod=Path(self.input_artifacts["LigandFrcmod"]),
#         )
#         self.run_tleap(self.work_dir, tleap_script, sysname)
#         self.output_artifacts = self.fill_output_artifacts(self.work_dir, sysname)
#
#         return self.output_artifacts
#
#     def run_tleap(self, output_dir: dirpath_t, tleap_script: filepath_t, sysname: str) -> None:
#         logleap = "logleap"
#         self.command.run(
#             ["tleap", "-f", str(tleap_script), ">", logleap],
#             cwd=output_dir,
#             logger=self.node_logger,
#             expected=(output_dir / f"binder_{sysname}.parm7", output_dir / f"binder_{sysname}.rst7"),
#         )
#         check_leap_log(output_dir / logleap, node_logger=self.node_logger)
#
#     def fill_output_artifacts(self, output_dir: dirpath_t, sysname: str) -> ArtifactContainer:
#         return ArtifactContainer(
#             sysname,
#             (
#                 ArtifactRegistry.create_instance_by_filename(
#                     output_dir / f"binder_{sysname}.parm7", tags=self.tags[self.artifact_map["BaseBinderStructureFile"]]
#                 ),
#                 ArtifactRegistry.create_instance_by_filename(
#                     output_dir / f"binder_{sysname}.rst7", tags=self.tags[self.artifact_map["BaseBinderStructureFile"]]
#                 ),
#             ),
#         )
#
#     def write_tleap(
#             self,
#             template_leaprc: str,
#             template_load_nonstandard: str,
#             template_load_pdb: str,
#             template_neutralize: str,
#             template_save_amberparm: str,
#             *,
#             cwd: dirpath_t,
#             in_pdb: Path,
#             lig_lib: Path,
#             lig_frcmod: Path,
#     ) -> Path:
#         """
#         Generates a tleap input script based on a template and writes it to a file sitting right next to the input PDB.
#         """
#
#         leaprc = super().load_file(
#             template_leaprc, {"SOLVENT_MODEL": self.solvent, "SBFF": self.force_field, "ATOM_TYPE": self.atom_type}
#         )
#         load_nonstandard = super().load_file(template_load_nonstandard, {"LIB": lig_lib, "FRCMOD": lig_frcmod})
#         load_pdb = super().load_file(template_load_pdb, {"PDB": in_pdb})
#         neutralize = super().load_file(template_neutralize)
#         if self.boxshape == "truncated_octahedron":
#             setbox = super().load_file(
#                 "solvateoct",
#                 {
#                     "SOLVENT_BOX_TYPE": super().SOLVENT_TO_BOX[self.solvent],
#                     "BOX_BUFFER_SIZE": "0",
#                     "CLOSENESS": "999.9",
#                 },
#             )
#         else:
#             setbox = super().load_file(
#                 "solvatebox",
#                 {
#                     "SOLVENT_BOX_TYPE": super().SOLVENT_TO_BOX[self.solvent],
#                     "BOX_BUFFER_SIZE": "0",
#                     "CLOSENESS": "999.9",
#                 },
#             )
#         save_amberparm = super().load_file(template_save_amberparm, {"TOPOLOGY": in_pdb.stem, "RESTART": in_pdb.stem})
#
#         # Join all sections
#         tleap_script = "".join([leaprc, load_nonstandard, load_pdb, neutralize, setbox, save_amberparm, "quit\n"])
#
#         # Write away
#         output_path = cwd / f"tleap_{self.__class__.__name__}_{in_pdb.stem}.in"
#         with open(output_path, "w") as outfile:
#             outfile.write(tleap_script)
#
#         return output_path
#
#     def _try_and_skip(self, sysname: str) -> bool:
#         if self.skippable:
#             try:
#                 self.output_artifacts = self.fill_output_artifacts(self.work_dir, sysname)
#                 self.node_logger.info(f"Skipped {self.id} WorkNode.")
#                 return True
#             except FileNotFoundError as e:
#                 self.node_logger.info(f"Can't skip {self.id}. Could not find file: {e}")
#         return False
