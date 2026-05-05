package org.opt4j.CAE.VRP;

import java.util.Collections;

import org.opt4j.CAE.VRP.VRPProblem.Item;
import org.opt4j.core.genotype.PermutationGenotype;
import org.opt4j.core.problem.Creator;
import com.google.inject.Inject;
/**
 * La clase {@link VRPCreator} genera el genotipo {@link PermutationGenotype} a partir del problema {@link VRPProblem}.
 * Genera una permutación de clientes y vehículos.
 * 
 * @author puente@uniovi.es
 * 
 */

public class VRPCreator implements Creator<PermutationGenotype<Item>> {
	/**
	 * referencia a la instancia del problema {@link VRPProblem} 
	 */
	protected final VRPProblem problem;
	/**
	 * constructor del generador de cromosomas
	 * @param problem instancia a resolver
	 */
	@Inject
	public VRPCreator(VRPProblem problem) {
		this.problem = problem;
	}
	
	/**
	 * genera un cromosoma (genotipo)
	 * @return el cromosoma 
	 */
	@Override
	public PermutationGenotype<Item> create() {
		PermutationGenotype<Item> genotype = new PermutationGenotype<Item>();
		// añade todos los clientes del problema al cromosoma
		for (Item item : problem.getClients()) 
			genotype.add(item);
		// añade todos los vehículos del problema al cromosoma excepto el 
		// primero que iría implicitamente al inicio del cromosoma
		for(int x = 1; x < problem.getVehicles().size(); x++)
		genotype.add(problem.getVehicles().get(x));
		
		
		// baraja todos los items
		Collections.shuffle(genotype);
		
		return genotype;
	}
}
