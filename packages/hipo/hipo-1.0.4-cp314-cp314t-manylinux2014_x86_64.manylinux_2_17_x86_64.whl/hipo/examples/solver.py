# solver.py
import hipo
import sys, re, os
#import json
import commentjson as json

fnA = sys.argv[1]
fnb = sys.argv[2]
config = sys.argv[3]

params = json.load(open(config))

A = hipo.ParCSRMatrix()
A.loadFromFile(fnA)
b = hipo.ParMatrix()
b.loadFromFile(fnb)
if b.getSize() == 0:
    b.resize(A.getRows(), 1)
    b.fill(1)

# transfer the matrix and vector to gpu 0.
dev = hipo.Device("cuda:0")
A = A.toDevice(dev)
b = b.toDevice(dev)

# use gpu 0 to finish the computation.
precond = hipo.createPrecond(params["preconditioner"])
precond.setup(A)
solver = hipo.createSolver(params["solver"])
solver.setup(A)

out = solver.solve(precond, A, b)
