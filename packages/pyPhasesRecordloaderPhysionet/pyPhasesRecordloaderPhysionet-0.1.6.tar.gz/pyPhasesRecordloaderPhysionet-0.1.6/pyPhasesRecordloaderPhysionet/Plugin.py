from pyPhases import PluginAdapter
from pyPhasesRecordloader import RecordLoader


class Plugin(PluginAdapter):
    def initPlugin(self):
        RecordLoader.registerRecordLoader(
            "RecordLoaderPhysio", "pyPhasesRecordloaderPhysionet.recordLoaders"
        )
        path = self.getConfig("physionet-path")
        self.project.setConfig("loader.physionet.filePath", f"{path}/training/")
