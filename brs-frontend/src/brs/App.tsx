import { AddBooking } from "./AddBooking";
import { Bookings } from "./BookingsList";
import { Login } from "./Login";

export function Brs() {
  return (
    <>
      <Login />
      <AddBooking />
      <Bookings />
    </>
  );
}
