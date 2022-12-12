from typing import List

from BaseProblem import OptimProblem, ProductionRules
from TreeCreation import TreeIndividual
from reglasPoly import ReglasPolinomios
from numpy import genfromtxt
import os


class MoeaRegresion(OptimProblem):
    # Constructor
    def __init__(self, inputFile: str) -> None:
        super().__init__("regresión simbólica", ReglasPolinomios())
        self.numObjectives = 2
        if not os.path.isfile(inputFile):
            raise Exception(f"\nEl archivo '{inputFile}' de puntos NO existe.\n")

        # Leer el archivo de N puntos de la forma (X, Y)
        # Esto resultará en un arreglo de dimensión N x 2
        self.datos = genfromtxt(inputFile, delimiter=',')

    # Esta función evalúa un vector de valores del individuo para
    # Regresar un escalar de tipo flotante
    # Esta función es parecida a la función evaluateProgram de ProblemaRegresion
    # Pero se añade el tamaño de los árboles al final.
    def evaluateProgram(self, program: TreeIndividual) -> List[float]:
        # Calcular el error cuadrado medio. Es decir, la desviación
        # de los puntos históricos de la predicción del modelo.
        # El modelo es el árbol 'program'.

        errorCuadrado = 0
        for punto in self.datos:
            x = punto[0]  # Este es el punto x de nuestros datos históricos
            y = punto[1]

            # Calcular predicción usando el modelo que vive en el árbol.
            yEstimada = program.evaluateTree(x)
            # print(f"x={x}, y={y}, p(x)=y'={yEstimada}")

            # Acumular la diferencia entre el valor y histórico y el estimado yEst.
            errorCuadrado += (y - yEstimada) ** 2

        # El error cuadrado medio es lo que queremos minimizar al ir
        # evolucionando el árbol que representa cada individuo.
        return [errorCuadrado, program.getDepth()]
