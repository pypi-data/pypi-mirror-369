import sys
import clr
from System import Double, UInt16, Int32

from qcodes.instrument.parameter import Parameter
from qcodes.instrument.base import Instrument

# add .net reference and import so python can see .net

DEFAULT_PORT = 11000

class QDdotNET(Instrument):

    def __init__(
        self,
        name: str,
        ip_address: str,
        instruent_type = "DynaCool",
        remote: bool = False,
        QDInstrumentdir: str = "",
        QDInstrumentname: str = "QDInstrument",
        port = DEFAULT_PORT,
        **kwargs,
    ) -> None:
        super().__init__(name=name, **kwargs)

        clr.AddReference(QDInstrumentdir+QDInstrumentname)
        
        from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

        INST_MAP = {"PPMS": QDInstrumentBase.QDInstrumentType.PPMS, "DynaCool":  QDInstrumentBase.QDInstrumentType.DynaCool}

        self.QDIBase = QDInstrumentBase
        self.QDIFactory = QDInstrumentFactory
        try:
            self.device = QDInstrumentFactory.GetQDInstrument(INST_MAP[instruent_type], remote, ip_address, UInt16(port))
        except Exception:
            raise RuntimeError("Unsupported instrument_type")
        
        self.Brate = 100
        self.Trate = 10
        self.minimim_temperature = 1.8

        self.temperature: Parameter = self.add_parameter(
            name = "temperature",
            parameter_class=QDTemperature,
            label = "temperature",
            unit = "K"
        )

        self.temperaturestatus: Parameter = self.add_parameter(
            name = "temperaturestatus",
            parameter_class=QDTemperatureStatus,
            label = "temperaturestatus",
        )

        self.field: Parameter = self.add_parameter(
            name = "field",
            parameter_class = QDField,
            label = "field",
            unit = "T"
        )

        self.fieldstatus: Parameter = self.add_parameter(
            name = "fieldstatus",
            parameter_class = QDFieldStatus,
            label = "fieldstatus",
        )

        self.position: Parameter = self.add_parameter(
            name = "position",
            parameter_class = QDPosition,
            label = "position",
            unit = "deg"
        )

    def get_field(self):
        return self.device.GetField(Double(0), self.QDIBase.FieldStatus(Int32(0)))
    
    def set_field(self, field):
        if -90000 <= field <= 90000:
            return self.device.SetField(field, self.Brate, self.QDIBase.FieldApproach(Int32(0)), self.QDIBase.FieldMode(0))
        else:
            raise RuntimeError("Field is out of bounds. Should be between -90000 and 90000 Oe")

    def get_position(self):
        return float(str(self.device.GetPosition("Horizontal Rotator", 0, 0)))
    
    def set_position(self, position):
        return self.device.SetPosition("Horizontal Rotator", position, 0, 0)

    def set_temperature(self, temp):
        if self.minimim_temperature <= temp <= 350:
            return self.device.SetTemperature(temp, self.Trate, self.QDIBase.TemperatureApproach(Int32(0)))
        else:
            raise RuntimeError("Temperature is out of bounds. Should be between " + str(self.minimim_temperature) + " and 350 K")

    def get_temperature(self) -> float:
        error, temperature, status = self.device.GetTemperature(Double(0), self.QDIBase.TemperatureStatus(Int32(0)))
        return (error, temperature, status)

    def set_t_rate(self, rate: float):
        self.Trate = rate
    
    def set_b_rate(self, rate: float):
        self.Brate = rate

    def get_idn(self):
        return {
            "vendor": "Qauntum Design",
            "model": "PPMS3",
            "serial": self.serial,
            "firmware": None,
        }
    

class QDPosition(Parameter):
    """
    Parameter class for the motor position
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def set_raw(self, position: float) -> None:
        """Sets the motor position"""
        self.instrument.set_position(position)

    def get_raw(self) -> float:
        """Returns the motor position"""
        return self.instrument.get_position()


class QDTemperature(Parameter):
    """
    Parameter class for the temperature
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def set_raw(self, temperature: float) -> None:
        """Sets the temperature"""
        self.instrument.set_temperature(temperature)

    def get_raw(self) -> float:
        """Returns the temperature"""
        return self.instrument.get_temperature()[1]


class QDTemperatureStatus(Parameter):
    """
    Parameter class for the temperature
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def get_raw(self) -> float:
        """Returns the temperature"""
        return int(self.instrument.get_temperature()[2])



class QDField(Parameter):
    """
    Parameter class for the field
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def set_raw(self, mag: float) -> None:
        """Sets the magnetic field"""
        self.instrument.set_field(mag)

    def get_raw(self) -> float:
        """Returns the magnetic field"""
        return self.instrument.get_field()[1]


class QDFieldStatus(Parameter):
    """
    Parameter class for the field status
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def get_raw(self) -> float:
        """Returns the magnetic field"""
        return int(self.instrument.get_field()[2])