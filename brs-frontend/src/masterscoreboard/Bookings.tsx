import MoreVert from "@mui/icons-material/MoreVert";
import {
  Box,
  Button,
  Card,
  CardContent,
  Dropdown,
  List,
  ListItem,
  ListItemContent,
  Menu,
  MenuButton,
  MenuItem,
  Typography,
} from "@mui/joy";
import axios from "axios";
import moment from "moment";
import { useState } from "react";
import { useRecoilRefresher_UNSTABLE, useRecoilValueLoadable } from "recoil";
import { currentBookings } from "./atoms";

export const Bookings = () => {
  const bookings = useRecoilValueLoadable(currentBookings);
  const refreshBookings = useRecoilRefresher_UNSTABLE(currentBookings);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const clearBookings = async () => {
    await axios.get("/api/int/clear_bookings/");
  };
  return (
    <Card sx={{ position: "relative" }}>
      <Box
        display={"flex"}
        justifyContent={"space-between"}
        alignItems={"center"}
      >
        <Typography level="title-lg">Scheduled</Typography>
        <Dropdown>
          <MenuButton aria-label="settings">
            <MoreVert />
          </MenuButton>

          <Menu
            id="basic-menu"
            // anchorEl={anchorEl}
            // open={open}
            // onClose={handleClose}
          >
            <MenuItem
              color="danger"
              onClick={async () => {
                await clearBookings();
                refreshBookings();
                // handleClose();
              }}
            >
              Clear bookings
            </MenuItem>
          </Menu>
        </Dropdown>
      </Box>

      {bookings.state === "hasValue" && (
        <CardContent>
          <List>
            {bookings.contents.jobs.map((b, idx) => {
              return (
                <Booking
                  key={b.id}
                  description={b.description}
                  id={b.id}
                  date={b.kwargs.date}
                  time={b.kwargs.time}
                  waitUntil={b.kwargs.wait_until}
                />
              );
            })}
          </List>
        </CardContent>
      )}
    </Card>
  );
};

const Booking = ({
  description,
  id,
  date,

  time,
  waitUntil,
}: {
  description: string;
  id: string;
  date?: string;
  time?: string;
  waitUntil?: string;
}) => {
  const [isCancellingJob, setIsCancellingJob] = useState(false);
  const refreshBookings = useRecoilRefresher_UNSTABLE(currentBookings);

  const cancelJob = async () => {
    setIsCancellingJob(true);
    try {
      await axios.post("/api/int/delete_booking/", { id });
    } finally {
      refreshBookings();
      setIsCancellingJob(false);
    }
  };
  return (
    <ListItem
      endAction={
        <Button disabled={isCancellingJob} onClick={cancelJob}>
          Cancel
        </Button>
      }
    >
      <ListItemContent>
        <Typography level="title-sm">
          Comp date: {moment(date).format("ddd DD MMM yyyy")}, time: {time}
        </Typography>
        {waitUntil ? (
          <Typography level="body-sm">
            Booking {moment(waitUntil).fromNow()}
          </Typography>
        ) : (
          "Booking within 30 seconds"
        )}
      </ListItemContent>
    </ListItem>
  );
};
