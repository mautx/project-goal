from TreeCreation import ProductionRules
from TreeCreation import RuleSet
from TreeCreation import Rule


# Clase que se deriva de la clase ProductionRules para
# definir las reglas para crear árboles de expresiones artiméticas.
# En particular, polinomios desde grado 1 hasta grado 3 (función lineal hasta cúbicas).
class ReglasPolinomios(ProductionRules):

   def __init__(self) -> None:
      super().__init__()

   # Este es el método importante y que debemos implementar para cada tipo de árbol
   # que representará la expresión o programa que es la solución a nuestro problema.
   # Es este ejemplo, se definirán las reglas para generar árboles que representen
   # polinomios
   def setRules(self):
      # Debemos definir el símbolo inicial de la gramática
      self.initSymbol = "Poly"
      
      #######
      # Esta gramática tendrá varias reglas de producción, para los símbolos siguientes:
      # Poly: reglas del símbolo inicial para generar cualquier polinomio.
      # Term: regla para generar el término de la forma x^n
      # Coef: reglas para sustituir por un coeficiente concreta (-2, -1, 0, 1, 2)
      # Var: reglas para sustituir por una variable concreta (solamente x en este problema)
      # Pow: reglas para sustituir por una potencia entera concreta.
      #######

      # Reglas de Poly
      # Poly -> Poly * Poly
      # Poly -> Poly + Poly
      # Poly -> x | -2.0 | -1.0 | 1.0 | 2.0
      Poly = RuleSet("Poly")
      Poly.addNonTerminalRule(Rule("*", ["Poly", "Poly"]))
      Poly.addNonTerminalRule(Rule("+", ["Poly", "Poly"]))
      Poly.addTerminalList(["x", "x", "x", "x", "x"])      
      Poly.addTerminalList(["-1", "0.25", "0.5", "0.75"])
      #Poly.addTerminalList(["-2.0", "-1.0", "1.0", "2.0"]) 
      self.rules[Poly.getSymbol()] = Poly

   # Una tabla de símbolos no sirve para definir el árbol, pero se necesita para
   # el momento de interpretar el árbol.
   # Como dependen de las constantes que pusimos en las reglas del método anterior,
   # es mejor definir aquí la tabla de símbolos.
   def getSymTable(self) -> dict:
      symTable = {}

      return symTable
     