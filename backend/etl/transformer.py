import logging
import unicodedata
import pandas as pd
import numpy as np
from core.exceptions import TransformException

logger = logging.getLogger('etl')

COLUMNAS_REQUERIDAS = [
    'nombre', 'edad', 'sexo', 'peso', 'altura',
    'presion_sistolica', 'presion_diastolica',
    'glucosa', 'colesterol', 'frecuencia_cardiaca',
    'saturacion_oxigeno', 'fumador'
]

COLUMNAS_NUMERICAS = [
    'edad', 'peso', 'altura', 'presion_sistolica',
    'presion_diastolica', 'glucosa', 'colesterol',
    'frecuencia_cardiaca', 'saturacion_oxigeno', 'temperatura'
]

RANGOS_CLINICOS = {
    'presion_sistolica': (70, 220),
    'presion_diastolica': (40, 140),
    'glucosa': (20, 600),
    'colesterol': (50, 500),
    'frecuencia_cardiaca': (30, 220),
    'saturacion_oxigeno': (50, 100),
    'edad': (0, 120),
    'peso': (1, 300),
    'altura': (0.3, 2.5),
    'temperatura': (32, 42),
}


def _normalizar_texto(nombre):
    return unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('ASCII').upper()


def _inferir_sexo_por_nombre(nombre):
    tokens = [_normalizar_texto(token) for token in str(nombre).split() if token]
    if not tokens:
        return None

    primer_nombre = tokens[0]
    if primer_nombre in NOMBRES_MASCULINOS and primer_nombre not in NOMBRES_FEMENINOS:
        return 'M'
    if primer_nombre in NOMBRES_FEMENINOS and primer_nombre not in NOMBRES_MASCULINOS:
        return 'F'
    if primer_nombre in NOMBRES_MASCULINOS and primer_nombre in NOMBRES_FEMENINOS:
        return None

    # Fallback: buscar en todos los tokens si el primero no se reconoce
    es_masculino = any(token in NOMBRES_MASCULINOS for token in tokens)
    es_femenino = any(token in NOMBRES_FEMENINOS for token in tokens)

    if es_masculino and not es_femenino:
        return 'M'
    if es_femenino and not es_masculino:
        return 'F'
    return None


NOMBRES_MASCULINOS = {
    'AARON', 'ABEL', 'ABELARDO', 'ABRAHAM', 'ADAN', 'ADOLFO', 'ADRIAN', 'CURRO',
    'AGUSTIN', 'ALAIN', 'ALAN', 'ALBERTO', 'ALCIMEDES', 'ALCIDES', 'ALEJANDRO',
    'ALEX', 'ALEXANDER', 'ALFONSO', 'ALFREDO', 'ALI', 'ALIPIO', 'ALONSO',
    'ALVARO', 'AMADEO', 'AMADO', 'AMBROSIO', 'ANASTACIO', 'ANATOLIO',
    'ANDERSON', 'ANDRES', 'ANDREY', 'ANGEL', 'ANGELO', 'ANIBAL', 'ANSELMO',
    'ANTENOR', 'ANTHONY', 'ANTONIO', 'APOLINAR', 'ARCADIO', 'ARIEL',
    'ARISTIDES', 'ARMANDO', 'ARNOLDO', 'ARQUIMEDES', 'ARTEMIO', 'ARTURO',
    'ASDRUBAL', 'ATILIO', 'AURELIO', 'AURELIANO',
    'BALDOMERO', 'BALTAZAR', 'BARTOLOME', 'BASILIO', 'BELISARIO',
    'BENJAMIN', 'BENITO', 'BENIGNO', 'BERNARDO', 'BERTILIO', 'BERTO',
    'BONIFACIO', 'BORJA', 'BRAULIO', 'BRUNO',
    'CALIXTO', 'CAMILO', 'CANDELARIO', 'CARLOS', 'CARMELO', 'CESAR',
    'CIPRIANO', 'CIRILO', 'CLARO', 'CLAUDIO', 'CLEMENTE', 'CONRADO',
    'CONSTANTINO', 'CRISTIAN', 'CRISTOBAL', 'CRUZ',
    'DAMIAN', 'DANIEL', 'DARIO', 'DAVID', 'DELFIN', 'DEMETRIO',
    'DESIDERIO', 'DIEGO', 'DIONISIO', 'DOMINGO', 'DONATO',
    'EDGAR', 'EDMUNDO', 'EDUARDO', 'EFRAIN', 'ELIAS', 'ELISEO', 'ELOY',
    'ELMER', 'ELPIDIO', 'EMILIANO', 'EMILIO', 'ENRIQUE',
    'EPIFANIO', 'ERASMO', 'ERICK', 'ERNESTO', 'ESDRAS', 'ESTEBAN',
    'ESTANISLAO', 'EUGENIO', 'EUSEBIO', 'EVARISTO', 'EZEQUIEL', 'EZRA',
    'FABIO', 'FABRICIO', 'FAUSTINO', 'FAUSTO', 'FEDERICO', 'FELICIANO',
    'FELIPE', 'FELIX', 'FERMIN', 'FERNANDO', 'FIDEL', 'FILIBERTO',
    'FLAVIO', 'FLORENCIO', 'FLORENTINO', 'FRANCISCO', 'FRANCO',
    'FREDDY', 'FREDY', 'FROILAN',
    'GABRIEL', 'GASPAR', 'GENARO', 'GEOVANNY', 'GERARDO', 'GERSON',
    'GILBERTO', 'GILDARDO', 'GINES', 'GIOVANNI', 'GLAUCO',
    'GONZALO', 'GREGORIO', 'GUILLERMO', 'GUSTAVO',
    'HECTOR', 'HELIODORO', 'HERACLIO', 'HERIBERTO', 'HERMELINDO',
    'HERMES', 'HERNAN', 'HILARIO', 'HOMERO', 'HORACIO', 'HUGO',
    'HUMBERTO',
    'IGNACIO', 'INDALECIO', 'HIPOLITO', 'ISAAC', 'ISAIAS', 'ISIDORO',
    'ISMAEL', 'ISRAEL', 'IVAN',
    'JACINTO', 'JAIME', 'JAVIER', 'JEREMIAS', 'JERONIMO', 'JESUS',
    'JOAQUIN', 'JONATHAN', 'JORGE', 'JOSE', 'JOSEF', 'JOSUE',
    'JUAN', 'JULIAN', 'JULIO', 'JUSTINO',
    'LAZARO', 'LEANDRO', 'LEON', 'LEONARDO', 'LEONCIO', 'LEOPOLDO',
    'LEOVIGILDO', 'LINO', 'LISANDRO', 'LORENZO', 'LORETO',
    'LUCIANO', 'LUCIO', 'LUIS', 'LUCAS',
    'MACARIO', 'MAGIN', 'MALCOM', 'MANUEL', 'MARCELINO', 'MARCELO',
    'MARCIAL', 'MARCIANO', 'MARCO', 'MARCOS', 'MARIANO', 'MARIO',
    'MARTIN', 'MATEO', 'MATIAS', 'MAURICIO', 'MAXIMILIANO',
    'MAXIMO', 'MELCHOR', 'MELITON', 'MIGUEL', 'MINOR', 'MODESTO',
    'MOISES', 'NARCISO', 'NATANAEL', 'NELSON',
    'NEPTALI', 'NESTOR', 'NICANOR', 'NICOLAS', 'NICOMEDES',
    'NORBERTO', 'NORVIN',
    'OCTAVIO', 'ODILON', 'OLIVER', 'OMAR', 'ORESTES', 'ORLANDO',
    'OSCAR', 'OSWALDO', 'OTILIO', 'OTTO', 'OVIDIO',
    'PABLO', 'PASCUAL', 'PATRICIO', 'PAULINO', 'PEDRO', 'PELAYO',
    'PEPITO', 'PERCY', 'PIO', 'PLACIDO', 'PLINIO', 'POLICARPO',
    'PONCIANO', 'PORFIRIO', 'PRIMO', 'PRISCILIANO', 'PROSPERO',
    'PRUDENCIO',
    'QUINTIN', 'QUIRINO',
    'RADAMES', 'RAFAEL', 'RAMIRO', 'RAMON', 'RAUL', 'RAYMUNDO',
    'REINALDO', 'RENE', 'REYES', 'REYNALDO', 'RICARDO', 'RIGOBERTO',
    'ROBERTO', 'ROBINSON', 'RODRIGO', 'ROGER', 'ROGELIO', 'ROLANDO',
    'ROMAN', 'ROMUALDO', 'RONALD', 'RONNY', 'ROQUE', 'ROSENDO',
    'RUBEN', 'RUFINO', 'RUPERTO', 'RUTILIO',
    'SALOMON', 'SALVADOR', 'SAMUEL', 'SANTIAGO', 'SANTO',
    'SATURNINO', 'SAUL', 'SEBASTIAN', 'SECUNDINO', 'SEGUNDO',
    'SEVERIANO', 'SEVERINO', 'SEVERO', 'SIGFRIDO', 'SILVANO',
    'SILVESTRE', 'SILVIO', 'SIMON', 'SOCORRO', 'SONNY',
    'TADEO', 'TELESFORO', 'TEODORO', 'TEODULO', 'TEOFILO',
    'TERENCIO', 'TIBURCIO', 'TIMOTEO', 'TITO', 'TOMAS', 'TOÑO',
    'TORIBIO', 'TRISTAN',
    'ULISES', 'URBANO', 'URIEL',
    'VALENTIN', 'VALERIANO', 'VICENTE', 'VICTOR', 'VICTORIANO',
    'VIDAL', 'VINICIO', 'VIRGILIO', 'VLADIMIR',
    'WALDO', 'WALTER', 'WILBER', 'WILFREDO', 'WILMER', 'WILSON',
    'XAVIER',
    'YADIER', 'YONI', 'YORDAN',
    'ZACARIAS', 'ZEKE',
    'AMADOR', 'CLEMENTE', 'CONTENTO', 'CRESCENCIO', 'FORTUNATO',
    'GRACILIANO', 'INOCENCIO', 'JUSTO', 'LADISLAO', 'NEMESIO',
    'PEREGRINO', 'REMIGIO', 'RENATO', 'SIXTO', 'VITO',
    'SERGIO', 'SAULO',
    'EDER', 'JEFERSON', 'WILLIAM', 'JHON', 'JHONY', 'JHOAN',
    'DEIVID', 'DEIBY', 'BRAYAN', 'KEVIN', 'BRANDON',
    'YEFERSON', 'YEISON', 'YOBAN', 'YONATAN',
    'JUNIOR', 'MAIKEL', 'MICHAEL', 'STIVEN', 'JEFFERSON',
    'ADRIEL', 'HANS', 'DERRICK', 'ELVIN', 'ISIDRO',
    'CELSO', 'CORNELIO', 'JACOBO', 'FULGENCIO', 'YAGO',
    'CELESTINO', 'CIRO', 'EDILBERTO', 'ELIGIO', 'HIGINIO',
    'HONORIO', 'MANOLO', 'PEPE', 'TEODOSIO', 'VALERIO',
    'ADELMO', 'NILO', 'EMIGDIO', 'CRISTHIAN',
    'ABEL', 'ADRIAN', 'ALAN', 'ALEX', 'ALEXANDER', 'ALFONSO',
    'ALONSO', 'ALVARO', 'ANDRES', 'ANGEL', 'ANTONIO', 'ARIEL',
    'ARTURO', 'BENJAMIN', 'BORJA', 'BRUNO', 'CAMILO',
    'CARLOS', 'CESAR', 'CRISTIAN', 'CRISTOBAL', 'DANIEL',
    'DARIO', 'DAVID', 'DIEGO', 'DOMINGO', 'EDUARDO',
    'EMILIO', 'ENRIQUE', 'ERNESTO', 'ESTEBAN', 'EUGENIO',
    'FABIO', 'FELIPE', 'FELIX', 'FERMIN', 'FERNANDO',
    'FIDEL', 'FLAVIO', 'FLORENCIO', 'FLORENTINO',
    'FRANCISCO', 'GABRIEL', 'GERARDO', 'GONZALO',
    'GUILLERMO', 'GUSTAVO', 'HECTOR', 'HERNAN', 'HILARIO',
    'HORACIO', 'HUGO', 'HUMBERTO', 'IGNACIO', 'IKER',
    'ISAAC', 'ISMAEL', 'ISRAEL', 'IVAN', 'JACINTO',
    'JAIME', 'JAVIER', 'JEREMIAS', 'JERONIMO', 'JESUS',
    'JOAQUIN', 'JONATAN', 'JORGE', 'JOSE', 'JOSEP',
    'JOSUE', 'JUAN', 'JULIAN', 'JULIO', 'LEANDRO',
    'LEONARDO', 'LEONCIO', 'LINO', 'LISANDRO', 'LOPE',
    'LORENZO', 'LORETO', 'LUCIANO', 'LUCIO', 'LUCAS',
    'LUIS', 'MACARIO', 'MANOLO', 'MANUEL', 'MARC',
    'MARCELINO', 'MARCELO', 'MARCIANO', 'MARCO', 'MARCOS',
    'MARIANO', 'MARIO', 'MARTIN', 'MATEO', 'MATIAS',
    'MAURICIO', 'MAXIMILIANO', 'MAXIMINO', 'MAXIMO',
    'MELCHOR', 'MIGUEL', 'MODESTO', 'MOISES', 'NACHO',
    'NACIO', 'NANDO', 'NARCISO', 'NATALIO', 'NAZARIO',
    'NICANOR', 'NICO', 'NICODEMO', 'NICOLAS', 'NILO',
    'OLEGARIO', 'OMAR', 'OSVALDO', 'OVIDIO', 'PABLO',
    'PANCHO', 'PASCUAL', 'PASTOR', 'PATRICIO', 'PAULINO',
    'PEDRO', 'PELAYO', 'PEPE', 'PEPITO', 'PLINIO',
    'PONCIO', 'PORFIRIO', 'PRIMITIVO', 'PRUDENCIO',
    'QUIQUE', 'QUIRINO', 'RAFAEL', 'RAIMUNDO', 'RAMIRO',
    'RAMON', 'RAUL', 'REINALDO', 'REMIGIO', 'RENATO',
    'RICARDO', 'ROBERTO', 'RODOLFO', 'RODRIGO', 'ROGELIO',
    'ROLANDO', 'ROMAN', 'ROQUE', 'RUBEN', 'RUFINO',
    'SALOMON', 'SALVADOR', 'SAMUEL', 'SANDALIO', 'SANTOS',
    'SATURNINO', 'SEBASTIAN', 'SEGIS', 'SERGIO', 'SEVERIANO',
    'SEVERINO', 'SIGFRIDO', 'SILVIO', 'SIMON', 'SOCORRO',
    'SOSIMO', 'TADEO', 'TEO', 'TEOBALDO', 'TEODORO',
    'TEODOSIO', 'TEOFILO', 'TIBURCIO', 'TITO', 'TOMAS',
    'TONI', 'TONO', 'TORIBIO', 'TRISTAN', 'ULISES',
    'URBANO', 'VALENTIN', 'VALERIO', 'VALERO', 'VASCO',
    'VICENTE', 'VICTOR', 'VICTORIANO', 'VIDAL', 'VINICIO',
    'VIRGILIO', 'VITO', 'WALTER', 'WILFREDO', 'XAVIER',
    'YAGO', 'ZACARIAS',
}

NOMBRES_FEMENINOS = {
    'ABIGAIL', 'ADELA', 'ADELAIDA', 'ADELINA', 'ADRIANA', 'AGUSTINA',
    'AIDA', 'AINA', 'AINHOA', 'ALBA', 'ALEJANDRA', 'ALEXANDRA',
    'ALFONSINA', 'ALICIA', 'ALINA', 'ALMA', 'ALONDRA', 'ALTAGRACIA',
    'AMADA', 'AMALIA', 'AMANDA', 'AMBAR', 'AMELIA', 'AMPARO',
    'ANA', 'ANABEL', 'ANALIA', 'ANASTASIA', 'ANDREA', 'ANGELA',
    'ANGELES', 'ANGELICA', 'ANGELITA', 'ANITA', 'ANNA', 'ANTONIA', 'APOLONIA',
    'ARACELI', 'ARACELY', 'ARANTZA', 'ARIANA', 'ARIANE', 'ARLENE',
    'ARTEMISA', 'ASUNCION', 'AUGUSTA', 'AURA', 'AUXILIADORA',
    'AVRIL', 'AZUCENA', 'AZUL',
    'BALBINA', 'BARBARA', 'BASILISA', 'BEGOÑA', 'BELEN', 'BERNARDA',
    'BERENICE', 'BERNARDINA', 'BETSABE', 'BIANCA', 'BLANCA', 'BRENDA',
    'BRIANDA', 'BRIGIDA', 'BRIGITTE',
    'CANDELARIA', 'CANDIDA', 'CARIDAD', 'CARLA', 'CARLOTA',
    'CARMEN', 'CAROLINA', 'CASANDRA', 'CATALINA', 'CATERINA',
    'CECILIA', 'CELESTE', 'CELIA', 'CELINA', 'CIRA', 'CLARA',
    'CLARISA', 'CLAUDIA', 'CLOTILDE', 'COLUMBA', 'CONCEPCION',
    'CONCORDIA', 'CONSUELO', 'CORAL', 'CORINA', 'CRISTINA', 'CRUZ',
    'DALILA', 'DANIELA', 'DARLENE', 'DEBORA', 'DELFINA', 'DELIA',
    'DENISSE', 'DESIREE', 'DIANA', 'DINA', 'DINORA', 'DOLORES',
    'DOMINGA', 'DOMITILA', 'DONATA', 'DORA', 'DORIS', 'DORITA', 'DULCE',
    'EDELMIRA', 'EDITH', 'EDUVIGES', 'ELENA', 'ELIANA', 'ELIGIA',
    'ELISA', 'ELISABETH', 'ELISENDA', 'ELMA', 'ELOISA', 'ELSA',
    'ELVIRA', 'EMELINA', 'EMILIA', 'EMILIANA', 'EMPERATRIZ',
    'ENCARNACION', 'ERIKA', 'ERMELINDA', 'ERNESTINA', 'ESMERALDA',
    'ESPERANZA', 'ESTEFANIA', 'ESTELA', 'ESTER', 'ESTRELLA',
    'EUGENIA', 'EULALIA', 'EUSEBIA', 'EVA', 'EVANGELINA', 'EVELYN',
    'EVITA',
    'FABIOLA', 'FATIMA', 'FELICIA', 'FELICITAS', 'FELICIDAD',
    'FELICITACION', 'FERNANDA', 'FIDELA', 'FILIPA', 'FILOMENA',
    'FLOR', 'FLORA', 'FLORENCIA', 'FLORENTINA', 'FRANCISCA',
    'GABRIELA', 'GEMA', 'GENOVEVA', 'GEORGINA', 'GERARDA',
    'GERMANA', 'GERTRUDIS', 'GILDA', 'GIMENA', 'GINA', 'GLADYS',
    'GLENDA', 'GLORIA', 'GRACIA', 'GRACIELA', 'GRISELDA',
    'GUADALUPE', 'GUILLERMINA', 'GUMERSINDA',
    'HAYDEE', 'HELENA', 'HERLINDA', 'HERMINIA', 'HILARIA',
    'HORTENSIA',
    'IBIS', 'IDA', 'ILIANA', 'INES', 'INFANTITA', 'INMACULADA',
    'IRENE', 'IRIS', 'IRMA', 'ISABEL', 'ISIDRA', 'ISOLINA',
    'ITZEL', 'IVETTE',
    'JACINTA', 'JAQUELINE', 'JASMIN', 'JENNIFER', 'JERONIMA',
    'JESSICA', 'JIMENA', 'JOAQUINA', 'JOSEFA', 'JOSEFINA',
    'JUANA', 'JULIA', 'JULIANA', 'JULIETA',
    'KAREN', 'KARINA', 'KATHERINE', 'KATIA', 'KIMBERLY',
    'LAURA', 'LEANDRA', 'LEIRE', 'LENA', 'LEOCADIA', 'LEONARDA',
    'LEONCIA', 'LEONOR', 'LETICIA', 'LIDIA', 'LIEN', 'LILIA',
    'LILIANA', 'LINA', 'LISBETH', 'LIVIA', 'LORENA', 'LORENZA',
    'LOURDES', 'LUCIA', 'LUCIANA', 'LUCILA', 'LUCINDA', 'LUDIVINA',
    'LUISA', 'LUISANA', 'LUPITA', 'LUZ',
    'MACARENA', 'MAGDALENA', 'MAGNOLIA', 'MANUELA', 'MARA',
    'MARCELA', 'MARCELINA', 'MARGARITA', 'MARIA',
    'MARIANA', 'MARICELA', 'MARIELA', 'MARILINA', 'MARILU',
    'MARINA', 'MARIPAZ', 'MARISELA', 'MARISOL', 'MARTA', 'MARTINA',
    'MATILDE', 'MAURA', 'MELANIA', 'MELBA', 'MELISA', 'MERCEDES',
    'MICAELA', 'MIGUELA', 'MINERVA', 'MIRANDA',
    'MIRIAM', 'MIRNA', 'MODESTA', 'MONICA', 'MONTSERRAT',
    'NANCY', 'NARCISA', 'NATALIA', 'NATALY', 'NATIVIDAD',
    'NAYELI', 'NELIDA', 'NEREIDA', 'NICOLE', 'NICOLASA',
    'NIEVES', 'NILDA', 'NOELIA', 'NOEMI', 'NORMA',
    'OBDULIA', 'OCTAVIA', 'ODALIS', 'ODALYS', 'OFELIA', 'OLGA', 'OLIMPIA',
    'OLIVIA', 'ORFELINA', 'OTILIA',
    'PABLA', 'PALOMA', 'PAOLA', 'PATRICIA', 'PAULA', 'PAULINA',
    'PAZ', 'PEARLA', 'PENELOPE', 'PERLA', 'PETRA', 'PETRONILA',
    'PILAR', 'PRISCILA', 'PRUDENCIA', 'PURIFICACION',
    'RAFAELA', 'RAMONA', 'RAQUEL', 'REBECA', 'REFUGIO',
    'REGINA', 'REINA', 'RENATA', 'RITA', 'ROBERTA', 'ROCIO',
    'RODOLFA', 'ROSA', 'ROSALBA', 'ROSALIA', 'ROSALINDA', 'ROSANA',
    'ROSARIO', 'ROSENDA', 'ROSITA', 'RUFINA', 'RUPERTA', 'RUTH',
    'SABINA', 'SALOME', 'SAMANTHA', 'SANDRA', 'SARA', 'SARITA',
    'SATURNINA', 'SELENA', 'SELENE', 'SERE', 'SERENA',
    'SILVIA', 'SILVINA', 'SOCORRO', 'SONIA', 'SORAYA', 'SOFIA',
    'SOLEDAD', 'SUSANA', 'SUSY',
    'TANIA', 'TATIANA', 'TEODORA', 'TEOFILA', 'TERESA', 'TEODOSIA',
    'TIMOTEA', 'TOMASA', 'TRINIDAD',
    'ULALIA', 'URBANA', 'URSULA',
    'VALENTINA', 'VALERIA', 'VANESA', 'VICENTA', 'VICTORIA',
    'VIOLETA', 'VIRGINIA', 'VISITACION',
    'WENDY', 'WILMA',
    'XIOMARA', 'XIMENA', 'XISCA',
    'YADIRA', 'YANET', 'YANIRA', 'YARA', 'YARITZA', 'YASMIN',
    'YENIFER', 'YESENIA', 'YOLANDA', 'YOLIMA',
    'ZORAIDA', 'ZULEMA', 'ZULMA',
    'CHUS', 'FIORELLA', 'GIANELLA', 'LUZMILA',
    'MAITE', 'NURIA', 'VERONICA', 'VIVIANA',
    'BERNARDITA', 'CARMINA', 'DANIELA',
    'ELIZABETH', 'ESTHER', 'MACARIA', 'MARITZA',
    'MAXIMA', 'PAQUITA', 'PASTORA',
    'PRESENTACION', 'PURA', 'REMEDIOS',
    'ROSAURA', 'SEVERA', 'VIRTUDES', 'AFRICA',
    'DANIA', 'ELVIA', 'ERLINDA', 'ETHEL', 'FANNY',
    'GILMA', 'HILDA', 'INDIRA', 'IVONNE',
    'KARLA', 'LOIDA', 'MARBELY', 'MARY',
    'NINFA', 'NORA', 'OLIVA',
    'ROSALVA', 'SULEMA', 'YULI', 'YULIANA',
    'MARCIA', 'ZENAIDA', 'ELODIA',
    'AINOA', 'AINOHA', 'CANDELA', 'CLOE',
    'CONCHITA', 'MILAGROS', 'MILAGRO', 'ROXANA',
    'LOLA', 'ODIS',
    'AMARILIS', 'AURELIA', 'ELBA', 'CHITA',
    'FLORA', 'GLORIA', 'ALBA', 'ALMA', 'MARTA', 'IRENE',
    'LUCIA', 'ELENA', 'ANDREA', 'CARLA', 'ROSA', 'SONIA',
    'LIDIA', 'MARINA', 'SILVIA', 'NORMA', 'INES', 'IRMA',
    'MARIA', 'CELIA', 'ELISA', 'LAURA', 'OLGA',
    'EMMA', 'PEPITA', 'FLORINDA', 'BEATRIZ', 'CAMILA',
    'FELISA', 'FIDELA', 'FILOMENA', 'FLORINA', 'FORTUNATA',
    'GERALDA', 'GRACIANA', 'GUIOMAR', 'ILEANA', 'ISAURA',
    'JACINTA', 'JESUSA', 'JIMENA', 'JORDANA', 'JULIETA',
    'LEANDRA', 'LEOCADIA', 'LETICIA', 'LEYRE', 'LIGIA',
    'LILIA', 'LUCIANA', 'LUCILA', 'LUISINA', 'LUNA',
    'LUPE', 'MACARIA', 'MAGDALENA', 'MANUELA', 'MARCELA',
    'MARGARITA', 'MARIANA', 'MARIBEL', 'MARICELA', 'MARICRUZ',
    'MARISOL', 'MARTINA', 'MATILDE', 'MAURA', 'MELANIA',
    'MELISA', 'MICAELA', 'MIGUELA', 'MILAGROS', 'MIRTA',
    'MODESTA', 'MONICA', 'MORENA', 'NARCISA', 'NATIVIDAD',
    'NICOLASA', 'NOELIA', 'NOEMI', 'OCTAVIA', 'OFELIA',
    'OLIMPIA', 'OLIVIA', 'OTILIA', 'PALOMA', 'PAOLA',
    'PASCUALA', 'PASTORA', 'PAULA', 'PAULINA', 'PERLA',
    'PERLITA', 'PETRONA', 'PIEDAD', 'PRISCILA', 'PRUDENCIA',
    'PURIFICACION', 'RAMONA', 'REBECA', 'REGINA', 'RENATA',
    'RICARDA', 'RITA', 'ROBERTA', 'ROCIO', 'ROSALINA',
    'ROSALINDA', 'ROSALVA', 'ROSALIA', 'ROSARIO', 'ROSAURA',
    'ROSENDA', 'ROXANA', 'RUPERTA', 'SABINA', 'SARITA',
    'SATURNINA', 'SELENA', 'SOLEDAD', 'TAMARA', 'TANIA',
    'TATIANA', 'TECLA', 'TEODORA', 'TEOFILA', 'TOMASA',
    'TRINIDAD', 'VALENTINA', 'VALERIA', 'VANESA', 'VICENTA',
    'VIOLETA', 'VIRGINIA', 'VISITACION', 'VIVIANA', 'XIMENA',
    'XIOMARA', 'YAIZA', 'ZAIDA', 'ZAIRA',
}


class DataTransformer:
    def transform(self, df):
        logger.info('Iniciando transformación de datos')
        df = df.copy()
        registros_iniciales = len(df)
        errores = 0

        df = self._normalizar_columnas(df)
        df = self._eliminar_duplicados(df)
        df = self._corregir_tipos(df)
        df = self._limpiar_errores_ortograficos(df)
        df = self._imputar_nulos(df)
        df = self._validar_rangos_clinicos(df)
        df = self._normalizar_variables_categoricas(df)
        df = self._corregir_sexo_por_nombre(df)
        df = self._calcular_imc(df)
        df = self._clasificar_imc(df)
        df = self._clasificar_riesgo(df)

        registros_finales = len(df)
        logger.info(f'Transformación completada: {registros_finales} registros limpios')

        return df, {
            'iniciales': registros_iniciales,
            'finales': registros_finales,
            'eliminados': registros_iniciales - registros_finales,
        }

    def _normalizar_columnas(self, df):
        df.columns = [col.strip().lower().replace(' ', '_').lstrip('\ufeff') for col in df.columns]
        mapping = {
            'nombre': 'nombre', 'nombre_completo': 'nombre', 'nombres': 'nombre',
            'nombre_del_paciente': 'nombre', 'paciente': 'nombre', 'name': 'nombre',
            'nombres_y_apellidos': 'nombre', 'nombre_paciente': 'nombre',

            'edad': 'edad', 'edad_(años)': 'edad', 'edad_años': 'edad',
            'edad_en_años': 'edad', 'age': 'edad', 'años': 'edad',

            'sexo': 'sexo', 'genero': 'sexo', 'género': 'sexo', 'sex': 'sexo',

            'peso': 'peso', 'peso_(kg)': 'peso', 'peso_kg': 'peso',
            'weight': 'peso', 'peso_corporal': 'peso',

            'altura': 'altura', 'altura_(m)': 'altura', 'altura_m': 'altura',
            'talla': 'altura', 'estatura': 'altura', 'height': 'altura',

            'presion_sistolica': 'presion_sistolica',
            'presión_sistólica': 'presion_sistolica',
            'sistolica': 'presion_sistolica', 'sistólica': 'presion_sistolica',
            'presion_arterial_sistolica': 'presion_sistolica',
            'presión_arterial_sistólica': 'presion_sistolica',
            'systolic': 'presion_sistolica', 'systolic_bp': 'presion_sistolica',
            'pas': 'presion_sistolica',

            'presion_diastolica': 'presion_diastolica',
            'presión_diastólica': 'presion_diastolica',
            'diastolica': 'presion_diastolica', 'diastólica': 'presion_diastolica',
            'presion_arterial_diastolica': 'presion_diastolica',
            'presión_arterial_diastólica': 'presion_diastolica',
            'diastolic': 'presion_diastolica', 'diastolic_bp': 'presion_diastolica',
            'pad': 'presion_diastolica',

            'glucosa': 'glucosa', 'glucosa_(mg/dl)': 'glucosa',
            'glucosa_mg/dl': 'glucosa', 'glucosa_mg_dl': 'glucosa',
            'glucose': 'glucosa', 'nivel_glucosa': 'glucosa',
            'azúcar_en_sangre': 'glucosa', 'glucosa_en_ayunas': 'glucosa',

            'colesterol': 'colesterol', 'colesterol_(mg/dl)': 'colesterol',
            'colesterol_mg/dl': 'colesterol', 'colesterol_mg_dl': 'colesterol',
            'cholesterol': 'colesterol', 'colesterol_total': 'colesterol',
            'nivel_colesterol': 'colesterol',

            'frecuencia_cardiaca': 'frecuencia_cardiaca',
            'frecuencia_cardíaca': 'frecuencia_cardiaca',
            'frecuencia_cardiaca_(lpm)': 'frecuencia_cardiaca',
            'frecuencia_cardiaca_lpm': 'frecuencia_cardiaca',
            'heart_rate': 'frecuencia_cardiaca', 'pulso': 'frecuencia_cardiaca',
            'fc': 'frecuencia_cardiaca',
            'frecuencia_cardiaca_bpm': 'frecuencia_cardiaca',

            'saturacion_oxigeno': 'saturacion_oxigeno',
            'saturación_oxígeno': 'saturacion_oxigeno',
            'saturacion_oxigeno_(%)': 'saturacion_oxigeno',
            'saturacion_oxigeno_%': 'saturacion_oxigeno',
            'oxygen_saturation': 'saturacion_oxigeno',
            'spo2': 'saturacion_oxigeno', 'sp_o2': 'saturacion_oxigeno',
            'sat_oxigeno': 'saturacion_oxigeno', 'o2_sat': 'saturacion_oxigeno',
            'oxigenacion': 'saturacion_oxigeno',

            'fumador': 'fumador', 'fuma': 'fumador', 'tabaquismo': 'fumador',
            'habito_tabaquico': 'fumador', 'hábito_tabáquico': 'fumador',
            'es_fumador': 'fumador', 'smoker': 'fumador', 'smoking': 'fumador',

            'consumidor_alcohol': 'consumidor_alcohol',
            'consumo_alcohol': 'consumidor_alcohol', 'alcohol': 'consumidor_alcohol',
            'bebedor': 'consumidor_alcohol', 'alcoholico': 'consumidor_alcohol',
            'alcoholic': 'consumidor_alcohol', 'alcohol_consumption': 'consumidor_alcohol',

            'actividad_fisica': 'actividad_fisica',
            'actividad_física': 'actividad_fisica', 'ejercicio': 'actividad_fisica',
            'nivel_actividad': 'actividad_fisica', 'physical_activity': 'actividad_fisica',

            'temperatura': 'temperatura',
            'temperatura_(ºC)': 'temperatura', 'temp': 'temperatura',
            'temperature': 'temperatura', 'temperatura_corporal': 'temperatura',

            'antecedentes_familiares': 'antecedentes_familiares',
            'antecedentes': 'antecedentes_familiares',
            'antecedentes_familiares_paciente': 'antecedentes_familiares',
            'family_history': 'antecedentes_familiares',

            'diagnostico': 'diagnostico',
            'diagnóstico': 'diagnostico',
            'diagnosis': 'diagnostico',
            'patología': 'diagnostico',
            'patologia': 'diagnostico',
            'enfermedad': 'diagnostico',
            'condición': 'diagnostico',
            'condicion': 'diagnostico',

            'fecha_consulta': 'fecha_consulta',
            'fecha_de_consulta': 'fecha_consulta', 'fecha_atencion': 'fecha_consulta',
            'fecha_atención': 'fecha_consulta', 'fecha_visita': 'fecha_consulta',
            'consultation_date': 'fecha_consulta', 'visit_date': 'fecha_consulta',

            'apellido': 'apellido', 'apellidos': 'apellido',
            'surname': 'apellido', 'last_name': 'apellido',
            'lastname': 'apellido', 'primer_apellido': 'apellido',
            'segundo_apellido': 'apellido',
        }
        df = df.rename(columns=mapping)

        if 'apellido' in df.columns and 'nombre' in df.columns:
            df['nombre'] = df['nombre'].fillna('').astype(str).str.strip() + ' ' + df['apellido'].fillna('').astype(str).str.strip()
            df['nombre'] = df['nombre'].str.strip()
            df = df.drop(columns=['apellido'])

        for col in COLUMNAS_REQUERIDAS:
            if col not in df.columns:
                raise TransformException(f'Columna requerida no encontrada: {col}')
        return df

    def _eliminar_duplicados(self, df):
        antes = len(df)
        df = df.drop_duplicates(subset=['nombre', 'edad', 'sexo'], keep='last')
        despues = len(df)
        if antes > despues:
            logger.info(f'Duplicados eliminados: {antes - despues}')
        return df

    def _corregir_tipos(self, df):
        for col in COLUMNAS_NUMERICAS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        for col, bool_map in [('fumador', True), ('consumidor_alcohol', True)]:
            if col in df.columns:
                df[col] = df[col].map({
                    'SI': True, 'si': True, 'Si': True, 'SÍ': True, 'sí': True,
                    'YES': True, 'yes': True, 'Yes': True, 'Y': True, '1': True, 1: True, 'true': True, True: True,
                    'NO': False, 'no': False, 'No': False, 'N': False, '0': False, 0: False, 'false': False, False: False,
                })
                df[col] = df[col].fillna(False).astype(bool)

        if 'fecha_consulta' in df.columns:
            df['fecha_consulta'] = pd.to_datetime(df['fecha_consulta'], errors='coerce')

        return df

    def _limpiar_errores_ortograficos(self, df):
        if 'sexo' in df.columns:
            df['sexo'] = df['sexo'].str.strip().str.upper()
            df['sexo'] = df['sexo'].replace({
                'HOMBRE': 'M', 'VARON': 'M', 'MASCULINO': 'M', 'M': 'M',
                'MUJER': 'F', 'FEMENINO': 'F', 'FEMENINA': 'F', 'F': 'F',
            })
            df.loc[~df['sexo'].isin(['M', 'F']), 'sexo'] = 'O'

        if 'nombre' in df.columns:
            df['nombre'] = df['nombre'].str.strip().str.title()
            df['nombre'] = df['nombre'].replace(r'\s+', ' ', regex=True)

        return df

    def _imputar_nulos(self, df):
        for col in COLUMNAS_NUMERICAS:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    logger.info(f'Nulos imputados en {col}: {null_count} con mediana={median_val:.2f}')
        return df

    def _validar_rangos_clinicos(self, df):
        for col, (min_val, max_val) in RANGOS_CLINICOS.items():
            if col in df.columns:
                fuera_rango = ((df[col] < min_val) | (df[col] > max_val)).sum()
                if fuera_rango > 0:
                    df[col] = df[col].clip(min_val, max_val)
                    logger.info(f'Valores fuera de rango corregidos en {col}: {fuera_rango}')
        return df

    def _normalizar_variables_categoricas(self, df):
        if 'diagnostico' in df.columns:
            df['diagnostico'] = df['diagnostico'].str.strip().str.upper()

        if 'actividad_fisica' in df.columns:
            df['actividad_fisica'] = df['actividad_fisica'].str.strip().str.upper()
            df['actividad_fisica'] = df['actividad_fisica'].replace({
                'SEDENTARIO': 'SEDENTARIO', 'SEDENTARIA': 'SEDENTARIO',
                'NO_REALIZA': 'SEDENTARIO', 'NINGUNA': 'SEDENTARIO', 'INACTIVO': 'SEDENTARIO',
                'MODERADO': 'MODERADO', 'MODERADA': 'MODERADO',
                'ACTIVO': 'ACTIVO', 'ACTIVA': 'ACTIVO', 'REGULAR': 'ACTIVO',
                'INTENSO': 'INTENSO', 'INTENSA': 'INTENSO', 'INTENSA': 'INTENSO',
                'ALTO': 'INTENSO', 'MUY_ACTIVO': 'INTENSO', 'MUY_ACTIVA': 'INTENSO',
            })
            valores_validos = {'SEDENTARIO', 'MODERADO', 'ACTIVO', 'INTENSO'}
            df.loc[~df['actividad_fisica'].isin(valores_validos), 'actividad_fisica'] = None

        return df

    def _corregir_sexo_por_nombre(self, df):
        if 'nombre' not in df.columns or 'sexo' not in df.columns:
            return df

        sexo_inferido = df['nombre'].fillna('').astype(str).apply(_inferir_sexo_por_nombre)
        cambios_m = sexo_inferido.eq('M') & (df['sexo'] != 'M')
        cambios_f = sexo_inferido.eq('F') & (df['sexo'] != 'F')

        df.loc[cambios_m, 'sexo'] = 'M'
        df.loc[cambios_f, 'sexo'] = 'F'

        if cambios_m.any() or cambios_f.any():
            logger.info(f'Sexo corregido por nombre completo: {cambios_m.sum()} a M, {cambios_f.sum()} a F')
        return df

    def _calcular_imc(self, df):
        df['imc'] = np.where(
            (df['peso'] > 0) & (df['altura'] > 0),
            df['peso'] / (df['altura'] ** 2),
            np.nan
        )
        df['imc'] = df['imc'].round(1)
        logger.info(f'IMC calculado para {df["imc"].notna().sum()} pacientes')
        return df

    def _clasificar_imc(self, df):
        condiciones = [
            df['imc'] < 18.5,
            (df['imc'] >= 18.5) & (df['imc'] < 25),
            (df['imc'] >= 25) & (df['imc'] < 30),
            (df['imc'] >= 30) & (df['imc'] < 35),
            (df['imc'] >= 35) & (df['imc'] < 40),
            df['imc'] >= 40,
        ]
        clasificaciones = [
            'BAJO_PESO', 'NORMAL', 'SOBREPESO',
            'OBESIDAD_I', 'OBESIDAD_II', 'OBESIDAD_III'
        ]
        df['imc_clasificacion'] = np.select(condiciones, clasificaciones, default='NORMAL')
        return df

    def _clasificar_riesgo(self, df):
        condiciones = [
            (df['presion_sistolica'] > 180) | (df['glucosa'] > 300) | (df['saturacion_oxigeno'] < 85),
            (df['presion_sistolica'] > 160) | (df['glucosa'] > 250) | (df['colesterol'] > 300) | (df['imc'] >= 35),
            (df['presion_sistolica'] > 140) | (df['glucosa'] > 200) | (df['colesterol'] > 240) | (df['fumador'] == True) | (df['imc'] >= 30),
        ]
        riesgos = ['CRITICO', 'ALTO', 'MEDIO']
        df['riesgo'] = np.select(condiciones, riesgos, default='BAJO')
        logger.info(f'Riesgo clasificado: {df["riesgo"].value_counts().to_dict()}')
        return df
