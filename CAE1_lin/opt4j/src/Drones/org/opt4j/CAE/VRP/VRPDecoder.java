package org.opt4j.CAE.VRP;

import org.opt4j.CAE.VRP.VRPProblem.Vehicle;
import org.opt4j.CAE.VRP.VRPProblem.Client;
import org.opt4j.CAE.VRP.VRPProblem.Swept;
import org.opt4j.CAE.VRP.VRPProblem.Item;
import org.opt4j.core.genotype.PermutationGenotype;
import org.opt4j.core.problem.Decoder;

import com.google.inject.Inject;
/**
 * El {@link VRPDecoder} genera el fenotipo a partir del genotipo 
 * {@link PermutationGenotype} generado por {@link VRPCreator}.
 * Genera el conjunto de rutas {@link VRPRoutes} de cada vehículo.
 * Para ello decodifica de izquierda a derecha la permutación. Definiendo los 
 * clientes {@link VRPProblem.Client} a 
 * visitar por cada vehículo {@link Vehicle} como la secuencia de clientes 
 * contenida entre un par de vehículos en el cromosoma.
 * 
 * @author puente@uniovi.es
 * 
 */

public class VRPDecoder implements Decoder<PermutationGenotype<Item>, VRPRoutes> {
	protected final VRPProblem problem;
	
	// A través de @Inject se le proporciona automáticamente la instancia 
	// previamente creada del VRProblem
	@Inject
	public VRPDecoder(VRPProblem problem) {
		this.problem = problem;
	}
	
	/**
	 * Decofica un cromosoma (genotipo) generando el conjunto de rutas de cada 
	 * vehiculo (fenotipo)
	 * @param genotype cromosoma a decodificar
	 * @return fenotipo como conjunto de rutas de cada vehículo
	 */
	@Override
	public VRPRoutes decode(PermutationGenotype<Item> genotype) {
		// El fenotipo será el conjunto de rutas (VRPRoutes)
		VRPRoutes vprRoutes = new VRPRoutes();
		// Nueva ruta para el vehículo incial (el que no se incluye en el 
		// cromosoma) - comenzando y finalizando en su estacion de control
		VRPRoute vprRoute = newRoute(0);
		// se añade al conjunto de rutas
		vprRoutes.add(vprRoute);
		// Añadimos ciudades hasta encontrar el sgte vehiculo
		for (Item item : genotype) {
			// si encontramos un vehículo...
			if(item instanceof Vehicle){
				// finalizamos la ruta del vehículo actual y...
				endRoute(vprRoute);
				// Creamos una nueva ruta para el nuevo vehículo encontrado
				vprRoute = newRoute(((Vehicle)item).getId());
				vprRoutes.add(vprRoute);
			} else {
				if (item instanceof Swept) {
					Point current = vprRoute.get(vprRoute.size() - 1);
					Point p1 = ((Swept) item).getPoint();
					Point p2 = ((Swept) item).getPoint2();
					if (current.distance(p1) < current.distance(p2)) {
						vprRoute.add(p1);
						vprRoute.add(p2);
					} else {
						vprRoute.add(p2);
						vprRoute.add(p1);
					}
				} else throw new RuntimeException("Tipo incorrecto de gen en decode()");
			}
			
		}
		// finalizamos la ruta del vehículo actual y...
		endRoute(vprRoute);
		///	System.out.println("Fenotipo: " + vprRoutes);
		return vprRoutes;
	}

	/**
	 * Crea una nueva ruta que se inicia en la estacion de control 
	 * @param id identificador del vehículo al que pertenece la ruta
	 * @return la nueva ruta
	 */
	private VRPRoute newRoute(int id){
		VRPRoute salesmanRoute = new VRPRoute(id);
		salesmanRoute.add(problem.getBase().getPoint());
		
		return salesmanRoute;
	}
	
	/**
	 * Finaliza la ruta con la vuelta a la estacion de control
	 * @param salesmanRoute - ruta actual
	 * @return la misma ruta
	 */
		private VRPRoute endRoute(VRPRoute salesmanRoute){
			// realmente no necesitamos añadir nada al ser una ruta circular
			// salesmanRoute.add(problem.getBase());
			
			return salesmanRoute;
		}
	
	
}
