# Copyright (c) 2008 Pycircuit Development Team
# See LICENSE for details.

"""
Test n-port module

"""

from pycircuit.circuit.constants import *
from pycircuit.circuit.circuit import SubCircuit, R, gnd
from pycircuit.circuit.nport import NPort, NPortY, NPortZ, NPortA, NPortS

from math import sqrt
import numpy as npy
from numpy.testing import assert_array_almost_equal

## The test vehicle is a 1dB tee resistive attenuator
## designed for 50ohm matching impedance
## o---R1----*---R3---o
##           |
##          R2
##           |
## o---------*--------o
##
T = 290
R1, R3 = 3., 3.
R2 = 433.

cir = SubCircuit()
nin,n1,nout = cir.add_nodes('nin','n1','nout')
cir['R1'] = R(nin,n1,r=R1)
cir['R2'] = R(n1,gnd,r=R2)
cir['R3'] = R(nout,n1,r=R3)

# S,Z,Y-parameters
Sref = npy.array([[0.00219681, 0.88898926],[0.88898926, 0.00219681]])
Zref = npy.array([[R1+R2, R2],[R2, R2+R3]])
Yref = npy.linalg.inv(Zref)
Aref = npy.array([[-Yref[1,1]/Yref[1,0], -1/Yref[1,0]],
                  [Yref[0,1]-Yref[0,0]*Yref[1,1]/Yref[1,0], 
                   -Yref[0,0]/Yref[1,0]]])

## Using Bosma's theorem
CYref = 4 * kboltzmann * T * npy.real(Yref)
CZref = 4 * kboltzmann * T * npy.real(Zref)
E = npy.eye(2)
CSref =  kboltzmann * T * (E - npy.mat(Sref) * npy.mat(Sref).H)

## This correlation matrix was obtained from hand calculations by "moving" the noise sources
## to the source
CAref = 4*kboltzmann*T * npy.array([[R3*(1+R1/R2)**2 + R1 + R2*(R1/R2)**2,
                                     (R2*R3+R1*R3+R2*R1) / R2**2],
                                     [(R2*R3+R1*R3+R2*R1) / R2**2, (R2+R3)/R2**2,]])


def test_nport_from_nport():
    nport = NPortY(Yref, CYref)

    nporty = NPortY(nport)
    nportz = NPortZ(nport)
    nporta = NPortA(nport)
    nports = NPortS(nport)

    assert_array_almost_equal(nporty.Y.astype(float), Yref)

    assert_array_almost_equal(nportz.Z.astype(float), Zref, decimal=2)

    assert_array_almost_equal(nporta.A.astype(float), Aref, decimal=2)

    assert_array_almost_equal(nports.S.astype(float), Sref)

    assert_array_almost_equal(nporty.CY.astype(float), CYref, decimal=25)

    assert_array_almost_equal(nportz.CZ.astype(float), CZref, decimal=22)

    assert_array_almost_equal(nporta.CA.astype(float), CAref, decimal=25)

    assert_array_almost_equal(nports.CS.astype(float), CSref, decimal=25)
    

def test_nport_conversion():
    nports = NPortY(Yref, CYref), NPortZ(Zref, CZref), \
        NPortS(Sref, CSref), NPortA(Aref, CAref)

    for nport in nports:
        print "testing nport = " + str(nport)

        assert_array_almost_equal(nport.Y.astype(float), Yref)

        assert_array_almost_equal(nport.Z.astype(float), Zref, decimal=2)

        assert_array_almost_equal(nport.A.astype(float), Aref, decimal=2)

        assert_array_almost_equal(nport.S.astype(float), Sref)
        
        assert_array_almost_equal(nport.CY.astype(float), CYref, decimal=25)

        assert_array_almost_equal(nport.CZ.astype(float), CZref, decimal=22)
    
        assert_array_almost_equal(nport.CA.astype(float), CAref, decimal=25)

        assert_array_almost_equal(nport.CS.astype(float), CSref, decimal=25)


def test_passive():
    nports = NPortY(Yref), NPortZ(Zref), \
        NPortS(Sref), NPortA(Aref)

    for nport in nports:
        nport.passive = True
        noisynport = nport.noisy_nport()

        assert_array_almost_equal(noisynport.CY.astype(float), CYref)

    