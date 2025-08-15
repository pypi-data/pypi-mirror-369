from pyPhasesRecordloader.recordLoaders.WFDBRecordLoader import WFDBRecordLoader


class RecordLoaderPhysio(WFDBRecordLoader):
    annotationExtension = "arousal"
