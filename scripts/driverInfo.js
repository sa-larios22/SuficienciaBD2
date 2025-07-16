function getDriverInfo(driverSurname) {
    const driver = db.drivers.findOne({ surname: driverSurname });
    if (!driver) {
        print(`No se encontraron datos para el piloto ${driverSurname}`);
        return;
    }

    print(`Piloto: ${driver.forename} ${driver.surname} (${driver.nationality})`);
    driver.seasons.forEach(season => {
        print(`    Temporada: ${season.year}`);
        season.races.forEach(race => {
            const raceDetails = db.seasons.findOne({ "races.raceId": race.raceId }, { "races.$": 1 });
            const constructor = db.constructors.findOne({ constructorId: race.constructorId });
            print(`        Carrera: ${raceDetails.races[0].name}`);
            print(`            Constructor: ${constructor.name}`);
            print(`            Posición: ${race.position || 'DNF'}`);
            print(`            Puntos: ${race.points}`);
            print(`            Vuelta más rápida: ${race.fastestLapTime || 'N/A'}`);
        });
    });
}

getDriverInfo("Hamilton");