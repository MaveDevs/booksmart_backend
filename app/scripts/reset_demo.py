"""
Booksmart Demo Reset Script
============================
Resets the demo user account to a clean state with realistic sample data.

Usage:
    python -m app.scripts.reset_demo

This script:
1. Deletes all existing data for the demo user (cascade)
2. Recreates the demo user with known credentials
3. Seeds an establishment with profile, services, agenda, workers
4. Seeds sample appointments, messages, ratings
"""

import sys
import os
from datetime import date, time, timedelta, datetime
from decimal import Decimal

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.users import User
from app.models.establishments import Establishment
from app.models.profiles import Profile
from app.models.services import Service
from app.models.agendas import Agenda
from app.models.special_closures import SpecialClosure
from app.models.appointments import Appointment, AppointmentStatus
from app.models.messages import Message
from app.models.ratings import Review
from app.models.workers import Worker
from app.models.worker_services import WorkerService
from app.models.notifications import Notification, NotificationType

# ─── Configuration ────────────────────────────────────────────
DEMO_EMAIL = "demo@booksmart.com"
DEMO_PASSWORD = "Demo2025!"
DEMO_NOMBRE = "Demo"
DEMO_APELLIDO = "Booksmart"
DEMO_ROL_ID = 2  # Owner role

# ─── Client pool (for simulated appointments) ────────────────
CLIENTES = [
    {"nombre": "María", "apellido": "García", "correo": "maria.garcia.demo@example.com"},
    {"nombre": "Carlos", "apellido": "López", "correo": "carlos.lopez.demo@example.com"},
    {"nombre": "Ana", "apellido": "Martínez", "correo": "ana.martinez.demo@example.com"},
    {"nombre": "Roberto", "apellido": "Hernández", "correo": "roberto.hdz.demo@example.com"},
    {"nombre": "Laura", "apellido": "Rodríguez", "correo": "laura.rdz.demo@example.com"},
]


def purge_demo_data(db):
    """Remove all demo-related data from the database."""
    # Find the demo user
    demo_user = db.query(User).filter(User.correo == DEMO_EMAIL).first()

    # Also clean up client demo users
    for client in CLIENTES:
        client_user = db.query(User).filter(User.correo == client["correo"]).first()
        if client_user:
            db.delete(client_user)

    if demo_user:
        # The CASCADE constraints will handle most deletions, but let's be explicit
        # for tables without CASCADE
        establishments = db.query(Establishment).filter(
            Establishment.usuario_id == demo_user.usuario_id
        ).all()

        for est in establishments:
            eid = est.establecimiento_id
            # Delete worker services first (many-to-many)
            db.query(WorkerService).filter(
                WorkerService.trabajador_id.in_(
                    db.query(Worker.trabajador_id).filter(Worker.establecimiento_id == eid)
                )
            ).delete(synchronize_session=False)
            # Delete messages via appointments
            appt_ids = [a.cita_id for a in db.query(Appointment.cita_id).join(Service).filter(
                Service.establecimiento_id == eid
            ).all()]
            if appt_ids:
                db.query(Message).filter(Message.cita_id.in_(appt_ids)).delete(synchronize_session=False)
            # Delete appointments
            db.query(Appointment).filter(
                Appointment.servicio_id.in_(
                    db.query(Service.servicio_id).filter(Service.establecimiento_id == eid)
                )
            ).delete(synchronize_session=False)
            # Delete reviews
            db.query(Review).filter(Review.establecimiento_id == eid).delete(synchronize_session=False)
            # Delete notifications for demo user
            db.query(Notification).filter(Notification.usuario_id == demo_user.usuario_id).delete(synchronize_session=False)
            # Delete special closures
            db.query(SpecialClosure).filter(SpecialClosure.establecimiento_id == eid).delete(synchronize_session=False)
            # Delete agendas
            db.query(Agenda).filter(Agenda.establecimiento_id == eid).delete(synchronize_session=False)
            # Delete workers
            db.query(Worker).filter(Worker.establecimiento_id == eid).delete(synchronize_session=False)
            # Delete services
            db.query(Service).filter(Service.establecimiento_id == eid).delete(synchronize_session=False)
            # Delete profile
            db.query(Profile).filter(Profile.establecimiento_id == eid).delete(synchronize_session=False)

        # Delete establishments
        db.query(Establishment).filter(Establishment.usuario_id == demo_user.usuario_id).delete(synchronize_session=False)
        # Delete the user
        db.delete(demo_user)

    db.commit()
    print("✓ Purged all existing demo data")


def create_demo_user(db) -> User:
    """Create the demo user account."""
    user = User(
        nombre=DEMO_NOMBRE,
        apellido=DEMO_APELLIDO,
        correo=DEMO_EMAIL,
        contrasena_hash=get_password_hash(DEMO_PASSWORD),
        rol_id=DEMO_ROL_ID,
        activo=True,
    )
    db.add(user)
    db.flush()
    print(f"✓ Created demo user: {DEMO_EMAIL} (ID: {user.usuario_id})")
    return user


def create_client_users(db) -> list[User]:
    """Create simulated client accounts for appointments."""
    users = []
    for client_data in CLIENTES:
        u = User(
            nombre=client_data["nombre"],
            apellido=client_data["apellido"],
            correo=client_data["correo"],
            contrasena_hash=get_password_hash("ClientDemo123!"),
            rol_id=1,  # Client role
            activo=True,
        )
        db.add(u)
        users.append(u)
    db.flush()
    print(f"✓ Created {len(users)} demo client accounts")
    return users


def create_establishment(db, owner: User) -> Establishment:
    """Create a sample barbershop establishment."""
    est = Establishment(
        usuario_id=owner.usuario_id,
        nombre="Barbería Elite Demo",
        descripcion="Barbería de demostración con servicios profesionales de corte, barba y styling.",
        direccion="Av. Universidad 123, Col. Centro, Cancún, Q.R.",
        latitud=Decimal("21.161908"),
        longitud=Decimal("-86.851528"),
        telefono="9981234567",
        activo=True,
    )
    db.add(est)
    db.flush()
    print(f"✓ Created establishment: {est.nombre} (ID: {est.establecimiento_id})")
    return est


def create_profile(db, est: Establishment) -> Profile:
    """Create public profile for the establishment."""
    profile = Profile(
        establecimiento_id=est.establecimiento_id,
        descripcion_publica="💈 Barbería Elite - La mejor experiencia en cortes y estilo. "
                            "Profesionales certificados con más de 10 años de experiencia. "
                            "¡Agenda tu cita y transforma tu look!",
    )
    db.add(profile)
    db.flush()
    print("✓ Created public profile")
    return profile


def create_services(db, est: Establishment) -> list[Service]:
    """Create sample services."""
    services_data = [
        {"nombre": "Corte Clásico", "descripcion": "Corte de cabello tradicional con acabado profesional", "duracion": 30, "precio": Decimal("150.00")},
        {"nombre": "Corte + Barba", "descripcion": "Corte de cabello completo más perfilado y afeitado de barba", "duracion": 45, "precio": Decimal("250.00")},
        {"nombre": "Barba Completa", "descripcion": "Perfilado, recorte y tratamiento de barba con toalla caliente", "duracion": 25, "precio": Decimal("120.00")},
        {"nombre": "Corte Infantil", "descripcion": "Corte para niños menores de 12 años", "duracion": 20, "precio": Decimal("100.00")},
        {"nombre": "Tratamiento Capilar", "descripcion": "Hidratación profunda, mascarilla y masaje capilar", "duracion": 40, "precio": Decimal("300.00")},
    ]
    services = []
    for s in services_data:
        svc = Service(
            establecimiento_id=est.establecimiento_id,
            nombre=s["nombre"],
            descripcion=s["descripcion"],
            duracion=s["duracion"],
            precio=s["precio"],
            activo=True,
        )
        db.add(svc)
        services.append(svc)
    db.flush()
    print(f"✓ Created {len(services)} services")
    return services


def create_agendas(db, est: Establishment) -> list[Agenda]:
    """Create weekly schedule (Mon-Sat open, Sun closed)."""
    from app.models.agendas import DayOfWeek

    schedule = [
        (DayOfWeek.LUNES, time(9, 0), time(19, 0)),
        (DayOfWeek.MARTES, time(9, 0), time(19, 0)),
        (DayOfWeek.MIERCOLES, time(9, 0), time(19, 0)),
        (DayOfWeek.JUEVES, time(9, 0), time(20, 0)),
        (DayOfWeek.VIERNES, time(9, 0), time(20, 0)),
        (DayOfWeek.SABADO, time(10, 0), time(17, 0)),
    ]
    agendas = []
    for day, start, end in schedule:
        a = Agenda(
            establecimiento_id=est.establecimiento_id,
            dia_semana=day,
            hora_inicio=start,
            hora_fin=end,
        )
        db.add(a)
        agendas.append(a)
    db.flush()
    print(f"✓ Created {len(agendas)} agenda entries (Mon-Sat)")
    return agendas


def create_workers(db, est: Establishment) -> list[Worker]:
    """Create sample workers."""
    workers_data = [
        {"nombre": "Javier", "apellido": "Ríos", "especialidad": "Barbero Senior", "telefono": "9981111111"},
        {"nombre": "Diego", "apellido": "Morales", "especialidad": "Estilista", "telefono": "9982222222"},
    ]
    workers = []
    for w in workers_data:
        worker = Worker(
            establecimiento_id=est.establecimiento_id,
            nombre=w["nombre"],
            apellido=w["apellido"],
            especialidad=w["especialidad"],
            telefono=w["telefono"],
            activo=True,
            fecha_contratacion=date.today() - timedelta(days=180),
        )
        db.add(worker)
        workers.append(worker)
    db.flush()
    print(f"✓ Created {len(workers)} workers")
    return workers


def assign_worker_services(db, workers: list[Worker], services: list[Service]):
    """Assign services to workers."""
    # Worker 1 (Barbero Senior) → all cutting services
    # Worker 2 (Estilista) → style & treatment services
    assignments = [
        (workers[0], [services[0], services[1], services[2], services[3]]),
        (workers[1], [services[0], services[1], services[4]]),
    ]
    count = 0
    for worker, svcs in assignments:
        for svc in svcs:
            ws = WorkerService(
                trabajador_id=worker.trabajador_id,
                servicio_id=svc.servicio_id,
            )
            db.add(ws)
            count += 1
    db.flush()
    print(f"✓ Assigned {count} worker-service relationships")


def create_special_closures(db, est: Establishment):
    """Create a couple of future special closures."""
    today = date.today()
    closures = [
        SpecialClosure(
            establecimiento_id=est.establecimiento_id,
            fecha=today + timedelta(days=15),
            motivo="Día de capacitación del equipo",
        ),
        SpecialClosure(
            establecimiento_id=est.establecimiento_id,
            fecha=today + timedelta(days=30),
            motivo="Mantenimiento del local",
        ),
    ]
    for c in closures:
        db.add(c)
    db.flush()
    print(f"✓ Created {len(closures)} special closures")


def create_appointments(db, services: list[Service], clients: list[User], workers: list[Worker]) -> list[Appointment]:
    """Create sample appointments spanning past, today, and future."""
    today = date.today()
    appointments = []

    # Past appointments (completed / cancelled)
    past_data = [
        (today - timedelta(days=3), time(10, 0), time(10, 30), services[0], clients[0], workers[0], AppointmentStatus.COMPLETADA),
        (today - timedelta(days=3), time(11, 0), time(11, 45), services[1], clients[1], workers[1], AppointmentStatus.COMPLETADA),
        (today - timedelta(days=2), time(14, 0), time(14, 25), services[2], clients[2], workers[0], AppointmentStatus.COMPLETADA),
        (today - timedelta(days=1), time(9, 0), time(9, 30), services[0], clients[3], workers[0], AppointmentStatus.CANCELADA),
        (today - timedelta(days=1), time(10, 0), time(10, 45), services[1], clients[4], workers[1], AppointmentStatus.COMPLETADA),
    ]

    # Today appointments
    today_data = [
        (today, time(9, 0), time(9, 30), services[0], clients[0], workers[0], AppointmentStatus.CONFIRMADA),
        (today, time(10, 0), time(10, 45), services[1], clients[2], workers[1], AppointmentStatus.PENDIENTE),
        (today, time(11, 30), time(11, 50), services[3], clients[1], workers[0], AppointmentStatus.CONFIRMADA),
        (today, time(14, 0), time(14, 40), services[4], clients[4], workers[1], AppointmentStatus.PENDIENTE),
    ]

    # Future appointments
    future_data = [
        (today + timedelta(days=1), time(9, 0), time(9, 30), services[0], clients[3], workers[0], AppointmentStatus.CONFIRMADA),
        (today + timedelta(days=1), time(10, 0), time(10, 25), services[2], clients[1], workers[0], AppointmentStatus.PENDIENTE),
        (today + timedelta(days=2), time(11, 0), time(11, 45), services[1], clients[0], workers[1], AppointmentStatus.PENDIENTE),
        (today + timedelta(days=3), time(15, 0), time(15, 40), services[4], clients[4], workers[1], AppointmentStatus.PENDIENTE),
    ]

    for fecha, hi, hf, svc, client, worker, estado in past_data + today_data + future_data:
        appt = Appointment(
            cliente_id=client.usuario_id,
            servicio_id=svc.servicio_id,
            trabajador_id=worker.trabajador_id,
            fecha=fecha,
            hora_inicio=hi,
            hora_fin=hf,
            estado=estado,
        )
        db.add(appt)
        appointments.append(appt)

    db.flush()
    print(f"✓ Created {len(appointments)} appointments ({len(past_data)} past, {len(today_data)} today, {len(future_data)} future)")
    return appointments


def create_messages(db, appointments: list[Appointment], demo_user: User, clients: list[User]):
    """Create sample chat messages for some appointments."""
    msg_count = 0

    # Messages for the first confirmed today appointment
    today_confirmed = [a for a in appointments if a.estado == AppointmentStatus.CONFIRMADA]
    if len(today_confirmed) >= 1:
        appt = today_confirmed[0]
        msgs = [
            (appt.cliente_id, "¡Hola! Confirmo mi cita para hoy. ¿Sigue en pie?"),
            (demo_user.usuario_id, "¡Hola! Sí, confirmada. Te esperamos a las 9:00. 👍"),
            (appt.cliente_id, "Perfecto, gracias. ¿Puedo llegar 5 minutos antes?"),
            (demo_user.usuario_id, "¡Claro! Sin problema. Te esperamos."),
        ]
        for i, (emisor_id, contenido) in enumerate(msgs):
            m = Message(
                cita_id=appt.cita_id,
                emisor_id=emisor_id,
                contenido=contenido,
            )
            db.add(m)
            msg_count += 1

    # Messages for a pending appointment
    today_pending = [a for a in appointments if a.estado == AppointmentStatus.PENDIENTE]
    if len(today_pending) >= 1:
        appt = today_pending[0]
        msgs = [
            (appt.cliente_id, "Buenos días, ¿tienen disponibilidad para hoy?"),
            (demo_user.usuario_id, "¡Buenos días! Sí, tenemos espacio. Tu cita está registrada como pendiente. ¿La confirmamos?"),
        ]
        for emisor_id, contenido in msgs:
            m = Message(
                cita_id=appt.cita_id,
                emisor_id=emisor_id,
                contenido=contenido,
            )
            db.add(m)
            msg_count += 1

    db.flush()
    print(f"✓ Created {msg_count} chat messages")


def create_ratings(db, est: Establishment, clients: list[User]):
    """Create sample reviews."""
    reviews_data = [
        (clients[0], 5, "¡Excelente servicio! El corte quedó perfecto y el trato fue muy amable. 100% recomendado."),
        (clients[1], 4, "Muy buen servicio, ambiente agradable. Solo tardaron un poco más de lo esperado."),
        (clients[2], 5, "La mejor barbería de la zona. Javier es un crack con la barba. Volveré pronto."),
        (clients[4], 4, "Buen tratamiento capilar, se nota la diferencia. El precio es justo."),
    ]
    for client, rating, comment in reviews_data:
        r = Review(
            establecimiento_id=est.establecimiento_id,
            usuario_id=client.usuario_id,
            calificacion=rating,
            comentario=comment,
        )
        db.add(r)
    db.flush()
    print(f"✓ Created {len(reviews_data)} reviews (avg: {sum(r[1] for r in reviews_data)/len(reviews_data):.1f})")


def create_notifications(db, demo_user: User):
    """Create sample notifications."""
    notifs = [
        (NotificationType.INFO, "¡Bienvenido a Booksmart! Tu cuenta demo está lista para explorar."),
        (NotificationType.RECORDATORIO, "Tienes 2 citas pendientes para hoy. Revisa tu calendario."),
        (NotificationType.ALERTA, "María García confirmó su cita para las 9:00 AM."),
    ]
    for tipo, mensaje in notifs:
        n = Notification(
            usuario_id=demo_user.usuario_id,
            mensaje=mensaje,
            tipo=tipo,
            leida=False,
        )
        db.add(n)
    db.flush()
    print(f"✓ Created {len(notifs)} notifications")


def main():
    print("=" * 60)
    print("  BOOKSMART DEMO RESET")
    print("=" * 60)
    print()

    db = SessionLocal()
    try:
        # 1. Purge existing demo data
        purge_demo_data(db)

        # 2. Create demo user
        demo_user = create_demo_user(db)

        # 3. Create client users
        clients = create_client_users(db)

        # 4. Create establishment
        est = create_establishment(db, demo_user)

        # 5. Create public profile
        create_profile(db, est)

        # 6. Create services
        services = create_services(db, est)

        # 7. Create weekly agenda
        create_agendas(db, est)

        # 8. Create workers
        workers = create_workers(db, est)

        # 9. Assign services to workers
        assign_worker_services(db, workers, services)

        # 10. Create special closures
        create_special_closures(db, est)

        # 11. Create appointments
        appointments = create_appointments(db, services, clients, workers)

        # 12. Create messages
        create_messages(db, appointments, demo_user, clients)

        # 13. Create ratings
        create_ratings(db, est, clients)

        # 14. Create notifications
        create_notifications(db, demo_user)

        # Commit everything
        db.commit()
        print()
        print("=" * 60)
        print("  ✅ DEMO RESET COMPLETE")
        print(f"  📧 Email:    {DEMO_EMAIL}")
        print(f"  🔑 Password: {DEMO_PASSWORD}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
