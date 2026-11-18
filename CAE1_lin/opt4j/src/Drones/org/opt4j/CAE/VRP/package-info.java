/**
 * <p>
 * Este proyecto implementa las clases necesarias para resolver el problema VRP básico.
 * Y sirve de base para implementar las clases necesarias para resolver
 * problemas derivados de este problema.
 * </p>
 * <p>
 * {@code org.opt4j.CAE.VRP.VRPProblem} modela la clase problema con todos 
 * los elementos que definen al problema. En este caso, los clientes a visitar 
 * y el número de vehículos disponibles para ello. Además se define una base 
 * para todos los vehículos con unas coordenadas fijas (0,0).
 * </p>
 * <p>
 * {@code org.opt4j.CAE.VRP.VRPCreator} modela el generador de cromosomas (genotipos) 
 * para ello utiliza la clase {@code org.opt4j.CAE.VRP.VRPProblem}, dando lugar
 * a objetos del tipo {@link org.opt4j.core.genotype.PermutationGenotype}. 
 * </p>
 * <p>
 * {@code org.opt4j.CAE.VRP.VRPDecoder} modela el decodificador de cromosomas (genotipos),
 * para ello utiliza la clase {@link org.opt4j.core.genotype.PermutationGenotype} 
 * dando lugar al fenotipo correspondiente, generando así objetos del tipo {@code org.opt4j.CAE.VRP.VRPRoutes}.  
 * </p>
 * <p>
 * {@code org.opt4j.CAE.VRP.VRPEvaluator} modela el evaluador (generador del fitness) del fenotipo {@code org.opt4j.CAE.VRP.VRPRoutes},
 * generando los valores de las funciones objetivo consideradas {@code org.opt4j.core.Objectives}.
 * </p>
 */

package org.opt4j.CAE.VRP;