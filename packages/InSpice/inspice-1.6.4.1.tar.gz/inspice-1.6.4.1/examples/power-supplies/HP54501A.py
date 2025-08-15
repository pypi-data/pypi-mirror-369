####################################################################################################

from InSpice.Spice.Netlist import SubCircuitFactory
from InSpice.Unit import *

####################################################################################################

class HP54501A(SubCircuitFactory):

    NAME = 'HP54501A'
    NODES = ('line_plus', 'line_minus')

    ##############################################

    def __init__(self, diode_model):

        super().__init__()

        self.C(1, 'line_plus', 'line_minus', 1@u_uF)

        self.X('D1', diode_model, 'top', 'line_plus')
        self.X('D2', diode_model, 'line_plus', 'scope_ground')
        self.X('D3', diode_model, 'top', 'line_minus')
        self.X('D4', diode_model, 'line_minus', 'scope_ground')

        self.R(1, 'top', 'output', 10)
        self.C(2, 'output', 'scope_ground', 50@u_uF)
        self.R(2, 'output', 'scope_ground', 900@u_Ω)
