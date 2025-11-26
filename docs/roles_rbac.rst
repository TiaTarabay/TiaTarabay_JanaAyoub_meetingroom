Roles and RBAC
==============

The SmartMeetingRoom system uses Role-Based Access Control (RBAC) to
decide what each caller is allowed to do. The caller identity and role
are propagated to the services via the ``X-User-Id`` and ``X-Role``
HTTP headers.

Roles
-----

The main roles are:

* **admin** – Full access to all services. Can manage users, rooms,
  bookings, and reviews, including override operations (e.g. force
  cancelling bookings).

* **regular_user** – Typical end user. Can manage their own bookings
  and reviews, but cannot view or modify data belonging to other users.

* **facility_manager** – Power user for room and capacity management.
  Can manage rooms and view all bookings for planning purposes, but
  does not have user administration privileges.

* **moderator** – Lightweight review administrator. Can moderate
  reviews (update, flag, or delete) but has no special privileges over
  users or rooms.

* **auditor** – Read-only role. Can inspect users, rooms, bookings,
  and reviews for auditing and logging, but cannot perform write
  operations.

* **service_account** – Non-human account used by other services
  (e.g. for background jobs or monitoring). It is granted minimal,
  read-only permissions.

RBAC Implementation
-------------------

Each service exposes helper functions such as
``get_current_user_id()``, ``get_current_role()``, and a central
authorization function (for example ``can_do_booking_action`` or
``can_do_review_action``). These functions examine the role, the
requested action, and (when relevant) the resource owner ID to decide
whether the request is allowed or must be rejected with
``403 Forbidden``.
