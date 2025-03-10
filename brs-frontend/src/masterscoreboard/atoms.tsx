import axios from "axios";
import { atom, selector } from "recoil";

export type Comp = {
  id: string;
  date: string;
  name: string;
  "signup-date": number | null;
  "signup-close": number | null;
  // gender: string;
  // notes: string;
  // action: string;
  // html_description: string;
  // book_from: number | null;
  // bookings_close_by: number | null;
};

export type Booking = {
  comp: Comp;
  booking_times: string[];
  player_ids: string[];
  booked: boolean;
};

export const currentBookings = selector({
  key: "intcurrentBookings",
  get: async () => {
    return (await axios.get("/api/int/curr_bookings/")).data;
  },
});

export const comps = selector<Comp[]>({
  key: "MScomps",
  get: async () => {
    const resp = await axios.get<{ comps: { [key: string]: Comp } }>(
      "/api/int/curr_comps/"
    );
    return Object.values(resp.data.comps);
  },
});

export const bookings = selector<Booking[]>({
  key: "MSbookings",
  get: async () => {
    const resp = await axios.get<{ bookings: Booking[] }>(
      "/api/int/curr_bookings/"
    );
    return resp.data.bookings;
  },
});
export const players = selector<Array<{ id: string; name: string }>>({
  key: "MSplayers",
  get: async () => {
    const resp = await axios.get<{
      players: Array<{ id: string; name: string }>;
    }>("/api/int/curr_players/");
    return resp.data.players;
  },
});

export const currComp = atom<Comp | null>({
  key: "MScurrComp",
  default: null,
});

export const loggedIn = atom({
  key: "MSloggedIn",
  default: false,
});

export const teeTimes = atom<{ hour: string; minute: string; id: number }[]>({
  key: "MSteeTimes",
  default: [{ hour: "08", minute: "30", id: 0 }],
});

export const userName = atom({
  key: "MSuserName",
  default: "254:~:Smith, Tony ",
});

export const passWord = atom({
  key: "MSpassWord",
  default: localStorage.getItem("ms-password") ?? "",
});

export const sortedPlayers = selector({
  key: "sortedPlayers",
  get: ({ get }) => {
    const ps = get(players);

    return ps;
    // return Object.fromEntries(
    //   Object.entries(ps)
    //     .filter((v: any) => {
    //       const [key, val] = v;
    //       if (val.length > 200) {
    //         return false;
    //       }
    //       return true;
    //     })
    //     .sort((a, b) => {
    //       const [keya, vala] = a;
    //       const [keyb, valb] = b;
    //       if (vala < valb) {
    //         return -1;
    //       }
    //       if (vala > valb) {
    //         return 1;
    //       }
    //       return 0;
    //     })
    // );
  },
});

export const book_comp = async (
  comp_id: string,
  signup_date: number,
  hour: string,
  minute: string,
  partnerIds: string[]
) => {
  return await axios.post("/api/int/scheduler/booking/", {
    comp_id,
    wait_until: signup_date,
    hour,
    minute,
    partnerIds,
  });
};
