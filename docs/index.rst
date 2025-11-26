SmartMeetingRoom Microservices Documentation
============================================

Welcome to the SmartMeetingRoom project documentation. This project implements a
microservices-based meeting room management system with separate services for:

- Users
- Rooms
- Bookings
- Reviews

Each service exposes a REST API and communicates with a shared PostgreSQL
database. Role-Based Access Control (RBAC) is enforced using the ``X-Role`` and
``X-User-Id`` headers, and the system is fully containerized using Docker and
docker-compose.


.. toctree::
   :maxdepth: 2


   api_reference
   roles_rbac

