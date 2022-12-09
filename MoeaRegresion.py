from BaseProblem import OptimProblem, ProductionRules
from TreeCreation import TreeIndividual
from reglasPoly import ReglasPolinomios
from numpy import genfromtxt
import os


class MoeaRegresion(OptimProblem):
    #Constructor
    def __init__(self, inputFile: str) -> None:
        super().__init__("regresión simbólica", ReglasPolinomios())

        if not os.path.isfile(inputFile):
            raise Exception(f"\nEl archivo '{inputFile}' de puntos NO existe.\n")

        # Leer el archivo de N puntos de la forma (X, Y)
        # Esto resultará en un arreglo de dimensión N x 2
        self.datos = genfromtxt(inputFile, delimiter=',')
