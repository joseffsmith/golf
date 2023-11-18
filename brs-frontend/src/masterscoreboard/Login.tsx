import { Visibility, VisibilityOff } from "@mui/icons-material";
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  LinearProgress,
  TextField,
} from "@mui/material";
import axios, { AxiosError } from "axios";
import { useState } from "react";
import { useRecoilState, useSetRecoilState } from "recoil";
import { errors } from "../atoms";
import { loggedIn, passWord } from "./atoms";

export const Login = () => {
  const setIsLoggedIn = useSetRecoilState(loggedIn);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [password, _setPassword] = useRecoilState(passWord);
  const [passwordVisible, setPasswordVisibility] = useState(false);
  const setErrors = useSetRecoilState(errors);
  // const [username, changeUsername] = useRecoilState(userName);

  const setPassword = (password: string) => {
    localStorage.setItem("ms-password", password);
    _setPassword(password);
  };
  const handleLogin = () => {
    if (!password) {
      return;
    }
    setIsLoggingIn(true);
    axios
      .get("/int/login/", { params: { password } })
      .then(() => {
        setIsLoggedIn(true);
      })
      .catch((err) => {
        setErrors((errors) => [...errors, new AxiosError("Login failed")]);
      })
      .finally(() => {
        setIsLoggingIn(false);
      });
  };

  const setIconVisiblity = () => {
    setPasswordVisibility(!passwordVisible);
  };

  return (
    <Card sx={{ maxWidth: "500px", width: "95%", overflow: "visible", my: 2 }}>
      <Box height={4}>{isLoggingIn && <LinearProgress />}</Box>
      <CardHeader title="MasterScoreboard password" />
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleLogin();
        }}
      ></form>
      <CardContent>
        <Box p={2}>
          {/* <Partner
            label="Username"
            partner={username}
            setPartner={changeUsername}
            current_players={[username]}
          /> */}

          <TextField
            fullWidth
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type={passwordVisible ? "text" : "password"}
            InputProps={{
              endAdornment: (
                <IconButton onClick={setIconVisiblity}>
                  {passwordVisible ? <Visibility /> : <VisibilityOff />}
                </IconButton>
              ),
            }}
          />
        </Box>
        <Box p={2} display="flex" justifyContent="flex-end">
          <Button
            variant="contained"
            onClick={handleLogin}
            disabled={password === "" || isLoggingIn}
          >
            Login
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};
