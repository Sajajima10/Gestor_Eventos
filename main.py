import os
from datetime import datetime
from core.persistence import Data_Manager
from core.logic import Scheduled # Asegúrate que el nombre coincida con tu clase
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
    print("6. Salir")
    return input("Seleccione una opción: ")

def main():
    # 1. Inicialización
    # Asegúrate de que las rutas sean correctas
    manager = Data_Manager("data/inventory.json", "data/rules.json")
    engine = Scheduled(manager)

    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            print("\n--- EVENTOS PLANIFICADOS ---")
            if not manager.events:
                print("No hay eventos en el calendario.")
            for ev in manager.events:
                print(ev) # Esto usa el __str__ que definimos en el modelo

        elif opcion == "2":
            print("\n--- NUEVO EVENTO ---")
            nombre = input("Nombre del evento: ")
            fecha_inicio = input("Inicio (YYYY-MM-DD HH:MM:SS): ")
            fecha_fin = input("Fin (YYYY-MM-DD HH:MM:SS): ")
            ids_str = input("IDs de recursos (separados por coma, ej: 01,13,25): ")
            
            # Procesar IDs
            ids = [i.strip().zfill(2) for i in ids_str.split(",")]

            try:
                # Convertir strings a datetime
                fmt = "%Y-%m-%d %H:%M:%S"
                start_dt = datetime.strptime(fecha_inicio, fmt)
                end_dt = datetime.strptime(fecha_fin, fmt)

                # Intentar planificar
                nuevo = engine.add_event(nombre, start_dt, end_dt, ids)
                print(f"✅ ¡ÉXITO! Evento '{nuevo.name}' creado con ID {nuevo.id}")

            except CIEAPlannerError as e:
                print(f"⚠️ ERROR DE PLANIFICACIÓN: {e}")
            except ValueError:
                print("❌ Formato de fecha inválido. Use YYYY-MM-DD HH:MM:SS")

        elif opcion == "3":
            print("\n--- BUSCAR HUECO INTELIGENTE ---")
            # Aquí podrías implementar la llamada a engine.find_next_gap
            print("Funcionalidad en desarrollo... (requiere método find_next_gap)")

        elif opcion == "4":
            ev_id = input("Ingrese el ID del evento a eliminar (ej: EV-01): ")
            # Lógica simple de eliminación
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
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()