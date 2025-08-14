#%%
from pathlib import Path
import json
from typing import Union

class Configuration:
    def __init__(self,
                 telkey: str = None,
                 configpath: Union[Path, str] = Path(__file__).resolve().parent):
        self.telkey = telkey
        self.config = dict()

        # global config params
        self.path_config = Path(configpath)
        self.path_home = Path.home()
        self.path_base = Path(__file__).resolve().parent.parent
        self._configfiles_global = list(self.path_config.glob('*.config'))
        config_global = self._load_configuration(self._configfiles_global)
        self.config.update(config_global)

        if self.telkey:
            self.path_telescope = self.path_config / self.telkey
            self._configfiles_telescopes = list(self.path_telescope.glob('*.config'))
            if not self._configfiles_telescopes:
                print('No configuration file is found.\nTo make default configuration files, run tcspy.configuration.make_config')
            else:
                config_unit = self._load_configuration(self._configfiles_telescopes)
                self.config.update(config_unit)
                
    def initialize(self):
        """Initialize the configuration by creating necessary config files."""
        if not self.telkey:
            raise ValueError("Telescope key (telkey) must be provided to initialize configuration.")
        self._initialize_config()

    def _load_configuration(self, configfiles):
        all_config = dict()
        for configfile in configfiles:
            with open(configfile, 'r') as f:
                config = json.load(f)
                all_config.update(config)
        return all_config

    def _make_configfile(self, dict_params: dict, filename: str, savepath: Union[str, Path]):
        filepath = Path(savepath) / filename
        with open(filepath, 'w') as f:
            json.dump(dict_params, f, indent=4)
        print(f'New configuration file made: {filepath}')

    def _initialize_config(self):
        savepath_tel = self.path_telescope
        savepath_config = self.path_config

        savepath_tel.mkdir(parents=True, exist_ok=True)

        # LOCAL CONFIGURATION
        sex_config = dict(
            SEX_CONFIG = str(self.path_config / 'sextractor' / f'{self.telkey}.sexconfig'),
            SEX_CONFIGDIR = str(self.path_config / 'sextractor'),
            SEX_LOGDIR = str(self.path_home / 'code' / 'sextractor' / 'log'),
            SEX_HISTORYDIR = str(self.path_home / 'code' / 'sextractor' / 'history')
        )
        astrometry_config = dict(
            ASTROMETRY_SEXCONFIG = str(self.path_config / 'sextractor' / f'{self.telkey}.astrometry.sexconfig')
            )
        scamp_config = dict(
            SCAMP_CONFIG = str(self.path_config / 'scamp' / 'default.scampconfig'),
            SCAMP_SEXCONFIG = str(self.path_config / 'sextractor' / f'{self.telkey}.scamp.sexconfig'),
            SCAMP_CONFIGDIR = str(self.path_config / 'scamp'),
            SCAMP_LOGDIR = str(self.path_home / 'code' / 'scamp' / 'log'),
            SCAMP_HISTORYDIR = str(self.path_home / 'code' / 'scamp' / 'history')
        )
        swarp_config = dict(
            SWARP_CONFIG = str(self.path_config / 'swarp' / f'{self.telkey}.swarpconfig'),
            SWARP_CONFIGDIR = str(self.path_config / 'swarp'),
            SWARP_LOGDIR = str(self.path_home / 'code' / 'swarp' / 'log'),
            SWARP_HISTORYDIR = str(self.path_home / 'code' / 'swarp' / 'history')
        )
        psfex_config = dict(
            PSFEX_CONFIG = str(self.path_config / 'psfex' / 'default.psfexconfig'),
            PSFEX_SEXCONFIG = str(self.path_config / 'sextractor' / f'{self.telkey}.psfex.sexconfig'),
            PSFEX_CONFIGDIR = str(self.path_config / 'psfex'),
            PSFEX_LOGDIR = str(self.path_home / 'code' / 'psfex' / 'log'),
            PSFEX_HISTORYDIR = str(self.path_home / 'code' / 'psfex' / 'history')
        )
        
        for cfg, name in [
            (sex_config, 'sex.config'),
            (astrometry_config, 'astrometry.config'),
            (scamp_config, 'scamp.config'),
            (swarp_config, 'swarp.config'),
            (psfex_config, 'psfex.config')
        ]:
            self._make_configfile(cfg, name, savepath_tel)

        # GLOBAL CONFIGURATION
        calibdata_config = dict(
            CALIBDATA_DIR = str(self.path_home / 'data' / 'calibdata'),
            CALIBDATA_MASTERDIR = str(self.path_home / 'data' / 'mcalibdata'),
            )
        refdata_config = dict(
            REFDATA_DIR = str(self.path_home / 'data' / 'refdata'),
            )
        obsdata_config = dict(OBSDATA_DIR = str(self.path_home / 'data' / 'obsdata'))
        scidata_config = dict(SCIDATA_DIR = str(self.path_home / 'data' / 'scidata'))
        catalog_config = dict(CATALOG_DIR = str(self.path_base / 'skycatalog' / 'catalog_archive'))
        observatory_config = dict(
            OBSERVATORY_LOCATIONINFO = str(self.path_config / 'obs_location.txt'),
            OBSERVATORY_TELESCOPEINFO = str(self.path_config / 'CCD.txt')
        )
        sdtdata_config = dict(
            SDTDATA_OBSSOURCEDIR = '/data/data1/obsdata/',
            SDTDATA_OBSDESTDIR = str(self.path_home / 'data' / 'obsdata' / '7DT'),
            SDTDATA_SCISOURCEDIR = '/data/data1/processed_1x1_gain2750/',
            SDTDATA_SCIDESTDIR = str(self.path_home / 'data' / 'scidata' / '7DT' / '7DT_C361K_HIGH_1x1')
        )

        for cfg, name in [
            (calibdata_config, 'calibdata.config'),
            (refdata_config, 'refdata.config'),
            (scidata_config, 'scidata.config'),
            (catalog_config, 'catalog.config'),
            (observatory_config, 'observatory.config'),
            (sdtdata_config, 'sdtdata.config'),
            (obsdata_config, 'obsdata.config')
        ]:
            self._make_configfile(cfg, name, savepath_config)

        # Remove per-telescope specific keys before saving global versions
        sex_config.pop('SEX_CONFIG', None)
        scamp_config.pop('SCAMP_SEXCONFIG', None)
        swarp_config.pop('SWARP_CONFIG', None)
        psfex_config.pop('PSFEX_SEXCONFIG', None)

        for cfg, name in [
            (sex_config, 'sex.config'),
            (scamp_config, 'scamp.config'),
            (swarp_config, 'swarp.config'),
            (psfex_config, 'psfex.config'),
        ]:
            self._make_configfile(cfg, name, savepath_config)
#%%
if __name__ == '__main__':
    telescope_keys = [
        '7DT_C361K_HIGH_1x1', '7DT_C361K_HIGH_2x2', '7DT_C361K_LOW_1x1', '7DT_C361K_LOW_2x2',
        'CBNUO_STX16803_1x1', 'LSGT_SNUCAMII_1x1', 'LSGT_ASI1600MM_1x1',
        'RASA36_KL4040_HIGH_1x1', 'RASA36_KL4040_MERGE_1x1', 'SAO_C361K_1x1',
        'SOAO_FLI4K_1x1', 'KCT_STX16803_1x1', 'SkyMapper_SG_32_Det_1x1']
    
    for key in telescope_keys:
        print(key)
        config = Configuration(telkey=key, configpath = './ezphot')
        #config._initialize_config()
        print(config.config)

# %%
