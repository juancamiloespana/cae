package org.opt4j.CAE.VRP;

import org.opt4j.CAE.CAEModule;
import org.opt4j.core.config.annotations.File;
import org.opt4j.core.config.annotations.Name;
import org.opt4j.core.config.annotations.Parent;
import org.opt4j.core.problem.ProblemModule;
import org.opt4j.core.start.Constant;

/**
 * Vehicle Routing Problem (VRP) implemented as a multi-objective optimization problem:
 * - Minimize the maximum distance traveled by any vehicle
 * - Minimize the number of vehicles used
 *
 * @see <a href="http://neo.lcc.uma.es/vrp/vehicle-routing-problem/">VRP reference</a>
 *
 * @author puente@uniovi.es
 */
@Parent(CAEModule.class)
public class DronesModule extends ProblemModule {
	@Constant(value = "vehiculos")
	protected int totalVehicles = 5;

	@Constant(value = "clientes")
	protected int clients = 500;

	@Constant(value = "swept file")
	@Name("Swept File")
	@File
	protected String fileName = "";

	public String getFileName() {
		return fileName;
	}

	public void setFileName(String fileName) {
		this.fileName = fileName;
	}

	@Constant(value = "control station file")
	@Name("Control Station File")
	@File
	protected String fileNameCS = "";

	public String getFileNameCS() {
		return fileNameCS;
	}

	public void setFileNameCS(String fileName) {
		this.fileNameCS = fileName;
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
	 * Wires Creator, Decoder, and Evaluator into the framework.
	 */
	@Override
	public void config() {
		bindProblem(VRPCreator.class, VRPDecoder.class, VRPEvaluator.class);
	}
}
