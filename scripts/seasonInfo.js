function getSeasonInfo(year) {
    const season = db.seasons.findOne({ year: year });
    if (!season) {
    print(`No se encontraron datos para la temporada ${year}`);
    return;
    }

    print(`Temporada: ${season.year}`);
    season.races.forEach(race => {
        print(`    Carrera: ${race.name} (Ronda ${race.round})`);
        print(`    Circuito: ${race.circuit.name}, ${race.circuit.location}, ${race.circuit.country}`);
        print("    Resultados:");
        race.results.forEach(result => {
            const driver = db.drivers.findOne({ driverId: result.driverId });
            const constructor = db.constructors.findOne({ constructorId: result.constructorId });
            const status = db.status.findOne({ statusId: result.statusId });
            print(`        ${result.position || 'DNF'}: ${driver.forename} ${driver.surname}`);
            print(`            Constructor: (${constructor.name})`);
            print(`            Puntos: (${result.points})`);
            print(`            Estatus: ${status ? status.status : 'Desconocido'}`);
        });
        print("    Participantes:");
        race.qualifying.forEach(qual => {
            const driver = db.drivers.findOne({ driverId: qual.driverId });
            print(`        ${qual.position}: ${driver.forename}`);
            print(`            Q1: ${qual.q1 || 'N/A'}`);
            print(`            Q2: ${qual.q2 || 'N/A'}`);
            print(`            Q3: ${qual.q3 || 'N/A'}`);
        });
        if (race.sprint_results.length > 0) {
            print("    Resultados del Sprint:");
            race.sprint_results.forEach(sprint => {
                const driver = db.drivers.findOne({ driverId: sprint.driverId });
                print(`  ${sprint.position}: ${driver.forename} ${driver.surname} - ${sprint.points} puntos`);
            });
        }
    });
}

getSeasonInfo(2024);