class TestSensor:
    """Main object which SETS and GETS the status of onboard sensor"""
    def __init__(self, channel):
        self.channel = channel
        self.temps = []
        self.history_length = 60
    
    def refresh_temp(self):
        """This is run every second to update the current temps"""
        # adc = self.chip.read(self.channel)

        # if adc != 0:
        #     # Convert digital signal to K then to farenheight
        #     k = 1.0/(0.003354017+0.0002531646*math.log((1023/adc-1.0)))
        #     f = ((k-273.15) * 9/5) + 32
        #     # Add the new temp to the list of history
        #     self.temps.append(f)
        #     # If the historical list is greater than 60, delete the first one (to keep us at 60 seconds of history per thermistor)
        #     if len(self.temps) > self.history_length:
        #         del self.temps[0]
        self.temps.append(50)
        # If the historical list is greater than 60, delete the first one (to keep us at 60 seconds of history per thermistor)
        if len(self.temps) > self.history_length:
            del self.temps[0]

    
    def temp(self):
        if len(self.temps) > 0:
            return sum(self.temps) / len(self.temps)
        else:
            return 0 # Default to 0 if no ADC
    