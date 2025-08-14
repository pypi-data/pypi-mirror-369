from .cr import CrConverter
from .ct import CTConverter, PCCTConverter, ScancoConverter
from .mese_siemens import MeSeConverterSiemensMagnitude
from .megre_siemens import MeGreConverterSiemensMagnitude, MeGreConverterSiemensPhase, MeGreConverterSiemensReal, \
    MeGreConverterSiemensImaginary, MeGreConverterSiemensReconstructedMap
from .dess_ge import DESSConverterGECombined, DESSConverterGEFid, DESSConverterGEEcho
from .mese_ge import MeSeConverterGEMagnitude
from .megre_ge import MeGreConverterGEMagnitude, MeGreConverterGEPhase, MeGreConverterGEReal, \
    MeGreConverterGEImaginary, MeGreConverterGEReconstructedMap
from .dess_siemens import DESSConverterSiemensMagnitude
from .mese_philips import MeSeConverterPhilipsMagnitude, MeSeConverterPhilipsPhase, MeSeConverterPhilipsReconstructedMap
from .megre_philips import MeGreConverterPhilipsMagnitude, MeGreConverterPhilipsPhase, MeGreConverterPhilipsReal, \
    MeGreConverterPhilipsImaginary, MeGreConverterPhilipsReconstructedMap
from .quantitative_maps import T1Converter, T2Converter, FFConverter, B0Converter, B1Converter

converter_list = [
    CrConverter,
    CTConverter,
    PCCTConverter,
    ScancoConverter,
    MeSeConverterSiemensMagnitude,
    MeGreConverterSiemensMagnitude,
    MeGreConverterSiemensPhase,
    MeGreConverterSiemensReal,
    MeGreConverterSiemensImaginary,
    MeGreConverterSiemensReconstructedMap,
    DESSConverterSiemensMagnitude,
    DESSConverterGECombined,
    DESSConverterGEFid,
    DESSConverterGEEcho,
    MeSeConverterGEMagnitude,
    MeGreConverterGEMagnitude,
    MeGreConverterGEPhase,
    MeGreConverterGEReal,
    MeGreConverterGEImaginary,
    MeGreConverterGEReconstructedMap,
    MeSeConverterPhilipsMagnitude,
    MeSeConverterPhilipsPhase,
    MeSeConverterPhilipsReconstructedMap,
    MeGreConverterPhilipsMagnitude,
    MeGreConverterPhilipsPhase,
    MeGreConverterPhilipsReal,
    MeGreConverterPhilipsImaginary,
    MeGreConverterPhilipsReconstructedMap,
]