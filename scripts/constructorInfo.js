function getConstructorInfo(constructorName) {
    const constructor = db.constructors.findOne({ name: constructorName });
    if (!constructor) {
        print(`No se encontraron datos para el constructores ${constructorName}`);
        return;
    }

    print(`Constructor: ${constructor.name} (${constructor.nationality})`);
    constructor.seasons.forEach(season => {
        print(`    Temporada: ${season.year}`);
        season.races.forEach(race => {
            const raceDetails = db.seasons.findOne({ "races.raceId": race.raceId }, { "races.$": 1 });
            print(`        Carrera: ${raceDetails.races[0].name}`);
            print(`            Puntos: ${race.points}`);
            print(`            Posición: ${race.position || 'N/A'}`);
            print("            Pilotos:");
            race.drivers.forEach(driver => {
                const driverDetails = db.drivers.findOne({ driverId: driver.driverId });
                print(`                - ${driverDetails.forename} ${driverDetails.surname}`);
                print(`                    Posición: ${driver.position || 'DNF'} - ${driver.points} puntos`);
            });
        });
    });
}

getConstructorInfo("McLaren");