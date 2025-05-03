from datetime import datetime, timedelta

class ReservationManager:
    def __init__(self, book_manager, user_manager):
        self.reservations = {}
        self.next_id = 1
        self.book_manager = book_manager
        self.user_manager = user_manager
        self.book_queues = {}
        self.reservation_expiry_days = 3

    def reserve_book(self, user_id, book_id):
        try:
            self.user_manager.get_user(user_id)
        except ValueError:
            raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

        try:
            book = self.book_manager.get_book(book_id)
        except ValueError:
            raise ValueError(f"Książka o ID {book_id} nie istnieje")

        if book.get("available") is True:
            raise ValueError(f"Książka o ID {book_id} jest już dostępna, można ją wypożyczyć zamiast rezerwować")

        for res_id, res in self.reservations.items():
            if res["user_id"] == user_id and res["book_id"] == book_id and res["status"] in ["waiting", "ready"]:
                raise ValueError(f"Użytkownik o ID {user_id} już zarezerwował książkę o ID {book_id}")

        reservation = {
            "user_id": user_id,
            "book_id": book_id,
            "status": "waiting",  # waiting, ready, completed, cancelled
            "reservation_date": datetime.now().isoformat(),
            "notification_sent": False
        }

        reservation_id = self.next_id
        self.reservations[reservation_id] = reservation
        self.next_id += 1

        if book_id not in self.book_queues:
            self.book_queues[book_id] = []
        self.book_queues[book_id].append(reservation_id)

        return reservation_id

    def cancel_reservation(self, reservation_id):
        if reservation_id not in self.reservations:
            raise ValueError(f"Rezerwacja o ID {reservation_id} nie istnieje")

        reservation = self.reservations[reservation_id]
        book_id = reservation["book_id"]

        if reservation["status"] not in ["waiting", "ready"]:
            raise ValueError(f"Nie można anulować rezerwacji o statusie {reservation['status']}")

        reservation["status"] = "cancelled"
        reservation["cancel_date"] = datetime.now().isoformat()

        if book_id in self.book_queues and reservation_id in self.book_queues[book_id]:
            self.book_queues[book_id].remove(reservation_id)

        return True

    def get_reservation(self, reservation_id):
        if reservation_id not in self.reservations:
            raise ValueError(f"Rezerwacja o ID {reservation_id} nie istnieje")
        return self.reservations[reservation_id]

    def list_reservations(self, status=None):
        if status:
            return [res for res_id, res in self.reservations.items()
                  if res["status"] == status]
        return list(self.reservations.values())

    def get_user_reservations(self, user_id):
        return [res for res_id, res in self.reservations.items()
              if res["user_id"] == user_id]

    def get_book_reservations(self, book_id):
        return [res for res_id, res in self.reservations.items()
              if res["book_id"] == book_id]

    def book_returned(self, book_id):
        if book_id not in self.book_queues or not self.book_queues[book_id]:
            return False

        next_reservation_id = self.book_queues[book_id][0]
        next_reservation = self.reservations[next_reservation_id]

        next_reservation["status"] = "ready"
        next_reservation["ready_date"] = datetime.now().isoformat()
        next_reservation["expiry_date"] = (datetime.now() + timedelta(days=self.reservation_expiry_days)).isoformat()
        next_reservation["notification_sent"] = True

        return next_reservation_id

    def check_expired_reservations(self):
        now = datetime.now()
        expired_reservations = []

        for res_id, res in self.reservations.items():
            if res["status"] == "ready" and "expiry_date" in res:
                expiry_date = datetime.fromisoformat(res["expiry_date"])
                if now > expiry_date:
                    res["status"] = "expired"
                    book_id = res["book_id"]
                    if book_id in self.book_queues and res_id in self.book_queues[book_id]:
                        self.book_queues[book_id].remove(res_id)
                    expired_reservations.append(res_id)

                    self.book_returned(book_id)

        return expired_reservations

    def complete_reservation(self, reservation_id):
        if reservation_id not in self.reservations:
            raise ValueError(f"Rezerwacja o ID {reservation_id} nie istnieje")

        reservation = self.reservations[reservation_id]
        book_id = reservation["book_id"]

        if reservation["status"] != "ready":
            raise ValueError(f"Tylko rezerwacje o statusie 'ready' mogą być zrealizowane")

        reservation["status"] = "completed"
        reservation["completion_date"] = datetime.now().isoformat()

        if book_id in self.book_queues and reservation_id in self.book_queues[book_id]:
            self.book_queues[book_id].remove(reservation_id)

        return True

    def get_position_in_queue(self, reservation_id):
        if reservation_id not in self.reservations:
            raise ValueError(f"Rezerwacja o ID {reservation_id} nie istnieje")

        reservation = self.reservations[reservation_id]
        book_id = reservation["book_id"]

        if book_id not in self.book_queues:
            return -1

        try:
            return self.book_queues[book_id].index(reservation_id) + 1
        except ValueError:
            return -1