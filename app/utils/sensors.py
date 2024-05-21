from .mcp3008 import MCP3008 as MCP
import math

# Roof is ADC ch 0 and water is ADC ch 7
ROOF_SENSOR = 0
WATER_SENSOR = 7

class Sensors:
    """Main object which SETS and GETS the status of all onboard sensors"""
    def __init__(self):
        self.chip = MCP()

        self.temps = {0:[],1:[]} # 0 = water temp, 1 = roof temp
        self.water_temp = 0
        self.roof_temp = 0
    
    def refresh_temps(self):
        """This is run every second to update the current temps"""
        adcs = [self.chip.read(WATER_SENSOR), self.chip.read(ROOF_SENSOR)]

        i = 0 # i tracks which adc number we are on in the list
        for adc in adcs:
            if adc != 0:
                # Convert digital signal to K then to farenheight
                k = 1.0/(0.003354017+0.0002531646*math.log((1023/adc-1.0)))
                f = ((k-273.15) * 9/5) + 32
                # Add the new temp to the list of history
                self.temps[i].append(f)
                # If the hisotrical list is greater than 60, delete the first one (to keep us at 60 seconds of history per thermistor)
                if len(self.temps[i]) > 60:
                    del self.temps[i][0]
            i += 1
        # Now we average the list of temps from the first thermistor to give us the water temp (if we have a history to avg)
        if len(self.temps[0]) > 0:
            self.water_temp = sum(self.temps[0]) / len(self.temps[0])
        else:
            self.water_temp = 200 # Default to OFF if no water temp
        # Now we average the list of temps from the second thermistor to give us the roof temp (if we have a history to avg)
        if len(self.temps[1]) > 0:
            self.roof_temp = sum(self.temps[1]) / len(self.temps[1])
        else:
            self.roof_temp = -1 # Default to OFF if no roof temp

    def data(self):
        return {"water_temp": self.water_temp, "roof_temp": self.roof_temp}
    