import axios from "axios";
import { atom, selector } from "recoil";

export const currentBookings = selector({
  key: "currentBookings",
  get: async () => {
    return (await axios.get("/brs/curr_bookings/")).data;
  },
});

export const loggedIn = atom({
  key: "loggedIn",
  default: false,
});
