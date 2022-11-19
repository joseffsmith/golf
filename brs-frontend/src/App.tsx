import { forwardRef, useEffect, useState } from "react";

import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import "./App.css";
import {
  AppBar,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  CssBaseline,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  Menu,
  MenuItem,
  Paper,
  Snackbar,
  TextField,
  Toolbar,
  Typography,
} from "@mui/material";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import axios, { AxiosError } from "axios";
import { format } from "date-fns";
import MuiAlert, { AlertProps } from "@mui/material/Alert";
import { MoreVert } from "@mui/icons-material";

const api_url = import.meta.env.VITE_API_URL;
const api_key = import.meta.env.VITE_API_SECRET;
axios.defaults.baseURL = api_url;
axios.defaults.headers["X-MS-JS-API-KEY"] = api_key;

const App = () => {
  const [error, setError] = useState<AxiosError | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [password, _setPassword] = useState(localStorage.getItem("password"));
  const [showModal, setShowModal] = useState(true);

  const setPassword = (password: string) => {
    localStorage.setItem("password", password);
    _setPassword(password);
  };
  const handleLogin = () => {
    if (!password) {
      return;
    }
    setIsLoggingIn(true);
    axios
      .get("/login/", { params: { password } })
      .then(() => {
        setIsLoggedIn(true);
        setShowModal(false);
      })
      .catch((err) => {
        setError(new AxiosError("Login failed"));
      })
      .finally(() => {
        setIsLoggingIn(false);
      });
  };

  axios.interceptors.response.use(
    (resp) => {
      return resp;
    },
    (err) => {
      setError(err);
      return Promise.reject(err);
    }
  );
  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <CssBaseline />
      <Box
        sx={{
          backgroundColor: (theme) => theme.palette.grey[100],
          overflowY: "auto",
        }}
        width="100%"
        pt={10}
        display="flex"
        flexDirection={"column"}
        justifyContent="flex-start"
        alignItems={"center"}
      >
        <AppBar position="fixed">
          <Toolbar>
            <Typography
              variant="h6"
              component="div"
              sx={{ flexGrow: 1, textAlign: "left" }}
            >
              Golf app
            </Typography>
            <Button
              variant="outlined"
              sx={{ color: "white" }}
              onClick={() => setShowModal(true)}
            >
              Change password
            </Button>
          </Toolbar>
        </AppBar>
        {isLoggedIn && <AuthedApp />}
      </Box>

      {error && (
        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError(null)}
        >
          <Alert onClose={() => setError(null)} severity="error">
            There was an issue, error: "{error.message}".
          </Alert>
        </Snackbar>
      )}
      <Dialog open={showModal}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleLogin();
          }}
        >
          <Box height={4}>{isLoggingIn && <LinearProgress />}</Box>
          <DialogTitle>Enter your BRS password</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button
              variant="contained"
              onClick={handleLogin}
              disabled={password === "" || isLoggingIn}
            >
              Save
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </LocalizationProvider>
  );
};

const Alert = forwardRef<HTMLDivElement, AlertProps>(function Alert(
  props,
  ref
) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

function AuthedApp() {
  var nextWeek = new Date(new Date().getTime() + 7 * 24 * 60 * 60 * 1000);
  const [date, setDate] = useState(nextWeek);
  const [hour, setHour] = useState(8);
  const [minute, setMinute] = useState(30);
  const [isBooking, setIsBooking] = useState(false);
  const [isLoadingBookings, setIsLoadingBookings] = useState(false);
  const [bookings, setBookings] = useState({ jobs: [] });
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    loadBookings();
  }, []);

  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const loadBookings = async () => {
    setIsLoadingBookings(true);
    const resp = await axios.get("/curr_bookings/");
    setBookings(resp.data);
    setIsLoadingBookings(false);
  };

  const clearBookings = async () => {
    setIsLoadingBookings(true);
    await axios.get("/clear_bookings/");
    setBookings({ jobs: [] });
    setIsLoadingBookings(false);
  };

  const handleAddBooking = async () => {
    if (isBooking) {
      return;
    }
    setIsBooking(true);
    await axios.post("/scheduler/booking/", {
      date: format(date, "yyyy/MM/dd"),
      hour,
      minute,
    });
    await loadBookings();
    setIsBooking(false);
  };

  return (
    <>
      <Card sx={{ width: 400, maxWidth: "90%", mx: 4, mb: 2 }}>
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
                disabled={isBooking}
                onClick={handleAddBooking}
              >
                Book
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>

      <Card sx={{ width: 400, maxWidth: "90%", mx: 4, mb: 2 }}>
        <Box height={"4px"}>{isLoadingBookings && <LinearProgress />}</Box>
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
        <CardContent>
          <List>
            {bookings.jobs.map((b) => {
              return (
                <ListItem
                  key={b}
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                  }}
                >
                  <>
                    {b}
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
      </Card>
    </>
  );
}

export default App;
