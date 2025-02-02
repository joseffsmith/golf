import { Box } from "@mui/joy";
import { AddBooking } from "./AddBooking";
import { Bookings } from "./BookingsList";
import { Login } from "./Login";

export function Brs() {
  return (
    <Box>
      <Box display={"flex"} width="100%" justifyContent={"flex-end"} p={2}>
        <Login />
      </Box>
      <Box
        maxWidth={450}
        margin={"0 auto"}
        display={"flex"}
        flexDirection={"column"}
        rowGap={2}
      >
        <AddBooking />
        <Bookings />
      </Box>
    </Box>
  );
}
