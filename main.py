import os
from datetime import datetime
from core.persistence import Data_Manager
from core.logic import Scheduled
from utils.error import CIEAPlannerError

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu():
    print("\n=== SISTEMA DE PLANIFICACIÓN CIEA ===")
    print("1. Listar todos los eventos")
    print("2. Planificar nuevo evento")
    print("3. Buscar próximo hueco disponible")
    print("4. Eliminar un evento")
    print("5. Ver inventario de recursos")
    print("6. Modificar un Evento")
    print("7. Salir")
    return input("Seleccione una opción: ")

def main():
    manager = Data_Manager("data/inventory.json", "data/rules.json")
    engine = Scheduled(manager)

    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            print("\n--- EVENTOS PLANIFICADOS ---")
            if not manager.events:
                print("No hay eventos en el calendario.")
            else:
                for ev in sorted(manager.events, key=lambda e: e.start):   # ahora ordenados por fecha
                    dur = ev.duration()
                    horas, segundos = divmod(dur.total_seconds(), 3600)
                    minutos = segundos // 60
                    duracion_str = f"{int(horas)}h {int(minutos)}m" if horas else f"{int(minutos)}m"
                    
                    recursos_nombres = []
                    for rid in ev.resource_ids:
                        if rid in manager.resources:
                            recursos_nombres.append(f"{manager.resources[rid].name} ({rid})")
                        else:
                            recursos_nombres.append(rid)
                    rec_str = ", ".join(recursos_nombres)
                    
                    print(f"ID: {ev.id}")
                    print(f"  Nombre: {ev.name}")
                    print(f"  Inicio: {ev.start.strftime('%Y-%m-%d %H:%M')}")
                    print(f"  Fin:    {ev.end.strftime('%Y-%m-%d %H:%M')}")
                    print(f"  Duración: {duracion_str}")
                    print(f"  Recursos: {rec_str}")
                    print()

        elif opcion == "2":
            print("\n--- NUEVO EVENTO ---")
            nombre = input("Nombre del evento: ")
            fecha_inicio = input("Inicio (YYYY-MM-DD HH:MM:SS): ")
            fecha_fin = input("Fin (YYYY-MM-DD HH:MM:SS): ")
            ids_str = input("IDs de recursos (separados por coma, ej: 01,13,25): ")
            ids = [i.strip().zfill(2) for i in ids_str.split(",")]

            try:
                fmt = "%Y-%m-%d %H:%M:%S"
                start_dt = datetime.strptime(fecha_inicio, fmt)
                end_dt = datetime.strptime(fecha_fin, fmt)
                nuevo = engine.add_event(nombre, start_dt, end_dt, ids)
                print(f"✅ ¡ÉXITO! Evento '{nuevo.name}' creado con ID {nuevo.id}")
            except CIEAPlannerError as e:
                print(f"⚠️ ERROR DE PLANIFICACIÓN: {e}")
            except ValueError:
                print("❌ Formato de fecha inválido. Use YYYY-MM-DD HH:MM:SS")

        elif opcion == "3":
            print("\n--- BUSCAR HUECO INTELIGENTE ---")
            try:
                duracion_h = float(input("Duración deseada (en horas): "))
                ids_str = input("IDs de recursos necesarios (separados por coma, ej: 01,13,25): ")
                ids = [i.strip().zfill(2) for i in ids_str.split(",")]
                inicio_hueco = engine.find_next_gap(duracion_h, ids)
                print(f"✅ Hueco encontrado: {inicio_hueco.strftime('%Y-%m-%d %H:%M:%S')}")
            except CIEAPlannerError as e:
                print(f"⚠️ {e}")
            except ValueError:
                print("❌ Entrada inválida (duración debe ser número, IDs formato correcto).")

        elif opcion == "4":
            ev_id = input("Ingrese el ID del evento a eliminar (ej: EV-01): ")
            evento_encontrado = None
            for ev in manager.events:
                if ev.id == ev_id:
                    evento_encontrado = ev
                    break
            if evento_encontrado:
                manager.events.remove(evento_encontrado)
                manager.save_all_data(manager.events)
                print(f"🗑️ Evento {ev_id} eliminado y recursos liberados.")
            else:
                print("❌ No se encontró ningún evento con ese ID.")

        elif opcion == "5":
            print("\n--- INVENTARIO DE RECURSOS ---")
            for r_id, r_obj in manager.resources.items():
                print(f"ID: {r_id} | {r_obj.name} ({r_obj.type})")

        elif opcion == "6":
            ev_id = input("Ingrese el ID del evento a modificar (ej: EV-01): ")
            # Buscar el evento para mostrar datos actuales
            original = None
            for ev in manager.events:
                if ev.id == ev_id:
                    original = ev
                    break
            if not original:
                print("❌ No se encontró ningún evento con ese ID.")
                continue

            print("\n--- DATOS ACTUALES DEL EVENTO ---")
            print(f"Nombre: {original.name}")
            print(f"Inicio: {original.start.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Fin:    {original.end.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Recursos: {', '.join(original.resource_ids)}")
            print("\nDeje en blanco para mantener el valor actual.")

            nuevo_nombre = input("Nuevo nombre: ")
            if not nuevo_nombre:
                nuevo_nombre = original.name

            nuevo_inicio_str = input("Nuevo inicio (YYYY-MM-DD HH:MM:SS): ")
            if not nuevo_inicio_str:
                nuevo_inicio = original.start
            else:
                try:
                    nuevo_inicio = datetime.strptime(nuevo_inicio_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    print("❌ Formato de fecha inválido.")
                    continue

            nuevo_fin_str = input("Nuevo fin (YYYY-MM-DD HH:MM:SS): ")
            if not nuevo_fin_str:
                nuevo_fin = original.end
            else:
                try:
                    nuevo_fin = datetime.strptime(nuevo_fin_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    print("❌ Formato de fecha inválido.")
                    continue

            nuevos_ids_str = input("Nuevos IDs de recursos (separados por coma): ")
            if not nuevos_ids_str:
                nuevos_ids = original.resource_ids
            else:
                nuevos_ids = [i.strip().zfill(2) for i in nuevos_ids_str.split(",")]

            try:
                engine.update_event(ev_id, nuevo_nombre, nuevo_inicio, nuevo_fin, nuevos_ids)
                print("✅ Evento modificado exitosamente.")
            except CIEAPlannerError as e:
                print(f"⚠️ ERROR: {e}")
                
        elif opcion == "7":
            print("Saliendo del Sistema...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()