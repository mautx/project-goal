from numpy.lib.function_base import select
from TreeCreation import ProductionRules
from TreeCreation import TreeIndividual

class OptimProblem:
   def __init__(self, name: str, treeRules: ProductionRules) -> None:
      self.__name = name
      self.__treeRules = treeRules

   def getTreeRules(self) -> ProductionRules:
      return self.__treeRules

   def getName(self) -> str:
      return self.__name

   # Este método debe ser implementado por la clase que implementa
   # cada problema particular.
   def evaluateProgram(self, program: TreeIndividual):
      raise NotImplementedError("\n\nDebes sobrecargar este método en tu subclase.\n\n") 

