from functools import partial
from qcodes import (VisaInstrument,
					validators as vals)
from qcodes.parameters import Parameter

import logging

log = logging.getLogger(__name__)


class Yokogawa7651(VisaInstrument):
	"""  
    QCoDeS driver for the Yokogawa 7651 I/V source.  

    Args:  
        VisaInstrument (_type_): _description_  

    Attributes:  
        voltage_range (Parameter):
			Set output voltage range in mV.  

        current_range (Parameter):
			Set output current range in mA.  

        voltage_limit (Parameter):
			Set output voltage limit in mV.  

        current_limit (Parameter):
			Set output current limit in mA. 

        voltage (Parameter):
			Set output voltage in mV.  

        current (Parameter):
			Set output current in mA.  

        output (Parameter):
			Output Status. ("on", "off")
    """  
	def __init__(self, name, address, **kwargs):
		# supplying the terminator means you don't need to remove it from every response
		super().__init__(name, address, terminator='\n', **kwargs)

		# init: crashes the I/O, clear from visa test panel fixes the issue
		# self.write('RC')

		
		self._status = {
			'mode': 'Voltage',
			'voltage_limit': None,
			'current_limit': None,
			'current': 0,
			'voltage': 0
			}
		''' 
			A Parameter object for the current output of the Yokogawa7651.

			Args:
				current: The current output of the Yokogawa7651. (mA)

			Returns:
				The current output of the Yokogawa7651. (mA)
		'''
		self.auto_current: Parameter = self.add_parameter(
            name="current",
            parameter_class=Y7651AutoCurrent,
            label="current",
            unit="mA",
        )

		self.auto_voltage: Parameter = self.add_parameter(
			name="voltage",
			parameter_class=Y7651AutoVoltage,
			label="voltage",
			unit="mV",
		)

		self.mode: Parameter = self.add_parameter(
			name="mode",
			parameter_class=Y7651Mode,
			label="mode",
		)

		self.voltage_range: Parameter = self.add_parameter(
			name = 'voltage_range',  
			label = 'Set the output voltage range in mV',
			vals = vals.Enum(10, 100, 1000, 10000, 30000),
			unit   = 'mV',
			set_cmd = partial(self._set_range, mode = "VOLT"),
			get_cmd = None
			)

		self.current_range: Parameter = self.add_parameter(
			name = 'current_range',  
			label = 'Set output current range in mA',
			vals = vals.Enum(1,10,100),
			unit   = 'A',
			set_cmd = partial(self._set_range, mode = "CURR"),
			get_cmd = None
			)

		self.voltage_limit: Parameter = self.add_parameter(
			name = 'voltage_limit',  
			label = 'Set output voltage limit in mV',
			vals = vals.Numbers(1000,30_000),
			unit   = 'mV',
			set_parser = self._div_1000_int,
			set_cmd = 'LV'+'{}'
			)

		self.current_limit: Parameter = self.add_parameter(
			name = 'current_limit',
			label = 'Set output current limit in mA',
			vals = vals.Numbers(5,120),
			unit   = 'A',
			set_parser = int,
			set_cmd = 'LA'+'{}')

		self.output = self.add_parameter(
			name = 'output',  
			label = 'Output State',
			set_cmd=lambda x: self.on() if x else self.off(),
			val_mapping={"off": 0, "on": 1,},
			)
	
	def on(self):
		self.write('O1E')
	
	def off(self):
		self.write('O0E')
	
	def _set_range(self, range:int, mode:str) -> None:
		if mode == "CURR":
			range_options = {1:"R4", 10:"R5", 100:"R6" }
			self.write('F5'+range_options[int(range)]+'E')
		elif mode == "VOLT":
			range_options = {10:"R2", 100:"R3", 1000:"R4", 10000:"R5", 30000:"R6" }
			self.write('F1'+range_options[int(range)]+'E')

	def _get_mode(self, status:str) -> str:
		if "F1R" in status:
			return "VOLT"
		elif "F5R" in status:
			return "CURR"
    
	def _get_range(self, status:str) -> int:
		if "F1R" in status:
			if "R2" in status:
				return 10
			elif "R3" in status:
				return 100
			elif "R4" in status:
				return 1000
			elif "R5" in status:
				return 10000
			elif "R6" in status:
				return 30000
		elif "F5R" in status:
			if "R4" in status:
				return 1
			elif "R5" in status:
				return 10
			elif "R6" in status:
				return 100

	def _volt_limit(self, status:str) -> int:
		if "LV" in status:
			return int(status[2:])

	def _curr_limit(self, status:str) -> int:
		if "LA" in status:
			return int(status[status.index("LA")+2:])

	def _get_status(self) -> None:
		status = self.ask('OS')
		slist = status.split()
		self.statusmap = {
			'mode': self._get_mode(slist[1]),
			'range': self._get_range(slist[1]),
			'voltage_limit': self._volt_limit(slist[3]),
			'current_limit': self._curr_limit(slist[3]),
			}

	def _div_1000_int(self,val):
		return int(val/1000)

	def _set_V(self,voltage):
		self._status['mode'] = 'Voltage'
		self._status['voltage'] = voltage
		if voltage>0:
			polarity = '+'
		else:
			polarity = '-'
		self.write('F1SA'+polarity+str(round(abs(voltage),6))+'E')

	def _set_A(self,current):
		self._status['mode'] = 'Current'
		self._status['current'] = current
		if current>0:
			polarity = '+'
		else:
			polarity = '-'
		self.write('F5SA'+polarity+str(round(abs(current),6))+'E')

	def initialize(self):
		self.write('RC')

	def reverse(self):
		self.write('RC')

	# To avoid identity query error
	def get_idn(self):
		return self.ask('OS')


class Y7651AutoCurrent(Parameter):
	def __init__(
        self,
        name: str,
        instrument: Yokogawa7651,
        **kwargs,) -> None:
		
		super().__init__(name, instrument=instrument, **kwargs)

	def get_raw(self):
		return self.instrument._status["current"]

	def set_raw(self, value):
		self.instrument._set_A(value)


class Y7651AutoVoltage(Parameter):
	def __init__(
		self,
		name: str,
		instrument: Yokogawa7651,
		**kwargs,) -> None:
		
		super().__init__(name, instrument=instrument, **kwargs)

	def get_raw(self):
		return self.instrument._status["voltage"]

	def set_raw(self, value):
		self.instrument._set_V(value)


class Y7651Mode(Parameter):
	def __init__(
		self,
		name: str,
		instrument: Yokogawa7651,
		**kwargs,) -> None:
		
		super().__init__(name, instrument=instrument, **kwargs)

	def get_raw(self):
		return self.instrument._status["mode"]

	def set_raw(self, value):
		if value == "Voltage":
			self.instrument.write('F1E')
		elif value == "Current":
			self.instrument.write('F5E')