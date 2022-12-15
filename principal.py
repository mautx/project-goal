# script principal para iniciar la ejecución del programa genético
import argparse, sys, os

## Importar el módulo principal del Programa Genético.
import gprogram as gp
from MoeaRegresion import MoeaRegresion

## Este módulo es que debemos cambiar para cada problema nuevo.
from ProblemaRegresion import *


# Esta función lee los argumentos pasados desde la consola.
def readArgs():
    parser = argparse.ArgumentParser(description='Parámetros para ejecutar el PG')

    parser.add_argument('-p', '--psize', type=int, required=True,
                        help='Population size')
    parser.add_argument('-g', '--ngens', type=int, required=True,
                        help='Number of generations')
    parser.add_argument('-x', '--pxover', type=float, required=False, default=0.9,
                        help='Probability for crossover')
    parser.add_argument('-m', '--pmut', type=float, required=False, default=0.1,
                        help='Probability for mutation')
    parser.add_argument('-d', '--depth', type=int, required=False, default=5,
                        help="Trees' maximum depth")
    parser.add_argument('-f', '--dFile', type=str, required=False, default='puntos_01.txt',
                        help="Archivo de entrada para el problema de regresión")

    args = parser.parse_args()
    return args


# La función que crea un objeto PG y realiza la optimización configurada.
def main():
    ### 1. Leer argumentos de la consola.
    args = readArgs()

    ### 2. Crear el problema que se resolverá con el PG
    ### En este ejemplo se crea el problema que define 2 cosas:
    ###    i) Cómo representar los polinomios que deberán ajustarse a nuestros puntos.
    ###   ii) Cómo evaluar cada uno de los árboles (polinomios) según la desviación a los puntos.
    archivoEntrada = args.dFile
    problema = MoeaRegresion(archivoEntrada)

    ### 3. Crear el objeto GP y optimizar el problema.
    myGP = gp.GeneticProgram(problema, args.psize, args.ngens, args.pxover, args.pmut, args.depth)
    myGP.optimize()

    ### La salida quedará en 3 archivos:
    # 1. fitness_history.txt: la aptitud y evaluación del MEJOR individuo en cada generación.
    # 2. lastPopFiteness.txt: la aptitud y evaluación de los N individuos de la población final.
    # 3. lastPopTrees.txt   : la representación en árbol de los N individuos de la población final.
    print("\n\nLa salida está en 3 archivos: fitness_history.txt, lastPopFitness.txt y lastPopTrees.txt\n\n")


if __name__ == "__main__":
    main()
