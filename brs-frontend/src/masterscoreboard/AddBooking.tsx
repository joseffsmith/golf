import {
  Autocomplete,
  Box,
  Button,
  Card,
  CardActions,
  // CardHeader,
  CardContent,
  CircularProgress,
  FormControl,
  FormLabel,
  Typography,
} from "@mui/joy";
import { TextField } from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers";
import axios from "axios";
import { format } from "date-fns";
import { useState } from "react";
import { useRecoilRefresher_UNSTABLE } from "recoil";
import { currentBookings } from "./atoms";

export const AddBooking = () => {
  var nextWeek = new Date(new Date().getTime() + 7 * 24 * 60 * 60 * 1000);
  const [date, setDate] = useState<Date | null>(nextWeek);
  const [time, setTime] = useState("08:00");
  const [isBooking, setIsBooking] = useState(false);

  const refreshBookings = useRecoilRefresher_UNSTABLE(currentBookings);

  const handleAddBooking = async () => {
    const username = localStorage.getItem("int-username");
    const password = localStorage.getItem("int-password");
    const courseName = localStorage.getItem("int-course");
    if (!username) {
      alert("Please log in first");
      return;
    }
    if (!courseName) {
      alert("Please select a course first");
      return;
    }
    if (!password) {
      alert("Please set a password first");
      return;
    }
    if (isBooking) {
      return;
    }
    if (!date) {
      return;
    }
    setIsBooking(true);
    await axios.post("/api/int/scheduler/booking/", {
      date: format(date, "dd-MM-yyyy"),
      time,
      password,
      courseName,
      username,
    });
    refreshBookings();
    setIsBooking(false);
  };
  const options = generateTimes();
  return (
    <Card>
      <Typography level="h4">Add booking</Typography>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAddBooking();
          }}
        >
          <FormControl sx={{ my: 1 }}>
            <FormLabel>Date</FormLabel>
            <DatePicker
              InputProps={{ size: "small" }}
              value={date}
              onChange={(e) => setDate(e)}
              inputFormat={"EEEE do MMM yyyy"}
              showDaysOutsideCurrentMonth
              disableMaskedInput
              renderInput={(params) => <TextField fullWidth {...params} />}
            />
          </FormControl>
          <Box display="flex" alignItems="flex-end" width={"100%"} gap={1}>
            <FormControl sx={{ flexGrow: 1 }}>
              <FormLabel>Time</FormLabel>
              <Autocomplete
                onChange={(e, val) => setTime(val!)}
                value={time}
                // every 8 minutes starting from 6am to 6pm
                options={options}
              />
            </FormControl>
          </Box>
          <CardActions>
            <Button disabled={isBooking} onClick={handleAddBooking}>
              {isBooking ? <CircularProgress /> : "Book"}
            </Button>
          </CardActions>
        </form>
      </CardContent>
    </Card>
  );
};

function generateTimes() {
  const intervalMinutes = 8;
  const times: string[] = [];

  // Create Date objects with an arbitrary date; only the time part matters.
  let current = new Date(0);
  current.setHours(6, 0, 0, 0);

  const endTime = new Date(0);
  endTime.setHours(18, 0, 0, 0);

  while (current <= endTime) {
    // Format hours and minutes as HH:MM
    const hours = current.getHours().toString().padStart(2, "0");
    const minutes = current.getMinutes().toString().padStart(2, "0");
    times.push(`${hours}:${minutes}`);

    // Add 8 minutes
    current = new Date(current.getTime() + intervalMinutes * 60000);
  }

  return times;
}
