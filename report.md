# Informe del Sistema de Planificación CIEA

## ¿Qué hace este programa?

El **Sistema de Planificación CIEA** es una herramienta para organizar eventos y recursos de un laboratorio de investigación avanzada. En lugar de llevar una agenda en papel o arriesgarse a reservar dos veces el mismo equipo, con este programa puedes planificar experimentos, reuniones o tareas, asignarles personas e instalaciones, y asegurarte de que todo cumple las normas de seguridad del centro.

En concreto, el programa permite:

- **Listar los eventos** que ya están en el calendario, viendo de un tirón qué recursos están pillados y en qué horario.
- **Crear un evento nuevo** diciendo qué recursos necesitas y en qué fecha. El sistema comprueba automáticamente si esos recursos están libres, si existen, y si al juntarlos no rompes ninguna regla (por ejemplo, mezclar productos que reaccionan mal entre sí).
- **Buscar el próximo hueco libre** para un conjunto de recursos y una duración. Si necesitas al Ingeniero Marcos y al Reactor Alpha durante tres horas, el programa te dice a partir de cuándo están disponibles los dos.
- **Eliminar un evento** y liberar automáticamente sus recursos.
- **Modificar un evento ya creado**, cambiando fechas o recursos, y que se vuelva a comprobar todo como si fuera nuevo.
- **Ver el inventario completo** de recursos, para saber qué IDs usar.

Los datos se guardan en archivos JSON, así que no hace falta instalar bases de datos ni configurar nada raro. Las reglas de uso también van en otro JSON, de manera que si cambian las políticas del laboratorio, basta con editar ese archivo sin tocar el código.

---

## Cómo lo diseñé y por qué tomé esas decisiones

Cuando empecé este proyecto, lo primero que hice fue separar el código en varias partes independientes, cada una con una tarea clara. Eso me ayudó a no perderme entre tanto requisito. Así nacieron estos módulos:

- **`models.py`**: define las clases `Event` y `Resource`. Son simples, solo guardan datos. Un recurso tiene un nombre, un tipo y un montón de atributos extra que pueden variar según el recurso (nivel de riesgo, potencia, etc.). Para no complicarme, dejé que esos atributos se guarden en un diccionario interno, de modo que añadir nuevas características en el futuro no rompa nada.

- **`persistence.py`**: es el único que lee y escribe los archivos JSON. Tener toda la entrada/salida centralizada aquí me ahorró muchos problemas. El inventario y los eventos conviven en un mismo archivo, y las reglas en otro. Así, quien quiera usar el programa solo necesita dos archivos de datos.

- **`logic.py`**: aquí está el cerebro del sistema. Contiene la clase `Scheduled`, que se encarga de:
  - Comprobar que las fechas tengan sentido (que el fin sea después del inicio).
  - Verificar que los recursos que me piden existan de verdad en el inventario.
  - Revisar que no haya conflictos de horario: si un recurso ya está reservado en ese intervalo, se avisa con un error claro.
  - Aplicar todas las reglas de negocio (inclusiones, exclusiones, categorías, reglas maestras).
  - Generar un identificador único para cada evento, evitando que se repitan incluso si borramos eventos anteriores.
  - Buscar huecos libres en el calendario para un conjunto de recursos.

  En lugar de devolver códigos de error, decidí usar **excepciones personalizadas**. Cada tipo de fallo (conflicto de recurso, violación de una regla, etc.) lanza una excepción distinta. Luego, desde la interfaz, capturo todas con un solo `try/except` y muestro un mensaje amigable. Me pareció más limpio que ir comprobando valores devueltos por cada método.

- **`utils/error.py`**: una familia de excepciones con un padre común, `CIEAPlannerError`. Así puedo capturar cualquier error del sistema de una sola vez, pero también distinguirlos si algún día necesito tratarlos por separado.

- **`main.py`**: la cara visible. Un menú por consola con opciones numeradas. Intenté que fuera claro y directo, con mensajes que usan emojis para que de un vistazo sepas si algo fue bien (✅) o mal (❌). La lista de eventos se muestra ordenada cronológicamente y con los nombres de los recursos, no solo sus códigos.

Una de las decisiones más importantes fue **mover todas las reglas de validación a un archivo JSON externo**. Separarlas en cuatro grupos (inclusión, exclusión, categorías y reglas maestras) hizo que el código de validación fuera sencillo: recorro listas y aplico condiciones. Si mañana quiero añadir una nueva regla, solo toco el JSON, no el Python.

---

## ¿Qué aprendí durante el desarrollo?

Este proyecto me enseñó varias cosas prácticas.

Primero, **separar el código en módulos con responsabilidades concretas** facilita la vida una barbaridad. Cuando algo fallaba, sabía exactamente dónde buscar. Si un recurso no se guardaba, la culpa era de `persistence.py`; si una regla no saltaba, el problema estaba en `logic.py`. Esa claridad mental evita horas de frustración.

Segundo, **usar excepciones propias en lugar de devolver códigos de error** hace que el código principal sea mucho más legible. En la interfaz solo tengo que poner un `try/except` general y olvidarme de comprobar qué ha devuelto cada función. El día que necesite añadir una nueva validación, lanzo una nueva excepción y ya está.

Tercero, los **archivos JSON pueden ser engañosos**. Un simple error de indentación en un bucle me hizo perder 49 de los 50 recursos al guardar. Aprendí a probar la carga y el guardado con conjuntos de datos reales, no solo con ejemplos chicos.

Cuarto, las **reglas de negocio suelen tener más matices de los que uno espera**. Al principio pensé que todas las inclusiones eran del tipo "si usas A, necesitas B". Luego vi que a veces bastaba con "una persona de seguridad" (cualquiera de dos) en lugar de todas. Así que tuve que añadir el concepto de `required_any`. Lo mismo pasó con las exclusiones: mi primera versión solo fallaba si estaban **todos** los recursos prohibidos, pero lo correcto era prohibir cualquier combinación de dos o más.

Por último, **probar con casos límite** es fundamental. Cosas como "¿qué pasa si borro un evento y luego creo otro con los mismos recursos?" o "¿qué ocurre si pongo dos de los tres recursos que una regla de exclusión prohíbe?" me destaparon errores que de otra forma no habría visto.

---

## Cómo se usa el programa (con ejemplos)

Para lanzar el programa, simplemente ejecuto en la terminal:

```bash
python main.py

Aparece un menú como este:
text

=== SISTEMA DE PLANIFICACIÓN CIEA ===
1. Listar todos los eventos
2. Planificar nuevo evento
3. Buscar próximo hueco disponible
4. Eliminar un evento
5. Ver inventario de recursos
6. Modificar un evento
7. Salir
Seleccione una opción:

Veamos un ejemplo completo de uso:

    Crear un evento sencillo
    Elijo la opción 2 y completo los datos:
    text

    Nombre del evento: Prueba de vacío
    Inicio (YYYY-MM-DD HH:MM:SS): 2026-08-15 08:00:00
    Fin (YYYY-MM-DD HH:MM:SS): 2026-08-15 10:00:00
    IDs de recursos (separados por coma, ej: 01,13,25): 03,15,05

    El sistema comprueba que la Cámara de Vacío (03), el Técnico Roberto (15) y el Cuarto Limpio (05) estén disponibles. Como lo están, responde:
    text

    ✅ ¡ÉXITO! Evento 'Prueba de vacío' creado con ID EV-01

    Conflicto de horario
    Intento crear otro evento que solape con el anterior usando la misma cámara:
    text

    Nombre: Análisis de materiales
    Inicio: 2026-08-15 09:00:00
    Fin: 2026-08-15 11:00:00
    IDs: 03,11

    El programa me frena inmediatamente:
    text

    ⚠️ ERROR DE PLANIFICACIÓN: Conflicto: El recurso 'Cámara de Vacío Cuántico' (ID: 03) ya está siendo usado en el evento 'Prueba de vacío'.

    Violación de una regla de seguridad
    Si intento usar el Túnel de Partículas (06) sin los equipos de protección obligatorios, me llevo un aviso:
    text

    IDs: 06,13
    ⚠️ ERROR: El manejo de instalaciones críticas requiere Blindaje de Plomo (34) y Escáner de Radiación (38).

    Me obliga a añadir los recursos que faltan para poder continuar.

    Buscar un hueco libre
    Supongamos que quiero hacer un experimento de 4 horas con el Reactor Alpha (01) y la Ingeniera Elena (13). Uso la opción 3:
    text

    Duración deseada (en horas): 4
    IDs de recursos necesarios: 01,13

    El sistema analiza los eventos que ocupan esos recursos y me responde:
    text

    ✅ Hueco encontrado: 2026-08-16 14:30:00

    Modificar un evento
    Si me doy cuenta de que la prueba de vacío necesita una hora más, elijo la opción 6, indico el ID EV-01 y cambio la hora de fin. El programa revalida todo y confirma el cambio.

    Eliminar un evento
    Con la opción 4 y el ID, el evento desaparece y sus recursos quedan libres.

    Ver el inventario
    La opción 5 me muestra todos los recursos disponibles, con sus IDs y tipos. Así sé qué códigos usar al planificar.

Dificultades que encontré y cómo las resolví
El cambio de rumbo: de base de datos a archivos JSON

La idea original era usar MariaDB como almacenamiento. Había empezado a diseñar tablas, relaciones y consultas SQL. Pero en cuanto intenté llevar el proyecto a otro ordenador, me estrellé con la realidad: había que instalar un servidor de bases de datos, configurar credenciales, crear esquemas… Eso lo podía hacer yo en mi equipo, pero para un usuario normal era un lío. Así que replanteé todo y decidí usar simples archivos JSON. Al principio me supo a "recortar", pero luego vi que era justo lo contrario: el programa se volvió portátil, no requiere instalaciones adicionales, los datos se pueden abrir con cualquier editor de texto, y el código de persistencia quedó reducido a lo esencial. Fue una lección de humildad: a veces lo más sencillo es lo más profesional.
El bug que me borraba los recursos sin avisar

En el método save_all_data de persistence.py, dos líneas que añadían los atributos de cada recurso al diccionario de salida estaban mal indentadas y se ejecutaban fuera del bucle. Consecuencia: solo se guardaba el último recurso de la lista. Cuando abrí el JSON después de planificar un evento, el inventario había menguado de 50 recursos a 1. El fallo era tan simple como añadir cuatro espacios. Desde entonces, pruebo la persistencia con datos grandes antes de cantar victoria.
Reglas de inclusión que se tomaban a la ligera

Mi primera versión usaba any() para comprobar si los recursos requeridos estaban presentes. Si una regla pedía blindaje y escáner, pero solo ponías uno, lo daba por bueno. Cambié a all() para que fuese estricto. Luego vi que en ciertos casos (como tener dos responsables de seguridad equivalentes) bastaba con que estuviera uno de ellos. Así que creé la distinción entre required (todos) y required_any (al menos uno), y adapté el validador. Esta experiencia me enseñó que los requisitos nunca son tan uniformes como uno cree.
IDs duplicados al borrar eventos

Generaba los identificadores contando cuántos eventos había y sumando uno. Pero si borrabas un evento y luego creabas otro, podías reusar el mismo número. Lo resolví buscando el número de ID más alto entre los existentes y sumándole uno. Un cambio pequeño pero clave para mantener la integridad.
Exclusión mutua demasiado permisiva

Al comprobar las exclusiones, solo bloqueaba el evento si estaban todos los recursos prohibidos juntos. Eso dejaba pasar combinaciones parciales peligrosas, como dos de tres reactores críticos. Cambié la condición para que falle con solo dos coincidencias (forbidden_count > 1). Otro recordatorio de que hay que ponerse en el peor escenario posible.
Un error tonto en el método __str__ de Resource

El método que imprime un recurso intentaba mostrar self.attribute (en singular), pero el nombre real del atributo era self.attributes (plural). Aunque el programa no lo usaba en su flujo normal, cualquier depuración con un print habría sido un desastre. Con añadir una "s" se solucionó. Detalles mínimos que te hacen perder tiempo si no pruebas todo.
Conclusión

El Sistema de Planificación CIEA ha sido un proyecto en el que he aprendido tanto de aciertos como de errores. Empecé con una idea ambiciosa (base de datos, instalaciones complejas) y acabé con una solución sencilla pero efectiva. La modularidad, el uso de JSON, las excepciones propias y las reglas externas han hecho que el programa sea fácil de mantener y de usar.

Me quedo con la enseñanza de que menos es más: una herramienta no es mejor por tener una base de datos potente detrás, sino por resolver el problema real sin añadir barreras. Y, por supuesto, con que probar a conciencia (incluso los bucles más inofensivos) te salva de sustos en producción.