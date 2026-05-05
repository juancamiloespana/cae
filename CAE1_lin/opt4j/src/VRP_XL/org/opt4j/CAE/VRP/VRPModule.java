package org.opt4j.CAE.VRP;

import org.opt4j.CAE.CAEModule;
import org.opt4j.core.config.annotations.File;
import org.opt4j.core.config.annotations.Parent;
import org.opt4j.core.problem.ProblemModule;
import org.opt4j.core.start.Constant;
/**
 * El problema de enrutamiento de vehículos (VRP, por su siglas en inglés) es un 
 * problema de optimización combinatoria y de programación de entero qué pregunta 
 * "¿Cuál es el conjunto óptimo de rutas para una flota de vehículos que debe satisfacer 
 * las demandas de un conjunto dado de clientes?". Es una generalización del conocido 
 * Problema del Viajante (TSP, por sus siglas en inglés).
 * En este caso se implementa como un problema multiobjetivo:
 * - Distancia máxima recorrida por los vehículos (a minimizar)
 * - Número de vehículos necesarios para cubrir todas las demandas (a minimizar)
 * 
 * @see <a
 *      href="http://neo.lcc.uma.es/vrp/vehicle-routing-problem/">http://neo.lcc.uma.es/vrp/vehicle-routing-problem/</a>
 * @see <a
 *      href="https://es.wikipedia.org/wiki/Problema_de_enrutamiento_de_veh%C3%ADculos">https://es.wikipedia.org/wiki/Problema_de_enrutamiento_de_vehículos</a>
 * 
 * @author puente@uniovi.es
 * 
 */
@Parent(CAEModule.class) // Para el módulo padre
public class VRPModule extends ProblemModule {
	@Constant(value = "vehiculos")
	protected int totalVehicles = 10;

	@Constant(value = "clientes")
	protected int clients = 100;
	
	@Constant(value = "nombre fichero")
	@File
	protected String fileName = "";

	public String getFileName() {
		return fileName;
	}

	public void setFileName(String fileName) {
		this.fileName = fileName;
	}

	
	public int getClients() {
		return clients;
	}
	public void setClients(int clients) {
		this.clients = clients;
	}
	public int getTotalVehicles() {
		return totalVehicles;
	}
	public void setTotalVehicles(int totalVehicles) {
		this.totalVehicles = totalVehicles;
	}
	
	/**
	 * Vincula las clases del problema que implementan las 
	 * interfaces Creator, Decoder y Evaluator
	 */
	@Override
	public void config() {
		bindProblem(VRPCreator.class, VRPDecoder.class, VRPEvaluator.class);
	}
}