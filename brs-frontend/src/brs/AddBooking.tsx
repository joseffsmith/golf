import {
  Box,
  Button,
  Card,
  CardActions,
  // CardHeader,
  CardContent,
  FormControl,
  FormLabel,
  Option,
  Select,
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
  const [hour, setHour] = useState(8);
  const [minute, setMinute] = useState(30);
  const [isBooking, setIsBooking] = useState(false);

  const refreshBookings = useRecoilRefresher_UNSTABLE(currentBookings);

  const handleAddBooking = async () => {
    const password = localStorage.getItem("brs-password");
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
    await axios.post("/api/scheduler/booking/", {
      date: format(date, "yyyy/MM/dd"),
      hour,
      minute,
      password: localStorage.getItem("brs-password"),
    });
    refreshBookings();
    setIsBooking(false);
  };
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
            <Typography level="body-lg" sx={{ mb: 1 }}>
              :
            </Typography>
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
            <Button disabled={isBooking} onClick={handleAddBooking}>
              Book
            </Button>
          </CardActions>
        </form>
      </CardContent>
    </Card>
  );
};
