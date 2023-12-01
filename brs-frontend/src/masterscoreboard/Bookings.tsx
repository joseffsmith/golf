import { MoreVert } from "@mui/icons-material";
import {
  Card,
  Box,
  LinearProgress,
  CardHeader,
  IconButton,
  Menu,
  MenuItem,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Button,
} from "@mui/material";
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
    await axios.get("/int/clear_bookings/");
  };
  return (
    <Card sx={{ maxWidth: "500px", width: "95%", overflow: "visible", my: 2 }}>
      <Box height={"4px"}>
        {bookings.state === "loading" && <LinearProgress />}
      </Box>
      <CardHeader
        title="Scheduled"
        action={
          <>
            <IconButton onClick={handleClick} aria-label="settings">
              <MoreVert />
            </IconButton>
            <Menu
              id="basic-menu"
              anchorEl={anchorEl}
              open={open}
              onClose={handleClose}
              MenuListProps={{
                "aria-labelledby": "basic-button",
              }}
            >
              <MenuItem
                color="error.main"
                onClick={async () => {
                  await clearBookings();
                  refreshBookings();
                  handleClose();
                }}
              >
                Clear bookings
              </MenuItem>
            </Menu>
          </>
        }
      />
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
                  hour={b.kwargs.hour}
                  minute={b.kwargs.minute}
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
  hour,
  minute,
  waitUntil,
}: {
  description: string;
  id: string;
  date?: string;
  minute?: string;
  hour?: string;
  waitUntil?: string;
}) => {
  const [isCancellingJob, setIsCancellingJob] = useState(false);
  const refreshBookings = useRecoilRefresher_UNSTABLE(currentBookings);

  const cancelJob = async () => {
    setIsCancellingJob(true);
    try {
      await axios.post("/int/delete_booking/", { id });
    } finally {
      refreshBookings();
      setIsCancellingJob(false);
    }
  };
  return (
    <ListItem
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
      }}
    >
      <ListItemText
        secondary={waitUntil ? `Booking ${moment(waitUntil).fromNow()}` : null}
      >
        Comp date: {date}, time: {hour}:{minute}
      </ListItemText>
      <ListItemSecondaryAction>
        <Button disabled={isCancellingJob} onClick={cancelJob}>
          Cancel
        </Button>
      </ListItemSecondaryAction>
    </ListItem>
  );
};
