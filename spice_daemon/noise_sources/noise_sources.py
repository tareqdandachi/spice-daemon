from ..yaml_interface import *
import numpy as np

class noise_sources(Element):
    
    def generate_asy_content(self, LIB_FILE, name, type="voltage"):
    
        if type=="current":
            accent = """LINE Normal 32 0 32 16
    LINE Normal 32 0 36 8
    LINE Normal 32 0 28 8"""
        elif type=="voltage":
            accent = """LINE Normal 32 0 32 8
    LINE Normal 28 4 36 4
    LINE Normal 28 16 36 16"""
        else: 
            raise TypeError
        
        return f"""Version 4
    SymbolType CELL
    LINE Normal 0 80 0 72
    {accent}
    LINE Normal 0 0 0 8
    CIRCLE Normal -32 8 32 72
    TEXT 0 40 Center 0 {name}
    SYMATTR Prefix X
    SYMATTR Description {type.lower()} noise source
    SYMATTR SpiceModel {name}
    SYMATTR ModelFile {LIB_FILE}
    PIN 0 0 NONE 8
    PINATTR PinName in
    PINATTR SpiceOrder 1
    PIN 0 80 NONE 8
    PINATTR PinName out
    PINATTR SpiceOrder 2
    """

    def lib_generator(self, NOISE_FILE_DEST_PREAMBLE, name, source_symbol="V"):
    
            return f""".subckt {name} in out

        ** NOISE SOURCE **
        {source_symbol} out in PWL file={NOISE_FILE_DEST_PREAMBLE}{name}.csv

        .ends {name}

        """
        
    def save_noise(self, NOISE_FILE_DEST_PREAMBLE, source_name, noise, t):

        with open(NOISE_FILE_DEST_PREAMBLE + source_name + ".csv", "w") as f:
        
            # set initial noise to zero to have a consistent DC operating point
            noise[0] = 0

            for i in range(0,len(t)):
                f.write("{:E}\t{:E}\n".format( t[i], noise[i] ))
                
            f.close()
        
    def update_PWL_file(self, NOISE_FILE_DEST_PREAMBLE, t):
        
        for source in self.source_data["sources"].keys():
                
            noise_data = self.source_data["sources"][source]["noise"]
            
            if noise_data["type"] == "gaussian":
                
                noise = np.random.normal(noise_data["mean"], noise_data["std"], len(t))
                
                self.save_noise(NOISE_FILE_DEST_PREAMBLE, source, noise, t)
                
            elif noise_data["type"] == "poisson":
                
                noise = noise_data["scale"] * np.random.poisson(noise_data["lambda"], len(t))
                
                self.save_noise(NOISE_FILE_DEST_PREAMBLE, source, noise, t)
                
            elif noise_data["type"] == "one_over_f":
                
                noise = noise_data["scale"] * cn.powerlaw_psd_gaussian(noise_data["power"], len(t), fmin=noise_data["fmin"])
                
                self.save_noise(NOISE_FILE_DEST_PREAMBLE, source, noise, t)
                
            elif noise_data["type"] == "custom":
                
                N = len(t)
            
                noise = eval(noise_data["command"])
                
                self.save_noise(NOISE_FILE_DEST_PREAMBLE, source, noise, t)
            
            else:
                print("Wrong noise type defined in .yaml file")
                raise TypeError