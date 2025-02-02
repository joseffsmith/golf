import {
  Card,
  Box,
  LinearProgress,
  // CardHeader,
  CardContent,
  Input,
  Option,
  Typography,
  Button,
  Select,
  FormControl,
  FormLabel,
  CardActions,
} from "@mui/joy";
import { FormControlLabel, TextField } from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers";
import axios from "axios";
import { format } from "date-fns";
import { useState } from "react";
import { useRecoilRefresher_UNSTABLE, useRecoilValue } from "recoil";
import { currentBookings, loggedIn } from "./atoms";

export const AddBooking = () => {
  var nextWeek = new Date(new Date().getTime() + 7 * 24 * 60 * 60 * 1000);
  const [date, setDate] = useState<Date | null>(nextWeek);
  const [hour, setHour] = useState(8);
  const [minute, setMinute] = useState(30);
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
    await axios.post("/api/scheduler/booking/", {
      date: format(date, "yyyy/MM/dd"),
      hour,
      minute,
    });
    refreshBookings();
    setIsBooking(false);
  };
  return (
    <Card>
      <Box height={"4px"}>{isBooking && <LinearProgress />}</Box>
      <Typography level="h4">Add booking</Typography>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAddBooking();
          }}
        >
          <Box>
            <DatePicker
              value={date}
              onChange={(e) => setDate(e)}
              inputFormat={"EEEE do MMM yyyy"}
              showDaysOutsideCurrentMonth
              disableMaskedInput
              renderInput={(params) => <TextField fullWidth {...params} />}
              // renderInput={(params) => <TextField {...params} />}
              label="date"
            />
          </Box>
          <Box display="flex" alignItems="flex-end" width={"100%"}>
            <FormControl sx={{ flexGrow: 1 }}>
              <FormLabel>Hour</FormLabel>
              <Select
                onChange={(e, val) => setHour(val!)}
                value={hour}
                // label="hour"
              >
                <Option value={6}>6</Option>
                <Option value={7}>7</Option>
                <Option value={8}>8</Option>
                <Option value={9}>9</Option>
                <Option value={10}>10</Option>
                <Option value={11}>11</Option>
                <Option value={12}>12</Option>
                <Option value={13}>13</Option>
                <Option value={14}>14</Option>
                <Option value={15}>15</Option>
                <Option value={16}>16</Option>
                <Option value={17}>17</Option>
                <Option value={18}>18</Option>
              </Select>
            </FormControl>
            <Typography level="body-lg">:</Typography>
            <FormControl sx={{ flexGrow: 1 }}>
              <FormLabel>Minute</FormLabel>
              <Select
                onChange={(e, val) => setMinute(val!)}
                value={minute}
                // label="minute"
              >
                <Option value={0}>0</Option>
                <Option value={10}>10</Option>
                <Option value={20}>20</Option>
                <Option value={30}>30</Option>
                <Option value={40}>40</Option>
                <Option value={50}>50</Option>
              </Select>
            </FormControl>
          </Box>
          <CardActions>
            <Button
              disabled={isBooking || !isLoggedIn}
              onClick={handleAddBooking}
            >
              Book
            </Button>
          </CardActions>
        </form>
      </CardContent>
    </Card>
  );
};
