from random import randint

from applications.audit.models import Audit, Audit_UserActivity
from applications.const import *
import random, string

from applications.users.models import Customer

def createUserActivityAudit(userActivity: str, customer: Customer):
    newAudit = Audit()
    newAudit.customer = customer
    newUserActivityAudit = Audit_UserActivity()
    newUserActivityAudit.audit = newAudit
    match userActivity:
        case "Email":
            newUserActivityAudit.emailChanged = True
        case "Password":
            newUserActivityAudit.passwordChanged = True
        case "Phone_Number":
            newUserActivityAudit.phoneNumberChanged = True
        case _:
            return
    newAudit.save()
    newUserActivityAudit.save()
    return


def alias_generator() -> str:
    four_letter_words = [
        "casa", "mesa", "luz", "pato", "sopa", "lago", "pico", "dona", "codo", "sala",
        "bano", "cara", "peor", "lira", "boca", "cama", "nube", "seda", "taco", "sana",
        "fama", "arma", "cola", "lima", "toro", "saco", "bajo", "celo", "jugo", "calo",
        "lado", "bote", "mama", "miel", "tina", "pala", "nene", "piso", "besa", "moro",
        "pepa", "cero", "vivo", "frio", "dado", "sino", "coco", "biri", "rata", "vaca",
        "oro", "rey", "sal", "caja", "voto", "tela", "jota", "fito", "buto", "mono",
        "cata", "guia", "pila", "pelo", "mira", "fuma", "kilo", "cada", "hilo", "lomo",
        "lira", "tapa", "pata", "lazo", "dura", "flor", "pasa", "solo", "nino", "rojo",
        "gria", "luto", "faro", "vida", "bota", "milo", "rima", "seda", "toro", "fino",
        "moro", "pico", "mole", "mari", "tina", "cama", "lago", "sal", "caro", "toro",
        "lago", "bici", "riso", "mato", "baza", "cala", "taco", "vino", "dama", "pato",
        "rayo", "baza", "puma", "losa", "nube", "rojo", "vela", "boda", "gato", "fama",
        "cero", "dino", "jaro", "pila", "vino", "papa", "belo", "moro", "celo", "bajo",
        "rima", "cota", "toro", "mira", "sola", "nube", "pito", "rata", "vara", "tapa",
        "milo", "caza", "nene", "duna", "sola", "taza", "biso", "lira", "sino", "cato",
        "gato", "mayo", "rima", "cabe", "loro", "sala", "sana", "tino", "palo", "dosa",
        "bama", "dama", "kilo", "moto", "lama", "pica", "pepa", "tola", "tira", "tato",
        "saco", "buna", "rino", "lido", "pano", "vaca", "silo", "gama", "raco", "mira",
        "mora", "doro", "lata", "bona", "lama", "risa", "baco", "cima", "toro", "doro"
    ]
    five_letter_words = [
        "coche", "tigre", "mujer", "pueblo", "flore", "tinta", "lomos", "salas", "perro", "corso",
        "canto", "rango", "famos", "banco", "silla", "piano", "suerte", "camis", "brote", "río",
        "huevo", "guapo", "pinta", "gente", "nacer", "canto", "largo", "fruta", "luzca", "nieve",
        "gordo", "nacer", "raton", "pueblo", "aura", "canto", "pasta", "joven", "denso", "tazas",
        "carga", "calor", "borde", "bicho", "carro", "nacer", "sello", "fondo", "corre", "ramon",
        "cerca", "falle", "cocina", "ciencia", "lucha", "mundo", "ciudad", "garra", "rueda", "juego",
        "ganar", "novia", "honor", "brisa", "horas", "mujer", "lomos", "reina", "sudor", "torre",
        "molar", "manta", "fuego", "nacer", "manos", "dentro", "salir", "salud", "flota", "horiz",
        "banda", "plato", "llama", "llave", "tapas", "pasta", "torre", "falsa", "garra", "tiempo",
        "velas", "llave", "perro", "lomos", "tanto", "pulga", "espejo", "papel", "carne", "piano"
    ]

    first = ''.join(random.choice(four_letter_words))
    second =''.join(random.choice(five_letter_words))
    third =''.join(random.choice(four_letter_words))
    return f'{first}.{second}.{third}'

def cuenta_unica_generator(psp: str, client_id: str, virtual: bool) -> str:
    if len(psp) != 4:
        raise ValueError("psp length should be 4")

    if len(client_id) != 12:
        raise ValueError("client id length should be 12")

    if virtual:
        key_indicator = NUMERO_DE_ENTIDAD_VIRTUAL
    else:
        key_indicator = NUMERO_DE_ENTIDAD_BANCARIA
    reserved_digit = str(randint(0, 9))

    # Calculus for the first verifier digit
    try:
        psp_chars = get_characters_to_int(psp)
    except ValueError as e:
        raise ValueError(e)

    sum1 = psp_chars[0] * 9 + psp_chars[1] * 7 + psp_chars[2] * 1 + psp_chars[3] * 3

    difference1 = 10 - get_last_digit(sum1)

    if difference1 == 10:
        first_verifier_digit = str(randint(0, 9))
    else:
        first_verifier_digit = str(difference1)

    # Calculus for the second verifier digit
    try:
        client_id_chars = get_characters_to_int(client_id)
    except ValueError as e:
        raise ValueError(e)

    sum2 = (
            client_id_chars[0] * 9 + client_id_chars[1] * 7 + client_id_chars[2] * 1 +
            client_id_chars[3] * 3 + client_id_chars[4] * 9 + client_id_chars[5] * 7 +
            client_id_chars[6] * 1 + client_id_chars[7] * 3 + client_id_chars[8] * 9 +
            client_id_chars[9] * 7 + client_id_chars[10] * 1 + client_id_chars[11] * 3
    )

    difference2 = 10 - get_last_digit(sum2)

    if difference2 == 10:
        second_verifier_digit = str(randint(0, 9))
    else:
        second_verifier_digit = str(difference2)

    # CVU building
    cvu = key_indicator + psp + first_verifier_digit + reserved_digit + client_id + second_verifier_digit

    if len(cvu) != 22:
        raise ValueError("error building cvu")

    return cvu

def get_characters_to_int(s):
    try:
        return [int(char) for char in s]
    except ValueError as e:
        raise ValueError("Invalid character in string") from e


def get_last_digit(num):
    return num % 10