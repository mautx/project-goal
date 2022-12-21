from typing import List
import numpy as np
import sys

# Importar las clases que implementan un individuo-árbol
from TreeCreation import *

# Importar la clase base de los problemas de optimización
from BaseProblem import OptimProblem


# Clase principal que implementa el ciclo para evolucionar
# una población de individuos representados por árboles.
class GeneticProgram:
    def __init__(self, problem: OptimProblem, popSize=10, gMax=10, pcross=0.9, pmut=0.1, maxDepth=5,
                 typeTree=TreeMethod.GROW):
        self.__popSize = popSize  # Tamaño de la población
        self.__gMax = gMax  # Número de generaciones para evolucionar la población
        self.__pCrossover = pcross  # Probabilidad de cruza de cada par de padres.
        self.__pMutation = pmut  # Probabilidad de mutación para cada individuo.
        self.__population = []  # Población actual al inicio de cada generación.
        self.__childrenPop = []  # Población de hijos como resultado de la cruza.
        self.__treeMethod = typeTree  # Método para crear la población.
        self.__superTree = None  # El mejor individuo en la población actual.
        self.__maxDepth = maxDepth  # Produndidad para crear los invidiudos (i.e., los árboles)
        self.__problem = problem  # El problema particular que resolverá el PG
        self.__fitnessFileName = "fitness_history.txt"
        self.__lastPopFitness = "lastPopFitness.txt"
        self.__lastPopTrees = "lastPopTrees.txt"
        fitFile = open(self.__fitnessFileName, "w")
        fitFile.write("")
        fitFile.close()

    # Implementa el ciclo principal del PG
    def optimize(self):
        ### 1. Inicializar la población de N individuos
        gen = 1
        self.__initPopulation(self.__population)
        # self.__showPopulation(self.__population) # Se puede comentar

        ### 2. Evaluar la 1a población de individuos
        self.__evalPopulation(self.__population)
        self.__superTree = self.__findBest(self.__population)

        # Ciclo principal para evolucionar la población de programas
        # durante gMax generaciones.
        for gen in range(1, self.__gMax + 1):
            ### 3. Seleccionar los padres según el método de la ruleta.
            padresIdx = self.__selectParents(self.__population)

            ### 4. Cruzar los padres seleccionados para producir la población de hijos.
            self.__childrenPop = self.__crossoverParents(padresIdx, self.__population)

            ### 5. Mutar los hijos según el porcentaje de mutación.
            self.__mutateChildren(self.__childrenPop)

            ### 5.1. Copiar el mejor individuo de la generación anterior en la población de hijos.
            self.__elitism(self.__childrenPop, self.__superTree)

            ### 6. Evaluar la población de hijos.
            self.__evalPopulation(self.__childrenPop)

            ### 7. Realizamos el otorgamiento de la aptitud
            self.__moeaRankings(self.__childrenPop)

            # self.__printEvalPop(self.__childrenPop)
            self.__superTree = self.__findBest(self.__childrenPop)

            # self.__showPopulation(self.__population)

            #print("\nMejor evaluación de la generación {}: {}".format(gen, self.__superTree.getRank()))  <-----------------------desprintear este
            # Guardar estadísticas de la generación actual
            self.__stats()

            ### Intercambiar las REFERENCIAS de las poblaciones para que
            ### 'population' sea la población actual para la siguiente generación.
            temp = self.__population
            self.__population = self.__childrenPop
            self.__childrenPop = temp
        ###### FIN del ciclo evolutivo

        # Guardar la salida en archivos
        self.__writeOutput(self.__population)

    ######## Fin de optimize()
    ################################################

    # Imprimir el valor de la evaluación de cada individuo.
    def __printEvalPop(self, pop):
        for i in range(len(pop)):
            print("{}: {}".format(i, pop[i].getEvaluation()))

    # Guardar en un archivo valores importantes de cada generación.
    def __stats(self):
        # Agregar al archivo de aptitudes los valores del mejor indiviudo de
        # la generación actual.
        with open(self.__fitnessFileName, "a") as fitFile:
            sTreeFitness = self.__superTree.getFitness()
            sTreeEval = self.__superTree.getEvaluation()
            fitFile.write("{}\t{}\n".format(sTreeFitness, sTreeEval))

    # Escribir la población final en dos archivos:
    # 1. La aptitud y evaluación.
    # 2. La representación de árbol de cada individuo.
    def __writeOutput(self, pop: List[TreeIndividual]):
        # Escribir en un archivo la aptitud y evaluación de última población
        fitFile = open(self.__lastPopFitness, "w")
        treeFile = open(self.__lastPopTrees, "w")

        i = 1
        for tree in pop:
            fitFile.write("{:10.6f}\n".format(tree.getFitness()))

            treeFile.write(f"Individual {i}")
            tree.showTree(treeFile)
            treeFile.write("\n\n")
            i += 1

        fitFile.close()
        treeFile.close()

    # Crea la población inicial usando el método de creación de árboles
    # dado en el constructor (GROW o FULL).
    # Es importante notar que al momento de la creación debemos indicarle las
    # reglas de producción, la cuales son parte de nuestro problema.
    def __initPopulation(self, pop: List[TreeIndividual]):
        for i in range(self.__popSize):
            ind = TreeIndividual(self.__problem.getTreeRules(), self.__maxDepth, self.__treeMethod)
            pop.append(ind)

    # Mostrar la población de árboles.
    def __showPopulation(self, pop: List[TreeIndividual]):
        for i in range(len(pop)):
            print("\nArbol ", i + 1, ":")
            pop[i].showTree()
            print("\n")

    # Este método evalúa cada uno de los individuos (árboles o programas)
    # y al final, se asigna la aptitud según su evaluación.
    #TODO preguntar si mejor hacemos una clase base para problemaGP
    def __evalPopulation(self, population: List[TreeIndividual]):

        i = 0
        for ind in population:
            # El árbol se interpreta y se usa para resolver nuestro problema.
            # El desempeño (eval) del árbol se regresa y guarda en el propio individuo.
            eval = self.__problem.evaluateProgram(ind)
            # print(f"\nEvaluación del individuo {i}: {eval}", end="")
            # ??????
            #i += 1
            ind.setEvaluation(eval)
            """
            # El mecanismo está hecho suponiendo minimización SIN restricción.
            if ind.getEvaluation() > 0:
                # Cuando la evaluation es cercana a 0 (lo cual queremos), la aptitud es GRANDE.
                ind.setFitness(1.0 / ind.getEvaluation())
            elif ind.getEvaluation() == 0:
                # Si la evaluación es 0, la aptitud será el mejor valor posible.
                ind.setFitness(sys.float_info.max)
            else:
                raise Exception("The evaluation must be equal or greater than 0")
            """
    # Este método asigna la aptitud de todos los individuos para que un vector
    # de puntos pueda ser considerado un.

    def __moeaRankings(self, population: List[TreeIndividual]):
        for i in range(len(population)):
            # Creamos el score que comenzará en 1 para evitar que la evaluación sea 0
            score = 1
            # Partimos desde el siguiente individuo en la lista hasta el tamaño total de la población
            for j in range(i + 1, len(population)):
                # Creamos dos vectores X y Y para evaluarlos con la dominancia
                x = population[i].getEvaluation()
                y = population[j].getEvaluation()


                #enviamos a la función isDominance un vector con los resultados de
                #el método evaluateTreede la clase MOEaregression
                # En caso de que Y domine a X, aumentamos el contador.
                if self.__isDominance(y, x):
                    score += 1

            #TODO ¿debemos de dejar el if?
            # El score pasa a ser la eval del individuo
            print("El rank: " + str(score))
            population[i].setRank(score)

            # El mecanismo está hecho suponiendo minimización SIN restricción.
            if population[i].getRank() > 0:
                # Cuando la evaluation es cercana a 0 (lo cual queremos), la aptitud es GRANDE.
                population[i].setFitness(1.0 / population[i].getRank())
                print("El fitness: " + str(population[i].getFitness()))
            elif population[i].getRank() == 1:
                # Si la evaluación es 0, la aptitud será el mejor valor posible.
                population[i].setFitness(sys.float_info.max)
            else:
                raise Exception("The evaluation must be equal or greater than 0")

    # Este método retorna verdadero en caso de que el primer vector domine al segundo
    def __isDominance(self, x: List[float], y: List[float]) -> bool:
        counter = 0
        for i in range(len(x)):
            if x[i] > y[i]:
                return False
            elif x[i] == y[i]:
                counter += 1
        if counter == len(x):
            return False
        else:
            return True

    # Seleccionar los padres que debemos cruzar usando el mecanismo de ruleta.
    # La salida son las posiciones de los padres seleccionados (incluso hay repetidos).
    def __selectParents(self, pop: List[TreeIndividual]):
        # El valor esperado determina la "circunferencia" total de la ruleta.
        expValue = self.__computeExpectedValue(pop)

        # "Girar" varias veces la ruleta para seleccionar cada vez un padre (posiblemente repetido)
        parentsIdx = []
        for i in range(len(pop)):
            parentsIdx.append(self.__rouletteSelection(pop, expValue))

        return parentsIdx

    # Cruzar los padres ya seleccionados, y regresa la población de hijos
    # resultante.
    def __crossoverParents(self, parentsIdx, pop: List[TreeIndividual]):
        childPop = []

        for j in range(0, len(pop) - 1, 2):
            p1Pos = parentsIdx[j]
            p2Pos = parentsIdx[j + 1]

            if flip(self.__pCrossover):
                child1, child2 = pop[p1Pos].crossover(pop[p2Pos])
            else:
                child1 = pop[p1Pos].copy()
                child2 = pop[p2Pos].copy()

            childPop.append(child1)
            childPop.append(child2)

        return childPop

    # Muta la población de hijos.
    def __mutateChildren(self, childPopulation: List[TreeIndividual]):
        for child in childPopulation:
            child.mutation(self.__pMutation)

    # Calcula el valor esperado de TODA población, es decir la suma de los
    # de los valores esperados de cada individuo.
    # Este valor sirve para determinar la longitud de la "circunferencia"
    # de la ruleta.
    def __computeExpectedValue(self, population: List[TreeIndividual]) -> float:
        fitnessSum = 0.0
        for ind in population:
            fitnessSum += ind.getFitness()

        avgFitness = fitnessSum / len(population)

        expValSum = 0.0
        for ind in population:
            if avgFitness != 0.0:
                ind.setExpectedVal(ind.getFitness() / avgFitness)
            else:
                ind.setExpectedVal(0.0)

            expValSum += ind.getExpectedVal()

        return expValSum

    # Implementación de la selección por ruleta.
    # Regresa la posición del padre seleccionado dentro de la lista de individuos.
    def __rouletteSelection(self, pop: List[TreeIndividual], sumExpValue) -> int:
        rnd = np.random.uniform(0.0, sumExpValue)
        sum = pop[0].getExpectedVal()
        j = 1

        while sum < rnd and j < len(pop):
            sum += pop[j].getExpectedVal()
            j += 1

        return j - 1

    # Este método obtiene el individuo más apto de la población dada.
    def __findBest(self, pop: List[TreeIndividual]) -> TreeIndividual:
        bestFit = 0.0
        bestFitPos = -1

        for i in range(len(pop)):
            if pop[i].getFitness() > bestFit:
                bestFit = pop[i].getFitness()
                bestFitPos = i

        return pop[bestFitPos].copy()

    # Inserta el mejor individuo en la población actual
    # para no perderlo en la siguiente generación.
    def __elitism(self, pop: List[TreeIndividual], bestPop: TreeIndividual):
        rnd = np.random.randint(len(pop))
        pop[rnd].assignTree(self.__superTree)
