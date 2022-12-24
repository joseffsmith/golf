import {
  Card,
  Box,
  LinearProgress,
  CardHeader,
  CardContent,
  TextField,
  MenuItem,
  Typography,
  Button,
} from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers";
import axios from "axios";
import { format } from "date-fns";
import { useState } from "react";
import { useRecoilRefresher_UNSTABLE, useRecoilValue } from "recoil";
import { currentBookings, loggedIn } from "./atoms";

export const AddBooking = () => {
  var nextWeek = new Date(new Date().getTime() + 7 * 24 * 60 * 60 * 1000);
  const [date, setDate] = useState<Date | null>(nextWeek);
  const [hour, setHour] = useState("8");
  const [minute, setMinute] = useState("30");
  const [isBooking, setIsBooking] = useState(false);
  const isLoggedIn = useRecoilValue(loggedIn);

  const refreshBookings = useRecoilRefresher_UNSTABLE(currentBookings);

  const handleAddBooking = async () => {
    if (isBooking) {
      return;
    }
    if (!date) {
      return;
    }
    setIsBooking(true);
    await axios.post("/brs/scheduler/booking/", {
      date: format(date, "yyyy/MM/dd"),
      hour,
      minute,
    });
    refreshBookings();
    setIsBooking(false);
  };
  return (
    <Card sx={{ maxWidth: "500px", width: "95%", overflow: "visible", my: 2 }}>
      <Box height={"4px"}>{isBooking && <LinearProgress />}</Box>
      <CardHeader title="Add booking" />
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAddBooking();
          }}
        >
          <Box p={2}>
            <DatePicker
              value={date}
              onChange={(e) => setDate(e)}
              inputFormat={"dd/MM/yyyy"}
              renderInput={(params) => <TextField fullWidth {...params} />}
              label="date"
            />
          </Box>
          <Box p={2} display="flex" alignItems="center">
            <TextField
              fullWidth
              select
              onChange={(e) => setHour(e.target.value)}
              value={hour}
              label="hour"
            >
              <MenuItem value={6}>6</MenuItem>
              <MenuItem value={7}>7</MenuItem>
              <MenuItem value={8}>8</MenuItem>
              <MenuItem value={9}>9</MenuItem>
              <MenuItem value={10}>10</MenuItem>
              <MenuItem value={11}>11</MenuItem>
              <MenuItem value={12}>12</MenuItem>
              <MenuItem value={13}>13</MenuItem>
              <MenuItem value={14}>14</MenuItem>
              <MenuItem value={15}>15</MenuItem>
              <MenuItem value={16}>16</MenuItem>
              <MenuItem value={17}>17</MenuItem>
              <MenuItem value={18}>18</MenuItem>
            </TextField>
            <Typography variant={"h5"}>:</Typography>
            <TextField
              fullWidth
              select
              onChange={(e) => setMinute(e.target.value)}
              value={minute}
              label="minute"
            >
              <MenuItem value={0}>0</MenuItem>
              <MenuItem value={10}>10</MenuItem>
              <MenuItem value={20}>20</MenuItem>
              <MenuItem value={30}>30</MenuItem>
              <MenuItem value={40}>40</MenuItem>
              <MenuItem value={50}>50</MenuItem>
            </TextField>
          </Box>
          <Box p={2} display="flex" justifyContent={"flex-end"}>
            <Button
              variant="contained"
              disabled={isBooking || !isLoggedIn}
              onClick={handleAddBooking}
            >
              Book
            </Button>
          </Box>
        </form>
      </CardContent>
    </Card>
  );
};
