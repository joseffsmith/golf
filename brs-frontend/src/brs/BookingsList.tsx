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
} from "@mui/material";
import axios from "axios";
import { useState } from "react";
import { useRecoilValueLoadable } from "recoil";
import { currentBookings } from "./atoms";

export const Bookings = () => {
  const bookings = useRecoilValueLoadable(currentBookings);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const clearBookings = async () => {
    await axios.get("/brs/clear_bookings/");
  };
  return (
    <Card sx={{ maxWidth: "95%", width: "100%", overflow: "visible", my: 2 }}>
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
                disabled
                color="error.main"
                onClick={async () => {
                  await clearBookings();
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
            {bookings.contents.jobs.map((b) => {
              return (
                <ListItem
                  key={b.description}
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                  }}
                >
                  <>
                    {b.description}
                    {/* <Box>
                      Tee time:{" "}
                      <code style={{ display: "inline" }}>{b.id}</code>
                      </Box>
                      <Box>
                      Booking time:{" "}
                      <code style={{ display: "inline" }}>{b.time}</code>
                    </Box> */}
                  </>
                </ListItem>
              );
            })}
          </List>
        </CardContent>
      )}
    </Card>
  );
};
