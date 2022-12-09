from BaseProblem import OptimProblem, ProductionRules
from TreeCreation import TreeIndividual
from reglasPoly import ReglasPolinomios
from numpy import genfromtxt
import os


class RegresionProblem(OptimProblem):
    def __init__(self, inputFile: str) -> None:
        super().__init__("regresión simbólica", ReglasPolinomios())

        if not os.path.isfile(inputFile):
            raise Exception(f"\nEl archivo '{inputFile}' de puntos NO existe.\n")

        # Leer el archivo de N puntos de la forma (X, Y)
        # Esto resultará en un arreglo de dimensión N x 2
        self.datos = genfromtxt(inputFile, delimiter=',')

    # Este método viene de la clase base OptimProblem y debemos
    # definirlo porque se refiere a nuestro problema particular.
    def evaluateProgram(self, program: TreeIndividual) -> float:
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
        return errorCuadrado
