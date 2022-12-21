from enum import Enum
import operator, sys, math
import numpy as np
from typing import Tuple, List


# Función que sesga hacia VERDADERO con un valor en [0, 1]
# Entre más cercano bias al 1, es más probable que resulte VERDADERO el volado.
# Entre más cercano bias al 0, es más probable que resulte FALSO el volado.
def flip(bias=0.5):
    rnd = np.random.uniform(0, 1)  # Núm real entre [0, 1.0) (ABIERTO)
    if rnd <= bias:
        return True
    else:
        return False

    # return True if rnd <= bias else False


class ProductionRules:
    def __init__(self) -> None:
        self.rules = {}  # Reglas que determinan qué tipos de símbolos se pueden colocar.
        self.initSymbol = None  # Símbolo inicial para empezar a construir el árbol.
        self.setRules()

    def getInitSymb(self) -> str:
        return self.initSymbol

    def getRulesFromSym(self, symbol: str):
        return self.rules[symbol]

    def setRules(self):
        self.initSymbol = "Expr"

        # Agregar las reglas para el símbolo S (símbolo inicial)
        Expr = RuleSet("Expr")

        # Agregar las reglas no terminales
        # Expr -> Expr OP Expr
        Expr.addNonTerminalRule(Rule("+", ["Expr", "Expr"]))
        Expr.addNonTerminalRule(Rule("-", ["Expr", "Expr"]))
        Expr.addNonTerminalRule(Rule("*", ["Expr", "Expr"]))
        Expr.addNonTerminalRule(Rule("^", ["Expr", "Expr"]))

        # Agregar las reglas terminales
        # Expr -> x
        Expr.addTerminalRule(Rule("x", ["x"]))

        # Expr -> -2 | - 1 | 0 | 1 | 2
        Expr.addTerminalRule(Rule("-2", ["-2"]))
        Expr.addTerminalRule(Rule("-1", ["-1"]))
        #      Expr.addTerminalRule(Rule("0", ["0"]))
        Expr.addTerminalRule(Rule("1", ["1"]))
        Expr.addTerminalRule(Rule("2", ["2"]))

        # Agregar las reglas al conjunto total de reglas
        self.rules["Expr"] = Expr  # Agregamos todas las reglas de OP

    def getSymTable(self) -> dict:
        symTable = {}
        symTable["-2"] = -2
        symTable["-1"] = -1
        #      symTable["0"]  =  0
        symTable["1"] = 1
        symTable["2"] = 2

        return symTable


# Modela solamente una regla de producción del tipo S -> A B C
class Rule:
    def __init__(self, name, elements) -> None:
        self.__name = name
        self.__elements = elements

    def numSymbols(self) -> int:
        return len(self.__elements)

    def ruleName(self):
        return self.__name

    def getElement(self, i):
        return self.__elements[i]


# Modela un conjunto de reglas de producción incluyendo tanto terminales como no terminales.
class RuleSet:
    def __init__(self, symbol) -> None:
        self.__symbol = symbol  # Símbolo de este conjunto de reglas.
        self.__terminals = []  # Conjunto de reglas terminales para el símbolo del conjunto.
        self.__nonTerminals = []  # Conjunto de reglas NO terminales para el símbolo el conjunto.

    def getSymbol(self) -> str:
        return self.__symbol

    def addTerminalRule(self, rule: Rule):
        self.__terminals.append(rule)

    def addTerminalList(self, symbolList: List[str]):
        for symb in symbolList:
            self.__terminals.append(Rule(symb, [symb]))

    def addNonTerminalRule(self, rule: Rule):
        self.__nonTerminals.append(rule)

    def getTerminalRule(self, i) -> Rule:
        return self.__terminals[i]

    def getNonTerminalRule(self, i) -> Rule:
        return self.__nonTerminals[i]

    def numTerminals(self):
        return len(self.__terminals)

    def numNonTerminals(self):
        return len(self.__nonTerminals)

    def onlyTerminals(self):
        return len(self.__terminals) > 0 and len(self.__nonTerminals) == 0

    def onlyNonTerminals(self):
        return len(self.__nonTerminals) > 0 and len(self.__terminals) == 0


# Implementa la clase nodo que sirve para construir un árbol de expresiones
# Abajo está la clase que contruye  un árbol.
class TreeNode:
    def __init__(self, item, arity):
        self.__item = item  # El dato que guarda este nodo.
        self.__arity = arity  # El número de hijos que puede tener máximo este nodo.
        self.__children = []  # Lista de hijos actuales del nodo.
        self.__ruleType = None  # Nombre del tipo de regla que generó este nodo.
        self.__parent = None  # Padre de este nodo. AHORA NO LO USO NI LO ASIGNO.

    def arity(self) -> int:
        return self.__arity

    def setArity(self, arity: int):
        self.__arity = arity

    def getItem(self):
        return self.__item

    def setItem(self, item):
        self.__item = item

    # Nos dice si el nodo es terminal (hoja) o no (i.e., no tiene hijos).
    def isTerminal(self) -> bool:
        return (self.arity() == 0)

    # Nos dice si el nodo representa una función (tiene hijos)
    def isFunction(self) -> bool:
        return (self.arity() > 0)

    def getChild(self, posChild: int) -> 'TreeNode':
        return self.__children[posChild]

    def setChild(self, child: 'TreeNode', posChild: int):
        self.__children[posChild] = child

    def addChild(self, child: 'TreeNode'):
        self.__children.append(child)

    def setChildren(self, nodoOrigen: 'TreeNode'):
        self.__children = []
        for i in range(nodoOrigen.arity()):
            self.addChild(nodoOrigen.getChild(i))

    def getParent(self) -> 'TreeNode':
        return self.__parent

    def setParent(self, parent: 'TreeNode'):
        self.__parent = parent

    def assignNode(self, sourceNode: 'TreeNode'):
        self.setItem(sourceNode.getItem())
        self.setArity(sourceNode.arity())
        self.setChildren(sourceNode)

    def clone(self) -> 'TreeNode':
        aclone = TreeNode(self.__item, self.__arity)
        aclone.setChildren(self)
        return aclone


class TreeMethod(Enum):
    GROW = 1
    FULL = 2


class TreeIndividual:
    def __init__(self, prodRules, maxDepth=5, spawnMethod=TreeMethod.GROW):
        self.__root = None  # Raiz del árbol
        self.__depth = 0  # Profundidad actual del árbol (núm. aristas de la hoja más lejana a la raíz)
        self.__maxDepth = maxDepth  # Profundidad máximo que puede tener el árbol.
        self.__pRules = prodRules  # Reglas de producción para generar los árboles de expresiones.
        self.__symTable = self.__pRules.getSymTable()
        self.__fitness = 0
        self.__eval = []
        self.__expVal = 0
        self.__valueVec = [float]
        self.__rank = 0

        if spawnMethod == TreeMethod.GROW:
            self.createGrowMethod(maxDepth)
        else:
            self.createFullMethod(maxDepth)

    def setProdRules(self, pRules):
        self.__pRules = pRules

    def getProdRules(self) -> ProductionRules:
        return self.__pRules

    def getExpectedVal(self) -> float:
        return self.__expVal

    def setExpectedVal(self, exVal):
        self.__expVal = exVal

    def getFitness(self) -> float:
        return self.__fitness

    def setFitness(self, fit):
        self.__fitness = fit

    def getEvaluation(self) -> List[float]:
        return self.__eval

    def setEvaluation(self, eval):
        self.__eval = eval

    def setRank(self, rank):
        self.__rank = rank

    def getRank(self) -> int:
        return self.__rank

    def getDepth(self) -> int:
        return self.__depth

    # Método público para crear un árbol usando el Full Method.
    # Simplemente invocamos en método general createTree
    # usando pGrow=1.0 (la probalidad de seguir aumentando el árbol es 1)
    def createFullMethod(self, maxDepth=5):
        self.__root = self.__createTree(maxDepth, self.__pRules.initSymbol, 1.0)
        self.__depth = maxDepth
        self.__maxDepth = maxDepth

    # Método público para crear un árbol usando el Grow Method.
    # Simplemente invocamos en método general createTree
    # usando pGrow=0.5 (i.e., 50% de probabilidad de aumentar/detener el crecimiento)
    def createGrowMethod(self, maxDepth=5):
        self.__root = self.__createTree(maxDepth, self.__pRules.initSymbol, 0.5)
        self.__depth = maxDepth
        self.__maxDepth = maxDepth

    # Método público que imprime el árbol usando la notación de LISP
    # Invoca el método privado que toma como parámetro el nodo raíz de  el árbol.
    def showTree(self, streamOutput=None):
        if streamOutput is None:
            streamOutput = sys.stdout

        self.__showTree(self.__root, 0, streamOutput)

    def evaluateTree(self, value):
        self.__symTable["x"] = value

        eval = self.__evaluateTree(self.__root)
        return eval

    def getRoot(self) -> TreeNode:
        return self.__root

    # Este operador elige un nodo aleatoriamente y lo reemplaza por
    # un subárbol de tamaño adecuado.
    # Si el árbol tiene profundidad P y el nodo seleccionado
    # Está a una profuindad Pm, entonces el subárbol deberá
    # tener profundidad máxima P-Pm.
    # El parámetro pmut es la probabilidad de que se detenga cerca de la raíz.
    # Es decir, si pmut=1 seleccionará el nodo raíz y reemplazará el árbol.
    #           si pmut=0 seleccionará una hoja y la reemplazará.
    def mutation(self, pmut):
        # Elegir aleatoriamente un nodo del árbol para mutar esa rama.
        mutNode, nodeLevel = self.__randomNode(self.__root, 0, pmut)

        # print("El símbolo del i-esimo nodo a mutar es: {}".format(mutNode.getItem()) )

        # Crear una nueva rama para ese nodo de la profudidad adecuada
        # para NO exceder la profunidad original.
        maxDepthNewBranch = self.__depth - nodeLevel
        newChild = self.__createTree(maxDepthNewBranch, self.__pRules.initSymbol, 1.0)
        # print("\nNew branch: ")
        # self.__showTree(newChild, 0, sys.stdout)

        mutNode.assignNode(newChild)

    # Este método regresa una copia completa de este árbol.
    def copy(self) -> 'TreeIndividual':
        cloneTree = TreeIndividual(self.getProdRules())
        cloneTree.assignTree(self)
        return cloneTree

    # Convierte este árbol en una copia del árbol dado como entrada.
    # Es decir, la asignación self <- sourceTree
    def assignTree(self, sourceTree: 'TreeIndividual'):
        self.__root = self.__copyTree(sourceTree.getRoot())
        self.__depth = sourceTree.__depth
        self.__maxDepth = sourceTree.__maxDepth
        self.__fitness = sourceTree.getFitness()
        self.__eval = sourceTree.getEvaluation()

    def __copyTree(self, root: TreeNode):
        node = None

        if root != None:
            # Crea una copia superficial del nodo raíz (sin hijos)
            node = TreeNode(root.getItem(), root.arity())

            if root.isFunction():
                for i in range(root.arity()):
                    node.addChild(self.__copyTree(root.getChild(i)))

        return node

    # This method combine this Tree with the given mate tree.
    def crossover(self, mate: 'TreeIndividual') -> Tuple['TreeIndividual', 'TreeIndividual']:
        # Create copies of the parents.
        childTree1 = TreeIndividual(self.getProdRules())
        childTree2 = TreeIndividual(self.getProdRules())
        childTree1.assignTree(self)
        childTree2.assignTree(mate)

        # print("\nEl hijo 1 copiado:")
        # childTree2.showTree()

        # Elegir los nodos que se intercambiarán de cada árbol (self y mate)
        xPointCh1, nodeLevel1 = self.__randomNode(childTree1.getRoot(), 0, 0.25)
        xPointCh2, nodeLevel2 = self.__randomNode(childTree2.getRoot(), 0, 0.25)
        # print("El punto de cruza 1 es: {} y tiene el símbolo {}:".format(nodeLevel1, xPointCh1.getItem()))
        # self.__showTree(xPointCh1, 0, sys.stdout)

        # print("\nEl punto de cruza 2 es: {} y tiene el símbolo {}:".format(nodeLevel2, xPointCh2.getItem()))
        # self.__showTree(xPointCh2, 0, sys.stdout)

        auxNode = xPointCh1.clone()
        xPointCh1.assignNode(xPointCh2)
        xPointCh2.assignNode(auxNode)

        return childTree1, childTree2

    def __randomNode(self, node: TreeNode, level, pPruning) -> Tuple[TreeNode, int]:
        # If current node is a leaf or is selected as the pruning node,
        # then stop the recursion and return the node.
        if node.isTerminal() or flip(pPruning):
            # node.setItem("M")
            # print("El nodo elegido tiene el item: ", node.getItem())
            return node, level
        else:
            # Elegir aleatoriamente uno de los hijos para seguir bajando.
            rndChild = np.random.randint(node.arity())
            return self.__randomNode(node.getChild(rndChild), level + 1, pPruning)

    ####################################################
    # A continuación solamente están los método PRIVADOS
    ####################################################

    # Método privado que recursivamente muestra  el árbol usando
    # la notación de LISP:
    # Es decir (FUNCIÓN  ARG1  ARG2 ... ARGN), donde ARG puede ser  un
    # subárbol de expresiones.
    # Es solamente una forma de mostrar, NO quiere decir que el programa
    # del árbol solamente puede ser LISP. También se podría mostrar como un
    # programa en C o Python si quisiéramos.
    # Por ejemplo, este árbol se mostraría así (LISP):
    # (SiOtro
    #     (<= SensorFrente d2 ) Avanzar1 Avanzar2 )

    # En notación Python esto significaría:
    # if SensorFrente <= d2:
    #    return Avanzar1
    # else:
    #    return Avanzar2
    #
    # El argumento level solamente sirve para indentar la salida correctamente.
    def __showTree(self, root, level, streamOutput):
        if root != None:
            if root.isFunction():
                print("\n", "\t" * level, "(", end="", file=streamOutput)  # Indentar la función según el nivel

            # Mostrar el nombre del terminal o función.
            print(root.getItem(), end=" ", file=streamOutput)  # Evitar el salto del línea

            # Mostrar RECURSIVAMENTE sus hijos (subárboles)
            for i in range(root.arity()):
                self.__showTree(root.getChild(i), level + 1, streamOutput)

            # Mostrar el paréntesis que cierra la función.
            if root.isFunction():
                print(")", end=" ", file=streamOutput)

    # Este es el método general para crear árboles:
    #   Si pGrow = 1, entonces se comportará con el método FULL, y
    #   Si pGrow < 1, se comporta como el método GROW.
    # Entre más grande pGrow, más probable que el árbol crezca hasta
    # alcanzar su profunidad máxima.
    # Es decir, con 1 crece al máximo, y con 0 crece al mínimo.
    #
    def __createTree(self, maxDepth, symbol, pGrow):
        node = None

        # Obtener el conjunto de reglas (terminales y no terminales) del símbolo de entrada.
        ruleSet = self.__pRules.rules[symbol]

        # Determinar si extender el nodo actual con la probabilidad dada pGrow
        grow = flip(pGrow)

        # Casos para poner un TERMINAL (fin del crecimiento del árbol):
        # 1. Ya se llegó a la profunidad máxima y ese símbolo sí tiene reglas con terminales.
        # 2. Se determinó aleatoriamente detener el cricimiento antes.
        # 3. Solamente hay terminales en el conjunto de reglas del símbolo dado.
        if ((maxDepth <= 0 and ruleSet.numTerminals() > 0) or
                (not grow and ruleSet.numTerminals() > 0) or
                ruleSet.onlyTerminals()):

            # Obtener aleatoriamente una de las reglas TERMINALES del símbolo de entrada
            r = ruleSet.getTerminalRule(np.random.randint(ruleSet.numTerminals()))
            node = TreeNode(r.ruleName(), 0)  # Nodo con 0 hijos (i.e., una hoja).
        else:  # Caso para poner una FUNCIÓN (seguir con el crecimiento del árbol)
            # Obtener aleatoriamente una de las reglas NO terminales del símbolo de entrada
            r = ruleSet.getNonTerminalRule(np.random.randint(ruleSet.numNonTerminals()))
            node = TreeNode(r.ruleName(), r.numSymbols())  # Nodo que tendrá numSymbols hijos

            # Crear recursivamente cada uno de sus hijos (subárboles)
            for i in range(r.numSymbols()):
                node.addChild(self.__createTree(maxDepth - 1, r.getElement(i), pGrow))

        return node

    # Evaluación recursiva en post-orden: eval rama IZQ, eval rama DER, eval raíz
    def __evaluateTree(self, root):
        # Si el nodo es terminal (constante, variable) regresar su valor
        if root.isTerminal():
            return self.__evalTerminal(root.getItem())
        else:
            # Si el nodo es un operador (+, -, *, ^) evaluamos post-orden
            leftValue = self.__evaluateTree(root.getChild(0))
            rightValue = self.__evaluateTree(root.getChild(1))
            return self.__apply(root.getItem(), leftValue, rightValue)

        return 0.0

    def __apply(self, oper, op1, op2):
        ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '^': operator.pow,
        }

        # print(f"\nOperacion: {op1} {oper} {op2}\n", flush=True)
        value = ops[oper](op1, op2)
        if math.isnan(value):
            raise Exception(f"\nResultó algo que no es número: {op1} {oper} {op2}.\n\n")

        return value

    def __evalTerminal(self, symb: str):
        if symb.isalpha():
            return self.__symTable[symb]
        else:
            return float(symb)


def main():
    rulesMath = ProductionRules()

    arbol1 = TreeIndividual(rulesMath, 3, TreeMethod.GROW)
    arbol1.createGrowMethod(3)
    arbol2 = TreeIndividual(rulesMath, 3, TreeMethod.GROW)
    arbol2.createGrowMethod(3)

    print("\nÁrbol UNO creado con el método GROW:")
    arbol1.showTree()
    print("\n")

    print("\nÁrbol DOS creado con el método GROW:")
    arbol2.showTree()
    print("\n")

    ch1, ch2 = arbol1.crossover(arbol2)

    print("\nÁrbol Hijo UNO:")
    ch1.showTree()
    print("\n")

    print("\nÁrbol Hijo DOS:")
    ch2.showTree()
    print("\n")

    ch2.mutation(0.0)
    print("\nEl Hijo DOS mutado resultó:")
    arbol2.showTree()
    print("\n")


if __name__ == "__main__":
    main()
