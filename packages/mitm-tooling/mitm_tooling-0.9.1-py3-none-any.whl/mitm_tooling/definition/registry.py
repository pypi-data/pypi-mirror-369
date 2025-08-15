import logging
import pathlib

import yaml

from .definition_representation import MITM, MITMDefinition, MITMDefinitionFile

logger = logging.getLogger('api')

mitm_definitions: dict[MITM, MITMDefinition] = {}
mitm_definition_files = {MITM.MAED: 'maed.yaml', MITM.OCEL2: 'ocel2.yaml'}  # MITM.DPPD: 'dppd.yaml'


def load_definitions():
    for m, fn in mitm_definition_files.items():
        p = pathlib.Path(__file__).parent.joinpath(fn).resolve()

        with open(p) as f:
            yam = yaml.load(f, Loader=yaml.FullLoader)
            mitm_definitions[m] = MITMDefinitionFile.model_validate(yam).to_definition()

    with open(pathlib.Path(__file__).parent.joinpath('mitm-def-schema.yaml').resolve(), 'w') as f:
        yaml.dump(MITMDefinitionFile.model_json_schema(by_alias=True), f)


def get_mitm_def(mitm: MITM) -> MITMDefinition | None:
    if mitm not in mitm_definitions:
        logger.error(f'Attempted to access non-existent MITM definition: {mitm}.')
        return None
    return mitm_definitions[mitm]


load_definitions()
